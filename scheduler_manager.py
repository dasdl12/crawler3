"""
定时任务管理器
支持定时采集、生成日报、推送海报的完整流程
"""
import asyncio
import json
import os
import logging
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import threading

from config import Config
from multi_date_crawler import MultiDateCrawler
from deepseek_api import DeepSeekAPI
from webhook import KingsoftWebhook
from poster_gen import PosterGenerator

logger = logging.getLogger(__name__)

class ScheduledTaskManager:
    """定时任务管理器"""
    
    def __init__(self):
        # 配置调度器
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Asia/Shanghai'
        )
        
        self.task_status = {}
        self.progress_callbacks = {}
        self.is_running = False
        
        # 任务配置存储文件
        try:
            self.config_file = os.path.join(Config.BASE_DIR, 'scheduled_tasks.json')
        except:
            # 如果无法访问BASE_DIR，使用临时目录
            import tempfile
            self.config_file = os.path.join(tempfile.gettempdir(), 'scheduled_tasks.json')
            logger.warning(f"使用临时目录存储任务配置: {self.config_file}")
        
        self._load_task_configs()
    
    def start(self):
        """启动调度器"""
        if not self.is_running:
            try:
                if not self.scheduler.running:
                    self.scheduler.start()
                self.is_running = True
                logger.info("定时任务调度器已启动")
            except Exception as e:
                logger.error(f"启动定时任务调度器失败: {e}")
                # 不要标记为运行状态，允许后续重试
                self.is_running = False
    
    def stop(self):
        """停止调度器"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("定时任务调度器已停止")
    
    def add_daily_report_task(self, task_name: str, schedule_time: str, 
                             sources: List[str] = None, 
                             webhook_enabled: bool = True,
                             poster_enabled: bool = True,
                             days_back: int = 0) -> Dict:
        """
        添加每日报告任务
        Args:
            task_name: 任务名称
            schedule_time: 执行时间 "HH:MM" 格式
            sources: 数据源列表
            webhook_enabled: 是否启用webhook推送
            poster_enabled: 是否生成海报
            days_back: 采集几天前的数据（0=今天，1=昨天）
        Returns:
            任务添加结果
        """
        try:
            if sources is None:
                sources = ['tencent', 'aibase']
            
            # 解析时间
            hour, minute = map(int, schedule_time.split(':'))
            
            # 创建任务配置
            task_config = {
                'name': task_name,
                'type': 'daily_report',
                'schedule_time': schedule_time,
                'sources': sources,
                'webhook_enabled': webhook_enabled,
                'poster_enabled': poster_enabled,
                'days_back': days_back,
                'created_at': datetime.now().isoformat(),
                'enabled': True
            }
            
            # 添加定时任务（只在工作日执行：周一到周五）
            job_id = f"daily_report_{task_name}"
            self.scheduler.add_job(
                func=self._execute_daily_report_task,
                trigger=CronTrigger(hour=hour, minute=minute, day_of_week='mon-fri'),
                args=[task_config],
                id=job_id,
                name=f"每日报告任务: {task_name} (仅工作日)",
                replace_existing=True
            )
            
            # 保存任务配置
            self._save_task_config(job_id, task_config)
            
            logger.info(f"已添加每日报告任务: {task_name}, 执行时间: {schedule_time} (仅工作日)")
            
            return {
                'success': True,
                'message': f'任务 "{task_name}" 添加成功 (仅工作日执行)',
                'job_id': job_id,
                'config': task_config
            }
            
        except Exception as e:
            logger.error(f"添加每日报告任务失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_one_time_task(self, task_name: str, execute_time: str,
                         date_list: List[str], sources: List[str] = None,
                         webhook_enabled: bool = True,
                         poster_enabled: bool = True) -> Dict:
        """
        添加一次性任务
        Args:
            task_name: 任务名称
            execute_time: 执行时间 "YYYY-MM-DD HH:MM"
            date_list: 要采集的日期列表
            sources: 数据源列表
            webhook_enabled: 是否启用webhook推送
            poster_enabled: 是否生成海报
        Returns:
            任务添加结果
        """
        try:
            if sources is None:
                sources = ['tencent', 'aibase']
            
            # 解析执行时间
            execute_datetime = datetime.strptime(execute_time, '%Y-%m-%d %H:%M')
            
            # 创建任务配置
            task_config = {
                'name': task_name,
                'type': 'one_time',
                'execute_time': execute_time,
                'date_list': date_list,
                'sources': sources,
                'webhook_enabled': webhook_enabled,
                'poster_enabled': poster_enabled,
                'created_at': datetime.now().isoformat(),
                'enabled': True
            }
            
            # 添加定时任务
            job_id = f"one_time_{task_name}_{int(execute_datetime.timestamp())}"
            self.scheduler.add_job(
                func=self._execute_one_time_task,
                trigger=DateTrigger(run_date=execute_datetime),
                args=[task_config],
                id=job_id,
                name=f"一次性任务: {task_name}",
                replace_existing=True
            )
            
            # 保存任务配置
            self._save_task_config(job_id, task_config)
            
            logger.info(f"已添加一次性任务: {task_name}, 执行时间: {execute_time}")
            
            return {
                'success': True,
                'message': f'任务 "{task_name}" 添加成功',
                'job_id': job_id,
                'config': task_config
            }
            
        except Exception as e:
            logger.error(f"添加一次性任务失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_daily_report_task(self, task_config: Dict):
        """执行每日报告任务"""
        task_name = task_config['name']
        job_id = f"daily_report_{task_name}"
        
        try:
            logger.info(f"开始执行每日报告任务: {task_name}")
            
            # 更新任务状态
            self.task_status[job_id] = {
                'status': 'running',
                'progress': 0,
                'message': '开始执行每日报告任务...',
                'start_time': datetime.now().isoformat(),
                'details': []
            }
            
            # 计算目标日期列表（周一=近3天，其它=单日）
            days_back = task_config.get('days_back', 0)
            today = date.today()
            weekday = today.weekday()  # Monday=0 ... Sunday=6
            
            if weekday == 0:
                # 周一：采集包含当天的近3天，升序便于报告显示 start_to_end
                date_list = [
                    (today - timedelta(days=2)).strftime('%Y-%m-%d'),
                    (today - timedelta(days=1)).strftime('%Y-%m-%d'),
                    today.strftime('%Y-%m-%d')
                ]
                self.task_status[job_id]['details'].append('📅 周一自动启用多日采集（近3天，含当天）')
            else:
                # 其他工作日：保持单日
                target_date = (today - timedelta(days=days_back)).strftime('%Y-%m-%d')
                date_list = [target_date]
            
            # 执行完整流程
            asyncio.run(self._run_complete_workflow(
                job_id=job_id,
                date_list=date_list,
                sources=task_config['sources'],
                webhook_enabled=task_config['webhook_enabled'],
                poster_enabled=task_config['poster_enabled']
            ))
            
        except Exception as e:
            logger.error(f"每日报告任务执行失败: {task_name}, 错误: {e}")
            self.task_status[job_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'任务执行失败: {str(e)}',
                'end_time': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _execute_one_time_task(self, task_config: Dict):
        """执行一次性任务"""
        task_name = task_config['name']
        execute_time = task_config['execute_time']
        job_id = f"one_time_{task_name}_{int(datetime.strptime(execute_time, '%Y-%m-%d %H:%M').timestamp())}"
        
        try:
            logger.info(f"开始执行一次性任务: {task_name}")
            
            # 更新任务状态
            self.task_status[job_id] = {
                'status': 'running',
                'progress': 0,
                'message': '开始执行一次性任务...',
                'start_time': datetime.now().isoformat(),
                'details': []
            }
            
            # 执行完整流程
            asyncio.run(self._run_complete_workflow(
                job_id=job_id,
                date_list=task_config['date_list'],
                sources=task_config['sources'],
                webhook_enabled=task_config['webhook_enabled'],
                poster_enabled=task_config['poster_enabled']
            ))
            
        except Exception as e:
            logger.error(f"一次性任务执行失败: {task_name}, 错误: {e}")
            self.task_status[job_id] = {
                'status': 'error',
                'progress': 0,
                'message': f'任务执行失败: {str(e)}',
                'end_time': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def _run_complete_workflow(self, job_id: str, date_list: List[str], 
                                   sources: List[str], webhook_enabled: bool, 
                                   poster_enabled: bool):
        """运行完整的工作流程：采集 -> 生成日报 -> 生成海报 -> 推送"""
        
        def update_progress(progress_data):
            self.task_status[job_id].update(progress_data)
        
        try:
            # 步骤1: 采集数据
            self.task_status[job_id]['message'] = '正在采集资讯数据...'
            self.task_status[job_id]['progress'] = 10
            self.task_status[job_id]['details'] = ['🔄 开始采集资讯数据...']
            
            crawler = MultiDateCrawler()
            crawler.set_progress_callback(update_progress)
            
            crawl_result = await crawler.crawl_multiple_dates(date_list, sources)
            
            if not crawl_result['success']:
                raise Exception(f"数据采集失败: {crawl_result.get('error', '未知错误')}")
            
            articles = crawl_result['articles']
            if not articles:
                raise Exception("没有采集到任何文章数据")
            
            self.task_status[job_id]['details'].append(f'✅ 采集完成，共获取 {len(articles)} 篇文章')
            
            # 步骤2: 生成AI日报
            self.task_status[job_id]['message'] = '正在生成AI日报...'
            self.task_status[job_id]['progress'] = 40
            self.task_status[job_id]['details'].append('🤖 开始生成AI日报...')
            
            # 使用第一个日期作为日报日期
            report_date = date_list[0] if len(date_list) == 1 else f"{date_list[0]}_to_{date_list[-1]}"
            
            api = DeepSeekAPI()
            try:
                report_result = await api.generate_daily_report(articles, report_date)
                
                if not report_result.get('success'):
                    raise Exception(f"AI日报生成失败: {report_result.get('error', '未知错误')}")
                
                report_content = report_result['content']
                
                # 保存日报（与手动操作保持一致的文件名格式）
                report_file = os.path.join(Config.REPORTS_DIR, f"report_{report_date.replace('-', '')}.json")
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report_result, f, ensure_ascii=False, indent=2)
                
                # 保存markdown文件（与手动操作保持一致）
                md_file = os.path.join(Config.REPORTS_DIR, f"report_{report_date.replace('-', '')}.md")
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                self.task_status[job_id]['details'].append('✅ AI日报生成完成')
                
            finally:
                await api.close_session()
            
            # 步骤3: 生成海报（如果启用）
            poster_path = None
            if poster_enabled:
                self.task_status[job_id]['message'] = '正在生成海报...'
                self.task_status[job_id]['progress'] = 65
                self.task_status[job_id]['details'].append('🎨 开始生成海报...')
                
                # 首先使用AI生成HTML模板（与手动操作保持一致）
                custom_html = None
                try:
                    self.task_status[job_id]['details'].append('📝 正在调用AI生成海报HTML...')
                    
                    # 重用已有的DeepSeek API实例或创建新的
                    html_api = DeepSeekAPI()
                    try:
                        html_result = await html_api.generate_poster_html(report_content, report_date)
                        if html_result.get('success'):
                            custom_html = html_result['html']
                            self.task_status[job_id]['details'].append('✅ AI HTML模板生成成功')
                            logger.info("定时任务：AI HTML模板生成成功")
                        else:
                            self.task_status[job_id]['details'].append(f'⚠️ AI HTML生成失败，将使用默认模板: {html_result.get("error")}')
                            logger.warning(f"定时任务：AI生成HTML失败，将使用默认模板: {html_result.get('error')}")
                    finally:
                        await html_api.close_session()
                        
                except Exception as e:
                    self.task_status[job_id]['details'].append(f'⚠️ AI HTML生成异常，将使用默认模板: {str(e)}')
                    logger.error(f"定时任务：AI生成HTML异常: {e}")
                
                # 生成海报图片
                self.task_status[job_id]['details'].append('🖼️ 正在渲染海报图片...')
                generator = PosterGenerator()
                poster_result = await generator.generate_poster_from_report(
                    report_content, 
                    report_date, 
                    custom_html=custom_html  # 使用AI生成的HTML或None（默认模板）
                )
                
                if poster_result.get('success'):
                    poster_path = poster_result['image_path']
                    html_source = "AI生成的HTML模板" if custom_html else "默认HTML模板"
                    self.task_status[job_id]['details'].append(f'✅ 海报生成完成（使用{html_source}）')
                    logger.info(f"定时任务：海报生成完成，使用{html_source}")
                else:
                    self.task_status[job_id]['details'].append(f'⚠️ 海报生成失败: {poster_result.get("error")}')
                    logger.warning(f"定时任务：海报生成失败: {poster_result.get('error')}")
            
            # 步骤4: 推送到Webhook（如果启用）
            if webhook_enabled:
                self.task_status[job_id]['message'] = '正在推送到群聊...'
                self.task_status[job_id]['progress'] = 85
                
                webhook = KingsoftWebhook()
                
                # 按照默认顺序：先推送日报，再推送海报
                # 推送日报
                self.task_status[job_id]['details'].append('📤 推送日报到群聊...')
                report_webhook_result = await webhook.send_daily_report(report_content, report_date)
                
                if report_webhook_result.get('success'):
                    self.task_status[job_id]['details'].append('✅ 日报推送完成')
                else:
                    self.task_status[job_id]['details'].append(f'⚠️ 日报推送失败: {report_webhook_result.get("error")}')
                    logger.warning(f"日报推送失败: {report_webhook_result.get('error')}")
                
                # 推送海报（如果生成成功）
                if poster_path and os.path.exists(poster_path):
                    self.task_status[job_id]['details'].append('📤 推送海报到群聊...')
                    poster_webhook_result = await webhook.send_poster_only(image_path=poster_path, date=report_date)
                    
                    if poster_webhook_result.get('success'):
                        self.task_status[job_id]['details'].append('✅ 海报推送完成')
                    else:
                        self.task_status[job_id]['details'].append(f'⚠️ 海报推送失败: {poster_webhook_result.get("error")}')
                        logger.warning(f"海报推送失败: {poster_webhook_result.get('error')}")
            
            # 任务完成
            self.task_status[job_id].update({
                'status': 'completed',
                'progress': 100,
                'message': '定时任务执行完成',
                'end_time': datetime.now().isoformat(),
                'results': {
                    'articles_count': len(articles),
                    'report_generated': True,
                    'poster_generated': poster_enabled and poster_path is not None,
                    'webhook_sent': webhook_enabled,
                    'date_range': date_list,
                    'report_file': report_file,
                    'poster_file': poster_path
                }
            })
            
            self.task_status[job_id]['details'].append('🎉 所有任务执行完成')
            logger.info(f"定时任务完成: {job_id}")
            
        except Exception as e:
            self.task_status[job_id].update({
                'status': 'error',
                'progress': 0,
                'message': f'任务执行失败: {str(e)}',
                'end_time': datetime.now().isoformat(),
                'error': str(e)
            })
            self.task_status[job_id]['details'].append(f'❌ 任务执行失败: {str(e)}')
            logger.error(f"定时任务执行失败: {job_id}, 错误: {e}")
    
    def get_scheduled_tasks(self) -> List[Dict]:
        """获取所有定时任务"""
        tasks = []
        
        try:
            # 确保调度器已启动
            if not self.is_running:
                logger.warning("调度器未运行，尝试启动...")
                self.start()
            
            # 检查调度器是否真正运行
            if not self.scheduler.running:
                logger.error("调度器启动失败，无法获取任务列表")
                return tasks
            
            for job in self.scheduler.get_jobs():
                try:
                    job_config = self._load_task_config(job.id)
                    task_info = {
                        'job_id': job.id,
                        'name': job.name,
                        'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                        'trigger': str(job.trigger),
                        'config': job_config,
                        'status': self.task_status.get(job.id, {'status': 'scheduled'})
                    }
                    tasks.append(task_info)
                except Exception as e:
                    logger.error(f"获取任务信息失败: {job.id}, 错误: {e}")
                    # 继续处理其他任务
                    continue
            
            logger.info(f"成功获取 {len(tasks)} 个定时任务")
            
        except Exception as e:
            logger.error(f"获取定时任务列表失败: {e}")
            # 返回空列表而不是抛出异常
            
        return tasks
    
    def remove_task(self, job_id: str) -> Dict:
        """移除定时任务"""
        try:
            self.scheduler.remove_job(job_id)
            self._remove_task_config(job_id)
            
            # 清理任务状态
            if job_id in self.task_status:
                del self.task_status[job_id]
            
            logger.info(f"已移除定时任务: {job_id}")
            
            return {
                'success': True,
                'message': f'任务 {job_id} 已移除'
            }
            
        except Exception as e:
            logger.error(f"移除定时任务失败: {job_id}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def pause_task(self, job_id: str) -> Dict:
        """暂停定时任务"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"已暂停定时任务: {job_id}")
            
            return {
                'success': True,
                'message': f'任务 {job_id} 已暂停'
            }
            
        except Exception as e:
            logger.error(f"暂停定时任务失败: {job_id}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def resume_task(self, job_id: str) -> Dict:
        """恢复定时任务"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"已恢复定时任务: {job_id}")
            
            return {
                'success': True,
                'message': f'任务 {job_id} 已恢复'
            }
            
        except Exception as e:
            logger.error(f"恢复定时任务失败: {job_id}, 错误: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_task_status(self, job_id: str) -> Dict:
        """获取任务状态"""
        return self.task_status.get(job_id, {'status': 'unknown'})
    
    def _save_task_config(self, job_id: str, config: Dict):
        """保存任务配置"""
        try:
            configs = self._load_all_task_configs()
            configs[job_id] = config
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)
                
        except PermissionError:
            logger.warning(f"无权限写入配置文件: {self.config_file}，任务配置将仅保存在内存中")
        except Exception as e:
            logger.error(f"保存任务配置失败: {e}")
    
    def _load_task_config(self, job_id: str) -> Dict:
        """加载单个任务配置"""
        configs = self._load_all_task_configs()
        return configs.get(job_id, {})
    
    def _load_all_task_configs(self) -> Dict:
        """加载所有任务配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载任务配置失败: {e}")
        
        return {}
    
    def _load_task_configs(self):
        """启动时加载已保存的任务配置"""
        try:
            configs = self._load_all_task_configs()
            
            for job_id, config in configs.items():
                if not config.get('enabled', True):
                    continue
                
                # 重新添加任务（只在工作日执行）
                if config['type'] == 'daily_report':
                    hour, minute = map(int, config['schedule_time'].split(':'))
                    self.scheduler.add_job(
                        func=self._execute_daily_report_task,
                        trigger=CronTrigger(hour=hour, minute=minute, day_of_week='mon-fri'),
                        args=[config],
                        id=job_id,
                        name=f"每日报告任务: {config['name']} (仅工作日)",
                        replace_existing=True
                    )
                    logger.info(f"已恢复每日报告任务: {config['name']} (仅工作日执行)")
                
        except Exception as e:
            logger.error(f"加载任务配置失败: {e}")
    
    def _remove_task_config(self, job_id: str):
        """移除任务配置"""
        try:
            configs = self._load_all_task_configs()
            if job_id in configs:
                del configs[job_id]
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(configs, f, ensure_ascii=False, indent=2)
                    
        except PermissionError:
            logger.warning(f"无权限修改配置文件: {self.config_file}")
        except Exception as e:
            logger.error(f"移除任务配置失败: {e}")


# 全局实例
scheduler_manager = ScheduledTaskManager()