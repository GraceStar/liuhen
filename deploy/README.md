# 留痕 · 服务器部署指南

## 1. 买服务器

阿里云轻量应用服务器，**2核 2G 内存 + 50G SSD + 4M 带宽**，**Ubuntu 22.04 镜像**，地区选最近的（杭州/上海）。

💰 价格：约 **34-68 元/月**。

购买后阿里云会给你：
- **公网 IP**（类似 `47.xx.xx.xx`）
- **root 密码**

## 2. 配防火墙

阿里云控制台 → 轻量服务器 → 防火墙 → 添加规则：

| 端口 | 用途 |
|---|---|
| 22 | SSH 远程登录 |
| 80 | HTTP 网页访问 |
| 443 | HTTPS（配域名后开启） |

## 3. SSH 登录

在本机终端运行：

```bash
ssh root@你的服务器IP
# 输入 root 密码
```

第一次登录会要求修改密码，按提示操作。

## 4. 一键部署

服务器上执行：

```bash
git clone https://github.com/GraceStar/liuhen.git /opt/liuhen
cd /opt/liuhen
bash deploy/setup.sh
```

脚本会自动完成：
- ✅ 安装 Python / Node / Nginx
- ✅ 构建前端
- ✅ 安装后端依赖
- ✅ 配置 systemd 守护进程
- ✅ 配置 Nginx 反向代理

## 5. 配置 DeepSeek Key

部署完成后编辑环境变量：

```bash
nano /opt/liuhen/backend/.env
# 把 DEEPSEEK_API_KEY=sk-placeholder 改成你自己的
```

然后重启后端：

```bash
systemctl restart liuhen
```

## 6. 访问

浏览器打开 `http://你的服务器IP` 即可。

## 常用命令

```bash
# 查看后端运行状态
systemctl status liuhen

# 重启后端
systemctl restart liuhen

# 查看实时日志
tail -f /var/log/liuhen/backend.log

# 重新加载 Nginx 配置
systemctl reload nginx

# 更新代码
bash /opt/liuhen/deploy/update.sh
```

## 后续：配域名 + HTTPS

详见 [HTTPS-SETUP.md](./HTTPS-SETUP.md)（可选）
