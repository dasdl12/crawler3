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
# 提升日志级别以进行更详细的调试
loglevel = "debug"

# 预加载应用
# 对于使用Playwright、threading或asyncio等库的复杂应用，
# preload_app = True 可能会因进程fork后资源不安全而导致worker崩溃。
# 将其设置为False可以确保每个worker独立加载应用，从而提高稳定性。
preload_app = False

# 最大请求数
max_requests = 1000
max_requests_jitter = 100