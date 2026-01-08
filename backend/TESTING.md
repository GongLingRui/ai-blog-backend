# Testing Guide - AI Muse Blog Backend

本文档提供 AI Muse Blog 后端的全面测试指南，包括单元测试、集成测试、端到端测试和性能测试。

## 目录

- [测试概述](#测试概述)
- [测试环境设置](#测试环境设置)
- [单元测试](#单元测试)
- [集成测试](#集成测试)
- [API 测试](#api-测试)
- [性能测试](#性能测试)
- [测试覆盖率](#测试覆盖率)
- [CI/CD 集成](#cicd-集成)
- [测试最佳实践](#测试最佳实践)

## 测试概述

### 测试策略

```mermaid
graph TB
    A[测试金字塔] --> B[端到端测试<br/>少量]
    A --> C[集成测试<br/>中等]
    A --> D[单元测试<br/>大量]

    D --> E[CRUD 函数]
    D --> F[工具函数]
    D --> G[Schema 验证]

    C --> H[API 端点]
    C --> I[数据库操作]
    C --> J[认证流程]

    B --> K[完整用户流程]
    B --> L[多服务交互]
```

### 测试技术栈

- **测试框架**: pytest 7.4+
- **异步支持**: pytest-asyncio 0.21+
- **HTTP 测试**: httpx 0.25+
- **覆盖率**: pytest-cov 4.1+
- **Mock**: pytest-mock
- **数据库**: pytest-fixture

## 测试环境设置

### 1. 安装测试依赖

```bash
cd backend
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx
```

### 2. 配置 pytest

创建 `pytest.ini`：

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    auth: Authentication tests
    api: API endpoint tests
```

### 3. 创建测试配置

创建 `tests/conftest.py`：

```python
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models.user import User

# 测试数据库 URL
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/test_ai_muse_blog"

# 创建测试引擎
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """创建测试数据库会话"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 删除所有表
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def async_client(db: Session) -> AsyncGenerator[AsyncClient, None]:
    """创建异步测试客户端"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db: Session) -> User:
    """创建测试用户"""
    from app.crud.user import create_user
    from app.schemas.user import UserCreate

    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="TestPass123!",
        full_name="Test User"
    )
    return create_user(db, user_in)

@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """创建认证头"""
    access_token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_user(db: Session) -> User:
    """创建管理员用户"""
    from app.crud.user import create_user
    from app.schemas.user import UserCreate
    from app.core.security import get_password_hash

    user_in = UserCreate(
        email="admin@example.com",
        username="admin",
        password="AdminPass123!",
        full_name="Admin User"
    )
    user = create_user(db, user_in)
    user.is_superuser = True
    db.commit()
    return user

@pytest.fixture
def admin_headers(admin_user: User) -> dict:
    """创建管理员认证头"""
    access_token = create_access_token(data={"sub": admin_user.email})
    return {"Authorization": f"Bearer {access_token}"}
```

### 4. 创建测试数据库

```bash
# 创建测试数据库
psql -U postgres -c "CREATE DATABASE test_ai_muse_blog;"
psql -U postgres -c "CREATE USER test_user WITH PASSWORD 'test_pass';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE test_ai_muse_blog TO test_user;"
```

## 单元测试

### CRUD 函数测试

```python
# tests/test_crud/test_user_crud.py
import pytest
from sqlalchemy.orm import Session

from app.crud.user import create_user, get_user, get_user_by_email, update_user
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User

def test_create_user(db: Session) -> None:
    """测试创建用户"""
    email = "test@example.com"
    username = "testuser"
    password = "TestPass123!"

    user_in = UserCreate(
        email=email,
        username=username,
        password=password,
        full_name="Test User"
    )
    user = create_user(db, user_in)

    assert user.email == email
    assert user.username == username
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.is_superuser is False
    assert hasattr(user, "hashed_password")

def test_get_user(db: Session, test_user: User) -> None:
    """测试获取用户"""
    user = get_user(db, test_user.id)
    assert user.email == test_user.email
    assert user.username == test_user.username

def test_get_user_by_email(db: Session, test_user: User) -> None:
    """测试通过邮箱获取用户"""
    user = get_user_by_email(db, test_user.email)
    assert user is not None
    assert user.id == test_user.id

def test_update_user(db: Session, test_user: User) -> None:
    """测试更新用户"""
    new_full_name = "Updated Name"
    user_update = UserUpdate(full_name=new_full_name)

    updated_user = update_user(db, test_user, user_update)
    assert updated_user.full_name == new_full_name
```

### 工具函数测试

```python
# tests/test_utils/test_security.py
import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)

def test_password_hashing() -> None:
    """测试密码哈希"""
    password = "TestPass123!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpass", hashed) is False

def test_access_token_creation() -> None:
    """测试创建 access token"""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

def test_access_token_decode() -> None:
    """测试解码 access token"""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)

    decoded = decode_access_token(token)
    assert decoded["sub"] == data["sub"]
    assert "exp" in decoded
```

### Schema 验证测试

```python
# tests/test_schemas/test_article_schemas.py
import pytest
from pydantic import ValidationError
from app.schemas.article import ArticleCreate, ArticleUpdate

def test_article_create_valid() -> None:
    """测试有效的文章创建 schema"""
    article_data = {
        "title": "Test Article",
        "content": "This is a test article content.",
        "summary": "Test summary",
        "category_id": 1,
        "tag_ids": [1, 2],
        "status": "draft"
    }

    article = ArticleCreate(**article_data)
    assert article.title == "Test Article"
    assert article.status == "draft"

def test_article_create_invalid() -> None:
    """测试无效的文章创建 schema"""
    # 标题太短
    with pytest.raises(ValidationError):
        ArticleCreate(
            title="",
            content="Content",
            category_id=1
        )

    # 无效的状态
    with pytest.raises(ValidationError):
        ArticleCreate(
            title="Test",
            content="Content",
            category_id=1,
            status="invalid_status"
        )

def test_article_update_partial() -> None:
    """测试部分更新"""
    update_data = ArticleUpdate(title="Updated Title")

    assert update_data.title == "Updated Title"
    assert update_data.content is None
    assert update_data.category_id is None
```

## 集成测试

### 数据库集成测试

```python
# tests/integration/test_database.py
import pytest
from sqlalchemy.orm import Session

from app.models.article import Article
from app.models.user import User
from app.crud.article import create_article, get_article, get_articles

def test_create_and_retrieve_article(db: Session, test_user: User) -> None:
    """测试创建和检索文章"""
    from app.schemas.article import ArticleCreate

    article_in = ArticleCreate(
        title="Integration Test Article",
        content="Content for integration test",
        summary="Test summary",
        category_id=1
    )

    article = create_article(db, article_in, author_id=test_user.id)

    retrieved = get_article(db, article.id)

    assert retrieved.id == article.id
    assert retrieved.title == article_in.title
    assert retrieved.author_id == test_user.id

def test_article_pagination(db: Session, test_user: User) -> None:
    """测试文章分页"""
    from app.schemas.article import ArticleCreate

    # 创建多篇文章
    for i in range(15):
        article_in = ArticleCreate(
            title=f"Article {i}",
            content=f"Content {i}",
            summary=f"Summary {i}",
            category_id=1
        )
        create_article(db, article_in, author_id=test_user.id)

    # 测试分页
    page1 = get_articles(db, skip=0, limit=10)
    page2 = get_articles(db, skip=10, limit=10)

    assert len(page1) == 10
    assert len(page2) == 5
```

### 认证集成测试

```python
# tests/integration/test_auth.py
import pytest
from fastapi.testclient import TestClient

def test_register_and_login(client: TestClient) -> None:
    """测试注册和登录流程"""
    # 注册
    register_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "NewPass123!",
        "full_name": "New User"
    }

    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == register_data["email"]
    assert "id" in data
    assert "hashed_password" not in data

    # 登录
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_protected_endpoint(client: TestClient, auth_headers: dict) -> None:
    """测试受保护的端点"""
    # 无认证
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

    # 有认证
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
```

## API 测试

### 文章 API 测试

```python
# tests/api/test_articles.py
import pytest
from fastapi.testclient import TestClient

def test_list_articles(client: TestClient) -> None:
    """测试获取文章列表"""
    response = client.get("/api/v1/articles")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert isinstance(data["items"], list)

def test_create_article(client: TestClient, auth_headers: dict) -> None:
    """测试创建文章"""
    article_data = {
        "title": "Test Article",
        "content": "This is test content",
        "summary": "Test summary",
        "category_id": 1,
        "status": "draft"
    }

    response = client.post(
        "/api/v1/articles",
        json=article_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == article_data["title"]
    assert "id" in data
    assert data["author"]["email"] == "test@example.com"

def test_get_article_by_slug(client: TestClient, db: Session) -> None:
    """测试通过 slug 获取文章"""
    # 假设数据库中有一篇 slug 为 "test-article" 的文章
    response = client.get("/api/v1/articles/slug/test-article")

    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "test-article"
    assert "content" in data

def test_update_article(client: TestClient, auth_headers: dict, db: Session) -> None:
    """测试更新文章"""
    # 先创建文章
    create_data = {
        "title": "Original Title",
        "content": "Original content",
        "category_id": 1
    }
    create_response = client.post("/api/v1/articles", json=create_data, headers=auth_headers)
    article_id = create_response.json()["id"]

    # 更新文章
    update_data = {
        "title": "Updated Title",
        "content": "Updated content"
    }
    response = client.put(
        f"/api/v1/articles/{article_id}",
        json=update_data,
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]

def test_delete_article(client: TestClient, auth_headers: dict) -> None:
    """测试删除文章"""
    # 创建文章
    create_data = {
        "title": "To Delete",
        "content": "Content",
        "category_id": 1
    }
    create_response = client.post("/api/v1/articles", json=create_data, headers=auth_headers)
    article_id = create_response.json()["id"]

    # 删除文章
    response = client.delete(f"/api/v1/articles/{article_id}", headers=auth_headers)
    assert response.status_code == 204

    # 验证已删除
    get_response = client.get(f"/api/v1/articles/{article_id}")
    assert get_response.status_code == 404

def test_article_pagination(client: TestClient) -> None:
    """测试文章分页"""
    response = client.get("/api/v1/articles?page=1&page_size=5")

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["items"]) <= 5

def test_article_filters(client: TestClient) -> None:
    """测试文章筛选"""
    # 按标签筛选
    response = client.get("/api/v1/articles?tag_id=1")
    assert response.status_code == 200

    # 按分类筛选
    response = client.get("/api/v1/articles?category_id=1")
    assert response.status_code == 200

    # 按状态筛选
    response = client.get("/api/v1/articles?status=published")
    assert response.status_code == 200

    # 搜索
    response = client.get("/api/v1/articles?search=test")
    assert response.status_code == 200

def test_unauthorized_article_operations(client: TestClient) -> None:
    """测试未授权的文章操作"""
    # 无认证创建文章
    response = client.post("/api/v1/articles", json={
        "title": "Test",
        "content": "Content",
        "category_id": 1
    })
    assert response.status_code == 401

    # 无认证更新文章
    response = client.put("/api/v1/articles/1", json={"title": "Updated"})
    assert response.status_code == 401

    # 无认证删除文章
    response = client.delete("/api/v1/articles/1")
    assert response.status_code == 401
```

### 点赞和收藏测试

```python
# tests/api/test_interactions.py
def test_like_article(client: TestClient, auth_headers: dict) -> None:
    """测试点赞文章"""
    # 点赞
    response = client.post("/api/v1/articles/1/like", headers=auth_headers)
    assert response.status_code == 201
    assert "id" in response.json()

    # 取消点赞
    response = client.delete("/api/v1/articles/1/like", headers=auth_headers)
    assert response.status_code == 204

def test_bookmark_article(client: TestClient, auth_headers: dict) -> None:
    """测试收藏文章"""
    # 收藏
    response = client.post("/api/v1/articles/1/bookmark", headers=auth_headers)
    assert response.status_code == 201

    # 获取收藏列表
    response = client.get("/api/v1/bookmarks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0

    # 取消收藏
    response = client.delete("/api/v1/articles/1/bookmark", headers=auth_headers)
    assert response.status_code == 204

def test_follow_user(client: TestClient, auth_headers: dict) -> None:
    """测试关注用户"""
    # 关注用户
    response = client.post("/api/v1/users/2/follow", headers=auth_headers)
    assert response.status_code == 201

    # 获取关注列表
    response = client.get("/api/v1/users/1/following", headers=auth_headers)
    assert response.status_code == 200

    # 取消关注
    response = client.delete("/api/v1/users/2/follow", headers=auth_headers)
    assert response.status_code == 204
```

## 性能测试

### 负载测试

```python
# tests/performance/test_load.py
import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

def test_concurrent_article_reads(client: TestClient) -> None:
    """测试并发读取文章"""
    def read_article():
        response = client.get("/api/v1/articles")
        return response.status_code == 200

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(read_article) for _ in range(100)]
        results = [f.result() for f in futures]

    end_time = time.time()
    elapsed = end_time - start_time

    assert all(results)
    assert elapsed < 5  # 100 个请求在 5 秒内完成
    print(f"Completed 100 requests in {elapsed:.2f} seconds")

def test_article_query_performance(client: TestClient, db: Session) -> None:
    """测试文章查询性能"""
    # 创建大量文章
    from app.schemas.article import ArticleCreate
    from app.crud.article import create_article

    for i in range(1000):
        article_in = ArticleCreate(
            title=f"Article {i}",
            content=f"Content {i}",
            summary=f"Summary {i}",
            category_id=1
        )
        create_article(db, article_in, author_id=1)

    # 测试查询性能
    start_time = time.time()
    response = client.get("/api/v1/articles?page=1&page_size=20")
    end_time = time.time()

    assert response.status_code == 200
    assert end_time - start_time < 1  # 查询应在 1 秒内完成

@pytest.mark.slow
def test_database_connection_pool() -> None:
    """测试数据库连接池"""
    from app.core.database import engine

    # 测试多个并发连接
    connections = []
    for _ in range(20):
        conn = engine.connect()
        connections.append(conn)

    # 验证所有连接都可用
    for conn in connections:
        result = conn.execute("SELECT 1")
        assert result.scalar() == 1
        conn.close()
```

### 查询性能测试

```python
# tests/performance/test_queries.py
import pytest
import time
from sqlalchemy.orm import Session

def test_query_with_indexes(db: Session) -> None:
    """测试带索引的查询性能"""
    # 测试按 slug 查询（有索引）
    start = time.time()
    db.query(Article).filter(Article.slug == "test-article").first()
    index_time = time.time() - start

    # 测试按内容查询（无索引）
    start = time.time()
    db.query(Article).filter(Article.content.contains("test")).first()
    no_index_time = time.time() - start

    # 有索引应该快得多
    assert index_time < no_index_time
    print(f"Index: {index_time:.4f}s, No Index: {no_index_time:.4f}s")

def test_n_plus_1_query(db: Session) -> None:
    """测试并修复 N+1 查询"""
    from sqlalchemy.orm import joinedload

    # N+1 查询（不好）
    start = time.time()
    articles = db.query(Article).limit(10).all()
    for article in articles:
        _ = article.author  # 触发额外查询
    n_plus_1_time = time.time() - start

    # Eager loading（好）
    start = time.time()
    articles = db.query(Article)\
        .options(joinedload(Article.author))\
        .limit(10).all()
    for article in articles:
        _ = article.author
    eager_time = time.time() - start

    assert eager_time < n_plus_1_time
    print(f"N+1: {n_plus_1_time:.4f}s, Eager: {eager_time:.4f}s")
```

## 测试覆盖率

### 生成覆盖率报告

```bash
# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html --cov-report=term-missing

# 查看报告
open htmlcov/index.html
```

### 覆盖率目标

| 模块 | 目标覆盖率 |
|------|-----------|
| CRUD 函数 | 95%+ |
| API 路由 | 90%+ |
| 工具函数 | 95%+ |
| Schema | 80%+ |
| 整体 | 85%+ |

### 排除不需要测试的代码

```python
# .coveragerc
[run]
omit =
    */tests/*
    */venv/*
    */__init__.py
    */config.py
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## CI/CD 集成

### GitHub Actions 工作流

创建 `.github/workflows/test.yml`：

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_ai_muse_blog
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run migrations
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_ai_muse_blog
      run: |
        alembic upgrade head

    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_ai_muse_blog
        REDIS_URL: redis://localhost:6379/0
        SECRET_KEY: test-secret-key
      run: |
        pytest --cov=app --cov-report=xml --cov-report=term-missing

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## 测试最佳实践

### 1. 测试命名

```python
# 好的命名
def test_create_article_with_valid_data_succeeds():
    pass

def test_create_article_with_duplicate_title_fails():
    pass

# 不好的命名
def test_article():
    pass
```

### 2. 测试隔离

```python
# 每个测试应该独立
def test_create_article(db: Session):
    # 创建新数据
    article = Article(title="Test")
    db.add(article)
    db.commit()

    # 测试
    assert article.id is not None

def test_delete_article(db: Session):
    # 不依赖上面的测试
    article = Article(title="Test2")
    db.add(article)
    db.commit()

    db.delete(article)
    db.commit()

    assert db.query(Article).filter_by(id=article.id).first() is None
```

### 3. 使用 Fixture

```python
# 使用 fixture 减少重复
@pytest.fixture
def sample_article(db: Session):
    article = Article(title="Sample", content="Content")
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def test_get_article(db: Session, sample_article: Article):
    result = get_article(db, sample_article.id)
    assert result.id == sample_article.id

def test_update_article(db: Session, sample_article: Article):
    updated = update_article(db, sample_article, {"title": "Updated"})
    assert updated.title == "Updated"
```

### 4. Mock 外部依赖

```python
from unittest.mock import Mock, patch

def test_send_notification():
    # Mock 外部服务
    with patch('app.services.email.send_email') as mock_email:
        mock_email.return_value = True

        send_notification(user_id=1, message="Test")

        # 验证调用
        mock_email.assert_called_once()
```

### 5. 测试边界情况

```python
def test_article_validation():
    # 空标题
    with pytest.raises(ValidationError):
        ArticleCreate(title="", content="Content")

    # 标题过长
    with pytest.raises(ValidationError):
        ArticleCreate(title="a" * 201, content="Content")

    # 无效状态
    with pytest.raises(ValidationError):
        ArticleCreate(title="Test", content="Content", status="invalid")

    # 正常情况
    article = ArticleCreate(title="Test", content="Content")
    assert article.title == "Test"
```

### 6. 异步测试

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

### 7. 参数化测试

```python
@pytest.mark.parametrize("status,expected", [
    ("draft", False),
    ("published", True),
])
def test_article_visibility(status: str, expected: bool):
    article = Article(status=status)
    assert article.is_visible() == expected
```

## 常见问题

### Q: 如何测试异步端点？

```python
@pytest.mark.asyncio
async def test_async_endpoint(async_client: AsyncClient):
    response = await async_client.post("/api/v1/articles", json={...})
    assert response.status_code == 201
```

### Q: 如何测试文件上传？

```python
def test_file_upload(client: TestClient, auth_headers: dict):
    file_content = b"fake image content"
    files = {"file": ("test.jpg", file_content, "image/jpeg")}

    response = client.post("/api/v1/upload/image", files=files, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "url" in data
```

### Q: 如何测试认证？

```python
def test_authentication_required(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_with_valid_token(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
```

## 资源

- [Pytest 文档](https://docs.pytest.org/)
- [FastAPI 测试文档](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy 测试](https://docs.sqlalchemy.org/en/20/orm/persistence_techniques.html#unit-of-work-pattern-transaction-semantics)

---

**最后更新**: 2024-01-08
**测试框架**: pytest 7.4+
