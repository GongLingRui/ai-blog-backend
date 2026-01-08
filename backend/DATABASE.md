# Database Design - AI Muse Blog

本文档详细说明 AI Muse Blog 的数据库设计，包括表结构、关系、索引和迁移。

## 目录

- [数据库概述](#数据库概述)
- [ER 图](#er-图)
- [表结构](#表结构)
- [关系](#关系)
- [索引](#索引)
- [数据库迁移](#数据库迁移)
- [性能优化](#性能优化)
- [备份策略](#备份策略)

## 数据库概述

### 技术栈

- **数据库**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **迁移工具**: Alembic 1.13+
- **连接池**: SQLAlchemy Pool

### 数据库配置

```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/ai_muse_blog"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

## ER 图

```mermaid
erDiagram
    users ||--o{ articles : "writes"
    users ||--o{ comments : "writes"
    users ||--o{ likes : "performs"
    users ||--o{ bookmarks : "saves"
    users ||--o{ follows : "initiates"
    users ||--o{ notifications : "receives"

    articles ||--o{ comments : "has"
    articles ||--o{ likes : "receives"
    articles ||--o{ bookmarks : "bookmarked in"
    articles ||--o{ article_tags : "has"
    articles }o--|| categories : "belongs to"

    tags ||--o{ article_tags : "associated with"

    users ||--o{ follow : "follows"
    users ||--o{ follow : "followed by"

    users {
        integer id PK
        string email UK
        string username UK
        string full_name
        string bio
        string avatar_url
        boolean is_active
        boolean is_superuser
        datetime created_at
        datetime updated_at
    }

    articles {
        integer id PK
        string title
        string slug UK
        text content
        text summary
        string cover_image
        integer author_id FK
        integer category_id FK
        string status
        integer views_count
        datetime created_at
        datetime updated_at
    }

    categories {
        integer id PK
        string name UK
        string slug UK
        text description
        string icon
        datetime created_at
    }

    tags {
        integer id PK
        string name UK
        string slug UK
        string color
        datetime created_at
    }

    article_tags {
        integer article_id FK
        integer tag_id FK
    }

    comments {
        integer id PK
        text content
        integer article_id FK
        integer author_id FK
        integer parent_id FK
        datetime created_at
        datetime updated_at
    }

    likes {
        integer id PK
        integer article_id FK
        integer user_id FK
        datetime created_at
    }

    bookmarks {
        integer id PK
        integer article_id FK
        integer user_id FK
        datetime created_at
    }

    follows {
        integer id PK
        integer follower_id FK
        integer following_id FK
        datetime created_at
    }

    notifications {
        integer id PK
        integer user_id FK
        string type
        text title
        text content
        boolean is_read
        datetime created_at
    }
```

## 表结构

### users（用户表）

存储用户账户信息和个人资料。

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    bio TEXT,
    avatar_url VARCHAR(500),
    website VARCHAR(255),
    twitter_handle VARCHAR(50),
    github_handle VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**字段说明**：
- `id`: 主键，自增
- `email`: 邮箱地址，唯一，用于登录
- `username`: 用户名，唯一，用于显示
- `hashed_password`: bcrypt 加密的密码
- `full_name`: 全名
- `bio`: 个人简介
- `avatar_url`: 头像图片 URL
- `website`: 个人网站
- `twitter_handle`: Twitter 账号
- `github_handle`: GitHub 账号
- `is_active`: 账户是否激活
- `is_superuser`: 是否管理员
- `created_at`: 创建时间
- `updated_at`: 更新时间

### articles（文章表）

存储文章内容。

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    cover_image VARCHAR(500),
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
    views_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_articles_author ON articles(author_id);
CREATE INDEX idx_articles_category ON articles(category_id);
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_slug ON articles(slug);
CREATE INDEX idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX idx_articles_status_created ON articles(status, created_at DESC);
CREATE INDEX idx_articles_views ON articles(views_count DESC);

-- 全文搜索索引
CREATE INDEX idx_articles_search ON articles USING gin(to_tsvector('english', title || ' ' || content || ' ' || COALESCE(summary, '')));
```

**字段说明**：
- `id`: 主键
- `title`: 文章标题
- `slug`: URL 友好的唯一标识符
- `content`: Markdown 格式的文章内容
- `summary`: 文章摘要
- `cover_image`: 封面图片 URL
- `author_id`: 作者 ID，外键关联 users
- `category_id`: 分类 ID，外键关联 categories
- `status`: 文章状态（draft: 草稿, published: 已发布）
- `views_count`: 浏览次数
- `created_at`: 创建时间
- `updated_at`: 更新时间

### categories（分类表）

存储文章分类。

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),  -- emoji
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_categories_slug ON categories(slug);
```

**字段说明**：
- `id`: 主键
- `name`: 分类名称
- `slug`: URL 标识符
- `description`: 分类描述
- `icon`: 图标（emoji 字符）
- `created_at`: 创建时间

### tags（标签表）

存储文章标签。

```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7),  -- hex color code
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_tags_slug ON tags(slug);
CREATE INDEX idx_tags_name ON tags(name);
```

**字段说明**：
- `id`: 主键
- `name`: 标签名称
- `slug`: URL 标识符
- `color`: 颜色代码（如 #FF5733）
- `created_at`: 创建时间

### article_tags（文章标签关联表）

多对多关系表。

```sql
CREATE TABLE article_tags (
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

-- 索引
CREATE INDEX idx_article_tags_article ON article_tags(article_id);
CREATE INDEX idx_article_tags_tag ON article_tags(tag_id);
```

### comments（评论表）

存储文章评论。

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_comments_article ON comments(article_id);
CREATE INDEX idx_comments_author ON comments(author_id);
CREATE INDEX idx_comments_parent ON comments(parent_id);
CREATE INDEX idx_comments_created_at ON comments(created_at DESC);
```

**字段说明**：
- `id`: 主键
- `content`: 评论内容
- `article_id`: 文章 ID
- `author_id`: 评论者 ID
- `parent_id`: 父评论 ID（用于嵌套回复）
- `created_at`: 创建时间
- `updated_at`: 更新时间

### likes（点赞表）

存储文章点赞记录。

```sql
CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(article_id, user_id)
);

-- 索引
CREATE INDEX idx_likes_article ON likes(article_id);
CREATE INDEX idx_likes_user ON likes(user_id);
CREATE INDEX idx_likes_article_user ON likes(article_id, user_id);
```

### bookmarks（收藏表）

存储文章收藏记录。

```sql
CREATE TABLE bookmarks (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(article_id, user_id)
);

-- 索引
CREATE INDEX idx_bookmarks_article ON bookmarks(article_id);
CREATE INDEX idx_bookmarks_user ON bookmarks(user_id);
CREATE INDEX idx_bookmarks_user_created ON bookmarks(user_id, created_at DESC);
```

### follows（关注表）

存储用户关注关系。

```sql
CREATE TABLE follows (
    id SERIAL PRIMARY KEY,
    follower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(follower_id, following_id),
    CHECK (follower_id != following_id)
);

-- 索引
CREATE INDEX idx_follows_follower ON follows(follower_id);
CREATE INDEX idx_follows_following ON follows(following_id);
```

### notifications（通知表）

存储用户通知。

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- comment, like, follow, mention
    title VARCHAR(200) NOT NULL,
    content TEXT,
    data JSONB,  -- 额外数据
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_user_created ON notifications(user_id, created_at DESC);
```

**字段说明**：
- `id`: 主键
- `user_id`: 接收者 ID
- `type`: 通知类型
- `title`: 通知标题
- `content`: 通知内容
- `data`: JSON 格式的额外数据
- `is_read`: 是否已读
- `created_at`: 创建时间

## 关系

### 用户相关

1. **用户 → 文章**（一对多）
   - 一个用户可以写多篇文章
   - ON DELETE CASCADE：删除用户时删除其所有文章

2. **用户 → 评论**（一对多）
   - 一个用户可以写多条评论

3. **用户 → 点赞**（一对多）
   - 一个用户可以点赞多篇文章

4. **用户 → 收藏**（一对多）
   - 一个用户可以收藏多篇文章

5. **用户 → 关注**（多对多自引用）
   - 用户可以关注其他用户
   - follower_id: 关注者
   - following_id: 被关注者

6. **用户 → 通知**（一对多）
   - 一个用户可以接收多条通知

### 文章相关

1. **文章 → 分类**（多对一）
   - 一篇文章属于一个分类
   - ON DELETE SET NULL：删除分类时文章的 category_id 设为 NULL

2. **文章 → 标签**（多对多）
   - 通过 article_tags 表关联

3. **文章 → 评论**（一对多）
   - 一篇文章可以有多个评论

4. **文章 → 点赞**（一对多）
   - 一篇文章可以被多个用户点赞

5. **文章 → 收藏**（一对多）
   - 一篇文章可以被多个用户收藏

### 评论相关

1. **评论 → 评论**（一对多自引用）
   - 评论可以有子评论（回复）
   - parent_id: 父评论 ID

## 索引策略

### B-tree 索引（默认）

```sql
-- 单列索引
CREATE INDEX idx_articles_author ON articles(author_id);

-- 复合索引
CREATE INDEX idx_articles_status_created ON articles(status, created_at DESC);
```

### GIN 索引（全文搜索）

```sql
-- 全文搜索
CREATE INDEX idx_articles_search ON articles USING gin(
    to_tsvector('english', title || ' ' || content)
);

-- JSONB 索引
CREATE INDEX idx_notifications_data ON notifications USING gin(data);
```

### 唯一索引

```sql
-- 防止重复
CREATE UNIQUE INDEX idx_articles_slug ON articles(slug);
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

### 部分索引

```sql
-- 只索引已发布的文章
CREATE INDEX idx_articles_published ON articles(created_at DESC)
WHERE status = 'published';
```

## 数据库迁移

### Alembic 迁移

#### 创建迁移

```bash
# 自动生成迁移
alembic revision --autogenerate -m "Add user preferences"

# 手动创建迁移
alembic revision -m "Add user preferences"
```

#### 应用迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级到特定版本
alembic upgrade +1
alembic upgrade 1234

# 降级
alembic downgrade -1
alembic downgrade base
```

#### 查看迁移状态

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 查看待执行的迁移
alembic heads
```

### 迁移示例

#### 添加新字段

```python
# alembic/versions/001_add_user_preferences.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users',
        sa.Column('preferences', sa.JSON(), nullable=True)
    )

def downgrade():
    op.drop_column('users', 'preferences')
```

#### 创建新表

```python
# alembic/versions/002_create_notifications_table.py
def upgrade():
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notifications_user', 'notifications', ['user_id'])

def downgrade():
    op.drop_table('notifications')
```

## 性能优化

### 查询优化

#### 使用 JOIN 代替子查询

```python
# 不好的做法
articles = db.query(Article).filter(
    Article.author_id.in_(
        db.query(User.id).filter(User.is_active == True)
    )
).all()

# 好的做法
articles = db.query(Article)\
    .join(User, Article.author_id == User.id)\
    .filter(User.is_active == True)\
    .all()
```

#### 使用 Eager Loading

```python
from sqlalchemy.orm import joinedload, subqueryload

# 避免N+1查询
articles = db.query(Article)\
    .options(
        joinedload(Article.author),
        joinedload(Artacte.category),
        subqueryload(Article.tags)
    )\
    .all()
```

#### 只查询需要的字段

```python
# 不好的做法
articles = db.query(Article).all()

# 好的做法
articles = db.query(
    Article.id,
    Article.title,
    Article.created_at
).all()
```

### 数据库配置优化

#### PostgreSQL 配置

```ini
# postgresql.conf

# 内存设置
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 64MB

# 连接设置
max_connections = 100

# 查询规划
random_page_cost = 1.1  # SSD
effective_io_concurrency = 200

# WAL
wal_buffers = 16MB
checkpoint_completion_target = 0.9

# 日志
log_min_duration_statement = 1000
```

### 连接池配置

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,           # 池中的连接数
    max_overflow=20,        # 超出 pool_size 后最多创建的连接数
    pool_timeout=30,        # 获取连接的超时时间
    pool_recycle=1800,      # 连接回收时间（秒）
    pool_pre_ping=True      # 连接前先 ping 测试
)
```

## 备份策略

### 逻辑备份（pg_dump）

```bash
# 备份整个数据库
pg_dump -U postgres -d ai_muse_blog > backup.sql

# 只备份结构
pg_dump -U postgres -d ai_muse_blog --schema-only > schema.sql

# 只备份数据
pg_dump -U postgres -d ai_muse_blog --data-only > data.sql

# 压缩备份
pg_dump -U postgres -d ai_muse_blog | gzip > backup.sql.gz

# 恢复
psql -U postgres -d ai_muse_blog < backup.sql
gunzip < backup.sql.gz | psql -U postgres -d ai_muse_blog
```

### 物理备份（pg_basebackup）

```bash
# 基础备份
pg_basebackup -U postgres -D /backup/dir -Ft -z -P

# 增量备份（需要 WAL 归档）
```

### 自动化备份脚本

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="ai_muse_blog"
DB_USER="postgres"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 删除 30 天前的备份
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_$DATE.sql.gz"
```

### 定时备份（Cron）

```bash
# 每天凌晨 2 点备份
0 2 * * * /path/to/backup.sh >> /var/log/db_backup.log 2>&1
```

## 数据完整性

### 约束

```sql
-- CHECK 约束
ALTER TABLE articles ADD CONSTRAINT check_status
    CHECK (status IN ('draft', 'published'));

-- 防止自己关注自己
ALTER TABLE follows ADD CONSTRAINT check_not_self
    CHECK (follower_id != following_id);

-- NOT NULL 约束
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
```

### 触发器

```sql
-- 自动更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## 监控

### 慢查询日志

```sql
-- 记录执行时间超过 1 秒的查询
ALTER DATABASE ai_muse_blog SET log_min_duration_statement = 1000;

-- 查看慢查询
SELECT * FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### 统计信息

```sql
-- 表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 索引使用情况
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

## 安全

### 行级安全（RLS）

```sql
-- 启用 RLS
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- 用户只能看到自己的草稿
CREATE POLICY user_drafts ON articles
    FOR SELECT
    USING (
        status = 'published'
        OR author_id = current_setting('app.user_id')::INTEGER
    );
```

### 数据库用户权限

```sql
-- 创建只读用户
CREATE USER readonly_user WITH PASSWORD 'password';
GRANT CONNECT ON DATABASE ai_muse_blog TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- 创建应用用户
CREATE USER app_user WITH PASSWORD 'password';
GRANT CONNECT ON DATABASE ai_muse_blog TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
```

## 常见问题

### Q: 如何处理软删除？

添加 `is_deleted` 字段而不是真正删除：

```sql
ALTER TABLE articles ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
CREATE INDEX idx_articles_deleted ON articles(is_deleted);

-- 查询时过滤
SELECT * FROM articles WHERE NOT is_deleted;
```

### Q: 如何实现多语言支持？

使用 JSONB 字段存储翻译：

```sql
ALTER TABLE articles ADD COLUMN title_translations JSONB;
UPDATE articles SET title_translations = jsonb_build_object(
    'en', title,
    'zh', title
);

-- 查询
SELECT title_translations->>'zh' AS title
FROM articles;
```

### Q: 如何优化全文搜索？

使用 tsvector 和 GIN 索引：

```sql
ALTER TABLE articles ADD COLUMN content_tsv TSVECTOR;
CREATE INDEX idx_articles_tsv ON articles USING gin(content_tsv);

CREATE OR REPLACE FUNCTION articles_tsv_trigger() RETURNS trigger AS $$
BEGIN
    NEW.content_tsv := to_tsvector('english', COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.content, ''));
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER tsvector_update BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION articles_tsv_trigger();

-- 搜索
SELECT * FROM articles
WHERE content_tsv @@ to_tsquery('english', 'machine & learning');
```

## 资源

- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
- [pgAdmin](https://www.pgadmin.org/)

---

**最后更新**: 2024-01-08
**数据库版本**: PostgreSQL 15+
