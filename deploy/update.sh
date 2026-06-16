#!/bin/bash
# 留痕 · 更新脚本 - 拉取最新代码并重新部署
# 用法：bash deploy/update.sh

set -e

echo "==================================="
echo "  留痕 (Liuhen) 更新"
echo "==================================="

cd /opt/liuhen
git pull

# 重新构建前端
cd frontend
npm install
npm run build

# 重启后端
cd ..
systemctl restart liuhen
systemctl reload nginx

echo ""
echo "✅ 更新完成"
echo "后端状态：$(systemctl is-active liuhen)"
