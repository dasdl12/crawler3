#!/bin/bash

# 安装Playwright浏览器
echo "Installing Playwright browsers..."
python -m playwright install --with-deps chromium

# 启动应用
echo "Starting Flask application..."
python app.py