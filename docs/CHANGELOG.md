# Changelog

All notable changes to AI Muse Blog will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Real-time notifications
- Article version history
- AI-powered content recommendations
- Mobile applications (iOS/Android)

## [1.0.0] - 2024-01-08

### Added

#### Authentication & Authorization
- User registration with email validation
- JWT-based authentication with access and refresh tokens
- Token refresh mechanism
- Password hashing with bcrypt
- Password change functionality
- Email verification system
- Password reset flow

#### User Management
- User profile creation and editing
- Avatar upload functionality
- User profile pages
- User statistics dashboard
- Follow/unfollow users
- User search functionality

#### Article Management
- Article creation with Markdown editor
- Article editing and deletion
- Draft and published status
- Article slug generation
- Article view counter
- Rich text content with syntax highlighting
- Cover image upload
- Article categories and tags
- Article search functionality
- Related articles recommendation

#### Content Organization
- Category management system
- Tag management system
- Tag search and filtering
- Category-based article filtering
- Tag cloud component

#### Social Features
- Comment system with threading
- Like/unlike articles
- Bookmark/save articles
- User notifications
- Comment likes
- Comment replies

#### API Endpoints
- RESTful API design
- OpenAPI/Swagger documentation
- Pagination support
- Sorting and filtering
- Full-text search
- Rate limiting
- CORS support

#### Frontend Features
- Responsive design (mobile, tablet, desktop)
- Dark mode support
- Modern UI with shadcn/ui components
- React Router for navigation
- TanStack Query for data fetching
- Optimistic updates
- Infinite scroll for article lists
- Skeleton loading states
- Error boundaries
- Toast notifications

#### Performance
- Redis caching layer
- Database query optimization
- Image optimization
- Code splitting
- Lazy loading
- CDN-ready static assets

#### Security
- Input validation with Pydantic
- SQL injection prevention
- XSS protection
- CSRF protection
- Rate limiting per IP
- Secure headers configuration
- Environment variable management

#### DevOps
- Docker containerization
- Docker Compose for local development
- Database migrations with Alembic
- Health check endpoints
- Logging system
- Error handling middleware

#### Testing
- Backend unit tests with Pytest
- API integration tests
- Frontend component tests
- E2E test setup
- Test coverage reporting

#### Documentation
- README with quick start guide
- Development guide
- Deployment guide
- API documentation
- Database design documentation
- Component documentation

### Technical Stack

#### Backend
- Python 3.11+
- FastAPI 0.104+
- SQLAlchemy 2.0+
- PostgreSQL 15+
- Redis 7+
- Alembic 1.13+
- Celery 5.3+
- Pydantic 2.5+

#### Frontend
- React 18.3+
- TypeScript 5.8+
- Vite 5.4+
- Tailwind CSS 3.4+
- shadcn/ui (Radix UI)
- TanStack Query 5.83+
- React Router DOM 6.30+
- React Markdown 10.1+
- React Syntax Highlighter 16.1+

### Database Schema

#### Tables
- users (用户表)
- articles (文章表)
- categories (分类表)
- tags (标签表)
- article_tags (文章标签关联表)
- comments (评论表)
- likes (点赞表)
- bookmarks (收藏表)
- follows (关注表)
- notifications (通知表)

### API Routes

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/change-password` - Change password

#### Users
- `GET /api/v1/users` - List users
- `GET /api/v1/users/{id}` - Get user details
- `PATCH /api/v1/users/{id}` - Update user
- `GET /api/v1/users/{id}/articles` - Get user's articles
- `POST /api/v1/users/{id}/follow` - Follow user
- `DELETE /api/v1/users/{id}/follow` - Unfollow user

#### Articles
- `GET /api/v1/articles` - List articles
- `GET /api/v1/articles/{id}` - Get article details
- `GET /api/v1/articles/slug/{slug}` - Get article by slug
- `POST /api/v1/articles` - Create article
- `PUT /api/v1/articles/{id}` - Update article
- `DELETE /api/v1/articles/{id}` - Delete article
- `POST /api/v1/articles/{id}/view` - Increment view count

#### Categories
- `GET /api/v1/categories` - List categories
- `GET /api/v1/categories/{id}` - Get category details

#### Tags
- `GET /api/v1/tags` - List tags
- `GET /api/v1/tags/search` - Search tags

#### Comments
- `GET /api/v1/articles/{article_id}/comments` - List comments
- `POST /api/v1/articles/{article_id}/comments` - Create comment
- `PUT /api/v1/comments/{id}` - Update comment
- `DELETE /api/v1/comments/{id}` - Delete comment

#### Likes
- `POST /api/v1/articles/{article_id}/like` - Like article
- `DELETE /api/v1/articles/{article_id}/like` - Unlike article

#### Bookmarks
- `GET /api/v1/bookmarks` - List bookmarks
- `POST /api/v1/articles/{article_id}/bookmark` - Bookmark article
- `DELETE /api/v1/articles/{article_id}/bookmark` - Remove bookmark

### Environment Variables

#### Backend
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### Frontend
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Known Issues

- Email delivery may require additional SMTP configuration
- File upload size limit currently set to 10MB
- Real-time notifications not yet implemented
- Article export functionality pending

### Migration Guide

See [MIGRATION_GUIDE.md](./ai-muse-blog/MIGRATION_GUIDE.md) for detailed migration instructions.

### Upgrade Instructions

```bash
# Pull latest code
git pull origin main

# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head

# Frontend
cd ../ai-muse-blog
npm install
npm run build

# Docker
docker compose up -d --build
```

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2024-01-08 | Initial release with core features |

## Future Releases

### v1.1.0 (Q1 2024)
- Real-time notifications with WebSocket
- Article version history
- Advanced search with filters
- User role management (admin, editor, author)
- Email notifications
- RSS feed

### v1.2.0 (Q2 2024)
- AI-powered content recommendations
- Social sharing integration
- Reading time estimation
- Table of contents auto-generation
- Article series management
- Bookmark folders

### v2.0.0 (Q3 2024)
- Mobile applications (React Native)
- Multi-language support (i18n)
- Advanced analytics dashboard
- API rate limiting per user
- GraphQL API alternative
- Webhook integrations

---

## Contributing

For contribution guidelines, see [DEVELOPMENT.md](./DEVELOPMENT.md).

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [repository-url]/wiki
- Email: support@example.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note:** This project is actively maintained. Check the [Unreleased] section for upcoming features.
