# 数据库设计文档
# 需要修改一下不要用SUpabase了，全部都是PsotGresql
## 数据库概述

AI Muse Blog 使用 PostgreSQL 作为主数据库，通过 Supabase 提供托管服务。

## 数据库设计原则

1. **规范化设计**：遵循第三范式，减少数据冗余
2. **性能优化**：合理使用索引，优化查询性能
3. **安全性**：使用 Row Level Security (RLS) 保护数据
4. **可扩展性**：设计支持未来功能扩展
5. **数据完整性**：使用约束和触发器保证数据一致性

## 数据库表结构

### 1. 用户扩展表 (profiles)

扩展 Supabase Auth 的默认用户表，存储额外的用户信息。

```sql
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    bio TEXT,
    website TEXT,
    location TEXT,
    twitter_username TEXT,
    github_username TEXT,
    linkedin_url TEXT,
    expertise TEXT[], -- AI专业领域，如['NLP', 'Computer Vision']
    role TEXT DEFAULT 'reader' CHECK (role IN ('reader', 'author', 'admin')),
    is_verified BOOLEAN DEFAULT false,
    notification_preferences JSONB DEFAULT '{"email": true, "push": false}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_profiles_username ON public.profiles(username);
CREATE INDEX idx_profiles_role ON public.profiles(role);

-- 添加更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 2. 文章表 (articles)

存储博客文章的主要信息。

```sql
CREATE TABLE public.articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    cover_image_url TEXT,
    author_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    category_id UUID REFERENCES public.categories(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    reading_time INTEGER, -- 预计阅读时间（分钟）
    is_featured BOOLEAN DEFAULT false,
    is_top BOOLEAN DEFAULT false,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_articles_author ON public.articles(author_id);
CREATE INDEX idx_articles_category ON public.articles(category_id);
CREATE INDEX idx_articles_status ON public.articles(status);
CREATE INDEX idx_articles_slug ON public.articles(slug);
CREATE INDEX idx_articles_published_at ON public.articles(published_at DESC);
CREATE INDEX idx_articles_view_count ON public.articles(view_count DESC);
CREATE INDEX idx_articles_like_count ON public.articles(like_count DESC);

-- 全文搜索索引
CREATE INDEX idx_articles_search ON public.articles USING GIN(to_tsvector('english', title || ' ' || content));

-- 更新时间触发器
CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON public.articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 自动生成slug的函数
CREATE OR REPLACE FUNCTION generate_slug(title TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN lower(regexp_replace(trim(title), '[^a-zA-Z0-9\s-]', '', 'g'));
END;
$$ LANGUAGE plpgsql;
```

### 3. 分类表 (categories)

文章分类系统。

```sql
CREATE TABLE public.categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    icon TEXT,
    color TEXT, -- 十六进制颜色代码
    parent_id UUID REFERENCES public.categories(id) ON DELETE SET NULL,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_categories_slug ON public.categories(slug);
CREATE INDEX idx_categories_parent ON public.categories(parent_id);
CREATE INDEX idx_categories_sort ON public.categories(sort_order);

-- 更新时间触发器
CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON public.categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 4. 标签表 (tags)

文章标签系统。

```sql
CREATE TABLE public.tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    color TEXT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_tags_slug ON public.tags(slug);
CREATE INDEX idx_tags_usage ON public.tags(usage_count DESC);
```

### 5. 文章标签关联表 (article_tags)

多对多关系表，关联文章和标签。

```sql
CREATE TABLE public.article_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES public.articles(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES public.tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(article_id, tag_id)
);

-- 创建索引
CREATE INDEX idx_article_tags_article ON public.article_tags(article_id);
CREATE INDEX idx_article_tags_tag ON public.article_tags(tag_id);
```

### 6. 评论表 (comments)

用户评论系统。

```sql
CREATE TABLE public.comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES public.articles(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES public.comments(id) ON DELETE CASCADE, -- 支持评论回复
    content TEXT NOT NULL,
    status TEXT DEFAULT 'published' CHECK (status IN ('pending', 'published', 'rejected', 'spam')),
    like_count INTEGER DEFAULT 0,
    isEdited BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_comments_article ON public.comments(article_id);
CREATE INDEX idx_comments_author ON public.comments(author_id);
CREATE INDEX idx_comments_parent ON public.comments(parent_id);
CREATE INDEX idx_comments_status ON public.comments(status);
CREATE INDEX idx_comments_created_at ON public.comments(created_at DESC);

-- 更新时间触发器
CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON public.comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 7. 点赞表 (likes)

用户点赞记录。

```sql
CREATE TABLE public.likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    target_id UUID NOT NULL,
    target_type TEXT NOT NULL CHECK (target_type IN ('article', 'comment')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, target_id, target_type)
);

-- 创建索引
CREATE INDEX idx_likes_user ON public.likes(user_id);
CREATE INDEX idx_likes_target ON public.likes(target_id, target_type);
```

### 8. 收藏表 (bookmarks)

用户收藏记录。

```sql
CREATE TABLE public.bookmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    article_id UUID NOT NULL REFERENCES public.articles(id) ON DELETE CASCADE,
    folder TEXT DEFAULT 'default', -- 收藏夹名称
    notes TEXT, -- 用户备注
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, article_id)
);

-- 创建索引
CREATE INDEX idx_bookmarks_user ON public.bookmarks(user_id);
CREATE INDEX idx_bookmarks_article ON public.bookmarks(article_id);
CREATE INDEX idx_bookmarks_folder ON public.bookmarks(user_id, folder);
```

### 9. 关注表 (follows)

用户关注关系。

```sql
CREATE TABLE public.follows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    follower_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    following_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(follower_id, following_id),
    CHECK (follower_id != following_id)
);

-- 创建索引
CREATE INDEX idx_follows_follower ON public.follows(follower_id);
CREATE INDEX idx_follows_following ON public.follows(following_id);
```

### 10. 通知表 (notifications)

系统通知。

```sql
CREATE TABLE public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('comment', 'like', 'follow', 'mention', 'system')),
    title TEXT NOT NULL,
    content TEXT,
    link TEXT, -- 跳转链接
    is_read BOOLEAN DEFAULT false,
    data JSONB, -- 额外数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_notifications_user ON public.notifications(user_id);
CREATE INDEX idx_notifications_read ON public.notifications(user_id, is_read);
CREATE INDEX idx_notifications_created_at ON public.notifications(created_at DESC);
```

### 11. 经典论文表 (classic_papers)

AI经典论文库。

```sql
CREATE TABLE public.classic_papers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    authors TEXT[], -- 作者数组
    year INTEGER,
    abstract TEXT,
    pdf_url TEXT,
    arxiv_id TEXT,
    doi TEXT,
    publication_venue TEXT,
    citation_count INTEGER DEFAULT 0,
    category_id UUID REFERENCES public.categories(id) ON DELETE SET NULL,
    tags TEXT[], -- 标签数组
    submitted_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    is_approved BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_papers_category ON public.classic_papers(category_id);
CREATE INDEX idx_papers_year ON public.classic_papers(year);
CREATE INDEX idx_papers_citations ON public.classic_papers(citation_count DESC);

-- 全文搜索索引
CREATE INDEX idx_papers_search ON public.classic_papers USING GIN(to_tsvector('english', title || ' ' || COALESCE(abstract, '')));

-- 更新时间触发器
CREATE TRIGGER update_papers_updated_at BEFORE UPDATE ON public.classic_papers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 12. 文件上传表 (uploads)

文件上传记录。

```sql
CREATE TABLE public.uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL, -- Supabase Storage路径
    file_size INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    usage_type TEXT CHECK (usage_type IN ('avatar', 'article_cover', 'article_image', 'attachment')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_uploads_user ON public.uploads(user_id);
CREATE INDEX idx_uploads_usage ON public.uploads(usage_type);
```

### 13. 阅读历史表 (reading_history)

用户阅读记录。

```sql
CREATE TABLE public.reading_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    article_id UUID NOT NULL REFERENCES public.articles(id) ON DELETE CASCADE,
    progress INTEGER DEFAULT 0, -- 阅读进度百分比
    is_completed BOOLEAN DEFAULT false,
    last_read_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, article_id)
);

-- 创建索引
CREATE INDEX idx_reading_history_user ON public.reading_history(user_id);
CREATE INDEX idx_reading_history_article ON public.reading_history(article_id);
```

### 14. 统计表 (statistics)

系统统计数据。

```sql
CREATE TABLE public.statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL UNIQUE,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_statistics_date ON public.statistics(date);
CREATE INDEX idx_statistics_metric ON public.statistics(metric_name, date);
```

## Row Level Security (RLS) 策略

### Profiles表策略

```sql
-- 启用RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- 所有人可以读取profile
CREATE POLICY "Public profiles are viewable by everyone"
    ON public.profiles FOR SELECT
    USING (true);

-- 用户只能更新自己的profile
CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- 已登录用户可以创建profile
CREATE POLICY "Authenticated users can create profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);
```

### Articles表策略

```sql
ALTER TABLE public.articles ENABLE ROW LEVEL SECURITY;

-- 所有人可以读取已发布的文章
CREATE POLICY "Published articles are viewable by everyone"
    ON public.articles FOR SELECT
    USING (status = 'published' OR auth.uid() = author_id);

-- 作者可以管理自己的文章
CREATE POLICY "Authors can manage own articles"
    ON public.articles FOR ALL
    USING (auth.uid() = author_id);

-- 已认证作者可以创建文章
CREATE POLICY "Authenticated authors can create articles"
    ON public.articles FOR INSERT
    WITH CHECK (
        auth.uid() = author_id AND
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role IN ('author', 'admin'))
    );
```

### Comments表策略

```sql
ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;

-- 所有人可以读取已发布的评论
CREATE POLICY "Published comments are viewable by everyone"
    ON public.comments FOR SELECT
    USING (status = 'published');

-- 用户可以管理自己的评论
CREATE POLICY "Users can manage own comments"
    ON public.comments FOR ALL
    USING (auth.uid() = author_id);

-- 已认证用户可以创建评论
CREATE POLICY "Authenticated users can create comments"
    ON public.comments FOR INSERT
    WITH CHECK (auth.uid() = author_id);
```

## 数据库视图

### 文章统计视图

```sql
CREATE OR REPLACE VIEW article_stats AS
SELECT
    a.id,
    a.title,
    a.author_id,
    p.username as author_name,
    a.view_count,
    a.like_count,
    a.comment_count,
    COUNT(DISTINCT l.id) as actual_like_count,
    COUNT(DISTINCT c.id) as actual_comment_count,
    COUNT(DISTINCT b.id) as bookmark_count
FROM public.articles a
LEFT JOIN public.profiles p ON a.author_id = p.id
LEFT JOIN public.likes l ON l.target_id = a.id AND l.target_type = 'article'
LEFT JOIN public.comments c ON c.article_id = a.id AND c.status = 'published'
LEFT JOIN public.bookmarks b ON b.article_id = a.id
GROUP BY a.id, a.title, a.author_id, p.username, a.view_count, a.like_count, a.comment_count;
```

## 数据库函数

### 更新文章计数

```sql
CREATE OR REPLACE FUNCTION update_article_counts()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_TABLE_NAME = 'comments' THEN
        IF TG_OP = 'INSERT' AND NEW.status = 'published' THEN
            UPDATE public.articles
            SET comment_count = comment_count + 1
            WHERE id = NEW.article_id;
        ELSIF TG_OP = 'UPDATE' AND OLD.status != 'published' AND NEW.status = 'published' THEN
            UPDATE public.articles
            SET comment_count = comment_count + 1
            WHERE id = NEW.article_id;
        ELSIF TG_OP = 'UPDATE' AND OLD.status = 'published' AND NEW.status != 'published' THEN
            UPDATE public.articles
            SET comment_count = comment_count - 1
            WHERE id = NEW.article_id;
        ELSIF TG_OP = 'DELETE' AND OLD.status = 'published' THEN
            UPDATE public.articles
            SET comment_count = comment_count - 1
            WHERE id = OLD.article_id;
        END IF;
    ELSIF TG_TABLE_NAME = 'likes' THEN
        IF TG_OP = 'INSERT' AND NEW.target_type = 'article' THEN
            UPDATE public.articles
            SET like_count = like_count + 1
            WHERE id = NEW.target_id;
        ELSIF TG_OP = 'DELETE' AND OLD.target_type = 'article' THEN
            UPDATE public.articles
            SET like_count = like_count - 1
            WHERE id = OLD.target_id;
        END IF;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_article_counts_after_comments
    AFTER INSERT OR UPDATE OR DELETE ON public.comments
    FOR EACH ROW EXECUTE FUNCTION update_article_counts();

CREATE TRIGGER update_article_counts_after_likes
    AFTER INSERT OR DELETE ON public.likes
    FOR EACH ROW EXECUTE FUNCTION update_article_counts();
```

### 更新标签使用次数

```sql
CREATE OR REPLACE FUNCTION update_tag_usage_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE public.tags
        SET usage_count = usage_count + 1
        WHERE id = NEW.tag_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE public.tags
        SET usage_count = GREATEST(usage_count - 1, 0)
        WHERE id = OLD.tag_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tag_count
    AFTER INSERT OR DELETE ON public.article_tags
    FOR EACH ROW EXECUTE FUNCTION update_tag_usage_count();
```

## 初始数据

### 默认分类

```sql
INSERT INTO public.categories (name, slug, description, icon, color, sort_order) VALUES
('深度学习', 'deep-learning', '深度学习相关文章', 'Brain', '#3B82F6', 1),
('自然语言处理', 'nlp', 'NLP技术和应用', 'MessageSquare', '#10B981', 2),
('计算机视觉', 'computer-vision', 'CV技术和应用', 'Camera', '#8B5CF6', 3),
('机器学习', 'machine-learning', '机器学习基础和进阶', 'Target', '#F59E0B', 4),
('强化学习', 'reinforcement-learning', '强化学习和RL应用', 'Gamepad2', '#EF4444', 5),
('AI伦理', 'ai-ethics', 'AI伦理和安全', 'Shield', '#6366F1', 6),
('工具框架', 'tools-frameworks', 'AI开发工具和框架', 'Wrench', '#14B8A6', 7);
```

### 默认标签

```sql
INSERT INTO public.tags (name, slug, description, color) VALUES
('Transformer', 'transformer', 'Transformer架构相关', '#3B82F6'),
('BERT', 'bert', 'BERT模型相关', '#F59E0B'),
('GPT', 'gpt', 'GPT系列模型', '#10B981'),
('PyTorch', 'pytorch', 'PyTorch框架', '#EE4C2C'),
('TensorFlow', 'tensorflow', 'TensorFlow框架', '#FF6F00'),
('LangChain', 'langchain', 'LangChain框架', '#8B5CF6'),
('LLM', 'llm', '大语言模型', '#EC4899'),
('Fine-tuning', 'fine-tuning', '模型微调', '#06B6D4'),
('Prompt Engineering', 'prompt-engineering', '提示工程', '#84CC16'),
('RAG', 'rag', '检索增强生成', '#F97316');
```

## 性能优化建议

1. **索引优化**
   - 为常用查询字段创建索引
   - 使用复合索引优化多条件查询
   - 定期分析和优化索引使用情况

2. **查询优化**
   - 使用 EXPLAIN ANALYZE 分析查询性能
   - 避免SELECT *，只查询需要的字段
   - 使用视图简化复杂查询

3. **连接池配置**
   - 配置合适的连接池大小
   - 使用连接池管理数据库连接

4. **缓存策略**
   - 使用 Redis 缓存热点数据
   - 实现查询结果缓存
   - 合理设置缓存过期时间

5. **定期维护**
   - 定期执行 VACUUM ANALYZE
   - 监控数据库性能指标
   - 清理无用数据

## 数据备份策略

1. **自动备份**
   - Supabase 自动备份（每天）
   - 保留最近7天的备份

2. **手动备份**
   - 重大更新前手动备份
   - 导出关键数据到本地

3. **灾难恢复**
   - 制定恢复流程
   - 定期测试恢复流程

## 更新日志

- **2024-01-08**: 创建数据库设计文档
