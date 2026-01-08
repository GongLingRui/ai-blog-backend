# Testing Guide - AI Muse Blog

本文档提供 AI Muse Blog 项目的全面测试指南，涵盖前端和后端的测试策略、工具和最佳实践。

## 目录

- [测试概述](#测试概述)
- [测试策略](#测试策略)
- [后端测试](#后端测试)
- [前端测试](#前端测试)
- [集成测试](#集成测试)
- [端到端测试](#端到端测试)
- [性能测试](#性能测试)
- [测试自动化](#测试自动化)

## 测试概述

### 测试金字塔

```mermaid
graph TB
    A[E2E Tests<br/>少量<br/>慢/脆弱]
    B[Integration Tests<br/>中等<br/>中等]
    C[Unit Tests<br/>大量<br/>快/可靠]

    A --> D[测试金字塔]
    B --> D
    C --> D

    E[70% 单元测试]
    F[20% 集成测试]
    G[10% E2E 测试]

    E --> H[理想比例]
    F --> H
    G --> H
```

### 测试目标

- **单元测试覆盖率**:
  - 后端: 85%+
  - 前端: 80%+

- **集成测试**: 覆盖关键业务流程
- **E2E 测试**: 覆盖主要用户场景
- **性能测试**: 确保响应时间和并发能力

## 测试策略

### 后端测试重点

1. **CRUD 操作**: 所有数据模型的创建、读取、更新、删除
2. **API 端点**: 请求验证、响应格式、错误处理
3. **业务逻辑**: 权限检查、数据验证、关联操作
4. **边界情况**: 空值、无效输入、极端情况

### 前端测试重点

1. **组件渲染**: 组件正确渲染和状态管理
2. **用户交互**: 点击、输入、表单提交
3. **数据获取**: API 调用、加载状态、错误处理
4. **路由**: 页面导航、参数传递

## 后端测试

### Pytest 配置

**文件**: `backend/pytest.ini`

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

### 单元测试示例

#### CRUD 测试

**文件**: `backend/tests/crud/test_user_crud.py`

```python
import pytest
from sqlalchemy.orm import Session

from app.crud.user import create_user, get_user, get_user_by_email
from app.schemas.user import UserCreate

def test_create_user(db: Session) -> None:
    """测试创建用户"""
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="TestPass123!"
    )
    user = create_user(db, user_in)

    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.is_active is True
    assert hasattr(user, "hashed_password")

def test_get_user_by_email(db: Session) -> None:
    """测试通过邮箱获取用户"""
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="TestPass123!"
    )
    create_user(db, user_in)

    user = get_user_by_email(db, "test@example.com")
    assert user is not None
    assert user.email == "test@example.com"

def test_get_user_not_found(db: Session) -> None:
    """测试获取不存在的用户"""
    user = get_user(db, 999)
    assert user is None
```

#### 服务层测试

**文件**: `backend/tests/services/test_auth_service.py`

```python
import pytest
from app.services.auth import authenticate_user, create_access_token

def test_authenticate_user_success(db: Session, test_user: User) -> None:
    """测试成功的用户认证"""
    authenticated_user = authenticate_user(
        db,
        test_user.email,
        "TestPass123!"
    )
    assert authenticated_user is not None
    assert authenticated_user.email == test_user.email

def test_authenticate_user_wrong_password(db: Session, test_user: User) -> None:
    """测试错误密码"""
    authenticated_user = authenticate_user(
        db,
        test_user.email,
        "WrongPassword"
    )
    assert authenticated_user is None

def test_authenticate_user_not_found(db: Session) -> None:
    """测试不存在的用户"""
    authenticated_user = authenticate_user(
        db,
        "nonexistent@example.com",
        "password"
    )
    assert authenticated_user is None
```

### API 测试示例

**文件**: `backend/tests/api/test_articles.py`

```python
import pytest
from fastapi.testclient import TestClient

def test_list_articles(client: TestClient) -> None:
    """测试获取文章列表"""
    response = client.get("/api/v1/articles")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)

def test_create_article(client: TestClient, auth_headers: dict) -> None:
    """测试创建文章"""
    article_data = {
        "title": "Test Article",
        "content": "Test content",
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

def test_create_article_unauthorized(client: TestClient) -> None:
    """测试未授权创建文章"""
    response = client.post("/api/v1/articles", json={
        "title": "Test",
        "content": "Content",
        "category_id": 1
    })

    assert response.status_code == 401

def test_get_article_not_found(client: TestClient) -> None:
    """测试获取不存在的文章"""
    response = client.get("/api/v1/articles/99999")
    assert response.status_code == 404
```

### 运行后端测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_articles.py

# 运行特定测试
pytest tests/test_articles.py::test_create_article

# 查看覆盖率
pytest --cov=app --cov-report=html

# 只运行快速测试
pytest -m "not slow"

# 并行运行（需要 pytest-xdist）
pytest -n auto
```

## 前端测试

### Vitest 配置

**文件**: `ai-muse-blog/vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData',
      ],
    },
  },
});
```

### 组件测试示例

**文件**: `ai-muse-blog/src/components/__tests__/ArticleCard.test.tsx`

```tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ArticleCard } from '../ArticleCard';

describe('ArticleCard', () => {
  const mockArticle = {
    id: 1,
    title: 'Test Article',
    slug: 'test-article',
    summary: 'Test summary',
    cover_image: 'https://example.com/image.jpg',
    author: {
      username: 'testuser',
      avatar_url: 'https://example.com/avatar.jpg',
    },
    category: {
      name: 'Technology',
    },
    tags: [
      { name: 'React' },
      { name: 'TypeScript' },
    ],
    views_count: 100,
    likes_count: 20,
    comments_count: 5,
    is_liked: false,
    is_bookmarked: false,
    created_at: '2024-01-08T10:00:00Z',
  };

  it('renders article information correctly', () => {
    render(<ArticleCard article={mockArticle} />);

    expect(screen.getByText('Test Article')).toBeInTheDocument();
    expect(screen.getByText('Test summary')).toBeInTheDocument();
    expect(screen.getByText('testuser')).toBeInTheDocument();
    expect(screen.getByText('Technology')).toBeInTheDocument();
  });

  it('displays tags correctly', () => {
    render(<ArticleCard article={mockArticle} />);

    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
  });

  it('calls onLike when like button is clicked', () => {
    const handleLike = vi.fn();
    render(<ArticleCard article={mockArticle} onLike={handleLike} />);

    const likeButton = screen.getByRole('button', { name: /like/i });
    fireEvent.click(likeButton);

    expect(handleLike).toHaveBeenCalledTimes(1);
  });

  it('displays loading skeleton when isLoading is true', () => {
    render(<ArticleCard article={mockArticle} isLoading />);
    expect(screen.getByTestId('article-card-skeleton')).toBeInTheDocument();
  });
});
```

### Hooks 测试示例

**文件**: `ai-muse-blog/src/hooks/__tests__/useArticles.test.ts`

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useArticles, useCreateArticle } from '../useArticles';
import * as api from '@/lib/api';

// Mock API
vi.mock('@/lib/api');

describe('useArticles', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
  });

  it('fetches articles successfully', async () => {
    const mockArticles = {
      items: [
        { id: 1, title: 'Article 1' },
        { id: 2, title: 'Article 2' },
      ],
      total: 2,
      page: 1,
      page_size: 10,
      total_pages: 1,
    };

    vi.mocked(api.articles.list).mockResolvedValue(mockArticles);

    const { result } = renderHook(() => useArticles(), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      ),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockArticles);
  });

  it('handles errors correctly', async () => {
    vi.mocked(api.articles.list).mockRejectedValue(new Error('Failed to fetch'));

    const { result } = renderHook(() => useArticles(), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      ),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toBeTruthy();
  });
});

describe('useCreateArticle', () => {
  it('creates article successfully', async () => {
    const mockArticle = { id: 1, title: 'New Article' };
    vi.mocked(api.articles.create).mockResolvedValue(mockArticle);

    const { result } = renderHook(() => useCreateArticle(), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      ),
    });

    await result.current.mutateAsync({
      title: 'New Article',
      content: 'Content',
      category_id: 1,
    });

    expect(result.current.isSuccess).toBe(true);
    expect(api.articles.create).toHaveBeenCalledWith({
      title: 'New Article',
      content: 'Content',
      category_id: 1,
    });
  });
});
```

### 运行前端测试

```bash
# 运行所有测试
npm run test

# 运行特定文件
npm run test ArticleCard.test.tsx

# 监视模式
npm run test:watch

# 覆盖率报告
npm run test:coverage

# UI 模式
npm run test:ui
```

## 集成测试

### API 集成测试

**文件**: `backend/tests/integration/test_article_flow.py`

```python
def test_complete_article_workflow(client: TestClient, auth_headers: dict) -> None:
    """测试完整的文章工作流"""
    # 1. 创建文章
    create_data = {
        "title": "Integration Test Article",
        "content": "This is a test",
        "category_id": 1,
        "status": "draft"
    }
    response = client.post("/api/v1/articles", json=create_data, headers=auth_headers)
    assert response.status_code == 201
    article_id = response.json()["id"]

    # 2. 获取文章
    response = client.get(f"/api/v1/articles/{article_id}")
    assert response.status_code == 200
    article = response.json()
    assert article["title"] == create_data["title"]

    # 3. 更新文章
    update_data = {"title": "Updated Title"}
    response = client.put(f"/api/v1/articles/{article_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == update_data["title"]

    # 4. 发布文章
    response = client.put(f"/api/v1/articles/{article_id}", json={"status": "published"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "published"

    # 5. 删除文章
    response = client.delete(f"/api/v1/articles/{article_id}", headers=auth_headers)
    assert response.status_code == 204

    # 6. 验证已删除
    response = client.get(f"/api/v1/articles/{article_id}")
    assert response.status_code == 404
```

### 前后端集成测试

**文件**: `tests/integration/test_auth_flow.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('user can register and login', async ({ page }) => {
    await page.goto('/auth');

    // 注册
    await page.click('text=注册');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.click('button[type="submit"]');

    // 验证跳转到登录页
    await expect(page).toHaveURL(/.*auth/);

    // 登录
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.click('button[type="submit"]');

    // 验证登录成功
    await expect(page).toHaveURL('/');
    await expect(page.locator('text=testuser')).toBeVisible();
  });

  test('protected routes require authentication', async ({ page }) => {
    await page.goto('/write');

    // 应该重定向到登录页
    await expect(page).toHaveURL(/.*auth.*/);
  });
});
```

## 端到端测试

### Playwright 配置

**文件**: `ai-muse-blog/playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

### E2E 测试示例

**文件**: `ai-muse-blog/e2e/article.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Article Management', () => {
  test.beforeEach(async ({ page }) => {
    // 登录
    await page.goto('/auth');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/');
  });

  test('can create an article', async ({ page }) => {
    await page.click('text=写文章');
    await expect(page).toHaveURL(/.*write/);

    // 填写表单
    await page.fill('input[name="title"]', 'E2E Test Article');
    await page.fill('textarea[name="content"]', 'This is an E2E test article.');
    await page.selectOption('select[name="category_id"]', '1');

    // 选择标签
    await page.click('button:has-text("选择标签")');
    await page.click('text=React');

    // 发布
    await page.click('button:has-text("发布文章")');

    // 验证成功
    await expect(page.locator('.toast')).toContainText('文章创建成功');
    await expect(page).toHaveURL(/.*articles/);
  });

  test('can view article details', async ({ page }) => {
    await page.goto('/articles');
    await page.click('.article-card:first-child');

    // 验证文章详情页加载
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.article-content')).toBeVisible();

    // 验证评论区域
    await expect(page.locator('.comment-section')).toBeVisible();
  });

  test('can like an article', async ({ page }) => {
    await page.goto('/articles/test-article');

    const likeButton = page.locator('button:has-text("点赞")');
    const initialCount = await likeButton.textContent();

    await likeButton.click();

    // 验证点赞数增加
    const newCount = await likeButton.textContent();
    expect(parseInt(newCount!)).toBe(parseInt(initialCount!) + 1);
  });
});
```

### 运行 E2E 测试

```bash
# 安装 Playwright 浏览器
npx playwright install

# 运行所有 E2E 测试
npm run test:e2e

# 运行特定文件
npx playwright test article.spec.ts

# 调试模式
npx playwright test --debug

# 生成测试报告
npx playwright show-report
```

## 性能测试

### 负载测试（Locust）

**文件**: `tests/performance/locustfile.py`

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # 登录
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        self.token = response.json()["access_token"]

    @task(3)
    def view_articles(self):
        self.client.get("/api/v1/articles")

    @task(2)
    def view_article(self):
        self.client.get("/api/v1/articles/1")

    @task(1)
    def create_article(self):
        self.client.post("/api/v1/articles", json={
            "title": "Performance Test Article",
            "content": "Content",
            "category_id": 1
        }, headers={"Authorization": f"Bearer {self.token}"})
```

### 运行性能测试

```bash
# 启动 Locust
locust -f tests/performance/locustfile.py

# 访问 http://localhost:8089
# 设置用户数和 spawn rate
```

### 数据库性能测试

**文件**: `backend/tests/performance/test_queries.py`

```python
import pytest
import time

def test_article_query_performance(db: Session):
    """测试文章查询性能"""
    # 创建大量数据
    for i in range(1000):
        article = Article(
            title=f"Article {i}",
            content=f"Content {i}",
            author_id=1,
            category_id=1
        )
        db.add(article)
    db.commit()

    # 测试查询性能
    start = time.time()
    articles = db.query(Article).limit(20).all()
    elapsed = time.time() - start

    assert elapsed < 0.1  # 查询应在 100ms 内完成
    assert len(articles) == 20
```

## 测试自动化

### GitHub Actions 工作流

**文件**: `.github/workflows/test.yml`

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
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

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt

    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_ai_muse_blog
      run: |
        cd backend
        pytest --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: |
        cd ai-muse-blog
        npm ci

    - name: Run tests
      run: |
        cd ai-muse-blog
        npm run test:coverage

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  e2e-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_ai_muse_blog

    steps:
    - uses: actions/checkout@v3

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: |
        cd ai-muse-blog
        npm ci

    - name: Install Playwright
      run: |
        cd ai-muse-blog
        npx playwright install --with-deps

    - name: Run E2E tests
      run: |
        cd ai-muse-blog
        npm run test:e2e

    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: playwright-report
        path: ai-muse-blog/playwright-report/
```

## 最佳实践

### 1. 测试命名

```python
# ✅ 好的命名
def test_create_article_with_valid_data_succeeds()
def test_create_article_with_duplicate_title_fails()
def test_get_article_returns_404_when_not_found()

# ❌ 不好的命名
def test_article()
def test_create()
```

### 2. AAA 模式（Arrange-Act-Assert）

```python
def test_update_article():
    # Arrange - 准备测试数据
    article = create_test_article()
    update_data = {"title": "Updated"}

    # Act - 执行操作
    result = update_article(article.id, update_data)

    # Assert - 验证结果
    assert result.title == "Updated"
```

### 3. 使用 Fixture

```python
@pytest.fixture
def test_article(db: Session):
    return Article(title="Test", content="Content")

def test_get_article(db: Session, test_article: Article):
    result = get_article(db, test_article.id)
    assert result.id == test_article.id
```

### 4. Mock 外部依赖

```python
from unittest.mock import patch

def test_send_email():
    with patch('app.services.email.send_email') as mock_email:
        mock_email.return_value = True

        send_notification(user_id=1)

        mock_email.assert_called_once()
```

### 5. 测试隔离

每个测试应该独立运行，不依赖其他测试：

```python
# ✅ 好的做法
def test_create_article():
    article = Article(title="Unique Title")
    db.add(article)
    db.commit()
    assert Article.query.filter_by(title="Unique Title").first() is not None

# ❌ 不好的做法 - 依赖其他测试
def test_create_article():
    # 假设用户已经在其他测试中创建
    article = Article(title="Test", author_id=1)
```

## 调试测试

### Pytest 调试

```bash
# 显示打印输出
pytest -s

# 进入调试器
pytest --pdb

# 在第一个失败时停止
pytest -x

# 显示详细的错误信息
pytest -vv
```

### Vitest 调试

```bash
# UI 模式
npm run test:ui

# 监视模式
npm run test:watch

# 调试特定文件
npm run test ArticleCard.test.tsx
```

### Playwright 调试

```bash
# 调试模式
npx playwright test --debug

# 显示浏览器
npx playwright test --headed

# 慢动作模式
npx playwright test --slow-mo=1000
```

## 资源

- [Pytest 文档](https://docs.pytest.org/)
- [Vitest 文档](https://vitest.dev/)
- [Playwright 文档](https://playwright.dev/)
- [Testing Library 文档](https://testing-library.com/)
- [Locust 文档](https://locust.io/)

---

**最后更新**: 2024-01-08
