# AI Muse Blog

## 前端地址:

https://github.com/GongLingRui/ai-muse-blog

一个现代化的 AI 学习博客平台，支持文章发布、评论、点赞、收藏、关注等功能。

## 项目简介

AI Muse Blog 是一个全栈博客平台，专为 AI 学习和技术分享而设计。它提供了完整的内容管理、社交互动和个性化体验功能。

### 核心特性

- **文章管理**
  - 富文本 Markdown 编辑器
  - 支持代码高亮
  - 文章草稿和发布
  - 文章浏览统计

- **社交互动**
  - 评论系统
  - 点赞功能
  - 收藏文章
  - 关注用户

- **内容组织**
  - 标签系统
  - 分类管理
  - 搜索功能
  - 推荐算法

- **用户体验**
  - 响应式设计
  - 深色模式
  - 实时通知
  - 个人资料管理

## 技术栈

### 后端
- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **缓存**: Redis 7+
- **任务队列**: Celery 5.3+
- **认证**: JWT (python-jose)
- **文档**: Swagger/OpenAPI

### 前端
- **框架**: React 18.3+
- **构建工具**: Vite 5.4+
- **语言**: TypeScript 5.8+
- **UI 组件**: shadcn/ui (Radix UI)
- **样式**: Tailwind CSS 3.4+
- **状态管理**: TanStack Query 5.83+
- **路由**: React Router DOM 6.30+
- **Markdown**: react-markdown
- **代码高亮**: react-syntax-highlighter

### DevOps
- **容器化**: Docker & Docker Compose
- **数据库迁移**: Alembic
- **代码质量**: ESLint, Black, Flake8
- **测试**: Pytest, Vitest

## 项目结构

```
ai-muse-blog/
├── backend/                  # 后端 API 服务
│   ├── app/                  # 应用主目录
│   │   ├── api/              # API 路由
│   │   ├── core/             # 核心功能
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic 模式
│   │   ├── crud/             # CRUD 操作
│   │   ├── services/         # 业务逻辑
│   │   └── middlewares/      # 中间件
│   ├── alembic/              # 数据库迁移
│   ├── tests/                # 测试
│   └── requirements.txt      # Python 依赖
├── ai-muse-blog/            # 前端应用
│   ├── src/
│   │   ├── components/       # React 组件
│   │   ├── contexts/         # React Context
│   │   ├── hooks/            # 自定义 Hooks
│   │   ├── lib/              # 工具库
│   │   ├── pages/            # 页面组件
│   │   └── types/            # TypeScript 类型
│   └── package.json          # Node 依赖
├── docs/                     # 项目文档
├── docker-compose.yml        # Docker 编排
└── README.md                 # 本文件
```

## 快速开始

### 前置要求

- Docker 和 Docker Compose
- 或 Node.js 18+ 和 Python 3.11+
- PostgreSQL 15+ (如果不使用 Docker)
- Redis 7+ (可选)

### 使用 Docker (推荐)

```bash
# 1. 克隆项目
git clone <repository-url>
cd ai-muse-blog

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量

# 3. 启动所有服务
docker-compose up -d

# 4. 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 5. 访问应用
# 前端: http://localhost
# 后端 API: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 手动安装

#### 后端安装

```bash
cd backend

# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 5. 初始化数据库
alembic upgrade head

# 6. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端安装

```bash
cd ai-muse-blog

# 1. 安装依赖
npm install

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 VITE_API_BASE_URL

# 3. 启动开发服务器
npm run dev

# 访问 http://localhost:5173
```

## 环境变量

### 根目录 `.env`

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ai_muse_blog

# JWT
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=AI Muse Blog
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### 后端 `.env`

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_muse_blog
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

### 前端 `.env`

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 核心功能

### 1. 用户认证
- 注册/登录
- JWT Token 认证
- Token 刷新机制
- 密码加密存储

### 2. 文章管理
- 创建/编辑/删除文章
- Markdown 编辑器
- 文章状态（草稿/已发布）
- 浏览量统计

### 3. 互动功能
- 评论系统
- 点赞/取消点赞
- 收藏/取消收藏
- 关注/取消关注

### 4. 内容组织
- 标签管理
- 分类管理
- 搜索文章
- 推荐算法

### 5. 用户功能
- 个人资料编辑
- 头像上传
- 我的文章
- 我的收藏
- 我的关注

## API 文档

启动后端服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发指南

详细的开发指南请参考：
- [开发指南](./DEVELOPMENT.md) - 开发环境设置和最佳实践
- [部署指南](./DEPLOYMENT.md) - 生产环境部署
- [变更日志](./CHANGELOG.md) - 版本更新记录

## 文档目录

- [项目概览](./docs/01-project-overview.md)
- [数据库设计](./docs/02-database-design.md)
- [后端 API 设计](./docs/03-backend-api-design.md)
- [前端优化](./docs/04-frontend-optimization.md)
- [实施总结](./docs/05-implementation-summary.md)
- [API 端点列表](./docs/06-api-endpoints.md)
- [测试指南](./docs/07-testing-guide.md)
- [故障排除](./docs/08-troubleshooting.md)

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](./LICENSE) 文件。

## 支持

如有问题或建议，请：
- 提交 Issue
- 发送邮件至 support@example.com
- 加入我们的 Discord 社区

## 路线图

### v1.1 (计划中)
- [ ] 实时通知系统
- [ ] 文章版本历史
- [ ] 协作编辑功能
- [ ] 移动应用

### v1.2 (计划中)
- [ ] AI 内容推荐
- [ ] 语音搜索
- [ ] 视频教程支持
- [ ] 多语言支持

## 致谢

感谢所有贡献者和开源项目的作者！

---

**Made with ❤️ by AI Muse Blog Team**
