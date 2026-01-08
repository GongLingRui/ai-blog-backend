# AI Muse Blog - Backend API

AI学习博客平台的后端服务，基于 FastAPI + PostgreSQL + SQLAlchemy 构建。

## 技术栈

- **Python 3.11+** - 编程语言
- **FastAPI 0.104+** - Web框架
- **SQLAlchemy 2.0+** - ORM
- **PostgreSQL 15+** - 关系型数据库
- **Alembic 1.12+** - 数据库迁移
- **Redis 5.0+** - 缓存和速率限制
- **Celery 5.3+** - 异步任务队列

## 项目结构

```
backend/
├── app/                      # 应用主目录
│   ├── api/                  # API路由
│   │   └── v1/               # API v1版本
│   ├── core/                 # 核心功能（数据库、安全等）
│   ├── models/               # SQLAlchemy模型
│   ├── schemas/              # Pydantic模式
│   ├── crud/                 # CRUD操作
│   ├── services/             # 业务逻辑服务
│   ├── middlewares/          # 中间件
│   ├── utils/                # 工具函数
│   ├── main.py               # 应用入口
│   └── config.py             # 配置管理
├── alembic/                  # 数据库迁移
├── tests/                    # 测试
├── uploads/                  # 上传文件
├── requirements.txt          # 依赖
├── .env.example              # 环境变量示例
└── README.md                 # 项目文档
```

## 快速开始

### 1. 环境要求

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (可选)

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量示例文件
copy .env.example .env

# 编辑.env文件，配置数据库连接等信息
```

必需配置项：
```
DATABASE_URL=postgresql://user:password@localhost:5432/ai_muse_blog
SECRET_KEY=your-secret-key-here
```

### 4. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 或使用初始化脚本
python scripts/init_db.py
```

### 5. 启动服务

```bash
# 开发模式（自动重载）
python -m app.main

# 或使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：
- API文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc

### 6. 开发工具

```bash
# 代码格式化
black app/ tests/

# 代码检查
flake8 app/ tests/

# 类型检查
mypy app/

# 运行测试
pytest

# 测试覆盖率
pytest --cov=app --cov-report=html
```

## API端点

### 认证
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新Token
- `GET /api/v1/auth/me` - 获取当前用户
- `PUT /api/v1/auth/change-password` - 修改密码

### 用户
- `GET /api/v1/users` - 获取用户列表
- `GET /api/v1/users/{id}` - 获取用户详情
- `PATCH /api/v1/users/{id}` - 更新用户资料
- `GET /api/v1/users/{id}/articles` - 获取用户的文章

### 文章
- `GET /api/v1/articles` - 获取文章列表
- `GET /api/v1/articles/{id}` - 获取文章详情
- `GET /api/v1/articles/slug/{slug}` - 通过slug获取文章
- `POST /api/v1/articles` - 创建文章
- `PUT /api/v1/articles/{id}` - 更新文章
- `DELETE /api/v1/articles/{id}` - 删除文章
- `POST /api/v1/articles/{id}/view` - 增加浏览量

### 分类
- `GET /api/v1/categories` - 获取分类列表
- `GET /api/v1/categories/{id}` - 获取分类详情

### 标签
- `GET /api/v1/tags` - 获取标签列表
- `GET /api/v1/tags/search` - 搜索标签

## 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 查看迁移历史
alembic history
```

## 开发指南

### 添加新的API端点

1. 在 `app/api/v1/` 中创建新的路由文件
2. 在 `app/api/v1/router.py` 中注册路由
3. 在 `app/schemas/` 中定义请求/响应模型
4. 在 `app/crud/` 中实现数据库操作
5. 在 `app/models/` 中定义数据模型

### 添加新的数据模型

1. 在 `app/models/` 中创建模型文件
2. 创建对应的Schema在 `app/schemas/`
3. 创建CRUD操作在 `app/crud/`
4. 运行 `alembic revision --autogenerate -m "description"`
5. 运行 `alembic upgrade head`

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t ai-muse-blog-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env ai-muse-blog-backend
```

### 生产环境

```bash
# 使用gunicorn运行
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | PostgreSQL连接字符串 | - |
| `SECRET_KEY` | JWT密钥 | - |
| `REDIS_URL` | Redis连接字符串 | redis://localhost:6379/0 |
| `DEBUG` | 调试模式 | True |
| `CORS_ORIGINS` | 允许的CORS源 | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token过期时间(分钟) | 15 |

## 许可证

MIT License
