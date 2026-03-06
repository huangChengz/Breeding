# AI育种项目申报系统 - 启动指南

## 前置要求

### 1. 安装 PostgreSQL
- 下载: https://www.postgresql.org/download/windows/
- 安装时设置用户名 `postgres` 和密码
- 默认端口: `5432`

### 2. 获取通义千问 API Key
- 访问: https://dashscope.console.aliyun.com/
- 注册/登录阿里云账号
- 进入控制台 -> 创建 API Key
- 复制 API Key

---

## 配置步骤

### 步骤 1: 配置数据库连接
编辑 `backend/.env` 文件:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=您设置的密码
POSTGRES_DB=breeding
```

### 步骤 2: 配置 API Key
编辑 `backend/.env` 文件:

```env
DASHSCOPE_API_KEY=您获取的API Key
```

### 步骤 3: 创建数据库
在 psql 或 pgAdmin 中执行:

```sql
CREATE DATABASE breeding;
```

### 步骤 4: 初始化数据库表
```bash
cd backend
psql -U postgres -d breeding -f ../database/schema.sql
```

---

## 启动项目

### 后端
```bash
cd backend
uvicorn app.main:app --reload
```

### 前端
```bash
cd frontend
npm run dev
```

---

## 访问系统
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
