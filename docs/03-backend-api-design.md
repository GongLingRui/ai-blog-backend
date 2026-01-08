# 后端API设计文档 (FastAPI)

## 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.104+ | Web框架 |
| SQLAlchemy | 2.0+ | ORM |
| PostgreSQL | 15+ | 关系型数据库 |
| Pydantic | 2.0+ | 数据验证 |
| Alembic | 1.12+ | 数据库迁移 |
| uvicorn | 0.24+ | ASGI服务器 |
| python-jose | 3.3+ | JWT处理 |
| passlib | 1.7+ | 密码哈希 |
| python-multipart | 0.0+ | 文件上传 |
| aiofiles | 23.2+ | 异步文件操作 |
| Pillow | 10.1+ | 图片处理 |
| redis | 5.0+ | 缓存 |
| celery | 5.3+ | 异步任务 |

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI应用入口
│   ├── config.py                  # 配置管理
│   ├── dependencies.py            # 依赖注入
│   │
│   ├── core/                      # 核心功能
│   │   ├── __init__.py
│   │   ├── security.py            # JWT和密码处理
│   │   ├── database.py            # 数据库连接
│   │   ├── redis.py               # Redis连接
│   │   └── utils.py               # 工具函数
│   │
│   ├── models/                    # SQLAlchemy模型
│   │   ├── __init__.py
│   │   ├── user.py                # 用户模型
│   │   ├── article.py             # 文章模型
│   │   ├── category.py            # 分类模型
│   │   ├── tag.py                 # 标签模型
│   │   ├── comment.py             # 评论模型
│   │   ├── like.py                # 点赞模型
│   │   ├── bookmark.py            # 收藏模型
│   │   ├── follow.py              # 关注模型
│   │   ├── notification.py        # 通知模型
│   │   ├── paper.py               # 论文模型
│   │   └── upload.py              # 上传模型
│   │
│   ├── schemas/                   # Pydantic模式
│   │   ├── __init__.py
│   │   ├── user.py                # 用户Schema
│   │   ├── article.py             # 文章Schema
│   │   ├── category.py            # 分类Schema
│   │   ├── tag.py                 # 标签Schema
│   │   ├── comment.py             # 评论Schema
│   │   ├── like.py                # 点赞Schema
│   │   ├── bookmark.py            # 收藏Schema
│   │   ├── follow.py              # 关注Schema
│   │   ├── notification.py        # 通知Schema
│   │   ├── paper.py               # 论文Schema
│   │   └── common.py              # 通用Schema
│   │
│   ├── crud/                      # CRUD操作
│   │   ├── __init__.py
│   │   ├── user.py                # 用户CRUD
│   │   ├── article.py             # 文章CRUD
│   │   ├── category.py            # 分类CRUD
│   │   ├── tag.py                 # 标签CRUD
│   │   ├── comment.py             # 评论CRUD
│   │   ├── like.py                # 点赞CRUD
│   │   ├── bookmark.py            # 收藏CRUD
│   │   ├── follow.py              # 关注CRUD
│   │   ├── notification.py        # 通知CRUD
│   │   └── paper.py               # 论文CRUD
│   │
│   ├── api/                       # API路由
│   │   ├── __init__.py
│   │   ├── deps.py                # API依赖
│   │   └── v1/                    # API v1
│   │       ├── __init__.py
│   │       ├── router.py          # 路由聚合
│   │       ├── auth.py            # 认证API
│   │       ├── users.py           # 用户API
│   │       ├── articles.py        # 文章API
│   │       ├── categories.py      # 分类API
│   │       ├── tags.py            # 标签API
│   │       ├── comments.py        # 评论API
│   │       ├── likes.py           # 点赞API
│   │       ├── bookmarks.py       # 收藏API
│   │       ├── follows.py         # 关注API
│   │       ├── notifications.py   # 通知API
│   │       ├── papers.py          # 论文API
│   │       └── upload.py          # 上传API
│   │
│   ├── services/                  # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── auth_service.py        # 认证服务
│   │   ├── article_service.py     # 文章服务
│   │   ├── notification_service.py # 通知服务
│   │   └── search_service.py      # 搜索服务
│   │
│   ├── utils/                     # 工具模块
│   │   ├── __init__.py
│   │   ├── slug.py                # slug生成
│   │   ├── image.py               # 图片处理
│   │   └── text.py                # 文本处理
│   │
│   ├── middlewares/               # 中间件
│   │   ├── __init__.py
│   │   ├── cors.py                # CORS配置
│   │   ├── error_handler.py       # 错误处理
│   │   └── rate_limit.py          # 速率限制
│   │
│   └── tasks/                     # Celery任务
│       ├── __init__.py
│       ├── celery_app.py          # Celery配置
│       └── tasks.py               # 任务定义
│
├── alembic/                       # 数据库迁移
│   ├── versions/
│   └── env.py
│
├── tests/                         # 测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_crud/
│   └── test_services/
│
├── scripts/                       # 脚本
│   ├── init_db.py                 # 初始化数据库
│   └── seed_data.py               # 填充初始数据
│
├── uploads/                       # 上传文件存储
│   ├── avatars/
│   ├── articles/
│   └── temp/
│
├── .env.example                   # 环境变量示例
├── .env                           # 环境变量
├── requirements.txt               # 依赖
├── pyproject.toml                 # 项目配置
├── alembic.ini                    # Alembic配置
└── README.md                      # 后端文档
```

## API基础信息

### Base URL

```
开发环境: http://localhost:8000
生产环境: https://api.yourdomain.com
```

### API版本

```
当前版本: v1
完整路径: /api/v1
```

### 认证方式

使用 JWT (JSON Web Token) 进行认证：

```
Authorization: Bearer <access_token>
```

### 响应格式

```typescript
// 成功响应 (200, 201)
{
  "success": true,
  "data": <response_data>,
  "message": "Success message"
}

// 错误响应 (400, 401, 403, 404, 500)
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  }
}

// 分页响应
{
  "success": true,
  "data": <items>,
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "pages": 5
  }
}
```

## API端点设计

### 1. 认证API (`/api/v1/auth`)

#### 1.1 用户注册

```python
POST /api/v1/auth/register

Request Body:
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe"  # 可选
}

Response 201:
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "username": "johndoe",
      "full_name": "John Doe",
      "role": "reader",
      "created_at": "2024-01-08T00:00:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
}
```

#### 1.2 用户登录

```python
POST /api/v1/auth/login

Request Body:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response 200:
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "username": "johndoe",
      "full_name": "John Doe",
      "role": "author"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
}
```

#### 1.3 刷新Token

```python
POST /api/v1/auth/refresh

Request Body:
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}

Response 200:
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
}
```

#### 1.4 获取当前用户

```python
GET /api/v1/auth/me

Headers:
Authorization: Bearer <access_token>

Response 200:
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "avatar_url": "https://...",
    "bio": "AI enthusiast",
    "role": "author",
    "is_verified": false,
    "created_at": "2024-01-08T00:00:00Z"
  }
}
```

#### 1.5 修改密码

```python
PUT /api/v1/auth/change-password

Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "old_password": "OldPass123!",
  "new_password": "NewPass456!"
}

Response 200:
{
  "success": true,
  "message": "Password changed successfully"
}
```

### 2. 用户管理API (`/api/v1/users`)

#### 2.1 获取用户列表

```python
GET /api/v1/users?page=1&page_size=20&role=author&search=john

Query Parameters:
- page: 页码（默认1）
- page_size: 每页数量（默认20，最大100）
- role: 角色过滤（reader, author, admin）
- search: 搜索用户名或邮箱

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "username": "johndoe",
      "full_name": "John Doe",
      "avatar_url": "https://...",
      "bio": "AI enthusiast",
      "role": "author",
      "is_verified": true,
      "followers_count": 123,
      "following_count": 45,
      "articles_count": 12
    }
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "pages": 5
  }
}
```

#### 2.2 获取用户详情

```python
GET /api/v1/users/{user_id}

Response 200:
{
  "success": true,
  "data": {
    "id": "uuid",
    "username": "johndoe",
    "full_name": "John Doe",
    "avatar_url": "https://...",
    "bio": "AI enthusiast and ML engineer",
    "website": "https://...",
    "location": "San Francisco, CA",
    "twitter_username": "johndoe",
    "github_username": "johndoe",
    "linkedin_url": "https://...",
    "expertise": ["NLP", "Computer Vision"],
    "role": "author",
    "is_verified": true,
    "followers_count": 123,
    "following_count": 45,
    "articles_count": 12,
    "created_at": "2024-01-08T00:00:00Z"
  }
}
```

#### 2.3 更新用户资料

```python
PATCH /api/v1/users/{user_id}

Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "full_name": "John Smith",
  "bio": "Updated bio",
  "website": "https://...",
  "location": "New York",
  "expertise": ["NLP", "Deep Learning", "LLM"]
}

Response 200:
{
  "success": true,
  "data": {
    "id": "uuid",
    "full_name": "John Smith",
    "bio": "Updated bio",
    "updated_at": "2024-01-08T00:00:00Z"
  }
}
```

#### 2.4 上传头像

```python
POST /api/v1/users/{user_id}/avatar

Headers:
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Request Body:
- file: binary (图片文件)

Response 200:
{
  "success": true,
  "data": {
    "avatar_url": "https://api.example.com/uploads/avatars/user_uuid.jpg"
  }
}
```

#### 2.5 获取用户的文章

```python
GET /api/v1/users/{user_id}/articles?page=1&page_size=10&status=published

Query Parameters:
- page: 页码
- page_size: 每页数量
- status: 文章状态（draft, published, archived）

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "Introduction to Transformers",
      "slug": "introduction-to-transformers",
      "excerpt": "Transformers have revolutionized NLP...",
      "cover_image_url": "https://...",
      "view_count": 1234,
      "like_count": 56,
      "comment_count": 12,
      "published_at": "2024-01-08T00:00:00Z"
    }
  ],
  "pagination": {
    "total": 12,
    "page": 1,
    "page_size": 10,
    "pages": 2
  }
}
```

### 3. 文章API (`/api/v1/articles`)

#### 3.1 获取文章列表

```python
GET /api/v1/articles?page=1&page_size=20&status=published&category_id=uuid&tag_id=uuid&search=transformer&sort=published_at&order=desc

Query Parameters:
- page: 页码（默认1）
- page_size: 每页数量（默认20）
- status: 状态过滤（draft, published, archived）
- category_id: 分类ID过滤
- tag_id: 标签ID过滤
- search: 搜索关键词（标题和内容）
- author_id: 作者ID过滤
- sort: 排序字段（published_at, view_count, like_count, created_at）
- order: 排序方向（asc, desc）

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "Understanding BERT",
      "slug": "understanding-bert",
      "excerpt": "BERT is a pre-trained language model...",
      "cover_image_url": "https://...",
      "author": {
        "id": "uuid",
        "username": "johndoe",
        "full_name": "John Doe",
        "avatar_url": "https://..."
      },
      "category": {
        "id": "uuid",
        "name": "NLP",
        "slug": "nlp"
      },
      "tags": [
        {"id": "uuid", "name": "Transformer", "slug": "transformer"},
        {"id": "uuid", "name": "NLP", "slug": "nlp"}
      ],
      "view_count": 2345,
      "like_count": 89,
      "comment_count": 23,
      "reading_time": 15,
      "is_featured": false,
      "published_at": "2024-01-08T00:00:00Z"
    }
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "page_size": 20,
    "pages": 8
  }
}
```

#### 3.2 获取单篇文章

```python
GET /api/v1/articles/{article_id} or /api/v1/articles/slug/{slug}

Response 200:
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Understanding BERT: A Comprehensive Guide",
    "slug": "understanding-bert",
    "content": "# Understanding BERT\n\nFull article content...",
    "excerpt": "BERT is a pre-trained language model...",
    "cover_image_url": "https://...",
    "author": {
      "id": "uuid",
      "username": "johndoe",
      "full_name": "John Doe",
      "avatar_url": "https://...",
      "bio": "AI enthusiast"
    },
    "category": {
      "id": "uuid",
      "name": "NLP",
      "slug": "nlp",
      "description": "Natural Language Processing"
    },
    "tags": [
      {"id": "uuid", "name": "Transformer", "slug": "transformer"},
      {"id": "uuid", "name": "BERT", "slug": "bert"},
      {"id": "uuid", "name": "NLP", "slug": "nlp"}
    ],
    "view_count": 2345,
    "like_count": 89,
    "comment_count": 23,
    "reading_time": 15,
    "is_featured": true,
    "is_top": false,
    "status": "published",
    "published_at": "2024-01-08T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-08T00:00:00Z"
  }
}
```

#### 3.3 创建文章

```python
POST /api/v1/articles

Headers:
Authorization: Bearer <access_token>
Content-Type: application/json

Request Body:
{
  "title": "Introduction to GPT-4",
  "content": "# GPT-4\n\nFull content...",
  "excerpt": "Learn about GPT-4...",
  "cover_image_url": "https://...",  # 可选
  "category_id": "uuid",
  "tags": ["LLM", "GPT", "OpenAI", "Tutorial"],
  "status": "draft"  # draft or published
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Introduction to GPT-4",
    "slug": "introduction-to-gpt-4",
    "status": "draft",
    "author_id": "uuid",
    "created_at": "2024-01-08T00:00:00Z"
  }
}
```

#### 3.4 更新文章

```python
PUT /api/v1/articles/{article_id}

Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "title": "Updated Title",
  "content": "Updated content...",
  "excerpt": "Updated excerpt...",
  "category_id": "uuid",
  "tags": ["LLM", "GPT", "OpenAI", "Tutorial", "Advanced"],
  "status": "published"
}

Response 200:
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Updated Title",
    "slug": "updated-title",
    "status": "published",
    "updated_at": "2024-01-08T00:00:00Z"
  }
}
```

#### 3.5 删除文章

```python
DELETE /api/v1/articles/{article_id}

Headers:
Authorization: Bearer <access_token>

Response 200:
{
  "success": true,
  "message": "Article deleted successfully"
}
```

#### 3.6 增加浏览量

```python
POST /api/v1/articles/{article_id}/view

Response 200:
{
  "success": true,
  "data": {
    "view_count": 2346
  }
}
```

#### 3.7 获取热门文章

```python
GET /api/v1/articles/trending?days=7&limit=10

Query Parameters:
- days: 统计天数（默认7）
- limit: 返回数量（默认10）

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "...",
      "slug": "...",
      "view_count": 12345,
      "like_count": 567,
      "comment_count": 89
    }
  ]
}
```

#### 3.8 获取推荐文章

```python
GET /api/v1/articles/{article_id}/related?limit=5

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "...",
      "slug": "...",
      "excerpt": "..."
    }
  ]
}
```

### 4. 分类API (`/api/v1/categories`)

#### 4.1 获取所有分类

```python
GET /api/v1/categories

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "深度学习",
      "slug": "deep-learning",
      "description": "深度学习相关文章",
      "icon": "Brain",
      "color": "#3B82F6",
      "parent_id": null,
      "sort_order": 1,
      "articles_count": 45
    }
  ]
}
```

#### 4.2 获取分类详情

```python
GET /api/v1/categories/{category_id}

Response 200:
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "深度学习",
    "slug": "deep-learning",
    "description": "深度学习相关文章",
    "icon": "Brain",
    "color": "#3B82F6",
    "articles_count": 45,
    "articles": [
      {
        "id": "uuid",
        "title": "Introduction to Deep Learning",
        "slug": "introduction-to-deep-learning",
        "published_at": "2024-01-08T00:00:00Z"
      }
    ]
  }
}
```

#### 4.3 创建分类（管理员）

```python
POST /api/v1/categories

Headers:
Authorization: Bearer <access_token> (需要admin权限)

Request Body:
{
  "name": "强化学习",
  "slug": "reinforcement-learning",
  "description": "强化学习和RL应用",
  "icon": "Gamepad2",
  "color": "#EF4444",
  "parent_id": null,
  "sort_order": 5
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "强化学习",
    "slug": "reinforcement-learning"
  }
}
```

#### 4.4 更新分类（管理员）

```python
PUT /api/v1/categories/{category_id}

Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "name": "强化学习进阶",
  "description": "Updated description"
}

Response 200:
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "强化学习进阶"
  }
}
```

#### 4.5 删除分类（管理员）

```python
DELETE /api/v1/categories/{category_id}

Headers:
Authorization: Bearer <access_token>

Response 200:
{
  "success": true,
  "message": "Category deleted successfully"
}
```

### 5. 标签API (`/api/v1/tags`)

#### 5.1 获取所有标签

```python
GET /api/v1/tags?sort=usage_count&order=desc

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Transformer",
      "slug": "transformer",
      "description": "Transformer架构相关",
      "color": "#3B82F6",
      "usage_count": 45
    }
  ]
}
```

#### 5.2 搜索标签

```python
GET /api/v1/tags/search?q=trans

Query Parameters:
- q: 搜索关键词

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Transformer",
      "slug": "transformer",
      "usage_count": 45
    }
  ]
}
```

#### 5.3 创建标签

```python
POST /api/v1/tags

Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "name": "LangChain",
  "slug": "langchain",
  "description": "LangChain框架",
  "color": "#8B5CF6"
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "LangChain",
    "slug": "langchain"
  }
}
```

### 6. 评论API (`/api/v1/comments`)

#### 6.1 获取文章评论

```python
GET /api/v1/comments?article_id={article_id}&parent_id=null&page=1&page_size=20

Query Parameters:
- article_id: 文章ID
- parent_id: 父评论ID（null获取顶级评论）
- page: 页码
- page_size: 每页数量

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "article_id": "uuid",
      "content": "Great article! Thanks for sharing.",
      "author": {
        "id": "uuid",
        "username": "janedoe",
        "full_name": "Jane Doe",
        "avatar_url": "https://..."
      },
      "parent_id": null,
      "like_count": 5,
      "replies_count": 2,
      "is_edited": false,
      "created_at": "2024-01-08T00:00:00Z",
      "replies": [
        {
          "id": "uuid",
          "content": "Reply to comment...",
          "author": {...},
          "created_at": "2024-01-08T01:00:00Z"
        }
      ]
    }
  ],
  "pagination": {
    "total": 23,
    "page": 1,
    "page_size": 20,
    "pages": 2
  }
}
```

#### 6.2 创建评论

```python
POST /api/v1/comments

Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "article_id": "uuid",
  "content": "Great article! Thanks for sharing.",
  "parent_id": "uuid"  # 可选，用于回复评论
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "article_id": "uuid",
    "content": "Great article! Thanks for sharing.",
    "author_id": "uuid",
    "status": "published",
    "created_at": "2024-01-08T00:00:00Z"
  }
}
```

#### 6.3 更新评论

```python
PUT /api/v1/comments/{comment_id}

Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "content": "Updated comment content"
}

Response 200:
{
  "success": true,
  "data": {
    "id": "uuid",
    "content": "Updated comment content",
    "is_edited": true,
    "updated_at": "2024-01-08T00:00:00Z"
  }
}
```

#### 6.4 删除评论

```python
DELETE /api/v1/comments/{comment_id}

Headers:
Authorization: Bearer <access_token>

Response 200:
{
  "success": true,
  "message": "Comment deleted successfully"
}
```

### 7. 点赞API (`/api/v1/likes`)

#### 7.1 点赞文章/评论

```python
POST /api/v1/likes

Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "target_id": "uuid",
  "target_type": "article"  # or "comment"
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "target_id": "uuid",
    "target_type": "article",
    "created_at": "2024-01-08T00:00:00Z"
  }
}
```

#### 7.2 取消点赞

```python
DELETE /api/v1/likes/{target_id}/{target_type}

Headers:
Authorization: Bearer <access_token>

Response 200:
{
  "success": true,
  "message": "Like removed successfully"
}
```

#### 7.3 检查是否已点赞

```python
GET /api/v1/likes/check?target_id={target_id}&target_type={target_type}

Headers:
Authorization: Bearer <access_token>

Response 200:
{
  "success": true,
  "data": {
    "is_liked": true
  }
}
```

### 8. 收藏API (`/api/v1/bookmarks`)

#### 8.1 获取用户收藏

```python
GET /api/v1/bookmarks?folder=default&page=1&page_size=20

Headers:
Authorization: Bearer <access_token>

Query Parameters:
- folder: 收藏夹名称
- page: 页码
- page_size: 每页数量

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "article": {
        "id": "uuid",
        "title": "Introduction to Transformers",
        "slug": "introduction-to-transformers",
        "excerpt": "...",
        "cover_image_url": "https://..."
      },
      "folder": "default",
      "notes": "Great reference",
      "created_at": "2024-01-08T00:00:00Z"
    }
  ],
  "pagination": {...}
}
```

#### 8.2 添加收藏

```python
POST /api/v1/bookmarks

Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "article_id": "uuid",
  "folder": "default",  # 可选
  "notes": "Great article"  # 可选
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "article_id": "uuid",
    "folder": "default"
  }
}
```

#### 8.3 删除收藏

```python
DELETE /api/v1/bookmarks/{article_id}

Headers:
Authorization: Bearer <access_token>

Response 200:
{
  "success": true,
  "message": "Bookmark removed successfully"
}
```

### 9. 关注API (`/api/v1/follows`)

#### 9.1 关注用户

```python
POST /api/v1/follows

Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "following_id": "uuid"
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "following_id": "uuid",
    "created_at": "2024-01-08T00:00:00Z"
  }
}
```

#### 9.2 取消关注

```python
DELETE /api/v1/follows/{user_id}

Headers:
Authorization: Bearer <access_token>

Response 200:
{
  "success": true,
  "message": "Unfollowed successfully"
}
```

#### 9.3 获取关注者列表

```python
GET /api/v1/follows/{user_id}/followers?page=1&page_size=20

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "username": "johndoe",
      "full_name": "John Doe",
      "avatar_url": "https://...",
      "followed_at": "2024-01-08T00:00:00Z"
    }
  ],
  "pagination": {...}
}
```

#### 9.4 获取正在关注列表

```python
GET /api/v1/follows/{user_id}/following?page=1&page_size=20

Response 200:
{
  "success": true,
  "data": [...]
}
```

### 10. 通知API (`/api/v1/notifications`)

#### 10.1 获取用户通知

```python
GET /api/v1/notifications?is_read=false&page=1&page_size=20

Headers:
Authorization: Bearer <access_token>

Query Parameters:
- is_read: 过滤已读/未读
- type: 通知类型（comment, like, follow, mention, system）
- page: 页码
- page_size: 每页数量

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "type": "comment",
      "title": "New comment on your article",
      "content": "John Doe commented on 'Introduction to Transformers'",
      "link": "/article/introduction-to-transformers",
      "is_read": false,
      "created_at": "2024-01-08T00:00:00Z"
    }
  ],
  "pagination": {...}
}
```

#### 10.2 标记通知为已读

```python
PATCH /api/v1/notifications/{notification_id}/read

Headers:
Authorization: Bearer <access_token>

Response 200:
{
  "success": true,
  "data": {
    "id": "uuid",
    "is_read": true
  }
}
```

#### 10.3 标记所有通知为已读

```python
POST /api/v1/notifications/read-all

Headers:
Authorization: Bearer <access_token>

Response 200:
{
  "success": true,
  "data": {
    "count": 5
  }
}
```

### 11. 经典论文API (`/api/v1/papers`)

#### 11.1 获取论文列表

```python
GET /api/v1/papers?category_id=uuid&year=2023&search=transformer&page=1&page_size=20

Query Parameters:
- category_id: 分类ID
- year: 年份
- search: 搜索关键词
- page: 页码
- page_size: 每页数量

Response 200:
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "Attention Is All You Need",
      "authors": ["Ashish Vaswani", "Noam Shazeer", "..."],
      "year": 2017,
      "abstract": "The dominant sequence transduction models...",
      "arxiv_id": "1706.03762",
      "citation_count": 50000,
      "category": {
        "name": "Deep Learning"
      },
      "tags": ["Transformer", "NLP"],
      "created_at": "2024-01-08T00:00:00Z"
    }
  ],
  "pagination": {...}
}
```

#### 11.2 提交论文

```python
POST /api/v1/papers

Headers:
Authorization: Bearer <access_token>

Request Body:
{
  "title": "Attention Is All You Need",
  "authors": ["Ashish Vaswani", "Noam Shazeer"],
  "year": 2017,
  "abstract": "The dominant sequence transduction models...",
  "arxiv_id": "1706.03762",
  "category_id": "uuid",
  "tags": ["Transformer", "NLP"]
}

Response 201:
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Attention Is All You Need",
    "is_approved": false
  }
}
```

### 12. 文件上传API (`/api/v1/upload`)

#### 12.1 上传图片

```python
POST /api/v1/upload/image

Headers:
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Request Body:
- file: binary (图片文件)
- type: string (avatar, article_cover, article_image)

Response 200:
{
  "success": true,
  "data": {
    "url": "https://api.example.com/uploads/articles/image_uuid.jpg",
    "filename": "image_uuid.jpg",
    "size": 123456
  }
}
```

## 错误处理

### HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 成功（无返回内容） |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 数据验证失败 |
| 429 | 请求过多（速率限制） |
| 500 | 服务器错误 |

### 错误响应示例

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "email": "Invalid email format",
      "password": "Password must be at least 8 characters"
    }
  }
}
```

## 速率限制

```python
# 默认限制
- 每个IP每分钟最多100个请求
- 每个用户每分钟最多200个请求

# 特殊端点限制
- 登录/注册: 每小时10次
- 文章创建: 每小时5次
- 评论: 每分钟10次
- 上传: 每分钟5次
```

## 缓存策略

```python
# Redis缓存
- 文章列表: 5分钟
- 文章详情: 10分钟
- 分类列表: 1小时
- 标签列表: 30分钟
- 热门文章: 10分钟
- 用户信息: 5分钟

# HTTP缓存头
Cache-Control: public, max-age=300, stale-while-revalidate=600
```

## 安全考虑

1. **密码加密**: bcrypt
2. **JWT**: access_token (15分钟), refresh_token (7天)
3. **CORS**: 配置允许的域名
4. **SQL注入**: SQLAlchemy自动防护
5. **XSS**: 输入验证和输出编码
6. **文件上传**: 类型验证、大小限制、病毒扫描

## 测试API

### 使用curl测试

```bash
# 获取文章列表
curl -X GET 'http://localhost:8000/api/v1/articles?page=1&page_size=10'

# 用户登录
curl -X POST 'http://localhost:8000/api/v1/auth/login' \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# 创建文章
curl -X POST 'http://localhost:8000/api/v1/articles' \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Article","content":"..."}'
```

### 自动生成API文档

FastAPI自动生成交互式API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 更新日志

- **2024-01-08**: 创建FastAPI后端设计文档
