#!/bin/bash
# 留痕 · 一键部署脚本
# 在服务器上首次部署时运行：bash deploy/setup.sh
# 后续更新代码后：bash deploy/update.sh

set -e

echo "==================================="
echo "  留痕 (Liuhen) 一键部署"
echo "==================================="

# ── 1. 安装系统依赖 ──
echo "[1/6] 安装系统依赖..."
apt update -y
apt install -y python3 python3-pip python3-venv nginx git

# ── 2. 安装 Node.js (如未安装) ──
if ! command -v node &> /dev/null; then
    echo "[2/6] 安装 Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
else
    echo "[2/6] Node.js 已安装: $(node -v)"
fi

# ── 3. 克隆/更新项目代码 ──
echo "[3/6] 同步项目代码..."
if [ ! -d "/opt/liuhen" ]; then
    git clone git@github.com:Grace/liuhen.git /opt/liuhen
else
    cd /opt/liuhen && git pull
fi

# ── 4. 构建前端 ──
echo "[4/6] 构建前端..."
cd /opt/liuhen/frontend
npm install
npm run build

# ── 5. 安装后端依赖 + .env ──
echo "[5/6] 配置后端..."
cd /opt/liuhen/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  请编辑 /opt/liuhen/backend/.env 填入 DEEPSEEK_API_KEY"
fi

mkdir -p /var/log/liuhen

# ── 6. 配置 systemd + nginx ──
echo "[6/6] 配置服务..."
cp /opt/liuhen/deploy/liuhen.service /etc/systemd/system/
cp /opt/liuhen/deploy/nginx.conf /etc/nginx/sites-available/liuhen
ln -sf /etc/nginx/sites-available/liuhen /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

systemctl daemon-reload
systemctl enable liuhen
systemctl restart liuhen
nginx -t && systemctl reload nginx

echo ""
echo "==================================="
echo "  ✅ 部署完成！"
echo "==================================="
echo "  访问地址：http://$(curl -s ifconfig.me)"
echo "  API 文档：http://$(curl -s ifconfig.me)/docs"
echo ""
echo "  常用命令："
echo "    systemctl status liuhen   # 查看后端状态"
echo "    systemctl restart liuhen  # 重启后端"
echo "    tail -f /var/log/liuhen/backend.log  # 查看日志"
echo "==================================="
