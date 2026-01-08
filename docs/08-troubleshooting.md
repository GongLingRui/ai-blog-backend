# Troubleshooting Guide - AI Muse Blog

本文档提供 AI Muse Blog 项目的常见问题、调试方法和解决方案。

## 目录

- [快速诊断](#快速诊断)
- [开发环境问题](#开发环境问题)
- [后端问题](#后端问题)
- [前端问题](#前端问题)
- [数据库问题](#数据库问题)
- [部署问题](#部署问题)
- [性能问题](#性能问题)
- [安全问题](#安全问题)

## 快速诊断

### 健康检查端点

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 预期响应
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

### 检查服务状态

```bash
# 检查所有 Docker 容器
docker compose ps

# 检查后端日志
docker compose logs backend

# 检查前端日志
docker compose logs frontend

# 实时查看日志
docker compose logs -f
```

### 常用诊断命令

```bash
# 检查端口占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# 检查数据库连接
psql -U postgres -h localhost -d ai_muse_blog

# 检查 Redis 连接
redis-cli ping

# 检查 Node 进程
ps aux | grep node
```

## 开发环境问题

### 问题：端口已被占用

**症状**:
```
Error: listen EADDRINUSE: address already in use :::8000
```

**解决方案**:

```bash
# 方案 1: 终止占用端口的进程
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9

# 方案 2: 更改端口
# 后端 (backend/.env)
PORT=8001

# 前端 (ai-muse-blog/vite.config.ts)
server: {
  port: 5174
}
```

### 问题：npm install 失败

**症状**:
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
```

**解决方案**:

```bash
# 方案 1: 清除缓存
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# 方案 2: 使用 --legacy-peer-deps
npm install --legacy-peer-deps

# 方案 3: 使用 bun 代替 npm
bun install
```

### 问题：Python 依赖安装失败

**症状**:
```
error: Microsoft Visual C++ 14.0 is required
```

**解决方案** (Windows):

```bash
# 方案 1: 安装预编译的二进制包
pip install --only-binary :all: <package-name>

# 方案 2: 使用 conda
conda install -c conda-forge <package-name>

# 方案 3: 安装 Visual Studio Build Tools
# 下载并安装 Visual Studio Build Tools
```

### 问题：Docker 构建失败

**症状**:
```
ERROR [builder] failed to solve
```

**解决方案**:

```bash
# 清除 Docker 缓存
docker system prune -a

# 重新构建
docker compose build --no-cache

# 检查磁盘空间
df -h

# 如果磁盘空间不足
docker system prune
docker volume prune
```

## 后端问题

### 问题：数据库连接失败

**症状**:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**诊断**:

```bash
# 检查 PostgreSQL 是否运行
docker compose ps postgres

# 测试数据库连接
psql -U postgres -h localhost -d ai_muse_blog

# 检查数据库日志
docker compose logs postgres
```

**解决方案**:

```bash
# 检查 DATABASE_URL
# backend/.env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_muse_blog

# 确保用户和密码正确
# 确保数据库存在
psql -U postgres -c "CREATE DATABASE ai_muse_blog;"

# 重启 PostgreSQL
docker compose restart postgres
```

### 问题：Alembic 迁移失败

**症状**:
```
FAILED: Target database is not up to date
```

**诊断**:

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history
```

**解决方案**:

```bash
# 方案 1: 重置到基础版本
alembic downgrade base
alembic upgrade head

# 方案 2: 手动标记为最新
alembic stamp head

# 方案 3: 删除并重建所有表
alembic downgrade base
# 手动删除所有表
alembic upgrade head
```

### 问题：CORS 错误

**症状**:
```
Access to XMLHttpRequest at 'http://localhost:8000' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**解决方案**:

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:80",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 问题：JWT Token 无效

**症状**:
```
Could not validate credentials
```

**诊断**:

```bash
# 检查 SECRET_KEY 是否一致
# backend/.env
echo $SECRET_KEY

# 检查 token 是否过期
# 使用 jwt.io 解码并检查 exp 字段
```

**解决方案**:

```python
# 确保 SECRET_KEY 已设置且长度至少 32 字符
# backend/.env
SECRET_KEY=your-secret-key-at-least-32-characters-long

# 重新生成 token
openssl rand -hex 32
```

### 问题：API 响应慢

**诊断**:

```python
# 启用 SQL 日志
# backend/app/core/database.py
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True  # 启用 SQL 查询日志
)
```

**解决方案**:

```python
# 1. 添加数据库索引
CREATE INDEX idx_articles_created_at ON articles(created_at DESC);

# 2. 使用 eager loading 避免N+1查询
from sqlalchemy.orm import joinedload

articles = db.query(Article)\
    .options(joinedload(Article.author))\
    .all()

# 3. 启用 Redis 缓存
from app.core.cache import cache_manager

@cache_manager.cache(ttl=300)
def get_popular_articles():
    return db.query(Article).order_by(Article.views.desc()).limit(10).all()
```

## 前端问题

### 问题：API 请求 404

**症状**:
```
GET http://localhost:5173/api/v1/articles 404 (Not Found)
```

**诊断**:

```bash
# 检查 VITE_API_BASE_URL
cat ai-muse-blog/.env

# 检查后端是否运行
curl http://localhost:8000/health
```

**解决方案**:

```bash
# ai-muse-blog/.env
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 重启开发服务器
npm run dev
```

### 问题：组件不重新渲染

**症状**: 数据更新后 UI 没有变化

**诊断**:

```tsx
// 使用 React DevTools 检查组件状态
// 检查 TanStack Query DevTools
```

**解决方案**:

```tsx
// 1. 确保正确使用 queryKey
const { data } = useQuery({
  queryKey: ['articles', page],  // 包含所有依赖
  queryFn: () => fetchArticles(page),
});

// 2. 手动失效缓存
import { useQueryClient } from '@tanstack/react-query';

const queryClient = useQueryClient();
queryClient.invalidateQueries({ queryKey: ['articles'] });

// 3. 使用 key 作为列表渲染的 key
{articles.map(article => (
  <ArticleCard key={article.id} article={article} />
))}
```

### 问题：路由 404

**症状**: 刷新页面后显示 404

**解决方案**:

```typescript
// ai-muse-blog/src/main.tsx
import { BrowserRouter } from 'react-router-dom';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);

// Vite 配置 (vite.config.ts)
export default defineConfig({
  // ...
  server: {
    // 开发环境已支持
  },
  build: {
    // 生产环境需要服务器配置
  }
});
```

Nginx 配置（生产环境）:

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### 问题：样式不生效

**症状**: Tailwind CSS 类名不生效

**解决方案**:

```bash
# 1. 检查 Tailwind 配置
cat ai-muse-blog/tailwind.config.ts

# 2. 确保样式文件被导入
# src/index.css
@tailwind base;
@tailwind components;
@tailwind utilities;

# 3. 检查 PostCSS 配置
cat ai-muse-blog/postcss.config.js

# 4. 清除缓存并重新构建
rm -rf dist
npm run build
```

### 问题：环境变量未定义

**症状**:
```
Uncaught ReferenceError: VITE_API_BASE_URL is not defined
```

**解决方案**:

```bash
# 1. 确保变量名以 VITE_ 开头
# ai-muse-blog/.env
VITE_API_BASE_URL=http://localhost:8000/api/v1  # ✅
API_BASE_URL=http://localhost:8000/api/v1       # ❌

# 2. 重启开发服务器
# Vite 只在启动时读取 .env 文件

# 3. 使用 import.meta.env 访问
const apiUrl = import.meta.env.VITE_API_BASE_URL;
```

## 数据库问题

### 问题：数据库锁死

**症状**:
```
ERROR: could not obtain lock on relation
```

**解决方案**:

```sql
-- 1. 查看活动连接
SELECT * FROM pg_stat_activity WHERE datname = 'ai_muse_blog';

-- 2. 终止长时间运行的查询
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'ai_muse_blog'
AND state = 'active'
AND query_start < now() - interval '5 minutes';

-- 3. 重启连接池
docker compose restart backend
```

### 问题：查询慢

**诊断**:

```sql
-- 启用慢查询日志
ALTER DATABASE ai_muse_blog SET log_min_duration_statement = 1000;

-- 查看慢查询
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**解决方案**:

```sql
-- 1. 分析查询计划
EXPLAIN ANALYZE
SELECT * FROM articles
WHERE author_id = 1
ORDER BY created_at DESC;

-- 2. 添加索引
CREATE INDEX idx_articles_author_created ON articles(author_id, created_at DESC);

-- 3. 更新表统计信息
ANALYZE articles;
VACUUM ANALYZE articles;
```

### 问题：磁盘空间不足

**诊断**:

```bash
# 检查数据库大小
SELECT pg_size_pretty(pg_database_size('ai_muse_blog'));

# 检查表大小
SELECT
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

**解决方案**:

```sql
-- 1. 清理死元组
VACUUM FULL;

-- 2. 清理并分析
VACUUM ANALYZE;

-- 3. 删除旧数据
DELETE FROM articles WHERE created_at < NOW() - INTERVAL '1 year';

-- 4. 归档旧数据
CREATE TABLE articles_archive AS
SELECT * FROM articles WHERE created_at < NOW() - INTERVAL '1 year';
DELETE FROM articles WHERE created_at < NOW() - INTERVAL '1 year';
```

## 部署问题

### 问题：Docker 容器不断重启

**诊断**:

```bash
# 查看容器日志
docker compose logs backend

# 查看容器退出代码
docker compose ps
```

**解决方案**:

```bash
# 常见原因和解决方案

# 1. 环境变量未设置
# 确保 .env 文件存在且配置正确

# 2. 健康检查失败
# 调整健康检查配置
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 40s  # 增加启动时间

# 3. 内存不足
# 限制内存使用
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
```

### 问题：SSL 证书错误

**症状**:
```
NET::ERR_CERT_AUTHORITY_INVALID
```

**解决方案**:

```bash
# 使用 Let's Encrypt 获取免费证书

# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com

# 自动续期
sudo certbot renew --dry-run

# 检查续期定时任务
sudo systemctl status certbot.timer
```

### 问题：Nginx 502 Bad Gateway

**诊断**:

```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查 Nginx 配置
sudo nginx -t

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

**解决方案**:

```nginx
# nginx/sites-available/ai-muse-blog

# 确保代理配置正确
location /api/ {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # 增加超时时间
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

## 性能问题

### 问题：页面加载慢

**诊断**:

```bash
# 使用 Lighthouse 分析
npm install -g lighthouse
lighthouse https://yourdomain.com --view

# 检查网络请求
# Chrome DevTools -> Network tab
```

**解决方案**:

```typescript
// 1. 代码分割
import { lazy, Suspense } from 'react';

const WriteArticle = lazy(() => import('./pages/WriteArticle'));

// 2. 图片优化
import Image from 'next/image';

<Image
  src={url}
  alt={alt}
  loading="lazy"
  width={200}
  height={100}
/>

// 3. 缓存策略
// React Query 配置
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,  // 5 分钟
      gcTime: 10 * 60 * 1000,    // 10 分钟
    },
  },
});
```

### 问题：内存泄漏

**诊断**:

```bash
# 检查 Node.js 内存使用
# Chrome DevTools -> Memory -> Take Heap Snapshot

# 检查 Python 内存使用
import psutil
print(psutil.virtual_memory())
```

**解决方案**:

```typescript
// 1. 清理事件监听器
useEffect(() => {
  const handler = () => {};
  window.addEventListener('resize', handler);

  return () => {
    window.removeEventListener('resize', handler);
  };
}, []);

// 2. 清理定时器
useEffect(() => {
  const interval = setInterval(() => {}, 1000);

  return () => {
    clearInterval(interval);
  };
}, []);

// 3. 取消未完成的请求
useEffect(() => {
  const controller = new AbortController();

  fetchData(controller.signal);

  return () => {
    controller.abort();
  };
}, []);
```

## 安全问题

### 问题：SQL 注入风险

**解决方案**:

```python
# ✅ 使用 ORM 参数化查询
from sqlalchemy.orm import Session

def get_article(db: Session, article_id: int):
    return db.query(Article).filter(Article.id == article_id).first()

# ❌ 不要使用字符串拼接
def get_article_bad(db: Session, article_id: str):
    return db.execute(f"SELECT * FROM articles WHERE id = {article_id}")
```

### 问题：XSS 攻击风险

**解决方案**:

```tsx
// ✅ React 默认转义
<div>{userInput}</div>

// ❌ 危险：不转义
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// 如果必须使用，先清理 HTML
import DOMPurify from 'dompurify';

const clean = DOMPurify.sanitize(userInput);
<div dangerouslySetInnerHTML={{ __html: clean }} />
```

### 问题：敏感信息泄露

**解决方案**:

```bash
# 1. 确保 .env 在 .gitignore 中
echo ".env" >> .gitignore

# 2. 不要在代码中硬编码敏感信息
# ❌ 坏的做法
SECRET_KEY = "my-secret-key"

# ✅ 好的做法
SECRET_KEY = os.getenv("SECRET_KEY")

# 3. 使用环境变量管理
# .env.example (提交到 git)
SECRET_KEY=your-secret-key-here

# .env (不提交)
SECRET_KEY=actual-secret-key-from-openssl-rand-hex-32
```

## 获取帮助

### 日志位置

```bash
# 后端日志
backend/logs/app.log
backend/logs/error.log

# Docker 日志
docker compose logs backend > backend.log

# Nginx 日志
/var/log/nginx/access.log
/var/log/nginx/error.log
```

### 调试模式

```python
# backend/app/main.py
# 启用调试模式
app = FastAPI(debug=True)

# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 社区资源

- GitHub Issues: [repository-url]/issues
- 文档: [repository-url]/wiki
- Stack Overflow: 标签 `ai-muse-blog`

## 预防措施

### 1. 定期备份

```bash
# 数据库备份
./scripts/backup.sh

# 文件备份
rsync -avz uploads/ backups/uploads/
```

### 2. 监控

```python
# 设置监控告警
from prometheus_client import Counter, start_http_server

REQUEST_COUNT = Counter('requests_total', 'Total requests')

@app.get("/api/v1/articles")
def get_articles():
    REQUEST_COUNT.inc()
    # ...
```

### 3. 健康检查

```bash
# 定期运行健康检查
#!/bin/bash
# health_check.sh

curl -f http://localhost:8000/health || echo "Backend is down!" | mail -s "Alert" admin@example.com
```

---

**最后更新**: 2024-01-08
