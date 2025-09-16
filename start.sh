#!/bin/bash

# 安装Playwright浏览器
echo "Installing Playwright browsers..."
python -m playwright install --with-deps chromium

# 启动应用使用gunicorn
echo "Starting Flask application with gunicorn..."
gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 app:app