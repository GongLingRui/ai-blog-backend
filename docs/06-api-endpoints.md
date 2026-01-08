# API Endpoints Reference - AI Muse Blog

本文档提供 AI Muse Blog 所有 API 端点的完整参考，包括请求格式、响应格式、示例代码和错误处理。

## 目录

- [API 概述](#api-概述)
- [认证端点](#认证端点)
- [用户端点](#用户端点)
- [文章端点](#文章端点)
- [分类和标签端点](#分类和标签端点)
- [评论端点](#评论端点)
- [互动端点](#互动端点)
- [文件上传端点](#文件上传端点)
- [状态码](#状态码)
- [错误格式](#错误格式)

## API 概述

### 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证**: Bearer Token (JWT)

### 通用请求头

```http
Content-Type: application/json
Authorization: Bearer <access_token>
Accept: application/json
```

### 通用响应头

```http
Content-Type: application/json; charset=utf-8
X-Request-ID: <uuid>
```

## 认证端点

### POST /auth/register

注册新用户。

**请求**:

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**响应** - 201 Created:

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

**错误响应**:

- 400: 邮箱已存在
- 422: 验证失败（密码太弱、邮箱格式错误等）

### POST /auth/login

用户登录。

**请求**:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**响应** - 200 OK:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### POST /auth/refresh

刷新 access token。

**请求**:

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应** - 200 OK:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### GET /auth/me

获取当前用户信息。

**请求**:

```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**响应** - 200 OK:

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

### PUT /auth/change-password

修改密码。

**请求**:

```http
PUT /api/v1/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "OldPass123!",
  "new_password": "NewPass456!"
}
```

**响应** - 200 OK:

```json
{
  "message": "Password changed successfully"
}
```

## 用户端点

### GET /users

获取用户列表。

**查询参数**:

- `page` (integer, 默认: 1): 页码
- `page_size` (integer, 默认: 20, 最大: 100): 每页数量
- `search` (string): 搜索关键词

**请求**:

```http
GET /api/v1/users?page=1&page_size=20&search=john
```

**响应** - 200 OK:

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

### GET /users/{id}

获取用户详情。

**请求**:

```http
GET /api/v1/users/1
```

**响应** - 200 OK:

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

### PATCH /users/{id}

更新用户资料。

**请求**:

```http
PATCH /api/v1/users/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "John Smith",
  "bio": "Full-stack developer",
  "website": "https://johnsmith.com"
}
```

**响应** - 200 OK:

```json
{
  "id": 1,
  "username": "johndoe",
  "full_name": "John Smith",
  "bio": "Full-stack developer",
  "website": "https://johnsmith.com",
  "updated_at": "2024-01-08T11:00:00Z"
}
```

### GET /users/{id}/articles

获取用户的文章。

**查询参数**:

- `page` (integer, 默认: 1)
- `page_size` (integer, 默认: 10)
- `status` (string): 'draft' | 'published'

**请求**:

```http
GET /api/v1/users/1/articles?page=1&page_size=10&status=published
```

**响应** - 200 OK:

```json
{
  "items": [...],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3
}
```

### POST /users/{id}/follow

关注用户。

**请求**:

```http
POST /api/v1/users/2/follow
Authorization: Bearer <access_token>
```

**响应** - 201 Created:

```json
{
  "id": 1,
  "follower_id": 1,
  "following_id": 2,
  "created_at": "2024-01-08T10:00:00Z"
}
```

### DELETE /users/{id}/follow

取消关注用户。

**请求**:

```http
DELETE /api/v1/users/2/follow
Authorization: Bearer <access_token>
```

**响应** - 204 No Content

### GET /users/{id}/followers

获取用户的粉丝列表。

**请求**:

```http
GET /api/v1/users/1/followers?page=1&page_size=20
```

**响应** - 200 OK:

```json
{
  "items": [
    {
      "id": 2,
      "username": "janedoe",
      "full_name": "Jane Doe",
      "avatar_url": "https://example.com/avatar2.jpg"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### GET /users/{id}/following

获取用户关注的人列表。

**请求**:

```http
GET /api/v1/users/1/following?page=1&page_size=20
```

**响应** - 200 OK: (格式同上)

## 文章端点

### GET /articles

获取文章列表。

**查询参数**:

- `page` (integer, 默认: 1)
- `page_size` (integer, 默认: 10, 最大: 100)
- `tag_id` (integer): 按标签筛选
- `category_id` (integer): 按分类筛选
- `author_id` (integer): 按作者筛选
- `status` (string): 'draft' | 'published'
- `sort` (string): 'created_at' | 'updated_at' | 'views' | 'likes'
- `order` (string): 'asc' | 'desc'
- `search` (string): 搜索关键词

**请求**:

```http
GET /api/v1/articles?page=1&page_size=10&tag_id=5&category_id=3&status=published&sort=created_at&order=desc
```

**响应** - 200 OK:

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

### GET /articles/{id}

获取文章详情。

**请求**:

```http
GET /api/v1/articles/1
```

**响应** - 200 OK:

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

### GET /articles/slug/{slug}

通过 slug 获取文章。

**请求**:

```http
GET /api/v1/articles/slug/introduction-to-machine-learning
```

**响应** - 200 OK: (同获取文章详情)

### POST /articles

创建文章。

**请求**:

```http
POST /api/v1/articles
Authorization: Bearer <access_token>
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

**响应** - 201 Created:

```json
{
  "id": 124,
  "title": "My New Article",
  "slug": "my-new-article",
  "status": "draft",
  "created_at": "2024-01-08T12:00:00Z"
}
```

### PUT /articles/{id}

更新文章。

**请求**:

```http
PUT /api/v1/articles/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content...",
  "status": "published"
}
```

**响应** - 200 OK:

```json
{
  "id": 1,
  "title": "Updated Title",
  "slug": "updated-title",
  "status": "published",
  "updated_at": "2024-01-08T11:00:00Z"
}
```

### DELETE /articles/{id}

删除文章。

**请求**:

```http
DELETE /api/v1/articles/1
Authorization: Bearer <access_token>
```

**响应** - 204 No Content

### POST /articles/{id}/view

增加文章浏览量。

**请求**:

```http
POST /api/v1/articles/1/view
```

**响应** - 200 OK:

```json
{
  "views_count": 1501
}
```

## 分类和标签端点

### GET /categories

获取分类列表。

**请求**:

```http
GET /api/v1/categories
```

**响应** - 200 OK:

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

### GET /categories/{id}

获取分类详情。

**请求**:

```http
GET /api/v1/categories/1
```

**响应** - 200 OK:

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

### GET /tags

获取标签列表。

**查询参数**:

- `page` (integer, 默认: 1)
- `page_size` (integer, 默认: 50)
- `sort` (string): 'name' | 'articles_count' | 'created_at'
- `order` (string): 'asc' | 'desc'

**请求**:

```http
GET /api/v1/tags?page=1&page_size=50&sort=articles_count&order=desc
```

**响应** - 200 OK:

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

### GET /tags/search

搜索标签。

**查询参数**:

- `q` (string): 搜索关键词

**请求**:

```http
GET /api/v1/tags/search?q=machine
```

**响应** - 200 OK:

```json
{
  "items": [
    {
      "id": 2,
      "name": "Machine Learning",
      "slug": "machine-learning",
      "articles_count": 85
    },
    {
      "id": 15,
      "name": "Deep Learning",
      "slug": "deep-learning",
      "articles_count": 42
    }
  ]
}
```

## 评论端点

### GET /articles/{article_id}/comments

获取文章评论。

**查询参数**:

- `page` (integer, 默认: 1)
- `page_size` (integer, 默认: 20)

**请求**:

```http
GET /api/v1/articles/1/comments?page=1&page_size=20
```

**响应** - 200 OK:

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

### POST /articles/{article_id}/comments

创建评论。

**请求**:

```http
POST /api/v1/articles/1/comments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Great article!",
  "parent_id": null
}
```

**响应** - 201 Created:

```json
{
  "id": 15,
  "content": "Great article!",
  "article_id": 1,
  "author_id": 2,
  "parent_id": null,
  "created_at": "2024-01-08T12:00:00Z"
}
```

### PUT /comments/{id}

更新评论。

**请求**:

```http
PUT /api/v1/comments/15
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Updated comment"
}
```

**响应** - 200 OK:

```json
{
  "id": 15,
  "content": "Updated comment",
  "updated_at": "2024-01-08T12:30:00Z"
}
```

### DELETE /comments/{id}

删除评论。

**请求**:

```http
DELETE /api/v1/comments/15
Authorization: Bearer <access_token>
```

**响应** - 204 No Content

## 互动端点

### POST /articles/{article_id}/like

点赞文章。

**请求**:

```http
POST /api/v1/articles/1/like
Authorization: Bearer <access_token>
```

**响应** - 201 Created:

```json
{
  "id": 123,
  "article_id": 1,
  "user_id": 2,
  "created_at": "2024-01-08T12:00:00Z"
}
```

### DELETE /articles/{article_id}/like

取消点赞文章。

**请求**:

```http
DELETE /api/v1/articles/1/like
Authorization: Bearer <access_token>
```

**响应** - 204 No Content

### GET /bookmarks

获取收藏列表。

**查询参数**:

- `page` (integer, 默认: 1)
- `page_size` (integer, 默认: 20)

**请求**:

```http
GET /api/v1/bookmarks?page=1&page_size=20
Authorization: Bearer <access_token>
```

**响应** - 200 OK:

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

### POST /articles/{article_id}/bookmark

收藏文章。

**请求**:

```http
POST /api/v1/articles/1/bookmark
Authorization: Bearer <access_token>
```

**响应** - 201 Created:

```json
{
  "id": 45,
  "article_id": 1,
  "user_id": 2,
  "created_at": "2024-01-08T12:00:00Z"
}
```

### DELETE /articles/{article_id}/bookmark

取消收藏文章。

**请求**:

```http
DELETE /api/v1/articles/1/bookmark
Authorization: Bearer <access_token>
```

**响应** - 204 No Content

## 文件上传端点

### POST /upload/image

上传图片。

**请求**:

```http
POST /api/v1/upload/image
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <binary>
```

**cURL 示例**:

```bash
curl -X POST \
  http://localhost:8000/api/v1/upload/image \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/image.jpg"
```

**响应** - 200 OK:

```json
{
  "url": "https://example.com/uploads/images/image_123.jpg",
  "filename": "image_123.jpg",
  "size": 102400,
  "content_type": "image/jpeg"
}
```

**限制**:
- 文件大小: 最大 10MB
- 支持格式: JPG, PNG, GIF, WEBP

## 状态码

| 状态码 | 说明 |
|--------|------|
| 200 OK | 请求成功 |
| 201 Created | 资源创建成功 |
| 204 No Content | 删除成功 |
| 400 Bad Request | 请求参数错误 |
| 401 Unauthorized | 未认证或 token 无效 |
| 403 Forbidden | 无权限 |
| 404 Not Found | 资源不存在 |
| 422 Unprocessable Entity | 验证失败 |
| 429 Too Many Requests | 超出速率限制 |
| 500 Internal Server Error | 服务器错误 |

## 错误格式

### 标准错误响应

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
    },
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### 速率限制错误

```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 60
}
```

## 示例代码

### JavaScript/TypeScript

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 登录
async function login(email: string, password: string) {
  const response = await api.post('/auth/login', { email, password });
  const { access_token } = response.data;

  // 设置默认 token
  api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

  return response.data;
}

// 获取文章列表
async function getArticles(page = 1, pageSize = 10) {
  const response = await api.get('/articles', {
    params: { page, page_size: pageSize },
  });
  return response.data;
}

// 创建文章
async function createArticle(article: ArticleCreate) {
  const response = await api.post('/articles', article);
  return response.data;
}
```

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 登录
def login(email: str, password: str):
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    return response.json()

# 获取文章列表
def get_articles(page: int = 1, page_size: int = 10, token: str = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(
        f"{BASE_URL}/articles",
        params={"page": page, "page_size": page_size},
        headers=headers
    )
    return response.json()

# 创建文章
def create_article(article: dict, token: str):
    response = requests.post(
        f"{BASE_URL}/articles",
        json=article,
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
```

### cURL

```bash
# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# 获取文章列表
curl http://localhost:8000/api/v1/articles?page=1&page_size=10

# 创建文章
curl -X POST http://localhost:8000/api/v1/articles \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"Content","category_id":1}'
```

## 速率限制

| 端点类型 | 限制 | 时间窗口 |
|----------|------|----------|
| 认证端点 | 5 请求 | 每分钟/IP |
| 公开端点 | 60 请求 | 每分钟/IP |
| 认证端点 | 120 请求 | 每分钟/用户 |

**响应头**:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1641672000
```

## 版本控制

当前 API 版本: **v1**

主要版本在 URL 中标识：`/api/v1/`

API 将遵循语义化版本控制。重大变更将通过主版本号递增来表示。

---

**最后更新**: 2024-01-08
**API 版本**: v1.0.0
