# Bid System 部署文档

## 🚀 快速开始

### 服务管理

```bash
# 查看所有命令
bid-system

# 或直接使用
bid-system status      # 查看状态
bid-system start       # 启动所有服务
bid-system stop        # 停止所有服务
bid-system restart    # 重启所有服务
bid-system logs        # 查看实时日志
bid-system recent-logs # 查看最近日志
bid-system update     # 拉取代码并重启
bid-system health      # 健康检查
```

---

## 📊 服务信息

### 端口

| 服务 | 端口 | 地址 |
|------|------|------|
| PostgreSQL | 5432 | localhost:5432 |
| FastAPI 后端 | 8000 | 0.0.0.0:8000 |

### API 访问

- **API 文档**：http://服务器IP:8000/docs
- **API 根路径**：http://服务器IP:8000/
- **健康检查**：http://服务器IP:8000/api/v1/health

### FRP 代理配置

如果使用 frp + caddy，配置如下：

**frp 客户端配置 (frpc.ini):**
```ini
[bid-system-backend]
type = tcp
local_ip = 127.0.0.1
local_port = 8000
remote_port = 8000  # 公网访问端口
```

**Caddy 配置:**
```caddy
bid.yourdomain.com {
    reverse_proxy localhost:8000
}
```

---

## 🔧 服务管理 (Systemd)

### 查看服务状态
```bash
systemctl status bid-system-backend
systemctl status postgresql
```

### 启动/停止/重启
```bash
# 后端
systemctl start bid-system-backend
systemctl stop bid-system-backend
systemctl restart bid-system-backend

# PostgreSQL
systemctl start postgresql
systemctl stop postgresql
systemctl restart postgresql
```

### 开机自启
```bash
systemctl enable bid-system-backend
systemctl enable postgresql
```

### 查看日志
```bash
# 后端实时日志
journalctl -u bid-system-backend -f

# 后端最近 50 条
journalctl -u bid-system-backend -n 50

# PostgreSQL 日志
journalctl -u postgresql -f
```

---

## 📁 项目结构

```
/root/.openclaw/workspace/bid_system_app/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── agents/            # PydanticAI 智能体
│   │   ├── api/               # API 路由
│   │   ├── db/                # 数据模型
│   │   ├── repositories/       # 数据访问层
│   │   ├── schemas/           # Pydantic 模型
│   │   └── services/          # 业务逻辑
│   ├── venv/                  # Python 虚拟环境
│   └── .env                   # 环境变量
├── frontend/                   # Next.js 前端（未部署）
├── manage.sh                   # 管理脚本
└── DEPLOYMENT.md              # 本文档
```

---

## 🔄 更新代码

### 方式 1：使用管理脚本（推荐）
```bash
bid-system update
```

### 方式 2：手动更新
```bash
cd /root/.openclaw/workspace/bid_system_app
git pull origin main
systemctl restart bid-system-backend
```

### 方式 3：查看更新历史
```bash
cd /root/.openclaw/workspace/bid_system_app
git log --oneline -10
```

---

## 🐛 故障排查

### 服务无法启动

1. 检查服务状态
   ```bash
   systemctl status bid-system-backend
   ```

2. 查看日志
   ```bash
   journalctl -u bid-system-backend -n 50
   ```

3. 检查端口占用
   ```bash
   lsof -i:8000
   ```

### 数据库连接失败

1. 检查 PostgreSQL 状态
   ```bash
   systemctl status postgresql
   ```

2. 测试连接
   ```bash
   PGPASSWORD=postgres psql -h localhost -U postgres -d bid_system_app
   ```

### FRP 代理无法访问

1. 检查 frpc 状态
   ```bash
   ps aux | grep frpc
   ```

2. 检查端口监听
   ```bash
   netstat -tuln | grep 8000
   ```

3. 查看防火墙
   ```bash
   ufw status
   ```

---

## 🔐 环境变量配置

编辑 `/root/.openclaw/workspace/bid_system_app/backend/.env`：

```bash
# 数据库
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=bid_system_app

# JWT 认证
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# AI Agent
OPENAI_API_KEY=your-openai-api-key
AI_MODEL=gpt-4o-mini
AI_TEMPERATURE=0.7

# CORS
CORS_ORIGINS=["http://your-frontend-domain"]
```

**修改后重启服务：**
```bash
systemctl restart bid-system-backend
```

---

## 📞 获取帮助

查看可用命令：
```bash
bid-system
```

查看项目文档：
```bash
cd /root/.openclaw/workspace/bid_system_app
cat README.md
```

---

## ✅ 部署检查清单

- [x] PostgreSQL 已安装并运行
- [x] FastAPI 后端已配置为 systemd 服务
- [x] 服务已设置为开机自启
- [x] 管理脚本已配置（bid-system）
- [ ] FRP 代理已配置（待配置）
- [ ] Caddy 反向代理已配置（待配置）
- [ ] 域名已配置（可选）
- [ ] SSL 证书已配置（可选）

---

**最后更新：** 2026-02-07
