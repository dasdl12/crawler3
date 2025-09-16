<<<<<<< HEAD
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import asyncio
import aiohttp
import re
import logging
from concurrent.futures import ThreadPoolExecutor
from playwright.async_api import async_playwright, Page, Browser
=======
"""
AIBase实时快讯采集器
监控 https://news.aibase.com/zh/news 页面的实时更新
"""
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
import asyncio
import re
import logging
>>>>>>> e0628e40f446a2e97574cb1ad9e02f4dcc7c8d1f

try:
    from config import IMAGE_CONFIG
except ImportError:
<<<<<<< HEAD
=======
    # 如果无法导入config，使用默认配置
>>>>>>> e0628e40f446a2e97574cb1ad9e02f4dcc7c8d1f
    IMAGE_CONFIG = {
        'enabled': True,
        'max_images_per_news': 5,
        'processing_timeout': 30
    }

logger = logging.getLogger(__name__)

class AIBaseNewsScraper:
<<<<<<< HEAD
    """AIBase实时快讯采集器 - 高速优化版本"""
=======
    """AIBase实时快讯采集器 - 独立实现，不继承BaseScraper"""
>>>>>>> e0628e40f446a2e97574cb1ad9e02f4dcc7c8d1f
    
    def __init__(self):
        self.name = "AIBase快讯"
        self.base_url = "https://news.aibase.com/zh/news"
        self.browser = None
        self.page = None
        self.logger = logging.getLogger(self.__class__.__name__)
<<<<<<< HEAD
        self.source_weight = 5
        self.latest_news_id = None
        
        # 新增：缓存和优化相关
        self.id_cache = set()  # 缓存已处理的ID
        self.session = None   # HTTP会话复用
        self.concurrent_limit = 25  # 增加并发限制以提高速度
        
    async def initialize_browser(self):
        """初始化浏览器实例和HTTP会话"""
=======
        self.source_weight = 5  # 权重分数
        
    async def initialize_browser(self):
        """初始化浏览器实例（用于持续监控）"""
>>>>>>> e0628e40f446a2e97574cb1ad9e02f4dcc7c8d1f
        if not self.browser:
            playwright = await async_playwright().start()
            browser_options = {
                'headless': True,
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-dev-shm-usage',
<<<<<<< HEAD
                    '--disable-blink-features=AutomationControlled',
                    '--disable-images',  # 禁用图片加载（如果不需要图片可以大幅提速）
                    '--disable-javascript',  # 如果可能的话禁用JS
                ]
            }
            self.browser = await playwright.chromium.launch(**browser_options)
            
        # 初始化HTTP会话
        if not self.session:
            connector = aiohttp.TCPConnector(
                limit=20,  # 连接池大小
                limit_per_host=10,
                keepalive_timeout=30
            )
            timeout = aiohttp.ClientTimeout(total=8, connect=3)  # 减少超时时间以提高速度
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )
            
    async def close_browser(self):
        """关闭浏览器和HTTP会话"""
=======
                    '--disable-blink-features=AutomationControlled'
                ]
            }
            self.browser = await playwright.chromium.launch(**browser_options)
            self.page = await self.browser.new_page()
            
            # 设置User-Agent
            await self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
    async def close_browser(self):
        """关闭浏览器实例"""
>>>>>>> e0628e40f446a2e97574cb1ad9e02f4dcc7c8d1f
        if self.page:
            await self.page.close()
            self.page = None
        if self.browser:
            await self.browser.close()
            self.browser = None
<<<<<<< HEAD
        # 修复：确保 aiohttp session 被关闭
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def _quick_check_news_exists(self, news_id: int, max_retries: int = 2) -> bool:
        """
        快速检查新闻ID是否存在（使用GET请求读取少量内容，带重试机制）
        Args:
            news_id: 新闻ID
            max_retries: 最大重试次数
        Returns:
            是否存在
        """
        if not self.session:
            await self.initialize_browser()
        
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                url = f"{self.base_url}/{news_id}"
                # 使用GET请求但限制读取的数据量
                async with self.session.get(url) as response:
                    # 读取前1024字节来判断是否为有效页面
                    try:
                        content = await response.read(1024)
                        # 检查是否为404页面或错误页面
                        if response.status == 200 and content:
                            content_str = content.decode('utf-8', errors='ignore').lower()
                            # 只检查明确的404标识，移除过于宽泛的'error'检查
                            if ('404' in content_str or 
                                'not found' in content_str or 
                                'page not found' in content_str or
                                '页面不存在' in content_str or
                                '找不到页面' in content_str):
                                logger.debug(f"ID {news_id} 检测到404页面特征")
                                return False
                            # 检查是否有正常的新闻内容标识
                            if any(keyword in content_str for keyword in ['新闻', 'news', '时间', 'date', '内容', 'content']):
                                return True
                            return True  # 默认认为是有效页面
                        elif response.status == 404:
                            return False  # 明确的404状态码
                        return False
                    except:
                        # 如果无法读取内容，仅通过状态码判断
                        return response.status == 200
            except asyncio.TimeoutError as e:
                last_error = e
                if attempt < max_retries:
                    logger.debug(f"检查新闻 {news_id} 超时，重试 {attempt + 1}/{max_retries}")
                    await asyncio.sleep(0.5 * (attempt + 1))  # 递增延迟
                    continue
                logger.debug(f"检查新闻 {news_id} 最终超时")
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    logger.debug(f"检查新闻 {news_id} 异常，重试 {attempt + 1}/{max_retries}: {e}")
                    await asyncio.sleep(0.5 * (attempt + 1))  # 递增延迟
                    continue
                logger.debug(f"检查新闻 {news_id} 最终失败: {e}")
        
        return False  # 重试失败后返回False

    async def _batch_check_news_exists(self, news_ids: List[int]) -> List[int]:
        """
        批量检查新闻ID是否存在
        Args:
            news_ids: 新闻ID列表
        Returns:
            存在的新闻ID列表
        """
        if not self.session:
            await self.initialize_browser()
            
        # 使用字典收集结果，并添加异步锁保护写入
        result_dict = {}
        result_lock = asyncio.Lock()
        semaphore = asyncio.Semaphore(self.concurrent_limit)
        
        async def check_single(news_id):
            async with semaphore:
                try:
                    logger.debug(f"开始检查 ID {news_id}")
                    exists = await self._quick_check_news_exists(news_id)
                    if exists:
                        async with result_lock:
                            result_dict[news_id] = True
                        logger.debug(f"ID {news_id} 存在")
                    else:
                        logger.debug(f"ID {news_id} 不存在")
                except Exception as e:
                    logger.debug(f"检查 ID {news_id} 时出错: {e}")
        
        tasks = [check_single(news_id) for news_id in news_ids]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # 从字典中提取存在的ID并排序
        existing_ids = sorted([news_id for news_id in result_dict.keys()])
        logger.info(f"批量检查完成，输入{len(news_ids)}个ID，找到{len(existing_ids)}个存在的ID")
        return existing_ids

    async def _get_news_html_fast(self, news_id: int) -> Optional[str]:
        """
        快速获取新闻页面HTML（使用aiohttp）
        Args:
            news_id: 新闻ID
        Returns:
            页面HTML内容
        """
        if not self.session:
            await self.initialize_browser()
            
        try:
            url = f"{self.base_url}/{news_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                return None
        except Exception as e:
            logger.debug(f"获取新闻 {news_id} HTML失败: {e}")
            return None

    def _parse_news_from_html(self, news_id: int, html: str) -> Optional[Dict]:
        """
        从HTML中快速解析新闻信息（使用正则表达式）
        Args:
            news_id: 新闻ID
            html: 页面HTML
        Returns:
            新闻数据字典
        """
        try:
            # 检查是否为真正的404页面（更精确的检测）
            if self._is_404_page(html):
                return None
            
            # 使用正则表达式快速提取信息
            # 提取标题 - 增加更多匹配模式
            title_patterns = [
                r'<h1[^>]*>(.*?)</h1>',
                r'<h2[^>]*>(.*?)</h2>',
                r'<title[^>]*>(.*?)</title>',
                r'class="[^"]*title[^"]*"[^>]*>(.*?)</[^>]+>',
                r'<meta\s+property="og:title"\s+content="([^"]*)"',
                r'<meta\s+name="title"\s+content="([^"]*)"',
                r'"title"\s*:\s*"([^"]*)"',  # JSON-LD格式
                r'data-title="([^"]*)"',      # 数据属性
            ]
            
            title = ""
            for pattern in title_patterns:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                    # 清理常见的网站后缀
                    title = re.sub(r'\s*[-|_]\s*(AIBase|快讯|新闻).*$', '', title)
                    if title and len(title) > 5:
                        logger.debug(f"ID {news_id} 使用模式匹配到标题: {title[:50]}...")
                        break
            
            if not title:
                logger.debug(f"ID {news_id} 标题提取失败")
                return None
            
            # 提取发布时间
            time_patterns = [
                r'发布时间\s*[:：]\s*(\d{4}年\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{2})',
                r'(\d{4}年\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{2})',
                r'(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2})',
                r'(\d{4}/\d{2}/\d{2}\s*\d{2}:\d{2})',
                r'"datePublished"[^>]*content="([^"]*)"',
                r'<time[^>]*datetime="([^"]*)"',
            ]
            
            publish_time = ""
            for pattern in time_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    publish_time = match.group(1)
                    break
            
            # 提取内容段落
            content_patterns = [
                r'<p[^>]*>(.*?)</p>',
                r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            ]
            
            content_paragraphs = []
            for pattern in content_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    # 清理HTML标签
                    clean_text = re.sub(r'<[^>]+>', '', match).strip()
                    clean_text = re.sub(r'\s+', ' ', clean_text)
                    if clean_text and len(clean_text) > 10 and not self._is_irrelevant_content(clean_text):
                        content_paragraphs.append(clean_text)
            
            # 提取图片（如果启用）
            images = []
            if IMAGE_CONFIG.get('enabled', False):
                img_pattern = r'<img[^>]*src=["\']([^"\']*)["\'][^>]*(?:alt=["\']([^"\']*)["\'])?[^>]*>'
                img_matches = re.findall(img_pattern, html, re.IGNORECASE)
                
                for src, alt in img_matches[:IMAGE_CONFIG.get('max_images_per_news', 5)]:
                    if src:
                        # 转换为绝对URL
                        if src.startswith('/'):
                            src = f"https://news.aibase.com{src}"
                        elif src.startswith('//'):
                            src = f"https:{src}"
                        elif not src.startswith(('http://', 'https://')):
                            src = f"https://news.aibase.com/{src}"
                        
                        if not self._is_decorative_or_related_image(src, alt):
                            images.append({
                                'url': src,
                                'alt': alt.strip() if alt else '',
                                'position': len(images)
                            })
            
            # 转换时间格式
            try:
                standard_time = self._parse_publish_time(publish_time)
                if not standard_time or standard_time == datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
                    logger.debug(f"ID {news_id} 时间解析失败，原始时间: {publish_time}")
            except Exception as e:
                logger.debug(f"ID {news_id} 时间解析异常: {e}, 原始时间: {publish_time}")
                standard_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            news_data = {
                'id': news_id,
                'title': title,
                'url': f"{self.base_url}/{news_id}",
                'time': standard_time,
                'date': standard_time.split(' ')[0] if ' ' in standard_time else standard_time[:10],
                'time_text': publish_time,
                'content': '\n\n'.join(content_paragraphs),
                'images': images,
                'structured_content': [],
                'summary': "",
                'source': 'AIBase快讯',
                'weight': self.source_weight
            }
            
            return news_data
            
        except Exception as e:
            logger.warning(f"解析新闻 {news_id} HTML失败: {e}")
            return None

    async def _batch_get_news_fast(self, news_ids: List[int]) -> List[Dict]:
        """
        批量快速获取新闻信息
        Args:
            news_ids: 新闻ID列表
        Returns:
            新闻数据列表
        """
        news_list = []
        semaphore = asyncio.Semaphore(self.concurrent_limit)
        
        async def get_single_news(news_id):
            async with semaphore:
                try:
                    html = await self._get_news_html_fast(news_id)
                    if html:
                        news_data = self._parse_news_from_html(news_id, html)
                        if news_data:
                            logger.debug(f"ID {news_id} 解析成功")
                            return news_data
                        else:
                            logger.warning(f"ID {news_id} HTML解析失败，内容存在但无法解析")
                    else:
                        logger.warning(f"ID {news_id} HTML获取失败")
                except Exception as e:
                    logger.warning(f"批量获取新闻 {news_id} 异常: {e}")
                return None
        
        # 并发执行
        tasks = [get_single_news(news_id) for news_id in news_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤有效结果
        for result in results:
            if isinstance(result, dict):
                news_list.append(result)
        
        logger.info(f"批量获取完成，输入{len(news_ids)}个ID，成功解析{len(news_list)}个")
        if len(news_list) < len(news_ids):
            logger.warning(f"有{len(news_ids) - len(news_list)}个ID解析失败")
        
        return news_list

    async def _discover_latest_news_id_fast(self) -> Optional[int]:
        """
        快速发现最新新闻ID（二分查找优化）
        """
        if not self.session:
            await self.initialize_browser()
        
        try:
            # 首先尝试从首页获取
            async with self.session.get(self.base_url) as response:
                if response.status == 200:
                    html = await response.text()
                    # 查找新闻链接
                    links = re.findall(r'/news/(\d+)', html)
                    if links:
                        max_id = max(int(link) for link in links)
                        logger.info(f"从首页发现最大ID: {max_id}")
                        
                        # 使用二分查找确定真正的最新ID
                        latest_id = await self._binary_search_latest_id(max_id)
                        return latest_id
            
            # 如果首页方法失败，使用保守估计
            estimated_id = 21000  # 基于当前趋势的估计
            return await self._binary_search_latest_id(estimated_id)
            
        except Exception as e:
            logger.error(f"快速发现最新ID失败: {e}")
            return None

    async def _binary_search_latest_id(self, start_id: int) -> int:
        """
        使用二分查找确定最新的有效ID
        Args:
            start_id: 起始搜索ID
        Returns:
            最新的有效ID
        """
        # 首先向上搜索找到一个不存在的ID
        upper_bound = start_id
        step = 100
        
        while await self._quick_check_news_exists(upper_bound):
            upper_bound += step
            step = min(step * 2, 1000)  # 指数增长，但限制最大步长
        
        # 现在在 start_id 和 upper_bound 之间二分查找
        left, right = start_id, upper_bound
        latest_valid = start_id
        
        while left <= right:
            mid = (left + right) // 2
            if await self._quick_check_news_exists(mid):
                latest_valid = mid
                left = mid + 1
            else:
                right = mid - 1
        
        logger.info(f"二分查找确定最新ID: {latest_valid}")
        return latest_valid

    async def get_latest_news(self, limit: int = 10) -> List[Dict]:
        """
        获取最新快讯（高速版本）
        """
        # --- FIX START: 添加 try...finally 确保资源关闭 ---
        try:
            logger.info(f"开始高速获取最新 {limit} 条快讯")
            
            await self.initialize_browser()
            
            # 快速发现最新ID
            latest_id = await self._discover_latest_news_id_fast()
            if not latest_id:
                logger.error("无法发现最新新闻ID")
                return []
            
            # 生成候选ID列表（批量处理）
            candidate_ids = list(range(latest_id, latest_id - limit * 2, -1))  # 多取一些以防有些ID不存在
            
            # 批量检查存在性
            logger.info(f"批量检查 {len(candidate_ids)} 个候选ID的存在性...")
            existing_ids = await self._batch_check_news_exists(candidate_ids)
            
            # 取前limit个
            target_ids = existing_ids[:limit]
            
            logger.info(f"开始并发获取 {len(target_ids)} 条新闻详情...")
            # 批量获取新闻详情
            news_list = await self._batch_get_news_fast(target_ids)
            
            # 按ID降序排序（最新的在前）
            news_list.sort(key=lambda x: x['id'], reverse=True)
            
            logger.info(f"高速获取完成，共获取 {len(news_list)} 条快讯")
            return news_list
        finally:
            await self.close_browser()
        # --- FIX END ---

    async def get_news_by_date(self, target_date: str) -> List[Dict]:
        """
        获取指定日期的快讯（高速版本）
        """
        try:
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
            logger.info(f"开始高速获取 {target_date} 的快讯")
            
            await self.initialize_browser()
            
            latest_id = await self._discover_latest_news_id_fast()
            if not latest_id:
                return []
            
            all_news = []
            batch_size = 30  # 增加每批处理的数量以提高效率
            current_id = latest_id
            # --- FIX START: 修正了循环终止逻辑 ---
            stop_fetching = False # 用于控制外层 while 循环
            max_batches = 25  # 最多处理25批（500篇文章）
            batch_count = 0
            
            while not stop_fetching and batch_count < max_batches:
                # 生成一批ID
                batch_ids = list(range(current_id, current_id - batch_size, -1))
                batch_count += 1
                
                logger.info(f"处理第 {batch_count} 批 (ID {batch_ids[-1]} - {batch_ids[0]})")
                
                # 批量检查存在性
                existing_ids = await self._batch_check_news_exists(batch_ids)
                
                if not existing_ids:
                    logger.warning(f"第 {batch_count} 批没有有效ID，跳过")
                    current_id -= batch_size
                    continue
                
                # 批量获取新闻详情
                batch_news = await self._batch_get_news_fast(existing_ids)
                
                # 为了逻辑更清晰，对获取到的批次按ID降序排序
                batch_news.sort(key=lambda x: x['id'], reverse=True)

                # 标记当前批次是否包含比目标日期更早的文章
                batch_contained_older_news = False

                # 遍历当前批次的所有结果，不再提前退出
                for news in batch_news:
                    try:
                        news_date_str = news.get('time')
                        if not news_date_str:
                            continue
                        news_date = datetime.strptime(news_date_str, "%Y-%m-%d %H:%M:%S").date()
                        
                        if news_date == target_date_obj:
                            all_news.append(news)
                            logger.info(f"找到目标日期文章: ID {news['id']}")
                        elif news_date < target_date_obj:
                            logger.info(f"遇到早于目标日期的文章: ID {news['id']}, 日期 {news_date}")
                            # 只设置标志，不中断循环，确保本批次处理完
                            batch_contained_older_news = True
                    except (ValueError, KeyError):
                        # 忽略解析时间失败或缺少 'time' 键的文章
                        continue
                
                # 在处理完整个批次后，检查是否需要停止
                if batch_contained_older_news:
                    stop_fetching = True

                # --- FIX END ---
                
                current_id = min(existing_ids) - 1 if existing_ids else current_id - batch_size
                
                # 每5批输出一次进度
                if batch_count % 5 == 0:
                    logger.info(f"已处理 {batch_count} 批，找到 {len(all_news)} 篇目标日期文章")
            
            # 去重并排序，以防万一有重复ID被加入
            final_news = {item['id']: item for item in all_news}.values()
            sorted_news = sorted(list(final_news), key=lambda x: x['id'], reverse=True)

            logger.info(f"高速获取完成，共找到 {len(sorted_news)} 篇 {target_date} 的快讯")
            return sorted_news
        finally:
            await self.close_browser()


    # 保留原有的辅助方法
    def _parse_publish_time(self, publish_time: str) -> str:
        """解析发布时间为标准格式"""
        if not publish_time:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # 优先处理 ISO 格式 (YYYY-MM-DDTHH:MM:SS...)
            iso_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', publish_time)
            if iso_match:
                return datetime.fromisoformat(iso_match.group(1)).strftime("%Y-%m-%d %H:%M:%S")

            time_formats = [
                ('%Y年%m月%d日 %H:%M', r'\d{4}年\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{2}'),
                ('%Y-%m-%d %H:%M', r'\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}'),
                ('%Y/%m/%d %H:%M', r'\d{4}/\d{2}/\d{2}\s*\d{2}:\d{2}'),
                ('%m-%d %H:%M', r'\d{2}-\d{2}\s*\d{2}:\d{2}'),
                ('%m/%d %H:%M', r'\d{2}/\d{2}\s*\d{2}:\d{2}'),
            ]
            
            for fmt, pattern in time_formats:
                match = re.search(pattern, publish_time)
                if match:
                    time_str = match.group(0)
                    time_str = re.sub(r'\s+', ' ', time_str).strip()
                    
                    try:
                        dt_obj = datetime.strptime(time_str, fmt)
                        # 如果年份是1900，说明格式不带年份，需要修正为当前年份
                        if dt_obj.year == 1900 or fmt in ['%m-%d %H:%M', '%m/%d %H:%M']:
                            now = datetime.now()
                            dt_obj = dt_obj.replace(year=now.year)
                            # 如果解析出的日期比当前日期晚，说明是去年的文章
                            if dt_obj > now:
                                dt_obj = dt_obj.replace(year=now.year - 1)

                        return dt_obj.strftime("%Y-%m-%d %H:%M:00")
                    except ValueError:
                        continue
        except:
            pass
        
        # 如果都失败了，返回一个当前时间作为备用
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _is_decorative_or_related_image(self, src: str, alt: str) -> bool:
        """判断是否为装饰性图片"""
        decorative_patterns = [
            r'logo', r'icon', r'avatar', r'banner', r'placeholder',
            r'loading', r'1x1|1\*1', r'\.gif$', r'ad[s]?[_\-]',
            r'share|social', r'button|btn', r'data:image/svg',
            r'thumb|thumbnail', r'small|sm\.', r'list\.|item\.',
        ]
        
        src_lower = src.lower()
        for pattern in decorative_patterns:
            if re.search(pattern, src_lower):
                return True
        
        return False

    def _is_irrelevant_content(self, text: str) -> bool:
        """判断是否为无关内容"""
        irrelevant_patterns = [
            r'^阅读原文$', r'^查看更多$', r'^展开.*%$',
            r'^点击.*查看$', r'^相关.*：$', r'^标签.*：$',
            r'^分享$', r'^收藏$', r'^点赞$', r'^评论$',
            r'^\d+$', r'^[<>\/\s]*$',
        ]
        
        stripped_text = text.strip()
        for pattern in irrelevant_patterns:
            if re.match(pattern, stripped_text, re.IGNORECASE):
                return True
        
        return len(stripped_text) < 10

    def _is_404_page(self, html: str) -> bool:
        """更精确地检测是否为404页面"""
        # 检查页面标题是否包含404相关信息
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).lower()
            if '404' in title and ('not found' in title or 'page not found' in title or '页面不存在' in title):
                return True
        
        # 检查是否有明确的404错误信息
        error_indicators = [
            r'<h1[^>]*>.*?404.*?not found.*?</h1>',
            r'<h1[^>]*>.*?页面不存在.*?</h1>',
            r'<div[^>]*class="[^"]*error[^"]*"[^>]*>.*?404.*?</div>',
            r'<div[^>]*class="[^"]*404[^"]*"[^>]*>',
        ]
        
        for pattern in error_indicators:
            if re.search(pattern, html, re.IGNORECASE | re.DOTALL):
                return True
        
        # 检查页面内容是否过短（可能是错误页面）
        # 移除HTML标签后检查文本长度
        text_content = re.sub(r'<[^>]+>', '', html)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # 如果页面文本内容过短，可能是错误页面
        if len(text_content) < 100:
            return True
        
        return False

    # 保持接口兼容性的方法
    async def get_news_detail(self, news_url: str) -> Optional[str]:
        """获取快讯详细内容（兼容性接口）"""
        # --- FIX START: 添加 try...finally 确保资源关闭 ---
        try:
            match = re.search(r'/news/(\d+)', news_url)
            if not match:
                return None
            
            await self.initialize_browser()
            news_id = int(match.group(1))
            html = await self._get_news_html_fast(news_id)
            if html:
                news_data = self._parse_news_from_html(news_id, html)
                return news_data.get('content') if news_data else None
            return None
        finally:
            await self.close_browser()
        # --- FIX END ---

    async def get_news_in_timerange(self, hours: int = 1) -> List[Dict]:
        """获取时间范围内的快讯（高速版本）"""
        # --- FIX START: 添加 try...finally 确保资源关闭 ---
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # 注意：这里调用了 get_latest_news，它内部已经有 try/finally
            # 但为了代码的健壮性，调用方也应该有自己的资源管理，
            # 或者重构此方法以避免嵌套调用带来的复杂性。
            # 这里我们假设 get_latest_news 内部会处理好自己的资源。
            # 一个更优的结构是让 get_latest_news 不关闭 session，由最外层调用者关闭。
            # 但为了最小化改动，我们暂时保持原样。
            
            # 获取足够多的最新快讯
            news_list = await self.get_latest_news(limit=min(hours * 20, 200))
            
            result = []
            for news in news_list:
                try:
                    news_datetime = datetime.strptime(news['time'], "%Y-%m-%d %H:%M:%S")
                    if news_datetime >= cutoff_time:
                        result.append(news)
                    else:
                        break  # 由于是按时间倒序，可以直接break
                except ValueError:
                    continue
            
            logger.info(f"获取到最近{hours}小时内的快讯 {len(result)} 条")
            return result
        finally:
            # 由于 get_latest_news 已经关闭了资源，这里再次调用可能无害但非最优。
            # 一个健壮的 close_browser 应该能处理重复关闭。
            # 我已经在 close_browser 中加入了 `if self.session and not self.session.closed:` 判断。
            await self.close_browser()
        # --- FIX END ---
=======
            
    async def get_latest_news(self, limit: int = 10) -> List[Dict]:
        """
        获取最新的快讯
        Args:
            limit: 获取的快讯数量限制
        Returns:
            快讯列表
        """
        news_list = []
        
        async with async_playwright() as p:
            browser_options = {
                'headless': True,
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            }
            browser = await p.chromium.launch(**browser_options)
            page = await browser.new_page()
            
            # 设置User-Agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            try:
                # 访问快讯页面
                await page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)
                
                # 滚动页面以加载更多内容
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1500)
                
                # 获取快讯元素 - 使用更通用的选择器
                news_selectors = [
                    "article",
                    "[class*='news-item']",
                    "[class*='article']",
                    ".leftPart a",
                    "div[class*='content'] > div"
                ]
                
                news_elements = None
                for selector in news_selectors:
                    news_elements = await page.query_selector_all(selector)
                    if news_elements and len(news_elements) > 0:
                        logger.info(f"使用选择器 {selector} 找到 {len(news_elements)} 个元素")
                        break
                        
                if not news_elements:
                    logger.warning("未找到快讯元素")
                    return news_list
                    
                # 提取快讯信息
                for i, element in enumerate(news_elements[:limit]):
                    try:
                        # 获取标题 - 简化逻辑，直接从列表页获取
                        title = ""
                        
                        # 优先使用精确的标题选择器
                        title_selectors = [
                            "div.text-\\[16px\\].leading-\\[24px\\].font600.mainColor",  # 用户提供的选择器
                            "[class*='title']",
                            "h1", "h2", "h3",
                            ".title"
                        ]
                        
                        for sel in title_selectors:
                            try:
                                title_elem = await element.query_selector(sel)
                                if title_elem:
                                    title = await title_elem.text_content()
                                    if title and title.strip():
                                        logger.debug(f"使用选择器 {sel} 获取到标题: {title[:30]}...")
                                        break
                            except:
                                continue
                        
                        # 如果还是没有标题，获取第一行文本
                        if not title:
                            full_text = await element.text_content()
                            if full_text:
                                lines = full_text.strip().split('\n')
                                if lines:
                                    title = lines[0].strip()
                        
                        if not title or not title.strip():
                            logger.warning(f"元素 {i+1} 未获取到标题，跳过")
                            continue
                        
                        # 清理不可见字符（如零宽空格），但保留原始标题内容
                        title = title.strip()
                        # 移除零宽空格等不可见字符
                        title = title.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
                        logger.debug(f"获取标题 {i+1}: {title[:50]}...")
                            
                        # 获取链接
                        link = ""
                        link_elem = await element.query_selector("a[href]")
                        if link_elem:
                            link = await link_elem.get_attribute('href')
                            if link and link.startswith('/'):
                                link = "https://news.aibase.com" + link
                        else:
                            # 如果元素本身是链接
                            if await element.get_attribute('href'):
                                link = await element.get_attribute('href')
                                if link and link.startswith('/'):
                                    link = "https://news.aibase.com" + link
                                    
                        # 获取时间
                        time_text = ""
                        time_selectors = [
                            "[class*='time']",
                            "[class*='date']",
                            ".tipColor",
                            "span:has-text('前')",
                            "time"
                        ]
                        for sel in time_selectors:
                            time_elem = await element.query_selector(sel)
                            if time_elem:
                                time_text = await time_elem.text_content()
                                if time_text and time_text.strip():
                                    break
                                    
                        # 获取摘要/内容
                        summary = ""
                        content_selectors = [
                            "[class*='summary']",
                            "[class*='desc']",
                            "[class*='content']",
                            "p"
                        ]
                        for sel in content_selectors:
                            content_elem = await element.query_selector(sel)
                            if content_elem:
                                summary = await content_elem.text_content()
                                if summary and len(summary.strip()) > 10:
                                    break
                                    
                        # 解析时间
                        publish_time = self._parse_time_text(time_text)
                        
                        news_item = {
                            'title': title.strip(),
                            'url': link or self.base_url,
                            'time': publish_time,
                            'date': publish_time.split(' ')[0] if ' ' in publish_time else publish_time[:10],
                            'time_text': time_text.strip() if time_text else "",
                            'summary': summary.strip() if summary else "",
                            'source': 'AIBase快讯',
                            'weight': self.source_weight
                        }
                        
                        news_list.append(news_item)
                        logger.debug(f"获取快讯 {i+1}: {news_item['title'][:30]}...")
                        
                    except Exception as e:
                        logger.error(f"处理快讯元素时出错: {e}")
                        continue
                
                # 为每条快讯获取详细内容（在同一个浏览器会话中）
                if news_list:
                    logger.info(f"开始获取 {len(news_list)} 条快讯的详细内容和图片...")
                    for i, news in enumerate(news_list):
                        try:
                            logger.debug(f"正在获取快讯 {i+1}/{len(news_list)} 的详情: {news['url']}")
                            detailed_result = await self._get_news_detail_with_page(page, news['url'])
                            if detailed_result:
                                news['content'] = detailed_result.get('content', '')
                                news['images'] = detailed_result.get('images', [])
                                news['structured_content'] = detailed_result.get('structured_content', [])
                                logger.info(f"获取详情成功 {i+1}/{len(news_list)}: {news['title'][:30]}... (内容: {len(news['content'])}字, 图片: {len(news['images'])}张)")
                                
                                # 输出图片URL用于调试
                                if news['images']:
                                    for img_idx, img in enumerate(news['images']):
                                        logger.debug(f"  图片{img_idx+1}: {img['url'][:80]}...")
                            else:
                                logger.warning(f"获取详情失败 {i+1}/{len(news_list)}: {news['title'][:30]}... URL: {news['url']}")
                                news['content'] = ""  # 不使用摘要，避免重复内容
                                news['images'] = []
                                news['structured_content'] = []
                        except Exception as e:
                            logger.error(f"获取详情异常 {i+1}/{len(news_list)}: {e}")
                            news['content'] = ""  # 不使用摘要，避免重复内容
                            news['images'] = []
                            news['structured_content'] = []
                            
                        # 添加短暂延迟，避免请求过快
                        if i < len(news_list) - 1:
                            await page.wait_for_timeout(500)  # 500ms延迟
                        
            except Exception as e:
                logger.error(f"获取快讯失败: {e}")
            finally:
                await browser.close()
                
        logger.info(f"共获取到 {len(news_list)} 条快讯")
        return news_list
        
    async def get_news_by_date(self, target_date: str) -> List[Dict]:
        """
        智能获取指定日期的快讯 - 只在列表页筛选，不获取所有文章详情
        Args:
            target_date: 目标日期，格式为 YYYY-MM-DD
        Returns:
            快讯列表
        """
        all_news = []
        
        try:
            # 解析目标日期
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
            logger.info(f"开始智能获取 {target_date} 的快讯")
            
            async with async_playwright() as p:
                browser_options = {
                    'headless': True,
                    'args': [
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled'
                    ]
                }
                browser = await p.chromium.launch(**browser_options)
                page = await browser.new_page()
                
                # 设置User-Agent
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                try:
                    page_num = 1
                    found_older_dates = False
                    target_articles = []
                    seen_titles = set()  # 用于去重
                    
                    # 首次加载页面
                    await page.goto(self.base_url, wait_until="networkidle", timeout=30000)
                    await page.wait_for_timeout(3000)
                    
                    while not found_older_dates and page_num <= 5:  # 最多翻5页
                        logger.info(f"正在处理第 {page_num} 页")
                        
                        # 如果不是第一页，点击分页按钮
                        if page_num > 1:
                            try:
                                # 记录翻页前的第一个文章标题，用于检测内容变化
                                first_article_before = await page.query_selector('.leftPart a')
                                first_title_before = await first_article_before.text_content() if first_article_before else ""
                                logger.debug(f"翻页前第一篇文章: {first_title_before[:30]}...")
                                
                                # 先滚动到页面底部，确保分页按钮可见
                                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                await page.wait_for_timeout(1000)
                                
                                # 增强调试：输出分页元素结构
                                try:
                                    logger.info(f"=== 第 {page_num} 页翻页调试信息 ===")
                                    pagination_debug = await page.evaluate('''
                                        () => {
                                            const result = {
                                                url: window.location.href,
                                                paginationElements: []
                                            };
                                            
                                            // 查找可能的分页容器
                                            const selectors = [
                                                'div.flex.justify-center ul',
                                                '.justify-center ul', 
                                                'ul',
                                                '[class*="pagination"]',
                                                'nav'
                                            ];
                                            
                                            selectors.forEach(selector => {
                                                const elements = document.querySelectorAll(selector);
                                                elements.forEach((elem, index) => {
                                                    // 检查是否包含页码
                                                    const text = elem.textContent;
                                                    if (text && /[1-9]/.test(text)) {
                                                        const info = {
                                                            selector: selector,
                                                            index: index,
                                                            html: elem.outerHTML.length > 500 ? 
                                                                  elem.outerHTML.substring(0, 500) + '...' : 
                                                                  elem.outerHTML,
                                                            text: text.replace(/\\s+/g, ' ').trim(),
                                                            children: Array.from(elem.children).map(child => ({
                                                                tag: child.tagName,
                                                                text: child.textContent.trim(),
                                                                classes: child.className
                                                            }))
                                                        };
                                                        result.paginationElements.push(info);
                                                    }
                                                });
                                            });
                                            
                                            return result;
                                        }
                                    ''')
                                    
                                    logger.info(f"当前URL: {pagination_debug['url']}")
                                    logger.info(f"找到 {len(pagination_debug['paginationElements'])} 个可能的分页元素:")
                                    
                                    for i, elem_info in enumerate(pagination_debug['paginationElements']):
                                        logger.info(f"  分页元素 {i+1}:")
                                        logger.info(f"    选择器: {elem_info['selector']}")
                                        logger.info(f"    文本内容: {elem_info['text'][:100]}...")
                                        logger.info(f"    子元素数: {len(elem_info['children'])}")
                                        logger.debug(f"    HTML结构: {elem_info['html']}")
                                        
                                        # 输出子元素信息
                                        for j, child in enumerate(elem_info['children'][:5]):  # 只显示前5个
                                            logger.debug(f"      子元素{j+1}: <{child['tag']}> '{child['text']}' class='{child['classes']}'")
                                    
                                    logger.info("=== 调试信息结束 ===")
                                    
                                except Exception as debug_error:
                                    logger.warning(f"调试信息获取失败: {debug_error}")
                                
                                # 精确的分页按钮选择器（优先使用AIBase特定的Nuxt+Tailwind选择器）
                                page_button_selectors = [
                                    # AIBase特定选择器（基于用户提供的信息）
                                    f'div.flex.justify-center.items-center.px-\\[10px\\] ul > li:nth-child({page_num})',
                                    f'.flex.justify-center ul > li:nth-child({page_num})',
                                    f'ul > li:nth-child({page_num}):has-text("{page_num}")',
                                    
                                    # 更通用的分页选择器
                                    f'div.flex.justify-center ul li:has-text("{page_num}")',
                                    f'.justify-center ul li:has-text("{page_num}")',
                                    f'ul.pagination li:has-text("{page_num}")',
                                    
                                    # 导航区域的按钮
                                    f'nav button:has-text("{page_num}")',
                                    f'[role="navigation"] button:has-text("{page_num}")',
                                    f'nav a:has-text("{page_num}"):not([href*="/news/"])',  # 不包含文章链接
                                    
                                    # 分页容器内的按钮
                                    f'.pagination button:has-text("{page_num}")',
                                    f'.pagination a:has-text("{page_num}"):not([href*="/news/"])',
                                    f'[class*="pagination"] button:has-text("{page_num}")',
                                    
                                    # 页脚区域的按钮
                                    f'footer button:has-text("{page_num}")',
                                    f'footer a:has-text("{page_num}"):not([href*="/news/"])',
                                    
                                    # 使用属性定位
                                    f'button[aria-label*="{page_num}"]',
                                    f'[data-page="{page_num}"]',
                                    f'button[data-page="{page_num}"]',
                                    
                                    # 排除文章区域的通用选择器
                                    f'button:has-text("{page_num}"):not(.leftPart button):not(.leftPart a)',
                                    f'a:has-text("{page_num}"):not(.leftPart a):not([href*="/news/"]):not([href*="/zh/news/"])',
                                ]
                                
                                button_clicked = False
                                clicked_element = None
                                
                                for selector in page_button_selectors:
                                    try:
                                        # 查找所有匹配的元素
                                        buttons = await page.query_selector_all(selector)
                                        if buttons:
                                            for button in buttons:
                                                # 验证元素是否真的是分页按钮
                                                element_text = await button.text_content()
                                                element_href = await button.get_attribute('href')
                                                
                                                # 如果是链接，检查href不包含文章ID
                                                if element_href and ('/news/' in element_href or len(element_href) > 50):
                                                    logger.debug(f"跳过文章链接: {element_href}")
                                                    continue
                                                
                                                # 检查元素是否在视窗内
                                                is_visible = await button.is_visible()
                                                if not is_visible:
                                                    continue
                                                
                                                logger.info(f"找到分页按钮: {selector}, 文本: '{element_text}', href: {element_href}")
                                                
                                                await button.click()
                                                clicked_element = button
                                                logger.info(f"点击第 {page_num} 页按钮成功")
                                                button_clicked = True
                                                break
                                        
                                        if button_clicked:
                                            break
                                            
                                    except Exception as e:
                                        logger.debug(f"分页按钮选择器 {selector} 失败: {e}")
                                        continue
                                
                                # 如果仍然没有找到，尝试JavaScript翻页（针对Vue/Nuxt优化）
                                if not button_clicked:
                                    logger.warning(f"未找到第 {page_num} 页的分页按钮，尝试JavaScript翻页")
                                    try:
                                        result = await page.evaluate(f'''
                                            () => {{
                                                console.log('开始JavaScript查找分页按钮 {page_num}');
                                                
                                                // 方法1: 优先查找AIBase特定的分页结构
                                                const paginationContainer = document.querySelector('div.flex.justify-center ul, .justify-center ul');
                                                if (paginationContainer) {{
                                                    console.log('找到分页容器:', paginationContainer);
                                                    const pageButton = paginationContainer.querySelector(`li:nth-child({page_num})`);
                                                    if (pageButton && pageButton.offsetParent !== null) {{
                                                        console.log('找到第{page_num}页按钮（li元素）:', pageButton);
                                                        // 查找li内的可点击元素
                                                        const clickableElement = pageButton.querySelector('button, a, span[role="button"]') || pageButton;
                                                        clickableElement.click();
                                                        return true;
                                                    }}
                                                }}
                                                
                                                // 方法2: 查找包含页码文本的元素（改进版）
                                                const allElements = document.querySelectorAll('*');
                                                for (let elem of allElements) {{
                                                    const text = elem.textContent?.trim();
                                                    if (text === '{page_num}') {{
                                                        // 检查元素是否在分页区域
                                                        const isInPagination = elem.closest('.pagination') || 
                                                                             elem.closest('[class*="justify-center"]') ||
                                                                             elem.closest('ul') && elem.closest('ul').querySelector('li');
                                                        
                                                        // 排除文章区域
                                                        const isInContent = elem.closest('.leftPart') || 
                                                                          elem.closest('article') ||
                                                                          elem.href?.includes('/news/');
                                                        
                                                        if (isInPagination && !isInContent && elem.offsetParent !== null) {{
                                                            console.log('找到分页元素（通用方法）:', elem);
                                                            
                                                            // 尝试触发Vue事件
                                                            if (elem.__vue__ || elem._vnode) {{
                                                                console.log('检测到Vue组件，尝试触发Vue事件');
                                                                const clickEvent = new MouseEvent('click', {{
                                                                    bubbles: true,
                                                                    cancelable: true,
                                                                    view: window
                                                                }});
                                                                elem.dispatchEvent(clickEvent);
                                                            }} else {{
                                                                elem.click();
                                                            }}
                                                            return true;
                                                        }}
                                                    }}
                                                }}
                                                
                                                // 方法3: 如果以上都失败，尝试模拟键盘导航
                                                console.log('尝试键盘导航方法');
                                                const currentPageElement = document.querySelector('[aria-current="page"], .active, .current');
                                                if (currentPageElement) {{
                                                    // 发送右箭头键事件
                                                    const keyEvent = new KeyboardEvent('keydown', {{
                                                        key: 'ArrowRight',
                                                        code: 'ArrowRight',
                                                        keyCode: 39
                                                    }});
                                                    currentPageElement.dispatchEvent(keyEvent);
                                                    return true;
                                                }}
                                                
                                                console.log('所有JavaScript翻页方法均失败');
                                                return false;
                                            }}
                                        ''')
                                        
                                        if result:
                                            logger.info(f"JavaScript翻页到第 {page_num} 页成功")
                                            button_clicked = True
                                        else:
                                            logger.error(f"JavaScript翻页到第 {page_num} 页失败")
                                            
                                    except Exception as js_error:
                                        logger.error(f"JavaScript翻页执行失败: {js_error}")
                                
                                # 最后的回退方案：尝试URL导航
                                if not button_clicked:
                                    logger.warning(f"常规翻页方法失败，尝试URL导航回退方案")
                                    try:
                                        # 尝试通过修改URL进行翻页
                                        current_url = page.url
                                        base_url = self.base_url
                                        
                                        # 尝试不同的URL模式
                                        url_patterns = [
                                            f"{base_url}?page={page_num}",
                                            f"{base_url}#page={page_num}",
                                            f"{base_url}/page/{page_num}",
                                            f"{current_url}&page={page_num}" if '?' in current_url else f"{current_url}?page={page_num}"
                                        ]
                                        
                                        for url_pattern in url_patterns:
                                            try:
                                                logger.info(f"尝试URL导航: {url_pattern}")
                                                await page.goto(url_pattern, wait_until="networkidle", timeout=10000)
                                                await page.wait_for_timeout(2000)
                                                
                                                # 检查是否成功加载了新内容
                                                new_test_elements = await page.query_selector_all('.leftPart a')
                                                if new_test_elements and len(new_test_elements) > 0:
                                                    new_first_article = new_test_elements[0]
                                                    new_title = await new_first_article.text_content() if new_first_article else ""
                                                    
                                                    if new_title and new_title != first_title_before:
                                                        logger.info(f"URL导航成功！新页面第一篇: {new_title[:30]}...")
                                                        button_clicked = True
                                                        break
                                                    else:
                                                        logger.debug(f"URL导航未产生内容变化")
                                                else:
                                                    logger.debug(f"URL导航后未找到内容元素")
                                                    
                                            except Exception as url_error:
                                                logger.debug(f"URL模式 {url_pattern} 失败: {url_error}")
                                                continue
                                    
                                    except Exception as fallback_error:
                                        logger.error(f"URL导航回退方案失败: {fallback_error}")
                                
                                if not button_clicked:
                                    logger.error(f"所有翻页方法（包括回退方案）都失败，跳出循环")
                                    break
                                
                                # 等待内容更新（改进的等待机制）
                                if button_clicked:
                                    logger.debug("等待页面内容更新...")
                                    try:
                                        # 多种等待策略，确保内容真正更新
                                        await page.wait_for_function(f'''
                                            () => {{
                                                // 策略1: 检查第一篇文章标题变化
                                                const firstArticle = document.querySelector('.leftPart a');
                                                const currentTitle = firstArticle ? firstArticle.textContent : '';
                                                const titleChanged = currentTitle !== '{first_title_before}' && currentTitle.length > 0;
                                                
                                                // 策略2: 检查URL参数变化（如果有）
                                                const urlChanged = window.location.href.includes('page={page_num}') || 
                                                                 window.location.hash.includes('{page_num}');
                                                
                                                // 策略3: 检查当前页指示器
                                                const currentPageMarker = document.querySelector('[aria-current="page"], .active, .current');
                                                const pageMarkerChanged = currentPageMarker && currentPageMarker.textContent.trim() === '{page_num}';
                                                
                                                return titleChanged || urlChanged || pageMarkerChanged;
                                            }}
                                        ''', timeout=8000)
                                        logger.info("页面内容已更新")
                                    except Exception as wait_error:
                                        logger.warning(f"等待内容更新超时，使用固定延迟: {wait_error}")
                                    
                                    # 额外等待确保内容完全加载（对于Vue/Nuxt应用很重要）
                                    await page.wait_for_timeout(3000)
                                    
                                    # 验证翻页是否真正成功
                                    try:
                                        new_first_article = await page.query_selector('.leftPart a')
                                        new_first_title = await new_first_article.text_content() if new_first_article else ""
                                        
                                        if new_first_title and new_first_title != first_title_before:
                                            logger.info(f"翻页验证成功，新页面第一篇文章: {new_first_title[:30]}...")
                                        else:
                                            logger.warning(f"翻页可能未成功，第一篇文章未变化")
                                    except Exception as verify_error:
                                        logger.debug(f"翻页验证失败: {verify_error}")
                                
                            except Exception as e:
                                logger.error(f"翻页到第 {page_num} 页失败: {e}")
                                break
                        
                        # 滚动页面以确保所有内容加载
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await page.wait_for_timeout(1500)
                        
                        # 输出当前页面URL用于调试
                        current_url = page.url
                        logger.info(f"当前页面URL: {current_url}")
                        
                        # 验证是否在列表页（不是详情页）
                        if '/news/' in current_url and current_url != self.base_url and '?page=' not in current_url:
                            logger.error(f"检测到跳转到详情页: {current_url}，翻页失败")
                            # 尝试返回列表页
                            await page.goto(self.base_url, wait_until="networkidle", timeout=30000)
                            await page.wait_for_timeout(2000)
                            logger.info("已返回列表页，停止翻页")
                            break
                        
                        # 验证页面内容（检查是否有快讯元素）
                        quick_test_elements = await page.query_selector_all('.leftPart a')
                        if len(quick_test_elements) == 0:
                            logger.error(f"第 {page_num} 页没有找到任何快讯元素，可能翻页失败或到达末页")
                            break
                        
                        # 获取快讯元素 - 使用多种备用选择器策略
                        news_selectors = [
                            ".leftPart a",  # AIBase的主要快讯链接
                            "div.grid.grid-cols-1 a",  # 网格布局中的链接
                            "a[href*='/news/']",  # 包含/news/的链接
                            "div.grid a",  # 简化的网格链接
                            ".grid-cols-1 > div",  # 网格直接子元素
                            "main a",  # 主内容区域的链接
                            "[class*='leftPart'] a",  # 包含leftPart的链接
                            "article",
                            "[class*='news-item']",
                            "[class*='article']",
                            "div[class*='content'] > div",
                            "div[class*='grid'] > div",  # 网格子元素
                            ".w-full a",  # 全宽链接
                        ]
                        
                        news_elements = None
                        for selector in news_selectors:
                            news_elements = await page.query_selector_all(selector)
                            logger.debug(f"选择器 {selector}: 找到 {len(news_elements) if news_elements else 0} 个元素")
                            if news_elements and len(news_elements) > 0:
                                logger.info(f"第 {page_num} 页使用选择器 {selector} 找到 {len(news_elements)} 个快讯元素")
                                break
                                
                        if not news_elements or len(news_elements) == 0:
                            logger.warning(f"第 {page_num} 页未找到任何快讯元素")
                            # 尝试输出页面内容用于调试
                            page_content = await page.content()
                            if "news" in page_content.lower():
                                logger.debug(f"页面包含'news'关键词，但未找到快讯元素，可能选择器需要调整")
                            break
                            
                        # 在列表页筛选匹配日期的文章
                        page_target_articles = []
                        
                        for i, element in enumerate(news_elements):
                            try:
                                # 获取时间文本 - 使用多种策略
                                time_text = ""
                                time_selectors = [
                                    ".tipColor div:first-child",  # AIBase的时间元素
                                    ".tipColor > div:first-child",  # 更精确的时间选择器
                                    ".tipColor div",  # tipColor下的任意div
                                    ".tipColor",  # tipColor本身
                                    "[class*='tipColor'] div:first-child",  # 包含tipColor的div
                                    "[class*='tipColor']",  # 包含tipColor的元素
                                    "[class*='time']",  # 包含time的元素
                                    "[class*='date']",  # 包含date的元素
                                    "span:has-text('前')",  # 包含'前'的span
                                    "span:has-text('小时')",  # 包含'小时'的span
                                    "span:has-text('分钟')",  # 包含'分钟'的span
                                    "time",  # time标签
                                    ".text-\\[12px\\]",  # 小字体样式（可能是时间）
                                    ".text-\\[14px\\]",  # 中等字体样式
                                    "small",  # small标签
                                ]
                                
                                for sel in time_selectors:
                                    time_elem = await element.query_selector(sel)
                                    if time_elem:
                                        time_text = await time_elem.text_content()
                                        if time_text and time_text.strip():
                                            logger.debug(f"第 {page_num} 页第 {i+1} 个元素, 使用选择器 {sel} 获取时间: '{time_text.strip()}'")
                                            break
                                
                                if not time_text:
                                    logger.debug(f"第 {page_num} 页第 {i+1} 个元素未找到时间信息，跳过")
                                    continue
                                    
                                # 解析日期 - 仅从相对时间解析，不处理文章内容中的历史日期
                                article_date = self._parse_date_from_time_text(time_text.strip(), target_date_obj)
                                
                                if not article_date:
                                    logger.debug(f"无法解析时间文本: {time_text}, 跳过此文章")
                                    continue
                                
                                # 检查日期比较
                                days_diff = (target_date_obj - article_date).days
                                logger.debug(f"文章日期: {article_date}, 目标日期: {target_date_obj}, 相差天数: {days_diff}")
                                
                                if days_diff == 0:
                                    # 匹配目标日期，准备获取详情
                                    logger.info(f"找到目标日期文章: {time_text} -> {article_date}")
                                    
                                    # 获取基本信息 - 标题
                                    title = ""
                                    title_selectors = [
                                        "div.text-\\[16px\\].leading-\\[24px\\].font600.mainColor",  # AIBase特定样式
                                        "[class*='title']",  # 包含title的class
                                        "h1", "h2", "h3", "h4",  # 标题标签
                                        ".title",  # title class
                                        ".font600",  # 粗体字（可能是标题）
                                        "[class*='font600']",  # 包含font600的元素
                                        ".mainColor",  # 主色调文字
                                        "[class*='mainColor']",  # 包含mainColor的元素
                                        ".text-\\[16px\\]",  # 16px文字
                                        ".leading-\\[24px\\]",  # 24px行高
                                        "strong",  # 加粗文字
                                        "b"  # 粗体
                                    ]
                                    
                                    for sel in title_selectors:
                                        try:
                                            title_elem = await element.query_selector(sel)
                                            if title_elem:
                                                title = await title_elem.text_content()
                                                if title and title.strip():
                                                    break
                                        except:
                                            continue
                                    
                                    if not title:
                                        full_text = await element.text_content()
                                        if full_text:
                                            lines = full_text.strip().split('\n')
                                            if lines:
                                                title = lines[0].strip()
                                    
                                    if not title or not title.strip():
                                        logger.debug(f"文章标题为空，跳过")
                                        continue
                                    
                                    # 去重检查
                                    title_key = title.strip()
                                    if title_key in seen_titles:
                                        logger.debug(f"重复文章，跳过: {title_key[:30]}...")
                                        continue
                                    
                                    # 获取链接
                                    link = ""
                                    link_elem = await element.query_selector("a[href]")
                                    if link_elem:
                                        link = await link_elem.get_attribute('href')
                                        if link and link.startswith('/'):
                                            link = "https://news.aibase.com" + link
                                    else:
                                        if await element.get_attribute('href'):
                                            link = await element.get_attribute('href')
                                            if link and link.startswith('/'):
                                                link = "https://news.aibase.com" + link
                                    
                                    # 添加到目标文章列表和去重集合
                                    seen_titles.add(title_key)
                                    page_target_articles.append({
                                        'title': title.strip(),
                                        'url': link or self.base_url,
                                        'time_text': time_text.strip(),
                                        'date': target_date,
                                        'article_date': article_date
                                    })
                                    
                                elif days_diff > 0:
                                    # 文章日期早于目标日期，停止翻页
                                    logger.info(f"遇到早于目标日期的文章: {time_text} -> {article_date} (早于目标日期{days_diff}天)")
                                    found_older_dates = True
                                    break
                                    
                            except Exception as e:
                                logger.debug(f"处理快讯元素时出错: {e}")
                                continue
                        
                        if page_target_articles:
                            logger.info(f"第 {page_num} 页找到 {len(page_target_articles)} 篇目标日期文章，总共 {len(target_articles) + len(page_target_articles)} 篇")
                            # 输出找到的文章标题（前30字符）
                            for idx, article in enumerate(page_target_articles):
                                logger.debug(f"  文章 {idx+1}: {article['title'][:50]}... [{article['time_text']}]")
                            target_articles.extend(page_target_articles)
                        else:
                            logger.info(f"第 {page_num} 页共检查了 {len(news_elements)} 个元素，未找到目标日期 {target_date} 的文章")
                            # 输出前几个元素的时间信息用于调试
                            for idx in range(min(3, len(news_elements))):
                                try:
                                    elem = news_elements[idx]
                                    time_elem = await elem.query_selector(".tipColor")
                                    if time_elem:
                                        sample_time = await time_elem.text_content()
                                        logger.debug(f"  样例文章 {idx+1} 时间: '{sample_time.strip() if sample_time else 'N/A'}'")
                                except Exception as e:
                                    logger.debug(f"  获取样例文章 {idx+1} 时间失败: {e}")
                        
                        page_num += 1
                        
                        # 改进的翻页停止逻辑：只有在found_older_dates为True时才停止
                        # 移除"连续页面无新内容就停止"的逻辑，继续翻页直到找到更早日期
                        
                        if page_target_articles:
                            # 如果找到了目标日期的文章，记录信息
                            last_article = page_target_articles[-1]
                            last_article_date = last_article.get('article_date')
                            logger.info(f"第 {page_num-1} 页找到目标文章，最后一篇日期: {last_article_date}")
                        else:
                            # 即使当前页没有目标文章，也继续翻页（可能更早的页面有目标文章）
                            logger.info(f"第 {page_num-1} 页未找到目标日期 {target_date} 的文章，继续翻页查找...")
                        
                        # 设置合理的最大翻页限制，避免无限翻页
                        if page_num > 10:
                            logger.warning(f"已翻页到第 {page_num-1} 页，达到最大翻页限制，停止翻页")
                            break
                        
                        # 只有在found_older_dates为True（找到更早日期的文章）时才停止翻页
                        if found_older_dates:
                            logger.info(f"检测到早于目标日期的文章，停止翻页")
                            break
                    
                    # 获取匹配文章的详细内容
                    if target_articles:
                        logger.info(f"开始获取 {len(target_articles)} 篇文章的详细内容")
                        
                        for i, article in enumerate(target_articles):
                            try:
                                logger.debug(f"正在获取文章 {i+1}/{len(target_articles)} 的详情: {article['url']}")
                                detailed_result = await self._get_news_detail_with_page(page, article['url'])
                                
                                if detailed_result:
                                    # 解析时间
                                    publish_time = self._parse_time_text(article['time_text'])
                                    
                                    news_item = {
                                        'title': article['title'],
                                        'url': article['url'],
                                        'time': publish_time,
                                        'date': article['date'],
                                        'time_text': article['time_text'],
                                        'content': detailed_result.get('content', ''),
                                        'images': detailed_result.get('images', []),
                                        'structured_content': detailed_result.get('structured_content', []),
                                        'summary': "",  # 不使用摘要避免重复
                                        'source': 'AIBase快讯',
                                        'weight': self.source_weight
                                    }
                                    
                                    all_news.append(news_item)
                                    logger.info(f"获取详情成功 {i+1}/{len(target_articles)}: {article['title'][:30]}... (内容: {len(news_item['content'])}字, 图片: {len(news_item['images'])}张)")
                                else:
                                    logger.warning(f"获取详情失败 {i+1}/{len(target_articles)}: {article['title'][:30]}...")
                                    
                                # 添加短暂延迟
                                if i < len(target_articles) - 1:
                                    await page.wait_for_timeout(500)
                                    
                            except Exception as e:
                                logger.error(f"获取详情异常 {i+1}/{len(target_articles)}: {e}")
                                continue
                    
                except Exception as e:
                    logger.error(f"智能获取快讯失败: {e}")
                finally:
                    await browser.close()
                    
        except Exception as e:
            logger.error(f"获取指定日期的快讯失败: {e}")
            
        logger.info(f"智能获取到 {target_date} 的快讯 {len(all_news)} 条")
        
        # 最终验证：检查采集结果
        if len(all_news) > 0:
            # 按页面分组统计
            page_stats = {}
            for news in all_news:
                # 假设可以从某种方式推断是第几页的（这里简单按顺序分组）
                page_index = all_news.index(news) // 8 + 1  # 假设每页8条
                if page_index not in page_stats:
                    page_stats[page_index] = 0
                page_stats[page_index] += 1
            
            for page_idx, count in page_stats.items():
                logger.info(f"第 {page_idx} 页采集: {count} 条快讯")
                
            # 检查是否达到预期数量
            if len(all_news) >= 20:
                logger.info(f"✅ 采集成功！共获取 {len(all_news)} 条快讯，达到预期")
            elif len(all_news) >= 8:
                logger.warning(f"⚠️  部分成功：获取 {len(all_news)} 条快讯，可能翻页未完全成功")
            else:
                logger.error(f"❌ 采集不足：仅获取 {len(all_news)} 条快讯，翻页可能失败")
        
        return all_news
    
    async def get_news_in_timerange(self, hours: int = 1) -> List[Dict]:
        """
        获取指定时间范围内的快讯
        Args:
            hours: 时间范围（小时）
        Returns:
            快讯列表
        """
        all_news = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        try:
            # 获取更多的快讯以确保覆盖时间范围
            news_list = await self.get_latest_news(limit=50)
            
            for news in news_list:
                news_time = news.get('time')
                if news_time:
                    # 解析时间并比较
                    try:
                        news_datetime = datetime.strptime(news_time, "%Y-%m-%d %H:%M:%S")
                        if news_datetime >= cutoff_time:
                            all_news.append(news)
                    except:
                        # 如果解析失败，根据time_text判断
                        time_text = news.get('time_text', '')
                        if self._is_within_hours(time_text, hours):
                            all_news.append(news)
                else:
                    # 没有时间信息的，根据time_text判断
                    time_text = news.get('time_text', '')
                    if self._is_within_hours(time_text, hours):
                        all_news.append(news)
                        
        except Exception as e:
            logger.error(f"获取时间范围内的快讯失败: {e}")
            
        logger.info(f"获取到最近{hours}小时内的快讯 {len(all_news)} 条")
        return all_news
        
    async def get_news_detail(self, news_url: str) -> Optional[str]:
        """
        获取快讯的详细内容
        Args:
            news_url: 快讯详情页URL
        Returns:
            格式化的快讯详细内容，失败时返回None
        """
        if not news_url or news_url == self.base_url:
            return None
            
        async with async_playwright() as p:
            browser_options = {
                'headless': True,
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-dev-shm-usage'
                ]
            }
            browser = await p.chromium.launch(**browser_options)
            page = await browser.new_page()
            
            # 设置User-Agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            try:
                # 访问详情页
                await page.goto(news_url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(1000)
                
                # 尝试多种内容选择器
                content_selectors = [
                    # 主要内容区域
                    "[class*='content'] p",
                    "[class*='article'] p", 
                    "[class*='detail'] p",
                    "main p",
                    ".content p",
                    ".article p",
                    ".detail p",
                    # 如果没有找到p标签，尝试获取整个内容区域
                    "[class*='content']",
                    "[class*='article']",
                    "[class*='detail']",
                    "main",
                    ".content",
                    ".article"
                ]
                
                content_paragraphs = []
                
                for selector in content_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            for element in elements:
                                text = await element.text_content()
                                if text and text.strip() and len(text.strip()) > 10:
                                    # 过滤掉导航、链接等无关内容
                                    if not self._is_irrelevant_content(text.strip()):
                                        content_paragraphs.append(text.strip())
                            
                            if content_paragraphs:
                                break  # 找到内容就停止
                    except:
                        continue
                
                if content_paragraphs:
                    # 合并段落，保持格式
                    formatted_content = '\n\n'.join(content_paragraphs)
                    
                    # 清理内容
                    formatted_content = self._clean_detail_content(formatted_content)
                    
                    return formatted_content
                
                return None
                
            except Exception as e:
                logger.error(f"获取快讯详情失败 {news_url}: {e}")
                return None
            finally:
                await browser.close()

    def _is_decorative_or_related_image(self, src: str, alt: str) -> bool:
        """判断是否为装饰性图片或相关推荐图片（需要过滤掉的）"""
        # 常见的装饰性图片特征
        decorative_patterns = [
            r'logo',
            r'icon',
            r'avatar',
            r'banner',
            r'placeholder',
            r'loading',
            r'1x1|1\*1',  # 1x1像素的跟踪图片
            r'\.gif$',    # GIF通常是装饰性的
            r'ad[s]?[_\-]',  # 广告图片
            r'share|social',
            r'button|btn',
            r'data:image/svg',  # SVG内联图片（通常是图标）
            r'%3c',  # URL编码的< 符号，表示可能是内联SVG
            r'%3e',  # URL编码的> 符号
            r'svg\+xml',  # SVG MIME类型
            r'base64',  # Base64编码的图片（通常是小图标）
            r'\.svg$',  # SVG文件
            r'userlogo',  # 用户头像
        ]
        
        # 相关推荐图片特征 - 重点过滤
        related_patterns = [
            r'thumb|thumbnail',  # 缩略图（通常是推荐内容）
            r'picmap/thumb/',    # chinaz的缩略图路径
            r'/thumb/',          # 通用缩略图路径
            r'_thumb\.',         # 文件名包含thumb
            r'small|sm\.',       # 小图标识
            r'list\.|item\.',    # 列表项图片
            r'related|recommend', # 相关推荐
            r'more|other',       # 更多内容
            r'sidebar|side',     # 侧边栏内容
            r'footer|header',    # 页头页脚
            r'nav|menu',         # 导航菜单
        ]
        
        # 检查URL中的装饰性特征
        for pattern in decorative_patterns:
            if re.search(pattern, src.lower()):
                return True
        
        # 检查URL中的相关推荐特征
        for pattern in related_patterns:
            if re.search(pattern, src.lower()):
                logger.debug(f"匹配相关推荐模式 '{pattern}': {src[:60]}...")
                return True
        
        # 检查alt文本
        if alt:
            # 装饰性alt文本
            for pattern in decorative_patterns:
                if re.search(pattern, alt.lower()):
                    return True
            
            # 如果alt文本明显是其他文章标题（包含常见AI关键词但与当前文章不符）
            other_article_indicators = [
                r'^\d+\.',  # 以数字开头（列表项）
                r'相关阅读|推荐阅读|延伸阅读',
                r'热门文章|精选文章',
                r'更多.*文章',
            ]
            
            for pattern in other_article_indicators:
                if re.search(pattern, alt):
                    logger.debug(f"匹配其他文章指示 '{pattern}': {alt[:30]}...")
                    return True
        
        # 检查图片尺寸指示（从URL中）
        size_patterns = [
            r'(\d+)x(\d+)',
            r'w(\d+)h(\d+)',
            r'_(\d+)_(\d+)'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, src.lower())
            if match:
                try:
                    width = int(match.group(1))
                    height = int(match.group(2))
                    # 过滤掉太小的图片（可能是装饰性的）
                    if width < 100 and height < 100:
                        return True
                    # 过滤掉明显的缩略图尺寸
                    if (width <= 200 and height <= 200) and ('thumb' in src.lower() or 'small' in src.lower()):
                        return True
                except:
                    pass
        
        # 特殊处理：placehold.co 占位图
        if 'placehold.co' in src.lower():
            return True
            
        return False

    def _final_cleanup_news(self, news: Dict) -> Dict:
        """最终清理新闻数据，确保格式正确"""
        import re
        
        # 清理标题，确保不包含摘要内容
        title = news.get('title', '')
        if title:
            # 如果标题过长（可能包含了摘要），取前面合理的部分
            if len(title) > 200:  # 正常标题不应超过200字符
                # 尝试在句号、问号、感叹号处截断
                for punct in ['。', '！', '？']:
                    if punct in title[:200]:
                        title = title[:title.find(punct) + 1]
                        break
                else:
                    # 如果没有标点，直接截断
                    title = title[:100] + "..."
            
            news['title'] = title.strip()
        
        # 清理时间信息，确保只包含时间而不是内容
        time_text = news.get('time_text', '')
        if time_text and len(time_text) > 50:  # 时间信息不应该太长
            # 尝试提取真正的时间信息
            time_patterns = [
                r'\d+\s*小时前',
                r'\d+\s*分钟前', 
                r'刚刚',
                r'今天\s*\d{1,2}:\d{2}',
                r'昨天\s*\d{1,2}:\d{2}'
            ]
            
            extracted_time = ""
            for pattern in time_patterns:
                match = re.search(pattern, time_text)
                if match:
                    extracted_time = match.group(0)
                    break
            
            if extracted_time:
                news['time_text'] = extracted_time
            else:
                news['time_text'] = "最近"  # 默认值
        
        # 确保摘要不包含在内容中（避免重复）
        summary = news.get('summary', '')
        content = news.get('content', '')
        
        if summary and content and summary in content:
            # 如果摘要是内容的一部分，清空摘要
            news['summary'] = ""
        
        return news

    def _is_irrelevant_content(self, text: str) -> bool:
        """判断是否为无关内容"""
        irrelevant_patterns = [
            r'^阅读原文$',
            r'^查看更多$',
            r'^展开.*%$',
            r'^点击.*查看$',
            r'^相关.*：$',
            r'^标签.*：$',
            r'^分享$',
            r'^收藏$',
            r'^点赞$',
            r'^评论$',
            r'^\d+$',  # 纯数字
            r'^[<>\/\s]*$',  # HTML标签残留
        ]
        
        for pattern in irrelevant_patterns:
            if re.match(pattern, text.strip(), re.IGNORECASE):
                return True
        
        # 太短的内容也认为是无关的
        if len(text.strip()) < 10:
            return True
            
        return False
    
    def _clean_detail_content(self, content: str) -> str:
        """清理详细内容"""
        if not content:
            return content
        
        # 清理模式
        clean_patterns = [
            r'展开剩余\d+%',
            r'查看更多内容',
            r'点击查看全文',
            r'阅读原文链接',
            r'本文.*转载.*',
            r'来源：.*',
            r'责任编辑：.*',
            r'版权声明.*',
            r'免责声明.*'
        ]
        
        cleaned = content
        for pattern in clean_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # 清理多余的空行
        lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
        
        # 重新组合，保持段落结构
        return '\n\n'.join(lines)
    
    async def _get_news_detail_with_page(self, page, news_url: str) -> Optional[Dict]:
        """
        使用现有的页面对象获取快讯详细内容和图片
        Args:
            page: Playwright页面对象
            news_url: 快讯详情页URL
        Returns:
            包含content和images的字典，失败时返回None
        """
        if not news_url or news_url == self.base_url:
            return None
            
        try:
            logger.debug(f"正在访问详情页: {news_url}")
            # 访问详情页
            await page.goto(news_url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(800)
            logger.debug(f"详情页加载完成")
            
            # 尝试多种内容选择器
            content_selectors = [
                # 主要内容区域
                "[class*='content'] p",
                "[class*='article'] p", 
                "[class*='detail'] p",
                "main p",
                ".content p",
                ".article p",
                ".detail p",
                # 如果没有找到p标签，尝试获取整个内容区域
                "[class*='content']",
                "[class*='article']",
                "[class*='detail']",
                "main",
                ".content",
                ".article"
            ]
            
            content_paragraphs = []
            images = []
            
            # 提取结构化内容（文本+图片）
            structured_content = []
            
            # 重新设计图片采集策略：优先在内容区域查找
            if IMAGE_CONFIG.get('enabled', False):
                logger.debug("开始采集文章图片...")
                
                # 首先尝试在主要内容区域查找图片
                content_images = []
                main_content_element = None
                
                # 寻找主要内容区域
                content_area_selectors = [
                    "[class*='content']",
                    "[class*='article']", 
                    "[class*='detail']",
                    "main",
                    ".content",
                    ".article",
                    ".detail"
                ]
                
                for selector in content_area_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            main_content_element = elements[0]
                            logger.debug(f"找到内容区域: {selector}")
                            break
                    except:
                        continue
                
                # 在内容区域查找图片（不再回退到页面级查找）
                if main_content_element:
                    content_images = await main_content_element.query_selector_all('img')
                    logger.debug(f"在内容区域找到 {len(content_images)} 个图片")
                else:
                    logger.debug("未找到内容区域，不采集图片")
                    content_images = []
                
                # 处理找到的图片
                for img_element in content_images[:IMAGE_CONFIG.get('max_images_per_news', 5)]:
                    try:
                        src = await img_element.get_attribute('src')
                        alt = await img_element.get_attribute('alt') or ''
                        
                        logger.debug(f"检查图片: src={src}, alt={alt}")
                        
                        if src:
                            # 转换相对URL为绝对URL
                            if src.startswith('/'):
                                src = f"https://news.aibase.com{src}"
                            elif src.startswith('//'):
                                src = f"https:{src}"
                            elif not src.startswith(('http://', 'https://')):
                                src = f"https://news.aibase.com/{src}"
                            
                            # 增强的过滤逻辑
                            if not self._is_decorative_or_related_image(src, alt):
                                image_data = {
                                    'url': src,
                                    'alt': alt.strip(),
                                    'position': len(images)
                                }
                                images.append(image_data)
                                logger.info(f"成功采集图片 {len(images)}: {src[:80]}...")
                            else:
                                logger.debug(f"过滤装饰性/相关推荐图片: {src[:60]}...")
                    except Exception as e:
                        logger.debug(f"处理图片时出错: {e}")
                        continue
            
            # 找到主要内容区域
            main_content_element = None
            for selector in content_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        main_content_element = elements[0]  # 取第一个匹配的元素
                        break
                except:
                    continue
            
            if main_content_element:
                logger.debug(f"找到主要内容区域，开始提取结构化内容")
                # 提取结构化内容（按DOM顺序）
                all_child_elements = await main_content_element.query_selector_all('*')
                logger.debug(f"内容区域包含 {len(all_child_elements)} 个子元素")
                
                for element in all_child_elements:
                    try:
                        tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                        
                        if tag_name == 'img':
                            logger.debug(f"发现img标签，IMAGE_CONFIG.enabled={IMAGE_CONFIG.get('enabled', False)}")
                            if IMAGE_CONFIG.get('enabled', False):
                                # 处理图片
                                if len(images) < IMAGE_CONFIG.get('max_images_per_news', 5):
                                    src = await element.get_attribute('src')
                                    alt = await element.get_attribute('alt') or ''
                                    
                                    logger.debug(f"图片原始src: {src}, alt: {alt}")
                                    
                                    if src:
                                        # 转换相对URL为绝对URL
                                        original_src = src
                                        if src.startswith('/'):
                                            src = f"https://news.aibase.com{src}"
                                        elif src.startswith('//'):
                                            src = f"https:{src}"
                                        elif not src.startswith(('http://', 'https://')):
                                            src = f"https://news.aibase.com/{src}"
                                        
                                        logger.debug(f"图片转换后URL: {src}")
                                        
                                        # 检查是否为装饰性图片
                                        is_decorative = self._is_decorative_image(src, alt)
                                        logger.debug(f"是否装饰性图片: {is_decorative}")
                                        
                                        if not is_decorative:
                                            image_data = {
                                                'url': src,
                                                'alt': alt.strip(),
                                                'position': len(structured_content)  # 在内容中的位置
                                            }
                                            images.append(image_data)
                                            structured_content.append({
                                                'type': 'image',
                                                'data': image_data
                                            })
                                            logger.info(f"成功提取图片: {src[:80]}... (alt: {alt[:30]}...)")
                                        else:
                                            logger.debug(f"过滤装饰性图片: {src[:80]}...")
                                else:
                                    logger.debug(f"已达到最大图片数量限制 {IMAGE_CONFIG.get('max_images_per_news', 5)}")
                            else:
                                logger.debug(f"图片功能未启用，跳过图片提取")
                        
                        elif tag_name in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            # 处理文本内容
                            text = await element.text_content()
                            if text and text.strip() and len(text.strip()) > 10:
                                if not self._is_irrelevant_content(text.strip()):
                                    structured_content.append({
                                        'type': 'text',
                                        'data': text.strip()
                                    })
                                    content_paragraphs.append(text.strip())
                    
                    except Exception as e:
                        logger.debug(f"处理元素时出错: {e}")
                        continue
            
            # 如果结构化提取失败，回退到原有逻辑
            else:
                logger.warning(f"未找到主要内容区域，尝试备用选择器")
            
            if not content_paragraphs:
                for selector in content_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            for element in elements:
                                text = await element.text_content()
                                if text and text.strip() and len(text.strip()) > 10:
                                    if not self._is_irrelevant_content(text.strip()):
                                        content_paragraphs.append(text.strip())
                            
                            if content_paragraphs:
                                break
                    except:
                        continue
            
            if content_paragraphs:
                # 合并段落，保持格式
                formatted_content = '\n\n'.join(content_paragraphs)
                
                # 清理内容
                formatted_content = self._clean_detail_content(formatted_content)
                
                logger.info(f"详情提取完成: 内容{len(formatted_content)}字符, {len(images)}张图片, {len(structured_content)}个结构化元素")
                
                return {
                    'content': formatted_content,
                    'images': images,
                    'structured_content': structured_content  # 新增结构化内容
                }
            
            return {
                'content': '',
                'images': images,
                'structured_content': structured_content
            }
            
        except Exception as e:
            logger.debug(f"获取快讯详情失败 {news_url}: {e}")
            return None
        
    def _parse_time_text(self, time_text: str) -> str:
        """
        解析时间文本，转换为标准时间格式
        Args:
            time_text: 时间文本（如"5分钟前"、"2小时前"等）
        Returns:
            标准时间字符串 (YYYY-MM-DD HH:MM:SS)
        """
        if not time_text:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        now = datetime.now()
        time_text = time_text.strip()
        
        # 处理"刚刚"
        if '刚刚' in time_text:
            return now.strftime("%Y-%m-%d %H:%M:%S")
            
        # 处理"X分钟前"
        minutes_match = re.search(r'(\d+)\s*分钟前', time_text)
        if minutes_match:
            minutes = int(minutes_match.group(1))
            target_time = now - timedelta(minutes=minutes)
            return target_time.strftime("%Y-%m-%d %H:%M:%S")
            
        # 处理"X小时前"
        hours_match = re.search(r'(\d+)\s*小时前', time_text)
        if hours_match:
            hours = int(hours_match.group(1))
            target_time = now - timedelta(hours=hours)
            return target_time.strftime("%Y-%m-%d %H:%M:%S")
            
        # 处理"今天 HH:MM"
        today_match = re.search(r'今天\s*(\d{1,2}):(\d{2})', time_text)
        if today_match:
            hour = int(today_match.group(1))
            minute = int(today_match.group(2))
            target_time = now.replace(hour=hour, minute=minute, second=0)
            return target_time.strftime("%Y-%m-%d %H:%M:%S")
            
        # 处理"昨天 HH:MM"
        yesterday_match = re.search(r'昨天\s*(\d{1,2}):(\d{2})', time_text)
        if yesterday_match:
            hour = int(yesterday_match.group(1))
            minute = int(yesterday_match.group(2))
            target_time = (now - timedelta(days=1)).replace(hour=hour, minute=minute, second=0)
            return target_time.strftime("%Y-%m-%d %H:%M:%S")
            
        # 处理标准日期时间格式
        datetime_patterns = [
            (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '%Y-%m-%d %H:%M:%S'),
            (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', '%Y-%m-%d %H:%M'),
            (r'\d{2}-\d{2} \d{2}:\d{2}', '%m-%d %H:%M'),
        ]
        
        for pattern, format_str in datetime_patterns:
            match = re.search(pattern, time_text)
            if match:
                date_str = match.group(0)
                try:
                    if format_str == '%m-%d %H:%M':
                        # 补充年份
                        date_str = f"{now.year}-{date_str}"
                        format_str = '%Y-%m-%d %H:%M'
                    parsed_time = datetime.strptime(date_str, format_str)
                    if format_str == '%Y-%m-%d %H:%M':
                        # 补充秒
                        return parsed_time.strftime("%Y-%m-%d %H:%M:00")
                    return parsed_time.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
                    
        # 默认返回当前时间
        return now.strftime("%Y-%m-%d %H:%M:%S")
        
    def _is_within_hours(self, time_text: str, hours: int) -> bool:
        """
        判断时间文本是否在指定小时数内
        Args:
            time_text: 时间文本
            hours: 小时数
        Returns:
            是否在范围内
        """
        if not time_text:
            return True  # 没有时间信息的默认包含
            
        time_text = time_text.strip()
        
        # 刚刚、X分钟前肯定在范围内
        if '刚刚' in time_text or '分钟前' in time_text:
            return True
            
        # X小时前
        hours_match = re.search(r'(\d+)\s*小时前', time_text)
        if hours_match:
            news_hours = int(hours_match.group(1))
            return news_hours <= hours
            
        # 今天的都算在范围内（如果hours >= 24）
        if '今天' in time_text and hours >= 24:
            return True
            
        # 昨天的不算（除非hours > 24）
        if '昨天' in time_text:
            return hours > 24
            
        # 默认包含
        return True
    
    def _parse_date_from_time_text(self, time_text: str, target_date: date) -> Optional[date]:
        """
        从时间文本中解析日期
        Args:
            time_text: 时间文本（如"5分钟前"、"2小时前"等）
            target_date: 目标日期，用于辅助判断
        Returns:
            解析出的日期，失败返回None
        """
        if not time_text:
            return None
            
        now = datetime.now()
        time_text = time_text.strip()
        
        try:
            # 处理"刚刚"
            if '刚刚' in time_text:
                return now.date()
                
            # 处理"X分钟前"
            minutes_match = re.search(r'(\d+)\s*分钟前', time_text)
            if minutes_match:
                minutes = int(minutes_match.group(1))
                target_time = now - timedelta(minutes=minutes)
                return target_time.date()
                
            # 处理"X小时前"
            hours_match = re.search(r'(\d+)\s*小时前', time_text)
            if hours_match:
                hours = int(hours_match.group(1))
                target_time = now - timedelta(hours=hours)
                return target_time.date()
                
            # 处理"今天 HH:MM"
            today_match = re.search(r'今天\s*(\d{1,2}):(\d{2})', time_text)
            if today_match:
                return now.date()
                
            # 处理"昨天 HH:MM"
            yesterday_match = re.search(r'昨天\s*(\d{1,2}):(\d{2})', time_text)
            if yesterday_match:
                return (now - timedelta(days=1)).date()
                
            # 处理"X天前"
            days_match = re.search(r'(\d+)\s*天前', time_text)
            if days_match:
                days = int(days_match.group(1))
                target_time = now - timedelta(days=days)
                return target_time.date()
                
            # 处理标准日期格式
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',
                r'\d{2}-\d{2}',
                r'\d{4}/\d{2}/\d{2}',
                r'\d{2}/\d{2}',
                r'\d{4}年\d{1,2}月\d{1,2}日',
                r'\d{1,2}月\d{1,2}日'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, time_text)
                if match:
                    date_str = match.group(0)
                    
                    # 尝试解析不同的日期格式
                    formats = [
                        '%Y-%m-%d',
                        '%m-%d',
                        '%Y/%m/%d', 
                        '%m/%d',
                        '%Y年%m月%d日',
                        '%m月%d日'
                    ]
                    
                    for fmt in formats:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt).date()
                            
                            # 对于只有月日的格式，需要补充年份
                            if fmt in ['%m-%d', '%m/%d', '%m月%d日']:
                                current_year = now.year
                                parsed_date = parsed_date.replace(year=current_year)
                                
                                # 如果解析出的日期是未来日期，使用上一年
                                if parsed_date > now.date():
                                    parsed_date = parsed_date.replace(year=current_year - 1)
                            
                            return parsed_date
                        except ValueError:
                            continue
                            
        except Exception as e:
            logger.debug(f"解析时间文本失败: {time_text}, 错误: {e}")
            
        return None
        
    async def monitor_news(self, callback, interval: int = 60):
        """
        持续监控快讯更新
        Args:
            callback: 发现新快讯时的回调函数
            interval: 检查间隔（秒）
        """
        logger.info(f"开始监控AIBase快讯，检查间隔: {interval}秒")
        
        known_news = set()  # 存储已知的快讯标题
        
        try:
            # 初始化浏览器
            await self.initialize_browser()
            
            # 首次获取快讯，建立基准
            initial_news = await self.get_latest_news(limit=20)
            for news in initial_news:
                known_news.add(news['title'])
            logger.info(f"初始化完成，已记录 {len(known_news)} 条快讯")
            
            while True:
                try:
                    # 等待指定间隔
                    await asyncio.sleep(interval)
                    
                    # 获取最新快讯
                    latest_news = await self.get_latest_news(limit=20)
                    
                    # 检查新快讯
                    new_items = []
                    for news in latest_news:
                        if news['title'] not in known_news:
                            new_items.append(news)
                            known_news.add(news['title'])
                            
                    # 如果有新快讯，调用回调
                    if new_items:
                        logger.info(f"发现 {len(new_items)} 条新快讯")
                        for news in new_items:
                            await callback(news)
                    else:
                        logger.debug("没有发现新快讯")
                        
                except Exception as e:
                    logger.error(f"监控循环出错: {e}")
                    # 继续监控，不中断
                    
        except KeyboardInterrupt:
            logger.info("监控被用户中断")
        except Exception as e:
            logger.error(f"监控出现严重错误: {e}")
        finally:
            # 清理资源
            await self.close_browser()
            logger.info("监控结束，资源已清理")
>>>>>>> e0628e40f446a2e97574cb1ad9e02f4dcc7c8d1f
