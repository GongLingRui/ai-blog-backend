# AI Muse Blog 测试指南

本文档提供了完整的测试指南，包括后端（pytest）和前端（Vitest）的测试配置、运行和最佳实践。

## 目录

- [后端测试](#后端测试)
- [前端测试](#前端测试)
- [测试覆盖率要求](#测试覆盖率要求)
- [最佳实践](#最佳实践)

---

## 后端测试

### 目录结构

```
backend/
├── tests/
│   ├── conftest.py              # pytest 配置和 fixtures
│   ├── unit/
│   │   └── test_crud/           # CRUD 单元测试
│   │       ├── test_user.py
│   │       ├── test_article.py
│   │       ├── test_comment.py
│   │       ├── test_bookmark.py
│   │       ├── test_like.py
│   │       └── test_follow.py
│   │   └── test_core/           # 核心功能单元测试
│   │       ├── test_security.py
│   │       ├── test_cache.py
│   │       └── test_utils.py
│   └── api/                     # API 集成测试
│       ├── test_auth.py
│       ├── test_articles.py
│       ├── test_comments.py
│       ├── test_bookmarks.py
│       ├── test_likes.py
│       ├── test_follows.py
│       └── test_upload.py
├── pytest.ini                   # pytest 配置文件
└── .env.test                    # 测试环境变量
```

### 环境配置

1. **安装测试依赖**（已在 requirements.txt 中）:
   ```bash
   pytest==7.4.3
   pytest-asyncio==0.21.1
   pytest-cov==4.1.0
   pytest-mock==3.12.0
   httpx==0.25.2
   ```

2. **配置测试数据库**:
   - 编辑 `.env.test` 文件
   - 确保测试数据库独立于开发数据库
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_muse_blog_test
   REDIS_URL=redis://localhost:6379/1
   ```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_crud/test_user.py

# 运行特定测试
pytest tests/unit/test_crud/test_user.py::test_create_user

# 运行单元测试（不包括集成测试）
pytest tests/unit/ -m "not integration"

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行测试并显示详细输出
pytest -v

# 运行测试并显示打印语句
pytest -s
```

### Fixtures

主要 fixtures 在 `conftest.py` 中定义：

```python
# 数据库
@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """创建测试数据库会话"""

# 测试客户端
@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator:
    """创建测试客户端"""

# 测试数据
@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """创建测试用户"""

@pytest_asyncio.fixture
async def test_article(db_session: AsyncSession, test_user: User) -> Article:
    """创建测试文章"""

# 认证
@pytest.fixture
def user_token(test_user: User) -> str:
    """生成用户访问令牌"""

@pytest.fixture
def user_headers(user_token: str) -> dict:
    """生成认证头"""
```

### 测试示例

**单元测试示例**:
```python
@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """测试创建用户"""
    user_in = UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="password123"
    )
    user = await create_user(db_session, user_in)

    assert user.username == "newuser"
    assert user.email == "newuser@example.com"
```

**API 集成测试示例**:
```python
@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """测试用户注册"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@example.com"
```

---

## 前端测试

### 目录结构

```
ai-muse-blog/
├── src/
│   ├── components/
│   │   └── __tests__/
│   │       ├── ArticleCard.test.tsx
│   │       ├── CommentForm.test.tsx
│   │       ├── CommentSection.test.tsx
│   │       ├── UserCard.test.tsx
│   │       ├── BookmarkList.test.tsx
│   │       └── TagCloud.test.tsx
│   ├── hooks/
│   │   └── __tests__/
│   │       ├── useArticles.test.ts
│   │       ├── useComments.test.ts
│   │       ├── useAuth.test.tsx
│   │       └── useBookmarks.test.ts
│   ├── lib/
│   │   └── __tests__/
│   │       └── api.test.ts
│   └── test-setup.ts            # 测试设置
├── vitest.config.ts             # Vitest 配置
└── package.json
```

### 环境配置

1. **安装测试依赖**:
   ```bash
   npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event @vitest/ui
   ```

2. **更新 package.json scripts**:
   ```json
   {
     "scripts": {
       "test": "vitest",
       "test:ui": "vitest --ui",
       "test:coverage": "vitest --coverage"
     }
   }
   ```

### 运行测试

```bash
# 运行所有测试
npm test

# 运行测试（watch 模式）
npm test -- --watch

# 运行测试并打开 UI
npm run test:ui

# 运行测试并生成覆盖率报告
npm run test:coverage

# 运行特定测试文件
npm test -- ArticleCard.test.tsx

# 运行匹配模式的测试
npm test -- --grep "Article"
```

### 测试设置

**test-setup.ts** 包含：
- jsdom 环境
- 全局 mocks（IntersectionObserver, ResizeObserver 等）
- LocalStorage mock
- Fetch mock
- 清理逻辑

### 测试示例

**组件测试示例**:
```typescript
describe('ArticleCard', () => {
  it('renders article title and excerpt', () => {
    renderWithProviders(<ArticleCard article={mockArticle} />)

    expect(screen.getByText('Test Article Title')).toBeInTheDocument()
    expect(screen.getByText('Test excerpt')).toBeInTheDocument()
  })

  it('handles like button click', async () => {
    renderWithProviders(<ArticleCard article={mockArticle} />)

    const likeButton = screen.getAllByRole('button')[0]
    fireEvent.click(likeButton)

    expect(likeButton).toBeInTheDocument()
  })
})
```

**Hook 测试示例**:
```typescript
describe('useArticles', () => {
  it('fetches articles list successfully', async () => {
    const { result } = renderHook(() => useArticles(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(result.current.data).toEqual({ items: [], total: 0 })
  })
})
```

**API 测试示例**:
```typescript
describe('ApiClient', () => {
  it('makes GET request with params', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: 'test' }),
    })

    await apiClient.get('/test', { page: '1' })

    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/test?page=1',
      expect.any(Object)
    )
  })
})
```

---

## 测试覆盖率要求

### 目标

- **总体覆盖率**: ≥ 70%
- **语句覆盖率**: ≥ 70%
- **分支覆盖率**: ≥ 70%
- **函数覆盖率**: ≥ 70%
- **行覆盖率**: ≥ 70%

### 查看覆盖率

**后端**:
```bash
# 生成 HTML 报告
pytest --cov=app --cov-report=html

# 在浏览器中打开
open htmlcov/index.html
```

**前端**:
```bash
# 生成覆盖率报告
npm run test:coverage

# 查看报告
open coverage/index.html
```

---

## 最佳实践

### 后端测试

1. **使用 fixtures 复用测试数据**
   - 定义清晰的 fixtures
   - 使用 factory 模式创建测试数据

2. **隔离测试**
   - 每个测试独立运行
   - 使用事务回滚清理数据
   - 避免测试间依赖

3. **异步测试**
   - 使用 `@pytest.mark.asyncio` 装饰器
   - 正确处理异步操作
   - 使用 `await` 等待异步完成

4. **Mock 外部依赖**
   - Mock Redis、外部 API 等
   - 使用 `pytest-mock` 进行 mocking

5. **测试命名**
   - 使用描述性测试名称
   - 格式: `test_<功能>_<场景>_<预期结果>`

### 前端测试

1. **组件测试**
   - 测试用户交互
   - 测试 props 变化
   - 测试条件渲染
   - 使用 screen queries 查询元素

2. **Hook 测试**
   - 测试状态变化
   - 测试副作用
   - 测试错误处理
   - 使用 renderHook

3. **Mock 管理**
   - Mock API 调用
   - Mock 外部依赖
   - 清理 mocks

4. **测试隔离**
   - 每个测试独立运行
   - 使用 cleanup 清理
   - 重置 mocks

5. **避免测试实现细节**
   - 测试用户可见行为
   - 不测试内部实现
   - 关注功能而非代码

### 通用最佳实践

1. **AAA 模式** (Arrange-Act-Assert):
   ```python
   def test_something():
       # Arrange - 准备测试数据和环境
       user = create_test_user()

       # Act - 执行被测试的操作
       result = process_user(user)

       # Assert - 验证结果
       assert result.status == 'active'
   ```

2. **一个测试一个断言**:
   - 保持测试简单
   - 失败时容易定位问题

3. **使用描述性名称**:
   ```python
   # 好的测试名称
   def test_user_cannot_login_with_wrong_password()

   # 不好的测试名称
   def test_login()
   ```

4. **测试边界情况**:
   - 空值
   - 极限值
   - 错误输入

5. **保持测试快速**:
   - 使用 in-memory 数据库
   - Mock 外部服务
   - 避免不必要的 I/O

6. **持续集成**:
   - 在 CI/CD 中运行测试
   - 测试失败阻止合并
   - 定期检查测试覆盖率

---

## 故障排除

### 后端测试

**问题**: 数据库连接失败
- 检查 `.env.test` 配置
- 确保测试数据库存在
- 检查数据库服务是否运行

**问题**: 异步测试失败
- 确保使用 `@pytest.mark.asyncio`
- 检查 event loop 配置
- 验证 await 使用正确

**问题**: Fixture 不工作
- 检查 fixture 参数名称
- 确保正确导入
- 检查作用域

### 前端测试

**问题**: 测试环境错误
- 检查 `vitest.config.ts`
- 确保正确设置 environment
- 验证依赖已安装

**问题**: Mock 不工作
- 检查 mock 路径
- 确保在测试前设置 mock
- 验证 mock 实现

**问题**: 测试超时
- 检查异步操作
- 增加超时时间
- 确保正确 cleanup

---

## 资源

- [Pytest 文档](https://docs.pytest.org/)
- [Vitest 文档](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [最佳实践指南](https://testing-library.com/docs/guiding-principles)
