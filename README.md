# 留痕 (Liuhen)

> 个人工作、学习与生活观察的记录与复盘面板

简洁风格的工作/学习/观察三大分类下自由主题管理、任务三态流转、AI 智能复盘、年终工作总结生成。

## ✨ 功能特性

- 📋 **三大分类**：工作 / 学习 / 观察，自由添加主题
- 🎯 **任务三态**：Todo → Doing → Done 状态流转，重要程度 1-5 星标注
- 📊 **成果面板**：多维筛选（时间/重要程度）+ Chart.js 可视化图表
- 🤖 **AI 复盘**：基于已完成任务，调用 DeepSeek 自动生成复盘与改进建议
- 📈 **年终总结**：一键生成 PPT 友好的工作汇报（大纲/数据/图表建议）
- 🎨 **三主题**：浅色 / 深色 / 跟随系统
- 📱 **响应式**：手机、平板、桌面自适应

## 🛠️ 技术栈

| 层 | 选型 |
|---|---|
| 前端 | Vue 3 + Vite + TypeScript + Tailwind CSS |
| 状态 | Pinia |
| 图表 | Chart.js |
| 后端 | Python FastAPI + SQLAlchemy |
| 数据库 | SQLite |
| AI | DeepSeek API (OpenAI 兼容) |
| 反向代理 | Nginx |
| 进程管理 | systemd |

## 📁 项目结构

```
liuhen/
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── views/          # 三个主页面（总览/看板/成果）
│   │   ├── components/     # 通用组件
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── api.ts          # 后端接口封装
│   │   └── main.ts         # 入口
│   └── package.json
├── backend/                # FastAPI 后端
│   ├── main.py             # 入口
│   ├── models.py           # 数据表定义
│   ├── schemas.py          # Pydantic 校验
│   ├── routes/             # API 路由
│   ├── services/           # AI 等服务
│   └── requirements.txt
├── deploy/                 # 部署相关文件
│   ├── liuhen.service      # systemd 服务
│   ├── nginx.conf          # Nginx 配置
│   └── setup.sh            # 一键部署脚本
└── start.bat               # 本地启动脚本
```

## 🚀 本地启动

### 1. 安装依赖

**后端**：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**前端**：
```bash
cd frontend
npm install
```

### 2. 配置环境变量

在 `backend/.env` 填入你的 DeepSeek API Key：
```bash
DEEPSEEK_API_KEY=sk-your-key-here
```

> 获取地址：<https://platform.deepseek.com/api_keys>

### 3. 启动服务

**双击**项目根目录的 `start.bat`（Windows）

或手动启动：
```bash
# 终端 1：后端
cd backend && python main.py

# 终端 2：前端
cd frontend && npm run dev
```

浏览器打开 <http://localhost:5173> 即可使用。

## 🌐 生产部署

详见 [deploy/README.md](deploy/README.md)：

1. 购买阿里云轻量应用服务器（2核2G, Ubuntu 22.04）
2. SSH 登录服务器
3. 克隆本仓库：`git clone https://github.com/GraceStar/liuhen.git`
4. 运行部署脚本：`bash deploy/setup.sh`
5. 配置 Nginx 和 systemd

## 📜 License

MIT
