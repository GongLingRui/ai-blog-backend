# 前端优化规划文档

## 前端现状分析

### 当前技术栈
- React 18.3.1 + TypeScript 5.8.3
- Vite 5.4.19 (构建工具)
- React Router DOM 6.30.1 (路由)
- TanStack Query 5.83.0 (服务端状态)
- shadcn/ui + Tailwind CSS 3.4.17 (UI)
- React Hook Form 7.61.1 + Zod 3.25.76 (表单)

### 现有问题

1. **API集成**: 目前使用Supabase，需要迁移到自建后端
2. **数据管理**: 需要优化服务端状态和客户端状态管理
3. **类型定义**: 需要完善TypeScript类型定义
4. **错误处理**: 需要统一的错误处理机制
5. **性能优化**: 需要优化加载性能和渲染性能
6. **测试**: 缺少单元测试和集成测试

## 前端架构优化

### 1. API客户端重构

#### API配置

```typescript
// src/config/api.ts
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  apiVersion: '/api/v1',
  timeout: 10000,
}

export const API_ENDPOINTS = {
  // 认证
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
    CHANGE_PASSWORD: '/auth/change-password',
  },
  // 用户
  USERS: {
    LIST: '/users',
    DETAIL: (id: string) => `/users/${id}`,
    UPDATE: (id: string) => `/users/${id}`,
    AVATAR: (id: string) => `/users/${id}/avatar`,
    ARTICLES: (id: string) => `/users/${id}/articles`,
  },
  // 文章
  ARTICLES: {
    LIST: '/articles',
    DETAIL: (id: string) => `/articles/${id}`,
    BY_SLUG: (slug: string) => `/articles/slug/${slug}`,
    CREATE: '/articles',
    UPDATE: (id: string) => `/articles/${id}`,
    DELETE: (id: string) => `/articles/${id}`,
    VIEW: (id: string) => `/articles/${id}/view`,
    TRENDING: '/articles/trending',
    RELATED: (id: string) => `/articles/${id}/related`,
  },
  // 分类
  CATEGORIES: {
    LIST: '/categories',
    DETAIL: (id: string) => `/categories/${id}`,
    CREATE: '/categories',
    UPDATE: (id: string) => `/categories/${id}`,
    DELETE: (id: string) => `/categories/${id}`,
  },
  // 标签
  TAGS: {
    LIST: '/tags',
    SEARCH: '/tags/search',
    CREATE: '/tags',
  },
  // 评论
  COMMENTS: {
    LIST: '/comments',
    DETAIL: (id: string) => `/comments/${id}`,
    CREATE: '/comments',
    UPDATE: (id: string) => `/comments/${id}`,
    DELETE: (id: string) => `/comments/${id}`,
  },
  // 点赞
  LIKES: {
    CREATE: '/likes',
    DELETE: (id: string, type: string) => `/likes/${id}/${type}`,
    CHECK: '/likes/check',
  },
  // 收藏
  BOOKMARKS: {
    LIST: '/bookmarks',
    CREATE: '/bookmarks',
    DELETE: (id: string) => `/bookmarks/${id}`,
  },
  // 关注
  FOLLOWS: {
    CREATE: '/follows',
    DELETE: (id: string) => `/follows/${id}`,
    FOLLOWERS: (id: string) => `/follows/${id}/followers`,
    FOLLOWING: (id: string) => `/follows/${id}/following`,
  },
  // 通知
  NOTIFICATIONS: {
    LIST: '/notifications',
    READ: (id: string) => `/notifications/${id}/read`,
    READ_ALL: '/notifications/read-all',
  },
  // 论文
  PAPERS: {
    LIST: '/papers',
    DETAIL: (id: string) => `/papers/${id}`,
    CREATE: '/papers',
  },
  // 上传
  UPLOAD: {
    IMAGE: '/upload/image',
  },
}
```

#### API客户端实现

```typescript
// src/lib/api-client.ts
import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios'
import { API_CONFIG } from '@/config/api'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.baseURL + API_CONFIG.apiVersion,
      timeout: API_CONFIG.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器 - 添加token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截器 - 处理错误和token刷新
    this.client.interceptors.response.use(
      (response) => response.data,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

        // Token过期，尝试刷新
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            const refreshToken = localStorage.getItem('refresh_token')
            const response = await this.post('/auth/refresh', { refresh_token: refreshToken })

            const { access_token } = response.data
            localStorage.setItem('access_token', access_token)

            originalRequest.headers = {
              ...originalRequest.headers,
              Authorization: `Bearer ${access_token}`,
            }

            return this.client(originalRequest)
          } catch (refreshError) {
            // 刷新失败，跳转登录
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/auth'
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config)
    return response
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config)
    return response
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config)
    return response
  }

  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch<T>(url, data, config)
    return response
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config)
    return response
  }
}

export const apiClient = new ApiClient()
```

### 2. 类型定义完善

```typescript
// src/types/index.ts

// 通用类型
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

export interface ApiError {
  success: false
  error: {
    code: string
    message: string
    details?: Record<string, any>
  }
}

export interface PaginationParams {
  page?: number
  page_size?: number
  sort?: string
  order?: 'asc' | 'desc'
}

export interface PaginatedResponse<T> {
  success: boolean
  data: T[]
  pagination: {
    total: number
    page: number
    page_size: number
    pages: number
  }
}

// 用户类型
export interface User {
  id: string
  email: string
  username: string
  full_name?: string
  avatar_url?: string
  bio?: string
  website?: string
  location?: string
  twitter_username?: string
  github_username?: string
  linkedin_url?: string
  expertise: string[]
  role: 'reader' | 'author' | 'admin'
  is_verified: boolean
  followers_count?: number
  following_count?: number
  articles_count?: number
  created_at: string
  updated_at?: string
}

export interface AuthResponse {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
}

// 文章类型
export interface Article {
  id: string
  title: string
  slug: string
  content: string
  excerpt?: string
  cover_image_url?: string
  author: Author
  category?: Category
  tags: Tag[]
  view_count: number
  like_count: number
  comment_count: number
  reading_time?: number
  is_featured: boolean
  is_top: boolean
  status: 'draft' | 'published' | 'archived'
  published_at?: string
  created_at: string
  updated_at?: string
}

export interface Author {
  id: string
  username: string
  full_name?: string
  avatar_url?: string
}

// 分类类型
export interface Category {
  id: string
  name: string
  slug: string
  description?: string
  icon?: string
  color?: string
  parent_id?: string
  sort_order: number
  articles_count?: number
}

// 标签类型
export interface Tag {
  id: string
  name: string
  slug: string
  description?: string
  color?: string
  usage_count?: number
}

// 评论类型
export interface Comment {
  id: string
  article_id: string
  content: string
  author: Author
  parent_id?: string
  like_count: number
  replies_count?: number
  is_edited: boolean
  status: 'pending' | 'published' | 'rejected' | 'spam'
  created_at: string
  updated_at?: string
  replies?: Comment[]
}

// 通知类型
export interface Notification {
  id: string
  type: 'comment' | 'like' | 'follow' | 'mention' | 'system'
  title: string
  content?: string
  link?: string
  is_read: boolean
  created_at: string
}

// 论文类型
export interface Paper {
  id: string
  title: string
  authors: string[]
  year?: number
  abstract?: string
  pdf_url?: string
  arxiv_id?: string
  doi?: string
  publication_venue?: string
  citation_count?: number
  category?: Category
  tags: string[]
  created_at: string
}
```

### 3. TanStack Query集成

```typescript
// src/lib/query-client.ts
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5分钟
      gcTime: 10 * 60 * 1000, // 10分钟
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})
```

```typescript
// src/hooks/queries/useArticles.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { API_ENDPOINTS } from '@/config/api'
import type { Article, PaginationParams } from '@/types'

export function useArticles(params?: PaginationParams & {
  status?: string
  category_id?: string
  tag_id?: string
  search?: string
}) {
  return useQuery({
    queryKey: ['articles', params],
    queryFn: () => apiClient.get(API_ENDPOINTS.ARTICLES.LIST, { params }),
  })
}

export function useArticle(id: string) {
  return useQuery({
    queryKey: ['article', id],
    queryFn: () => apiClient.get(API_ENDPOINTS.ARTICLES.DETAIL(id)),
    enabled: !!id,
  })
}

export function useArticleBySlug(slug: string) {
  return useQuery({
    queryKey: ['article', slug],
    queryFn: () => apiClient.get(API_ENDPOINTS.ARTICLES.BY_SLUG(slug)),
    enabled: !!slug,
  })
}

export function useCreateArticle() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<Article>) =>
      apiClient.post(API_ENDPOINTS.ARTICLES.CREATE, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] })
    },
  })
}

export function useUpdateArticle() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Article> }) =>
      apiClient.put(API_ENDPOINTS.ARTICLES.UPDATE(id), data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['article', variables.id] })
      queryClient.invalidateQueries({ queryKey: ['articles'] })
    },
  })
}

export function useDeleteArticle() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) =>
      apiClient.delete(API_ENDPOINTS.ARTICLES.DELETE(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] })
    },
  })
}
```

### 4. Context优化

```typescript
// src/contexts/AuthContext.tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { apiClient } from '@/lib/api-client'
import { API_ENDPOINTS } from '@/config/api'
import type { User, AuthResponse } from '@/types'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<AuthResponse>
  register: (data: RegisterData) => Promise<AuthResponse>
  logout: () => void
  updateUser: (data: Partial<User>) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  async function checkAuth() {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setIsLoading(false)
      return
    }

    try {
      const response = await apiClient.get<ApiResponse<User>>(API_ENDPOINTS.AUTH.ME)
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      setIsLoading(false)
    }
  }

  async function login(email: string, password: string) {
    const response = await apiClient.post<ApiResponse<AuthResponse>>(
      API_ENDPOINTS.AUTH.LOGIN,
      { email, password }
    )

    const { user, access_token, refresh_token } = response.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    setUser(user)

    return response.data
  }

  async function register(data: RegisterData) {
    const response = await apiClient.post<ApiResponse<AuthResponse>>(
      API_ENDPOINTS.AUTH.REGISTER,
      data
    )

    const { user, access_token, refresh_token } = response.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    setUser(user)

    return response.data
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  async function updateUser(data: Partial<User>) {
    if (!user) return

    const response = await apiClient.patch<ApiResponse<User>>(
      API_ENDPOINTS.USERS.UPDATE(user.id),
      data
    )

    setUser(response.data)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
```

### 5. 错误处理

```typescript
// src/components/ui/ErrorBoundary.tsx
import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo)
    // 可以在这里发送错误到日志服务
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-gray-900">Oops!</h1>
              <p className="text-gray-600 mt-2">Something went wrong.</p>
              <button
                onClick={() => window.location.reload()}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Reload Page
              </button>
            </div>
          </div>
        )
      )
    }

    return this.props.children
  }
}
```

```typescript
// src/utils/error-handler.ts
import type { ApiError } from '@/types'

export function handleApiError(error: any): string {
  if (error.response?.data) {
    const apiError = error.response.data as ApiError
    return apiError.error.message || 'An error occurred'
  }

  if (error.message) {
    return error.message
  }

  return 'An unexpected error occurred'
}

export function getErrorMessage(error: any, field?: string): string | undefined {
  if (error.response?.data?.error?.details) {
    const details = error.response.data.error.details
    return field ? details[field] : undefined
  }
  return undefined
}
```

### 6. 性能优化

#### 代码分割

```typescript
// src/App.tsx
import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './lib/query-client'
import { AuthProvider } from './contexts/AuthContext'
import { ErrorBoundary } from './components/ui/ErrorBoundary'
import { Navbar } from './components/Navbar'
import { LoadingSpinner } from './components/ui/loading-spinner'

// 懒加载页面组件
const Index = lazy(() => import('./pages/Index'))
const Articles = lazy(() => import('./pages/Articles'))
const ArticleDetail = lazy(() => import('./pages/ArticleDetail'))
const WriteArticle = lazy(() => import('./pages/WriteArticle'))
const Auth = lazy(() => import('./pages/Auth'))
const NotFound = lazy(() => import('./pages/NotFound'))

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AuthProvider>
            <div className="min-h-screen bg-background">
              <Navbar />
              <main>
                <Suspense fallback={<LoadingSpinner />}>
                  <Routes>
                    <Route path="/" element={<Index />} />
                    <Route path="/articles" element={<Articles />} />
                    <Route path="/article/:slug" element={<ArticleDetail />} />
                    <Route path="/write" element={<WriteArticle />} />
                    <Route path="/auth" element={<Auth />} />
                    <Route path="*" element={<NotFound />} />
                  </Routes>
                </Suspense>
              </main>
            </div>
          </AuthProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
```

#### 虚拟滚动

```typescript
// src/components/ArticleList.tsx
import { useVirtualizer } from '@tanstack/react-virtual'

export function ArticleList({ articles }: { articles: Article[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: articles.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 300, // 估计每项高度
    overscan: 5,
  })

  return (
    <div ref={parentRef} className="h-screen overflow-auto">
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => {
          const article = articles[virtualItem.index]
          return (
            <div
              key={article.id}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${virtualItem.start}px)`,
              }}
            >
              <ArticleCard article={article} />
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

### 7. 测试

#### 单元测试示例

```typescript
// src/components/__tests__/ArticleCard.test.tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ArticleCard } from '../ArticleCard'
import type { Article } from '@/types'

describe('ArticleCard', () => {
  const mockArticle: Article = {
    id: '1',
    title: 'Test Article',
    slug: 'test-article',
    content: 'Test content',
    excerpt: 'Test excerpt',
    author: { id: '1', username: 'testuser' },
    tags: [],
    view_count: 100,
    like_count: 10,
    comment_count: 5,
    is_featured: false,
    is_top: false,
    status: 'published',
    created_at: '2024-01-08',
  }

  it('renders article title', () => {
    render(<ArticleCard article={mockArticle} />)
    expect(screen.getByText('Test Article')).toBeInTheDocument()
  })

  it('renders article stats', () => {
    render(<ArticleCard article={mockArticle} />)
    expect(screen.getByText('100')).toBeInTheDocument() // views
    expect(screen.getByText('10')).toBeInTheDocument() // likes
  })
})
```

## 优化清单

### 高优先级
- [ ] API客户端重构（迁移到自建后端）
- [ ] 完善TypeScript类型定义
- [ ] 实现统一错误处理
- [ ] 集成TanStack Query
- [ ] 优化认证流程

### 中优先级
- [ ] 实现代码分割
- [ ] 添加图片懒加载
- [ ] 优化SEO
- [ ] 添加PWA支持
- [ ] 实现主题持久化

### 低优先级
- [ ] 添加单元测试
- [ ] 添加E2E测试
- [ ] 实现性能监控
- [ ] 添加国际化支持

## 性能目标

- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1
- TTI (Time to Interactive): < 3.5s
- Bundle Size: < 500KB (gzipped)

## 更新日志

- **2024-01-08**: 创建前端优化规划文档
