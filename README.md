# 🤖 AI资讯采集系统

<div align="center">

![AI资讯采集系统](logo.png)

**智能化AI资讯采集、处理与推送平台**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Railway](https://img.shields.io/badge/Deploy-Railway-purple.svg)](https://railway.app)

</div>

## 📋 目录

- [🎯 项目简介](#-项目简介)
- [✨ 核心功能](#-核心功能)
- [🏗️ 系统架构](#️-系统架构)
- [🚀 快速开始](#-快速开始)
- [⚙️ 配置说明](#️-配置说明)
- [📖 使用指南](#-使用指南)
- [🔧 部署方案](#-部署方案)
- [🛠️ 开发指南](#️-开发指南)
- [❓ 常见问题](#-常见问题)
- [📞 技术支持](#-技术支持)

## 🎯 项目简介

AI资讯采集系统是一个现代化的自动化资讯收集、处理和推送平台。系统集成了多源数据采集、AI智能处理、可视化海报生成和多渠道推送功能，为企业和个人提供高效的AI资讯管理解决方案。

### 🌟 核心特色

- **🔄 全自动化流程**：从采集到推送的完整自动化工作流
- **🧠 AI智能处理**：基于DeepSeek的内容筛选和改写
- **🎨 精美海报生成**：自动生成专业级可视化海报
- **📱 现代化界面**：响应式Web界面，支持多设备访问
- **⏰ 定时任务调度**：支持每日定时和一次性任务
- **☁️ 云端部署**：支持Railway等云平台一键部署

## ✨ 核心功能

### 📰 多源智能采集

#### 数据源支持
- **腾讯研究院AI速递** (权重8分)
  - 深度行业分析和趋势洞察
  - 自动识别标题中的日期信息
  - 高质量内容优先级处理

- **AIBase快讯** (权重5分)
  - 实时AI技术动态
  - 产品发布和更新信息
  - 行业新闻和事件追踪

#### 采集模式
- **单日采集**：指定特定日期的资讯
- **多日采集**：批量采集多个不连续日期
- **日期范围**：连续日期区间的批量采集

### 🤖 AI智能处理

#### DeepSeek集成
- **内容筛选**：基于权重和质量的智能筛选
- **内容改写**：专业的资讯整合和改写
- **格式优化**：生成结构化的Markdown日报
- **质量评估**：多维度内容质量评分

#### 处理策略
```
评分标准：来源权重 × 内容质量
- 高质量 (8-10分)：重大技术突破、重要产品发布
- 中等质量 (5-7分)：产品更新、公司动态
- 低质量 (2-4分)：重复信息、广告软文
```

### 🎨 海报生成系统

#### 设计特色
- **现代化设计**：渐变背景和专业排版
- **响应式布局**：适配不同尺寸和设备
- **AI定制模板**：可选AI生成个性化HTML模板
- **高质量输出**：JPG格式，适合社交媒体分享

#### 技术实现
- 基于Playwright的HTML到图片转换
- 支持自定义CSS样式和布局
- 自动Logo添加和品牌标识
- 优化的图片压缩和质量控制

### 📲 多渠道推送

#### 金山文档集成
- **Webhook推送**：支持企业群聊机器人
- **多格式支持**：Markdown文本和图片格式
- **实时状态反馈**：推送结果和错误处理
- **批量推送**：支持日报和海报同时推送

### ⏰ 定时任务系统

#### 任务类型
- **每日任务**：固定时间的日常采集和推送
- **一次性任务**：指定时间的单次执行任务
- **灵活配置**：自定义数据源、功能开关和执行参数

#### 任务管理
- **可视化管理**：Web界面的任务创建和管理
- **状态监控**：实时任务执行状态和进度
- **错误处理**：自动重试和错误通知机制

### 💻 现代化界面

#### 用户体验
- **Vue.js驱动**：响应式单页应用
- **实时更新**：WebSocket风格的状态同步
- **进度可视化**：任务执行过程的实时展示
- **多标签管理**：内容预览和管理的分类展示

#### 功能模块
- **采集控制面板**：日期选择和数据源配置
- **内容预览系统**：原始文章、AI日报、海报预览
- **系统监控**：日志查看和状态监控
- **配置管理**：API密钥和Webhook配置

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Web界面层 (Vue.js)                      │
├─────────────────────────────────────────────────────────────┤
│                   Flask API服务层                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │   爬虫模块   │ │  AI处理模块  │ │  海报生成   │ │ 推送模块 │ │
│  │             │ │             │ │             │ │         │ │
│  │ • 腾讯研究院 │ │ • DeepSeek  │ │ • Playwright│ │ • 金山文档│ │
│  │ • AIBase   │ │ • 内容筛选   │ │ • HTML转图片 │ │ • Webhook│ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   定时任务调度层                            │
│              (APScheduler + 任务管理)                      │
├─────────────────────────────────────────────────────────────┤
│                     数据存储层                              │
│          (文件系统 + 缓存 + 配置管理)                       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+ (推荐3.11)
- **操作系统**: Windows 10/11, Linux, macOS
- **内存**: 最小2GB，推荐4GB+
- **网络**: 稳定的互联网连接

### 本地部署

#### 1. 克隆项目
```bash
git clone <repository-url>
cd crawler3
```

#### 2. 创建虚拟环境
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt

# 安装Playwright浏览器
python -m playwright install chromium
```

#### 4. 配置环境变量
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
# DEEPSEEK_API_KEY=sk-your-api-key
# KINGSOFT_WEBHOOK_URL=your-webhook-url
```

#### 5. 启动应用
```bash
python app.py
```

访问 `http://localhost:5000` 开始使用。

### Docker部署

#### 1. 构建镜像
```bash
docker build -t ai-crawler .
```

#### 2. 运行容器
```bash
docker run -d \
  -p 5000:5000 \
  -e DEEPSEEK_API_KEY=your-api-key \
  -e KINGSOFT_WEBHOOK_URL=your-webhook-url \
  --name ai-crawler \
  ai-crawler
```

### Railway云部署

#### 1. 连接GitHub
- Fork本项目到您的GitHub账户
- 在Railway中连接GitHub仓库

#### 2. 配置环境变量
```bash
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
KINGSOFT_WEBHOOK_URL=your-kingsoft-webhook-url
```

#### 3. 自动部署
Railway将自动检测Dockerfile并完成部署。

## ⚙️ 配置说明

### 环境变量配置

| 变量名 | 必需 | 说明 | 示例 |
|--------|------|------|------|
| `DEEPSEEK_API_KEY` | ✅ | DeepSeek API密钥 | `sk-xxx...` |
| `KINGSOFT_WEBHOOK_URL` | ✅ | 金山文档Webhook地址 | `https://xz.wps.cn/api/v1/webhook/send?key=xxx` |
| `PORT` | ❌ | 服务端口 | `5000` |
| `DEBUG` | ❌ | 调试模式 | `false` |

### API密钥获取

#### DeepSeek API
1. 访问 [DeepSeek开放平台](https://platform.deepseek.com)
2. 注册账户并完成实名认证
3. 在API管理页面创建新的API密钥
4. 复制密钥并配置到环境变量

#### 金山文档Webhook
1. 在金山文档群聊中添加机器人
2. 进入机器人管理页面
3. 获取Webhook URL
4. 配置到环境变量

### 系统配置

#### 爬虫配置 (`config.py`)
```python
CRAWLER_CONFIG = {
    'concurrent_limit': 4,      # 并发限制
    'request_timeout': 30,      # 请求超时
    'retry_count': 3,          # 重试次数
    'delay_between_requests': 1 # 请求间隔
}
```

#### 海报配置
```python
IMAGE_CONFIG = {
    'poster_width': 530,       # 海报宽度
    'poster_height': 960,      # 海报高度
    'processing_timeout': 30   # 处理超时
}
```

#### 缓存配置
```python
CACHE_CONFIG = {
    'enabled': True,           # 启用缓存
    'expire_hours': 24,        # 过期时间
    'max_cache_files': 100     # 最大文件数
}
```

## 📖 使用指南

### 基础操作流程

#### 1. 系统初始化
- 访问Web界面
- 点击右上角"设置"配置API密钥
- 使用"连接测试"验证配置

#### 2. 资讯采集
```
选择采集模式 → 设置目标日期 → 选择数据源 → 开始采集
```

**采集模式说明**：
- **单日采集**：适合日常使用，采集指定日期的资讯
- **多日采集**：适合补充历史数据，可选择多个不连续日期
- **日期范围**：适合批量处理，连续日期区间采集

#### 3. AI处理
```
查看采集结果 → 生成AI日报 → 预览和编辑 → 保存日报
```

**AI处理特点**：
- 自动筛选高质量内容（≥6分）
- 智能去重和分类整理
- 生成结构化Markdown格式
- 支持手动编辑和调整

#### 4. 海报生成
```
确保有AI日报 → 生成海报 → 预览效果 → 下载或推送
```

**海报特色**：
- 现代化设计风格
- 自动适配内容长度
- 支持AI定制模板
- 高质量JPG输出

#### 5. 内容推送
```
配置Webhook → 推送日报文本 → 推送海报图片 → 查看推送状态
```

### 高级功能

#### 定时任务设置

**每日任务配置**：
1. 点击"添加定时任务"
2. 选择"每日任务"
3. 设置执行时间（如09:00）
4. 配置采集参数和功能开关
5. 保存并启动任务

**一次性任务配置**：
1. 选择"一次性任务"
2. 设置具体执行时间
3. 输入目标日期列表
4. 配置处理选项
5. 提交任务

#### 内容编辑功能

**日报编辑**：
- 点击"编辑日报"进入编辑模式
- 支持Markdown语法
- 实时预览效果
- 保存后自动更新

**自定义海报**：
- 修改`poster_gen.py`中的HTML模板
- 调整CSS样式和布局
- 使用AI生成个性化模板

#### 批量操作

**多日期采集**：
```
日期格式：2024-01-01
每行一个日期，支持批量输入
系统自动验证日期格式
```

**批量推送**：
- 支持日报和海报同时推送
- 自动处理推送队列
- 错误重试机制

### 监控和维护

#### 系统日志
- **实时日志**：在"系统日志"标签查看
- **日志级别**：INFO、WARNING、ERROR
- **日志保留**：最新50条记录

#### 任务状态监控
- **执行状态**：运行中、已完成、错误
- **进度显示**：百分比进度条
- **详细信息**：执行步骤和结果

#### 文件管理
- **缓存文件**：`cache/` 目录
- **日报文件**：`exports/reports/` 目录
- **海报文件**：`exports/posters/` 目录

## 🔧 部署方案

### 生产环境部署

#### 使用Gunicorn
```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 app:app
```

#### 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 使用Supervisor进程管理
```ini
[program:ai-crawler]
command=/path/to/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
directory=/path/to/crawler3
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ai-crawler.log
```

### 云平台部署

#### Railway部署
1. **准备工作**
   - 确保项目包含`Dockerfile`和`railway.json`
   - 配置环境变量

2. **部署步骤**
   ```bash
   # 安装Railway CLI
   npm install -g @railway/cli
   
   # 登录Railway
   railway login
   
   # 部署项目
   railway up
   ```

3. **配置域名**
   - 在Railway控制台配置自定义域名
   - 设置环境变量

#### Heroku部署
1. **创建应用**
   ```bash
   heroku create your-app-name
   ```

2. **配置环境变量**
   ```bash
   heroku config:set DEEPSEEK_API_KEY=your-key
   heroku config:set KINGSOFT_WEBHOOK_URL=your-url
   ```

3. **部署代码**
   ```bash
   git push heroku main
   ```

#### Docker Compose部署
```yaml
version: '3.8'
services:
  ai-crawler:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - KINGSOFT_WEBHOOK_URL=${KINGSOFT_WEBHOOK_URL}
    volumes:
      - ./cache:/app/cache
      - ./exports:/app/exports
    restart: unless-stopped
```

### 性能优化

#### 系统优化
- **内存管理**：定期清理缓存文件
- **并发控制**：调整爬虫并发数量
- **超时设置**：合理设置请求超时时间

#### 缓存策略
- **文章缓存**：避免重复采集
- **图片缓存**：减少海报生成时间
- **API缓存**：降低API调用频率

## 🛠️ 开发指南

### 项目结构

```
crawler3/
├── app.py                    # Flask主应用
├── config.py                 # 配置管理
├── requirements.txt          # 依赖包列表
├── Dockerfile               # Docker配置
├── railway.json             # Railway部署配置
├── gunicorn.conf.py         # Gunicorn配置
├── Procfile                 # Heroku部署配置
├── logo.png                 # 项目Logo
├── .env.example             # 环境变量模板
├── .gitignore              # Git忽略文件
│
├── scrapers/               # 爬虫模块
│   ├── __init__.py
│   ├── base_scraper.py     # 基础爬虫类
│   ├── sohu_scraper.py     # 腾讯研究院爬虫
│   └── aibase_news_scraper.py # AIBase爬虫
│
├── templates/              # HTML模板
│   └── index.html          # 主界面模板
│
├── static/                 # 静态资源
├── cache/                  # 缓存目录
├── exports/                # 导出目录
│   ├── reports/            # 日报文件
│   └── posters/            # 海报图片
│
├── deepseek_api.py         # DeepSeek API集成
├── webhook.py              # 金山文档推送
├── poster_gen.py           # 海报生成
├── utils.py                # 工具函数
├── env_manager.py          # 环境管理
├── multi_date_crawler.py   # 多日期采集
└── scheduler_manager.py    # 定时任务管理
```

### 核心模块说明

#### 爬虫模块 (`scrapers/`)
- **BaseScraper**: 抽象基类，定义爬虫接口
- **SohuScraper**: 腾讯研究院爬虫实现
- **AIBaseNewsScraper**: AIBase快讯爬虫实现

#### API集成 (`deepseek_api.py`)
- DeepSeek API的异步调用封装
- 内容处理和改写功能
- 错误处理和重试机制

#### 海报生成 (`poster_gen.py`)
- HTML模板渲染
- Playwright图片转换
- Logo添加和图片优化

#### 推送模块 (`webhook.py`)
- 金山文档Webhook集成
- 多格式内容推送
- 推送状态管理

### 开发环境设置

#### 1. 开发依赖安装
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8
```

#### 2. 代码格式化
```bash
# 使用Black格式化代码
black .

# 使用flake8检查代码质量
flake8 .
```

#### 3. 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_scrapers.py
```

### 扩展开发

#### 添加新的数据源

1. **创建爬虫类**
```python
from scrapers.base_scraper import BaseScraper, Article

class NewScraper(BaseScraper):
    def __init__(self):
        super().__init__("新数据源", "https://example.com")
    
    async def get_article_list(self, start_date, end_date):
        # 实现文章列表获取
        pass
    
    async def get_article_detail(self, article_url, list_date=""):
        # 实现文章详情获取
        pass
```

2. **集成到主应用**
```python
# 在app.py中添加新的爬虫
from scrapers.new_scraper import NewScraper

# 在爬取逻辑中使用
if 'newsource' in sources:
    scraper = NewScraper()
    articles = await scraper.scrape_articles(start_date, end_date)
```

#### 自定义AI处理

1. **修改提示词模板**
```python
# 在config.py中修改AI_PROMPT_TEMPLATE
AI_PROMPT_TEMPLATE = """
自定义的AI处理提示词...
"""
```

2. **扩展处理功能**
```python
# 在deepseek_api.py中添加新方法
async def custom_processing(self, content):
    # 自定义处理逻辑
    pass
```

#### 自定义海报模板

1. **修改HTML模板**
```python
# 在poster_gen.py中修改_create_default_html方法
def _create_default_html(self, content, date):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            /* 自定义CSS样式 */
        </style>
    </head>
    <body>
        <!-- 自定义HTML结构 -->
    </body>
    </html>
    """
```

2. **AI生成模板**
```python
# 扩展DeepSeek API支持模板生成
async def generate_poster_html(self, content, date):
    # AI生成HTML模板的逻辑
    pass
```

### API接口文档

#### 核心API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页面 |
| `/health` | GET | 健康检查 |
| `/api/config` | GET | 获取系统配置 |
| `/api/crawl` | POST | 开始单日采集 |
| `/api/crawl_multiple` | POST | 开始多日采集 |
| `/api/progress` | GET | 获取任务进度 |
| `/api/generate_report` | POST | 生成AI日报 |
| `/api/generate_poster` | POST | 生成海报 |
| `/api/send_report` | POST | 推送日报 |
| `/api/send_poster` | POST | 推送海报 |

#### 请求示例

**开始采集**
```bash
curl -X POST http://localhost:5000/api/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-01",
    "sources": ["tencent", "aibase"]
  }'
```

**生成日报**
```bash
curl -X POST http://localhost:5000/api/generate_report \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-01",
    "articles": [...]
  }'
```

## ❓ 常见问题

### 安装和配置问题

**Q: Playwright安装失败怎么办？**
A: 
```bash
# 尝试手动安装
python -m playwright install chromium
python -m playwright install-deps

# 如果仍然失败，检查网络连接或使用代理
```

**Q: DeepSeek API调用失败？**
A: 
1. 检查API密钥是否正确
2. 确认账户余额是否充足
3. 验证网络连接是否正常
4. 查看API调用频率限制

**Q: 金山文档推送失败？**
A: 
1. 验证Webhook URL是否有效
2. 检查机器人是否正常工作
3. 确认消息格式是否符合要求
4. 查看推送频率是否过高

### 使用问题

**Q: 爬虫无法获取内容？**
A: 
1. 检查目标网站是否可访问
2. 确认网站结构是否发生变化
3. 调整爬虫的选择器和逻辑
4. 查看系统日志获取详细错误

**Q: 海报生成失败？**
A: 
1. 确认Playwright浏览器已安装
2. 检查系统内存是否充足
3. 验证HTML模板语法是否正确
4. 查看图片处理相关的错误日志

**Q: 定时任务不执行？**
A: 
1. 检查任务配置是否正确
2. 确认系统时间是否准确
3. 查看调度器是否正常启动
4. 检查任务状态和错误信息

### 性能问题

**Q: 系统运行缓慢？**
A: 
1. 调整爬虫并发数量
2. 优化缓存策略
3. 增加系统内存
4. 检查网络连接质量

**Q: 内存占用过高？**
A: 
1. 定期清理缓存文件
2. 调整图片处理参数
3. 优化数据处理逻辑
4. 重启应用释放内存

### 部署问题

**Q: Docker部署失败？**
A: 
1. 检查Dockerfile语法
2. 确认基础镜像可用
3. 验证端口映射配置
4. 查看容器日志信息

**Q: Railway部署问题？**
A: 
1. 确认railway.json配置正确
2. 检查环境变量设置
3. 验证健康检查端点
4. 查看部署日志

## 📞 技术支持

### 获取帮助

如果您在使用过程中遇到问题，可以通过以下方式获取帮助：

1. **查看文档**：仔细阅读本README和代码注释
2. **检查日志**：查看系统日志获取详细错误信息
3. **搜索问题**：在GitHub Issues中搜索相似问题
4. **提交Issue**：详细描述问题和复现步骤

### 问题反馈

提交Issue时请包含以下信息：

- **系统环境**：操作系统、Python版本
- **错误信息**：完整的错误日志和堆栈跟踪
- **复现步骤**：详细的操作步骤
- **配置信息**：相关的配置参数（注意脱敏）

### 贡献指南

欢迎贡献代码和改进建议：

1. **Fork项目**到您的GitHub账户
2. **创建分支**进行功能开发或bug修复
3. **提交PR**并详细描述更改内容
4. **代码审查**通过后合并到主分支

### 版本信息

- **当前版本**: v1.0.0
- **更新时间**: 2024-09-18
- **Python要求**: 3.8+
- **许可证**: MIT License

### 致谢

感谢以下开源项目和服务：

- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Playwright](https://playwright.dev/) - 浏览器自动化
- [Vue.js](https://vuejs.org/) - 前端框架
- [DeepSeek](https://platform.deepseek.com/) - AI服务
- [Railway](https://railway.app/) - 云部署平台

---

<div align="center">

**🚀 开始您的AI资讯采集之旅！**

[快速开始](#-快速开始) • [配置指南](#️-配置说明) • [使用教程](#-使用指南) • [部署方案](#-部署方案)

</div>
