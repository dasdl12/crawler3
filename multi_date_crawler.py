"""
多日期采集管理器
支持批量采集多个日期的资讯数据
"""
import asyncio
import json
import os
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor
import threading

from config import Config
from scrapers.sohu_scraper import SohuScraper
from scrapers.aibase_news_scraper import AIBaseNewsScraper

logger = logging.getLogger(__name__)

class MultiDateCrawler:
    """多日期采集管理器"""
    
    def __init__(self):
        self.progress_callback = None
        self.is_running = False
        
    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback
        
    def _update_progress(self, status: str, progress: int, message: str, details: List[str] = None):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback({
                "status": status,
                "progress": progress,
                "message": message,
                "details": details or []
            })
    
    async def crawl_multiple_dates(self, date_list: List[str], sources: List[str] = None) -> Dict:
        """
        采集多个日期的资讯
        Args:
            date_list: 日期列表 ['2024-09-16', '2024-09-17', '2024-09-18']
            sources: 数据源列表 ['tencent', 'aibase']
        Returns:
            采集结果字典
        """
        if sources is None:
            sources = ['tencent', 'aibase']
            
        self.is_running = True
        all_articles = []
        total_dates = len(date_list)
        errors = []
        
        try:
            self._update_progress("running", 0, f"开始采集 {total_dates} 个日期的资讯...", 
                                [f"目标日期: {', '.join(date_list)}", f"数据源: {', '.join(sources)}"])
            
            # 按日期逐个采集
            for i, target_date in enumerate(date_list):
                if not self.is_running:
                    break
                    
                date_progress = int((i / total_dates) * 90)  # 留10%给最后的保存
                self._update_progress("running", date_progress, 
                                    f"正在采集 {target_date} 的资讯... ({i+1}/{total_dates})")
                
                try:
                    # 采集单个日期的数据
                    date_articles, date_errors = await self._crawl_single_date(target_date, sources)
                    all_articles.extend(date_articles)
                    errors.extend(date_errors)
                    
                    self._update_progress("running", date_progress + 5, 
                                        f"{target_date} 采集完成，获得 {len(date_articles)} 篇文章")
                    
                except Exception as e:
                    error_msg = f"{target_date} 采集失败: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    self._update_progress("running", date_progress, error_msg)
            
            # 保存合并结果
            return await self._save_results(date_list, all_articles, sources, errors)
            
        except Exception as e:
            error_msg = f"多日期采集失败: {str(e)}"
            logger.error(error_msg)
            self._update_progress("error", 0, error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'articles': all_articles,
                'total': len(all_articles),
                'date_range': date_list,
                'sources': sources,
                'errors': errors
            }
        finally:
            self.is_running = False
    
    async def _crawl_single_date(self, target_date: str, sources: List[str]) -> Tuple[List, List[str]]:
        """
        采集单个日期的资讯
        Args:
            target_date: 目标日期 YYYY-MM-DD
            sources: 数据源列表
        Returns:
            (文章列表, 错误列表)
        """
        articles = []
        errors = []
        
        # 转换日期格式
        target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # 采集腾讯研究院
        if 'tencent' in sources:
            try:
                scraper = SohuScraper()
                tencent_articles, tencent_errors = await scraper.scrape_articles(target_date_obj, target_date_obj)
                articles.extend(tencent_articles)
                errors.extend([f"腾讯研究院({target_date}): {error}" for error in tencent_errors])
                logger.info(f"腾讯研究院 {target_date}: 获取 {len(tencent_articles)} 篇文章")
            except Exception as e:
                error_msg = f"腾讯研究院 {target_date} 采集异常: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # 采集AIBase快讯
        if 'aibase' in sources:
            try:
                scraper = AIBaseNewsScraper()
                # AIBase采集前一天的数据
                aibase_date_obj = target_date_obj - timedelta(days=1)
                aibase_date = aibase_date_obj.strftime('%Y-%m-%d')
                
                news_list = await scraper.get_news_by_date(aibase_date)
                
                # 转换为Article格式
                for news in news_list:
                    # 创建一个简单的文章对象
                    article_dict = {
                        'title': news.get('title', ''),
                        'date': target_date,  # 使用目标日期
                        'content': news.get('content', news.get('summary', '')),
                        'url': news.get('url', ''),
                        'source': news.get('source', 'AIBase快讯'),
                        'weight': news.get('weight', 5)
                    }
                    
                    # 创建一个具有to_dict方法的对象
                    class SimpleArticle:
                        def __init__(self, data):
                            self.__dict__.update(data)
                        def to_dict(self):
                            return self.__dict__
                    
                    articles.append(SimpleArticle(article_dict))
                
                logger.info(f"AIBase快讯 {target_date}(实际{aibase_date}): 获取 {len(news_list)} 条快讯")
            except Exception as e:
                error_msg = f"AIBase快讯 {target_date} 采集异常: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return articles, errors
    
    async def _save_results(self, date_list: List[str], all_articles: List, sources: List[str], errors: List[str]) -> Dict:
        """保存采集结果"""
        self._update_progress("running", 90, "正在保存采集结果...")
        
        # 生成合并的缓存文件
        date_range = f"{date_list[0]}_to_{date_list[-1]}" if len(date_list) > 1 else date_list[0]
        cache_file = os.path.join(Config.CACHE_DIR, f"articles_multi_{date_range.replace('-', '')}.json")
        
        result_data = {
            'date_range': date_list,
            'articles': [article.to_dict() if hasattr(article, 'to_dict') else article for article in all_articles],
            'timestamp': datetime.now().isoformat(),
            'total': len(all_articles),
            'sources': sources,
            'errors': errors
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        success_msg = f"多日期采集完成！共获取 {len(all_articles)} 篇文章"
        if errors:
            success_msg += f"，{len(errors)} 个错误"
            
        self._update_progress("completed", 100, success_msg, 
                            [f"采集日期: {len(date_list)} 天", 
                             f"成功文章: {len(all_articles)} 篇",
                             f"错误数量: {len(errors)} 个",
                             f"缓存文件: {os.path.basename(cache_file)}"])
        
        return {
            'success': True,
            'articles': [article.to_dict() if hasattr(article, 'to_dict') else article for article in all_articles],
            'total': len(all_articles),
            'date_range': date_list,
            'sources': sources,
            'errors': errors,
            'cache_file': cache_file
        }
    
    def stop_crawling(self):
        """停止采集"""
        self.is_running = False
        logger.info("多日期采集已停止")

    @staticmethod
    def generate_date_range(start_date: str, end_date: str) -> List[str]:
        """
        生成日期范围列表
        Args:
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
        Returns:
            日期列表
        """
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        date_list = []
        current = start
        while current <= end:
            date_list.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return date_list

    @staticmethod
    def parse_date_input(date_input: str) -> List[str]:
        """
        解析日期输入，支持多种格式
        Args:
            date_input: 日期输入，支持：
                - 单个日期: "2024-09-16"
                - 日期范围: "2024-09-16,2024-09-18"
                - 日期列表: "2024-09-16,2024-09-17,2024-09-18"
        Returns:
            日期列表
        """
        if not date_input:
            return [date.today().strftime('%Y-%m-%d')]
        
        # 分割日期
        dates = [d.strip() for d in date_input.split(',')]
        
        # 验证日期格式
        valid_dates = []
        for date_str in dates:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                valid_dates.append(date_str)
            except ValueError:
                logger.warning(f"无效日期格式: {date_str}")
        
        return valid_dates if valid_dates else [date.today().strftime('%Y-%m-%d')]


# 全局实例
multi_date_crawler = MultiDateCrawler()