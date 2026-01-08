# Backend API Documentation - AI Muse Blog

本文档提供 AI Muse Blog 后端 API 的详细说明，包括认证、请求/响应格式、错误处理等。

## 目录

- [API 概述](#api-概述)
- [认证](#认证)
- [通用响应格式](#通用响应格式)
- [错误处理](#错误处理)
- [API 端点](#api-端点)
- [数据模型](#数据模型)
- [速率限制](#速率限制)

## API 概述

### 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: JWT Bearer Token

### API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 认证

### JWT Token 认证

API 使用 JWT (JSON Web Token) 进行认证。需要先登录获取 access token，然后在请求头中携带 token。

#### 获取 Token

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

响应：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### 使用 Token

在请求头中添加 Authorization：

```bash
GET /api/v1/articles
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 刷新 Token

Access token 默认 15 分钟过期，使用 refresh token 获取新的 access token：

```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Token 过期处理

当 access token 过期时，API 返回 401 错误：

```json
{
  "detail": "Could not validate credentials"
}
```

客户端应该：
1. 捕获 401 错误
2. 使用 refresh token 调用 `/api/v1/auth/refresh`
3. 更新本地存储的 token
4. 重试原始请求

## 通用响应格式

### 成功响应

单个对象：

```json
{
  "id": 1,
  "title": "Article Title",
  "content": "Article content...",
  "created_at": "2024-01-08T10:30:00Z"
}
```

列表响应（分页）：

```json
{
  "items": [
    { "id": 1, "title": "Article 1" },
    { "id": 2, "title": "Article 2" }
  ],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

### 创建/更新响应

创建成功（201 Created）：

```json
{
  "id": 123,
  "title": "New Article",
  "created_at": "2024-01-08T10:30:00Z"
}
```

更新成功（200 OK）：

```json
{
  "id": 123,
  "title": "Updated Article",
  "updated_at": "2024-01-08T11:00:00Z"
}
```

### 删除响应

删除成功（204 No Content）：无响应体

## 错误处理

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | OK - 请求成功 |
| 201 | Created - 资源创建成功 |
| 204 | No Content - 删除成功 |
| 400 | Bad Request - 请求参数错误 |
| 401 | Unauthorized - 未认证 |
| 403 | Forbidden - 无权限 |
| 404 | Not Found - 资源不存在 |
| 422 | Unprocessable Entity - 验证失败 |
| 429 | Too Many Requests - 速率限制 |
| 500 | Internal Server Error - 服务器错误 |

### 错误响应格式

```json
{
  "detail": "Error message description",
  "status_code": 400,
  "error": "VALIDATION_ERROR"
}
```

### 验证错误

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## API 端点

### 认证端点

#### 用户注册

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePassword123!",
  "full_name": "John Doe"  // 可选
}
```

响应：201 Created

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-08T10:00:00Z"
}
```

#### 用户登录

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

响应：200 OK

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### 获取当前用户

```bash
GET /api/v1/auth/me
Authorization: Bearer <token>
```

响应：200 OK

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "bio": "Software developer",
  "avatar_url": "https://example.com/avatar.jpg",
  "is_active": true,
  "followers_count": 100,
  "following_count": 50,
  "articles_count": 25,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 修改密码

```bash
PUT /api/v1/auth/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

响应：200 OK

```json
{
  "message": "Password changed successfully"
}
```

### 用户端点

#### 获取用户列表

```bash
GET /api/v1/users?page=1&page_size=20&search=john
Authorization: Bearer <token>
```

查询参数：
- `page`: 页码（默认：1）
- `page_size`: 每页数量（默认：20，最大：100）
- `search`: 搜索关键词（用户名或邮箱）

响应：200 OK

```json
{
  "items": [
    {
      "id": 1,
      "username": "johndoe",
      "full_name": "John Doe",
      "avatar_url": "https://example.com/avatar.jpg",
      "bio": "Software developer",
      "followers_count": 100,
      "articles_count": 25
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### 获取用户详情

```bash
GET /api/v1/users/{user_id}
```

响应：200 OK

```json
{
  "id": 1,
  "username": "johndoe",
  "full_name": "John Doe",
  "bio": "Software developer",
  "avatar_url": "https://example.com/avatar.jpg",
  "website": "https://johndoe.com",
  "twitter_handle": "@johndoe",
  "github_handle": "johndoe",
  "followers_count": 100,
  "following_count": 50,
  "articles_count": 25,
  "is_following": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 更新用户资料

```bash
PATCH /api/v1/users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "John Smith",
  "bio": "Full-stack developer",
  "website": "https://johnsmith.com"
}
```

响应：200 OK

#### 获取用户的文章

```bash
GET /api/v1/users/{user_id}/articles?page=1&page_size=10&status=published
```

查询参数：
- `page`: 页码
- `page_size`: 每页数量
- `status`: 文章状态（published, draft）

响应：200 OK（格式与文章列表相同）

### 文章端点

#### 获取文章列表

```bash
GET /api/v1/articles?page=1&page_size=10&tag_id=5&category_id=3&author_id=1&status=published&sort=created_at&order=desc&search=ai
```

查询参数：
- `page`: 页码（默认：1）
- `page_size`: 每页数量（默认：10，最大：100）
- `tag_id`: 按标签筛选
- `category_id`: 按分类筛选
- `author_id`: 按作者筛选
- `status`: 文章状态（published, draft）
- `sort`: 排序字段（created_at, updated_at, views, likes）
- `order`: 排序方向（asc, desc）
- `search`: 搜索关键词

响应：200 OK

```json
{
  "items": [
    {
      "id": 1,
      "title": "Introduction to Machine Learning",
      "slug": "introduction-to-machine-learning",
      "summary": "Learn the basics of ML...",
      "cover_image": "https://example.com/image.jpg",
      "author": {
        "id": 1,
        "username": "johndoe",
        "avatar_url": "https://example.com/avatar.jpg"
      },
      "category": {
        "id": 3,
        "name": "Machine Learning"
      },
      "tags": [
        { "id": 5, "name": "AI" },
        { "id": 6, "name": "Python" }
      ],
      "status": "published",
      "views_count": 1500,
      "likes_count": 45,
      "comments_count": 12,
      "is_liked": false,
      "is_bookmarked": false,
      "reading_time": 8,
      "created_at": "2024-01-08T10:00:00Z",
      "updated_at": "2024-01-08T10:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

#### 获取文章详情

```bash
GET /api/v1/articles/{article_id}
Authorization: Bearer <token>  // 可选，未登录也可以访问
```

响应：200 OK

```json
{
  "id": 1,
  "title": "Introduction to Machine Learning",
  "slug": "introduction-to-machine-learning",
  "content": "# Introduction\n\nMachine learning is...",
  "summary": "Learn the basics of ML...",
  "cover_image": "https://example.com/image.jpg",
  "author": {
    "id": 1,
    "username": "johndoe",
    "full_name": "John Doe",
    "avatar_url": "https://example.com/avatar.jpg",
    "bio": "Software developer"
  },
  "category": {
    "id": 3,
    "name": "Machine Learning",
    "slug": "machine-learning"
  },
  "tags": [
    { "id": 5, "name": "AI", "slug": "ai" },
    { "id": 6, "name": "Python", "slug": "python" }
  ],
  "status": "published",
  "views_count": 1500,
  "likes_count": 45,
  "comments_count": 12,
  "is_liked": false,
  "is_bookmarked": false,
  "reading_time": 8,
  "created_at": "2024-01-08T10:00:00Z",
  "updated_at": "2024-01-08T10:00:00Z"
}
```

#### 通过 Slug 获取文章

```bash
GET /api/v1/articles/slug/{slug}
```

响应：200 OK（与获取文章详情相同）

#### 创建文章

```bash
POST /api/v1/articles
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My New Article",
  "content": "Article content in Markdown...",
  "summary": "Brief summary",
  "cover_image": "https://example.com/image.jpg",
  "category_id": 3,
  "tag_ids": [5, 6],
  "status": "draft"
}
```

响应：201 Created

```json
{
  "id": 124,
  "title": "My New Article",
  "slug": "my-new-article",
  "status": "draft",
  "created_at": "2024-01-08T12:00:00Z"
}
```

#### 更新文章

```bash
PUT /api/v1/articles/{article_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content...",
  "status": "published"
}
```

响应：200 OK

#### 删除文章

```bash
DELETE /api/v1/articles/{article_id}
Authorization: Bearer <token>
```

响应：204 No Content

#### 增加浏览量

```bash
POST /api/v1/articles/{article_id}/view
```

响应：200 OK

```json
{
  "views_count": 1501
}
```

### 分类端点

#### 获取分类列表

```bash
GET /api/v1/categories
```

响应：200 OK

```json
{
  "items": [
    {
      "id": 1,
      "name": "Artificial Intelligence",
      "slug": "artificial-intelligence",
      "description": "AI related articles",
      "articles_count": 45,
      "icon": "🤖"
    },
    {
      "id": 2,
      "name": "Web Development",
      "slug": "web-development",
      "description": "Web development tutorials",
      "articles_count": 120,
      "icon": "💻"
    }
  ],
  "total": 2
}
```

#### 获取分类详情

```bash
GET /api/v1/categories/{category_id}
```

响应：200 OK

```json
{
  "id": 1,
  "name": "Artificial Intelligence",
  "slug": "artificial-intelligence",
  "description": "AI related articles",
  "articles_count": 45,
  "icon": "🤖",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 标签端点

#### 获取标签列表

```bash
GET /api/v1/tags?page=1&page_size=50&sort=articles_count&order=desc
```

查询参数：
- `page`: 页码
- `page_size`: 每页数量
- `sort`: 排序字段（name, articles_count, created_at）
- `order`: 排序方向

响应：200 OK

```json
{
  "items": [
    {
      "id": 1,
      "name": "Python",
      "slug": "python",
      "articles_count": 150,
      "color": "#3776AB"
    },
    {
      "id": 2,
      "name": "Machine Learning",
      "slug": "machine-learning",
      "articles_count": 85,
      "color": "#FF6F00"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 50,
  "total_pages": 1
}
```

#### 搜索标签

```bash
GET /api/v1/tags/search?q=machine
```

查询参数：
- `q`: 搜索关键词

响应：200 OK

```json
{
  "items": [
    {
      "id": 2,
      "name": "Machine Learning",
      "slug": "machine-learning",
      "articles_count": 85
    }
  ]
}
```

### 评论端点

#### 获取文章评论

```bash
GET /api/v1/articles/{article_id}/comments?page=1&page_size=20
```

响应：200 OK

```json
{
  "items": [
    {
      "id": 1,
      "content": "Great article!",
      "author": {
        "id": 2,
        "username": "janedoe",
        "avatar_url": "https://example.com/avatar2.jpg"
      },
      "parent_id": null,
      "replies_count": 2,
      "likes_count": 5,
      "is_liked": false,
      "created_at": "2024-01-08T11:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

#### 创建评论

```bash
POST /api/v1/articles/{article_id}/comments
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Great article!",
  "parent_id": null  // 如果是回复评论，填写父评论 ID
}
```

响应：201 Created

#### 更新评论

```bash
PUT /api/v1/comments/{comment_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "Updated comment"
}
```

响应：200 OK

#### 删除评论

```bash
DELETE /api/v1/comments/{comment_id}
Authorization: Bearer <token>
```

响应：204 No Content

### 点赞端点

#### 点赞文章

```bash
POST /api/v1/articles/{article_id}/like
Authorization: Bearer <token>
```

响应：201 Created

```json
{
  "id": 123,
  "article_id": 1,
  "user_id": 2,
  "created_at": "2024-01-08T12:00:00Z"
}
```

#### 取消点赞

```bash
DELETE /api/v1/articles/{article_id}/like
Authorization: Bearer <token>
```

响应：204 No Content

### 收藏端点

#### 获取收藏列表

```bash
GET /api/v1/bookmarks?page=1&page_size=20
Authorization: Bearer <token>
```

响应：200 OK

```json
{
  "items": [
    {
      "id": 1,
      "article": {
        "id": 1,
        "title": "Article Title",
        "slug": "article-slug",
        "summary": "Article summary...",
        "author": { "username": "johndoe" }
      },
      "created_at": "2024-01-08T10:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 20,
  "total_pages": 2
}
```

#### 收藏文章

```bash
POST /api/v1/articles/{article_id}/bookmark
Authorization: Bearer <token>
```

响应：201 Created

#### 取消收藏

```bash
DELETE /api/v1/articles/{article_id}/bookmark
Authorization: Bearer <token>
```

响应：204 No Content

### 关注端点

#### 关注用户

```bash
POST /api/v1/users/{user_id}/follow
Authorization: Bearer <token>
```

响应：201 Created

```json
{
  "id": 1,
  "follower_id": 2,
  "following_id": 1,
  "created_at": "2024-01-08T10:00:00Z"
}
```

#### 取消关注

```bash
DELETE /api/v1/users/{user_id}/follow
Authorization: Bearer <token>
```

响应：204 No Content

#### 获取关注列表

```bash
GET /api/v1/users/{user_id}/followers?page=1&page_size=20
GET /api/v1/users/{user_id}/following?page=1&page_size=20
```

响应：200 OK

### 文件上传端点

#### 上传图片

```bash
POST /api/v1/upload/image
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary>
```

响应：200 OK

```json
{
  "url": "https://example.com/uploads/images/image_123.jpg",
  "filename": "image_123.jpg",
  "size": 102400
}
```

## 数据模型

### User（用户）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 用户 ID |
| email | string | 邮箱（唯一） |
| username | string | 用户名（唯一） |
| full_name | string | 全名 |
| bio | string | 个人简介 |
| avatar_url | string | 头像 URL |
| website | string | 个人网站 |
| twitter_handle | string | Twitter 账号 |
| github_handle | string | GitHub 账号 |
| is_active | boolean | 是否激活 |
| is_superuser | boolean | 是否管理员 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### Article（文章）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 文章 ID |
| title | string | 标题 |
| slug | string | URL 友好的唯一标识 |
| content | string | Markdown 内容 |
| summary | string | 摘要 |
| cover_image | string | 封面图片 URL |
| author_id | integer | 作者 ID |
| category_id | integer | 分类 ID |
| status | string | 状态（draft, published） |
| views_count | integer | 浏览量 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### Comment（评论）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 评论 ID |
| content | string | 评论内容 |
| article_id | integer | 文章 ID |
| author_id | integer | 评论者 ID |
| parent_id | integer | 父评论 ID（null 表示顶层评论） |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### Category（分类）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 分类 ID |
| name | string | 分类名称 |
| slug | string | URL 标识 |
| description | string | 描述 |
| icon | string | 图标（emoji） |
| created_at | datetime | 创建时间 |

### Tag（标签）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 标签 ID |
| name | string | 标签名称 |
| slug | string | URL 标识 |
| color | string | 颜色代码（hex） |

## 速率限制

为了防止滥用，API 实施了速率限制。

### 默认限制

| 端点类型 | 限制 |
|----------|------|
| 认证端点 | 5 请求/分钟/IP |
| 公开端点 | 60 请求/分钟/IP |
| 认证端点 | 120 请求/分钟/用户 |

### 速率限制响应头

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1641672000
```

### 超出限制响应

```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 60
}
```

## 分页

所有列表端点都支持分页。

### 查询参数

- `page`: 页码（从 1 开始）
- `page_size`: 每页数量（默认：20，最大：100）

### 响应格式

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

## 排序和筛选

### 排序

```bash
GET /api/v1/articles?sort=created_at&order=desc
```

参数：
- `sort`: 排序字段
- `order`: 排序方向（asc, desc）

### 筛选

```bash
GET /api/v1/articles?category_id=3&tag_id=5&status=published
```

### 搜索

```bash
GET /api/v1/articles?search=machine+learning
GET /api/v1/tags/search?q=python
```

## WebSocket（计划中）

实时通知功能将使用 WebSocket。

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  // 发送认证消息
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your-jwt-token'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('New notification:', message);
};
```

## SDK 和客户端库

### Python

```python
from ai_muse_client import AIMuseClient

client = AIMuseClient(api_key="your-api-key")
articles = client.articles.list(page=1, page_size=10)
```

### JavaScript/TypeScript

```typescript
import { AIMuseClient } from '@ai-muse/sdk';

const client = new AIMuseClient({
  baseURL: 'http://localhost:8000/api/v1',
  token: 'your-jwt-token'
});

const articles = await client.articles.list();
```

## 常见问题

### Q: 如何处理大文件上传？

使用分块上传：

```bash
POST /api/v1/upload/chunk
Content-Type: multipart/form-data

chunk: <binary>
chunk_index: 0
total_chunks: 10
upload_id: unique-upload-id
```

### Q: 如何实现批量操作？

批量创建标签：

```bash
POST /api/v1/tags/batch
Authorization: Bearer <token>
Content-Type: application/json

{
  "tags": [
    { "name": "Tag 1" },
    { "name": "Tag 2" }
  ]
}
```

## 变更日志

查看 [CHANGELOG.md](../CHANGELOG.md) 了解 API 变更历史。

## 支持

如有问题，请：
- 查看 Swagger 文档：http://localhost:8000/docs
- 提交 GitHub Issue
- 发送邮件至 api-support@example.com

---

**最后更新**: 2024-01-08
**API 版本**: v1.0.0
