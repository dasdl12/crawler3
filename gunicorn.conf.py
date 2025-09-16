import os

# 绑定地址和端口
bind = f"0.0.0.0:{os.getenv('PORT', 8080)}"

# 工作进程数
workers = 1

# 超时设置
timeout = 300
keepalive = 2

# 日志配置
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 预加载应用
preload_app = True

# 最大请求数
max_requests = 1000
max_requests_jitter = 100