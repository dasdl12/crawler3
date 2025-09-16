"""
AI资讯采集系统 - Flask主应用
"""
import asyncio
import json
import os
import logging
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from concurrent.futures import ThreadPoolExecutor
import threading

# 导入自定义模块
from config import Config
from scrapers.sohu_scraper import SohuScraper
from scrapers.aibase_news_scraper import AIBaseNewsScraper
from deepseek_api import DeepSeekAPI
from webhook import KingsoftWebhook
from poster_gen import PosterGenerator
from env_manager import env_manager
from multi_date_crawler import multi_date_crawler
from scheduler_manager import scheduler_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(Config)

# 确保目录存在
Config.ensure_dirs()

# 启动定时任务调度器
scheduler_manager.start()

# 全局变量
current_task = None
task_progress = {"status": "idle", "progress": 0, "message": "", "details": []}

def run_async(coro):
    """在新事件循环中运行异步任务"""
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    with ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_thread)
        return future.result()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/config')
def get_config():
    """获取系统配置"""
    return jsonify({
        'deepseek_configured': bool(Config.DEEPSEEK_API_KEY),
        'webhook_configured': bool(Config.KINGSOFT_WEBHOOK_URL),
        'cache_enabled': Config.CACHE_CONFIG.get('enabled', True),
        'image_enabled': Config.IMAGE_CONFIG.get('enabled', True)
    })

@app.route('/api/config/details')
def get_config_details():
    """获取详细配置信息（脱敏）"""
    try:
        config_details = env_manager.get_display_config()
        validation_status = env_manager.validate_config()
        
        return jsonify({
            'success': True,
            'config': config_details,
            'status': validation_status
        })
    except Exception as e:
        logger.error(f"获取配置详情失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config/save', methods=['POST'])
def save_config():
    """保存配置"""
    try:
        data = request.json
        
        # 验证必需字段
        if not data:
            return jsonify({'success': False, 'error': '缺少配置数据'}), 400
        
        # 准备更新数据
        updates = {}
        
        # 处理DeepSeek API Key
        if 'deepseek_api_key' in data:
            api_key = data['deepseek_api_key'].strip()
            if api_key and not api_key.startswith('*'):  # 不是脱敏数据
                updates['DEEPSEEK_API_KEY'] = api_key
        
        # 处理Webhook URL
        if 'webhook_url' in data:
            webhook_url = data['webhook_url'].strip()
            if webhook_url and not '*' in webhook_url:  # 不是脱敏数据
                updates['KINGSOFT_WEBHOOK_URL'] = webhook_url
        
        # 更新配置
        if updates:
            success = env_manager.update_env(updates)
            if success:
                # 强制重新加载dotenv环境
                try:
                    from dotenv import load_dotenv
                    load_dotenv(override=True)
                except ImportError:
                    pass
                
                # 重新加载配置到Config类
                Config.DEEPSEEK_API_KEY = env_manager.get_value('DEEPSEEK_API_KEY', '')
                Config.KINGSOFT_WEBHOOK_URL = env_manager.get_value('KINGSOFT_WEBHOOK_URL', '')
                
                return jsonify({
                    'success': True, 
                    'message': f'配置已保存，更新了 {len(updates)} 项配置'
                })
            else:
                return jsonify({'success': False, 'error': '保存配置失败'}), 500
        else:
            return jsonify({'success': False, 'error': '没有需要更新的配置'}), 400
        
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/test_connections', methods=['POST'])
def test_connections():
    """测试API连接"""
    global task_progress
    
    try:
        task_progress = {"status": "running", "progress": 0, "message": "正在测试连接...", "details": []}
        
        results = {}
        
        # 测试DeepSeek API
        task_progress["message"] = "测试DeepSeek API连接..."
        task_progress["progress"] = 25
        
        try:
            api = DeepSeekAPI()
            deepseek_result = run_async(api.test_connection())
            results['deepseek'] = deepseek_result
            task_progress["details"].append(f"DeepSeek API: {'✅ 成功' if deepseek_result.get('success') else '❌ 失败'}")
        except Exception as e:
            results['deepseek'] = {'success': False, 'error': str(e)}
            task_progress["details"].append(f"DeepSeek API: ❌ 失败 - {str(e)}")
        
        # 测试Webhook连接
        task_progress["message"] = "测试Webhook连接..."
        task_progress["progress"] = 50
        
        try:
            webhook = KingsoftWebhook()
            webhook_result = run_async(webhook.test_webhook())
            results['webhook'] = webhook_result
            task_progress["details"].append(f"金山文档Webhook: {'✅ 成功' if webhook_result.get('success') else '❌ 失败'}")
        except Exception as e:
            results['webhook'] = {'success': False, 'error': str(e)}
            task_progress["details"].append(f"金山文档Webhook: ❌ 失败 - {str(e)}")
        
        # 测试爬虫连接
        task_progress["message"] = "测试爬虫连接..."
        task_progress["progress"] = 75
        
        # 简单的连接测试，不实际爬取
        results['scrapers'] = {'success': True, 'message': '爬虫模块加载正常'}
        task_progress["details"].append("爬虫模块: ✅ 加载正常")
        
        task_progress["status"] = "completed"
        task_progress["progress"] = 100
        task_progress["message"] = "连接测试完成"
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        task_progress["status"] = "error"
        task_progress["message"] = f"连接测试失败: {str(e)}"
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/crawl', methods=['POST'])
def start_crawl():
    """开始爬取任务"""
    global current_task, task_progress
    
    if current_task and current_task.is_alive():
        return jsonify({'success': False, 'error': '已有任务在运行中'}), 400
    
    data = request.json
    target_date = data.get('date', date.today().strftime('%Y-%m-%d'))
    sources = data.get('sources', ['tencent', 'aibase'])
    
    def crawl_task():
        global task_progress
        
        # 在函数开头导入datetime相关模块
        from datetime import datetime, timedelta
        
        try:
            task_progress = {
                "status": "running", 
                "progress": 0, 
                "message": "开始爬取任务...", 
                "details": [],
                "articles": []
            }
            
            all_articles = []
            
            # 爬取腾讯研究院
            if 'tencent' in sources:
                task_progress["message"] = "正在爬取腾讯研究院AI速递..."
                task_progress["progress"] = 20
                
                try:
                    scraper = SohuScraper()
                    target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
                    articles, errors = run_async(scraper.scrape_articles(target_date_obj, target_date_obj))
                    
                    all_articles.extend([article.to_dict() for article in articles])
                    task_progress["details"].append(f"腾讯研究院: 成功获取 {len(articles)} 篇文章")
                    
                    if errors:
                        task_progress["details"].extend([f"腾讯研究院错误: {error}" for error in errors[:3]])
                        
                except Exception as e:
                    task_progress["details"].append(f"腾讯研究院爬取失败: {str(e)}")
            
            # 爬取AIBase快讯
            if 'aibase' in sources:
                task_progress["message"] = "正在爬取AIBase快讯..."
                task_progress["progress"] = 50
                
                try:
                    scraper = AIBaseNewsScraper()
                    # AIBase采集前一天的数据（因为AIBase当天快讯对应前一天信息）
                    target_date_obj = datetime.strptime(target_date, '%Y-%m-%d')
                    aibase_date = (target_date_obj - timedelta(days=1)).strftime('%Y-%m-%d')
                    task_progress["details"].append(f"AIBase采集日期: {aibase_date} (前一天，因为AIBase快讯时效对应前一天信息)")
                    
                    news_list = run_async(scraper.get_news_by_date(aibase_date))
                    
                    # 转换为Article格式
                    for news in news_list:
                        article_dict = {
                            'title': news.get('title', ''),
                            'date': news.get('date', target_date),
                            'content': news.get('content', news.get('summary', '')),
                            'url': news.get('url', ''),
                            'source': news.get('source', 'AIBase快讯'),
                            'weight': news.get('weight', 5)
                        }
                        all_articles.append(article_dict)
                    
                    task_progress["details"].append(f"AIBase快讯: 成功获取 {len(news_list)} 条快讯")
                    
                except Exception as e:
                    task_progress["details"].append(f"AIBase快讯爬取失败: {str(e)}")
            
            task_progress["message"] = "爬取完成，正在保存缓存..."
            task_progress["progress"] = 80
            task_progress["articles"] = all_articles
            
            # 保存到缓存
            cache_file = os.path.join(Config.CACHE_DIR, f"articles_{target_date.replace('-', '')}.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'date': target_date,
                    'articles': all_articles,
                    'timestamp': datetime.now().isoformat(),
                    'total': len(all_articles)
                }, f, ensure_ascii=False, indent=2)
            
            task_progress["status"] = "completed"
            task_progress["progress"] = 100
            task_progress["message"] = f"爬取完成！共获取 {len(all_articles)} 篇文章"
            
            logger.info(f"爬取任务完成: {target_date}, 共 {len(all_articles)} 篇文章")
            
        except Exception as e:
            task_progress["status"] = "error"
            task_progress["message"] = f"爬取任务失败: {str(e)}"
            logger.error(f"爬取任务失败: {e}")
    
    current_task = threading.Thread(target=crawl_task)
    current_task.start()
    
    return jsonify({'success': True, 'message': '爬取任务已启动'})

@app.route('/api/progress')
def get_progress():
    """获取任务进度"""
    return jsonify(task_progress)

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    """生成AI日报"""
    global task_progress
    
    try:
        data = request.json
        target_date = data.get('date', date.today().strftime('%Y-%m-%d'))
        articles = data.get('articles', [])
        
        if not articles:
            # 尝试从缓存加载
            cache_file = os.path.join(Config.CACHE_DIR, f"articles_{target_date.replace('-', '')}.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    articles = cache_data.get('articles', [])
        
        if not articles:
            return jsonify({'success': False, 'error': '没有可用的文章数据'}), 400
        
        task_progress = {
            "status": "running",
            "progress": 0,
            "message": "正在生成AI日报...",
            "details": []
        }
        
        # 使用DeepSeek生成日报
        api = DeepSeekAPI()
        result = run_async(api.generate_daily_report(articles, target_date))
        
        if result.get('success'):
            # 保存日报
            report_file = os.path.join(Config.REPORTS_DIR, f"report_{target_date.replace('-', '')}.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # 保存markdown文件
            md_file = os.path.join(Config.REPORTS_DIR, f"report_{target_date.replace('-', '')}.md")
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(result['content'])
            
            task_progress["status"] = "completed"
            task_progress["progress"] = 100
            task_progress["message"] = "AI日报生成成功"
            
            return jsonify({
                'success': True,
                'report': result,
                'files': {
                    'json': report_file,
                    'markdown': md_file
                }
            })
        else:
            task_progress["status"] = "error"
            task_progress["message"] = f"日报生成失败: {result.get('error', '未知错误')}"
            
            return jsonify({
                'success': False,
                'error': result.get('error', '日报生成失败')
            }), 500
            
    except Exception as e:
        task_progress["status"] = "error"
        task_progress["message"] = f"生成日报时出错: {str(e)}"
        
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send_report', methods=['POST'])
def send_report():
    """发送日报到Webhook"""
    try:
        data = request.json
        content = data.get('content', '')
        target_date = data.get('date', date.today().strftime('%Y-%m-%d'))
        
        if not content:
            return jsonify({'success': False, 'error': '没有可发送的内容'}), 400
        
        webhook = KingsoftWebhook()
        result = run_async(webhook.send_daily_report(content, target_date))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save_report', methods=['POST'])
def save_report():
    """保存编辑后的日报"""
    try:
        data = request.json
        content = data.get('content', '')
        target_date = data.get('date', date.today().strftime('%Y-%m-%d'))
        
        if not content:
            return jsonify({'success': False, 'error': '日报内容不能为空'}), 400
        
        # 保存JSON格式
        report_data = {
            'content': content,
            'date': target_date,
            'timestamp': datetime.now().isoformat(),
            'edited': True,
            'success': True
        }
        
        report_file = os.path.join(Config.REPORTS_DIR, f"report_{target_date.replace('-', '')}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        # 保存Markdown格式
        md_file = os.path.join(Config.REPORTS_DIR, f"report_{target_date.replace('-', '')}.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"日报编辑保存成功: {target_date}")
        
        return jsonify({
            'success': True,
            'message': '日报保存成功',
            'files': {
                'json': report_file,
                'markdown': md_file
            }
        })
        
    except Exception as e:
        logger.error(f"保存日报失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate_poster', methods=['POST'])
def generate_poster():
    """生成海报"""
    global task_progress
    
    try:
        task_progress = {"status": "running", "progress": 0, "message": "开始生成海报...", "details": []}
        
        data = request.json
        content = data.get('content', '')
        target_date = data.get('date', date.today().strftime('%Y-%m-%d'))
        custom_html = data.get('html', None)
        
        if not content:
            task_progress["status"] = "error"
            task_progress["message"] = "没有可生成海报的内容"
            return jsonify({'success': False, 'error': '没有可生成海报的内容'}), 400
        
        task_progress["progress"] = 10
        task_progress["message"] = "解析内容..."
        task_progress["details"].append("✅ 内容解析完成")
        
        # 如果有自定义HTML，优先使用AI生成
        if not custom_html and data.get('use_ai', False):
            task_progress["progress"] = 25
            task_progress["message"] = "使用AI生成HTML模板..."
            
            api = DeepSeekAPI()
            try:
                html_result = run_async(api.generate_poster_html(content, target_date))
                if html_result.get('success'):
                    custom_html = html_result['html']
                    task_progress["details"].append("✅ AI HTML模板生成成功")
                    logger.info("使用AI生成的HTML模板")
                else:
                    task_progress["details"].append("⚠️ AI生成HTML失败，使用默认模板")
                    logger.warning(f"AI生成HTML失败，将使用默认模板: {html_result.get('error')}")
            except Exception as e:
                task_progress["details"].append("⚠️ AI生成HTML异常，使用默认模板")
                logger.error(f"AI生成HTML异常: {e}")
            finally:
                # 确保关闭session
                run_async(api.close_session())
        else:
            task_progress["details"].append("✅ 使用默认HTML模板")
        
        task_progress["progress"] = 50
        task_progress["message"] = "生成海报图片..."
        
        # 生成海报
        generator = PosterGenerator()
        result = run_async(generator.generate_poster_from_report(content, target_date, custom_html))
        
        # 增强返回结果的信息
        if result.get('success'):
            html_source = "AI生成的HTML模板" if custom_html else "默认HTML模板"
            result['html_source'] = html_source
            result['path'] = result['image_path']  # 添加前端期望的字段
            
            task_progress["status"] = "completed"
            task_progress["progress"] = 100
            task_progress["message"] = "海报生成完成"
            task_progress["details"].append(f"✅ 海报生成成功，使用: {html_source}")
            
            logger.info(f"海报生成成功，使用: {html_source}")
        else:
            task_progress["status"] = "error"
            task_progress["message"] = f"海报生成失败: {result.get('error')}"
            task_progress["details"].append(f"❌ 海报生成失败: {result.get('error')}")
            
            logger.error(f"海报生成失败: {result.get('error')}")
        
        return jsonify(result)
        
    except Exception as e:
        task_progress["status"] = "error"
        task_progress["message"] = f"海报生成异常: {str(e)}"
        task_progress["details"].append(f"❌ 异常错误: {str(e)}")
        
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send_poster', methods=['POST'])
def send_poster():
    """发送海报到Webhook（只发送图片，不包含文字版本）"""
    try:
        data = request.json
        image_path = data.get('image_path', '')
        target_date = data.get('date', date.today().strftime('%Y-%m-%d'))
        
        if not os.path.exists(image_path):
            return jsonify({'success': False, 'error': '海报文件不存在'}), 400
        
        webhook = KingsoftWebhook()
        result = run_async(webhook.send_poster_only(image_path=image_path, date=target_date))
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/files/<path:filename>')
def serve_file(filename):
    """提供文件下载"""
    file_path = None
    
    # 查找文件
    for directory in [Config.REPORTS_DIR, Config.POSTERS_DIR, Config.CACHE_DIR]:
        potential_path = os.path.join(directory, filename)
        if os.path.exists(potential_path):
            file_path = potential_path
            break
    
    if file_path:
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': '文件不存在'}), 404

@app.route('/api/list_files')
def list_files():
    """列出所有生成的文件"""
    files = {
        'reports': [],
        'posters': [],
        'cache': []
    }
    
    # 扫描报告文件
    if os.path.exists(Config.REPORTS_DIR):
        for filename in os.listdir(Config.REPORTS_DIR):
            if filename.endswith(('.json', '.md')):
                file_path = os.path.join(Config.REPORTS_DIR, filename)
                files['reports'].append({
                    'name': filename,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                })
    
    # 扫描海报文件
    if os.path.exists(Config.POSTERS_DIR):
        for filename in os.listdir(Config.POSTERS_DIR):
            if filename.endswith('.jpg'):
                file_path = os.path.join(Config.POSTERS_DIR, filename)
                files['posters'].append({
                    'name': filename,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                })
    
    return jsonify(files)

@app.route('/api/crawl_multiple', methods=['POST'])
def start_multiple_crawl():
    """开始多日期爬取任务"""
    global current_task, task_progress
    
    if current_task and current_task.is_alive():
        return jsonify({'success': False, 'error': '已有任务在运行中'}), 400
    
    data = request.json
    date_input = data.get('dates', '')  # 可以是单个日期、日期列表或日期范围
    sources = data.get('sources', ['tencent', 'aibase'])
    
    # 解析日期输入
    if isinstance(date_input, list):
        date_list = date_input
    elif isinstance(date_input, str):
        if ',' in date_input:
            date_list = [d.strip() for d in date_input.split(',')]
        else:
            date_list = [date_input.strip()]
    else:
        return jsonify({'success': False, 'error': '无效的日期格式'}), 400
    
    # 验证日期格式
    try:
        for date_str in date_list:
            datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'success': False, 'error': '日期格式无效，请使用 YYYY-MM-DD 格式'}), 400
    
    def crawl_task():
        global task_progress
        
        try:
            # 设置进度回调
            def update_progress(progress_data):
                global task_progress
                task_progress.update(progress_data)
                task_progress["articles"] = progress_data.get("articles", [])
            
            multi_date_crawler.set_progress_callback(update_progress)
            
            # 执行多日期采集
            result = run_async(multi_date_crawler.crawl_multiple_dates(date_list, sources))
            
            if result['success']:
                task_progress.update({
                    "status": "completed",
                    "progress": 100,
                    "message": f"多日期采集完成！共获取 {result['total']} 篇文章",
                    "articles": result['articles']
                })
            else:
                task_progress.update({
                    "status": "error",
                    "progress": 0,
                    "message": f"多日期采集失败: {result.get('error', '未知错误')}"
                })
                
        except Exception as e:
            task_progress.update({
                "status": "error",
                "progress": 0,
                "message": f"多日期采集异常: {str(e)}"
            })
            logger.error(f"多日期采集异常: {e}")
    
    current_task = threading.Thread(target=crawl_task)
    current_task.start()
    
    return jsonify({
        'success': True, 
        'message': f'多日期采集任务已启动，目标日期: {", ".join(date_list)}'
    })

@app.route('/api/scheduler/tasks', methods=['GET'])
def get_scheduled_tasks():
    """获取所有定时任务"""
    try:
        tasks = scheduler_manager.get_scheduled_tasks()
        return jsonify({
            'success': True,
            'tasks': tasks
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scheduler/add_daily_task', methods=['POST'])
def add_daily_task():
    """添加每日定时任务"""
    try:
        data = request.json
        
        required_fields = ['task_name', 'schedule_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必需字段: {field}'}), 400
        
        result = scheduler_manager.add_daily_report_task(
            task_name=data['task_name'],
            schedule_time=data['schedule_time'],
            sources=data.get('sources', ['tencent', 'aibase']),
            webhook_enabled=data.get('webhook_enabled', True),
            poster_enabled=data.get('poster_enabled', True),
            days_back=data.get('days_back', 0)
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scheduler/add_onetime_task', methods=['POST'])
def add_onetime_task():
    """添加一次性定时任务"""
    try:
        data = request.json
        
        required_fields = ['task_name', 'execute_time', 'date_list']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'缺少必需字段: {field}'}), 400
        
        result = scheduler_manager.add_one_time_task(
            task_name=data['task_name'],
            execute_time=data['execute_time'],
            date_list=data['date_list'],
            sources=data.get('sources', ['tencent', 'aibase']),
            webhook_enabled=data.get('webhook_enabled', True),
            poster_enabled=data.get('poster_enabled', True)
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scheduler/remove_task/<job_id>', methods=['DELETE'])
def remove_task(job_id):
    """移除定时任务"""
    try:
        result = scheduler_manager.remove_task(job_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scheduler/pause_task/<job_id>', methods=['POST'])
def pause_task(job_id):
    """暂停定时任务"""
    try:
        result = scheduler_manager.pause_task(job_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scheduler/resume_task/<job_id>', methods=['POST'])
def resume_task(job_id):
    """恢复定时任务"""
    try:
        result = scheduler_manager.resume_task(job_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scheduler/task_status/<job_id>')
def get_task_status(job_id):
    """获取任务状态"""
    try:
        status = scheduler_manager.get_task_status(job_id)
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/date_range', methods=['POST'])
def generate_date_range():
    """生成日期范围"""
    try:
        data = request.json
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'success': False, 'error': '缺少开始日期或结束日期'}), 400
        
        date_list = multi_date_crawler.generate_date_range(start_date, end_date)
        
        return jsonify({
            'success': True,
            'date_list': date_list,
            'count': len(date_list)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("启动AI资讯采集系统...")
    logger.info(f"DeepSeek API配置: {'✅ 已配置' if Config.DEEPSEEK_API_KEY else '❌ 未配置'}")
    logger.info(f"Webhook配置: {'✅ 已配置' if Config.KINGSOFT_WEBHOOK_URL else '❌ 未配置'}")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        use_reloader=False
    )