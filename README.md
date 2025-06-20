# E-commerce API

A professional Django REST Framework e-commerce API with JWT authentication and SMS-based registration.

## Features

- 📱 SMS-based user registration and authentication
- 🔐 JWT token authentication with refresh tokens
- 🛍️ Product catalog with categories, filtering, and search
- 🛒 Shopping cart functionality
- 📦 Order management system
- ⭐ Product reviews and ratings
- 👤 User profile management
- 🚀 Production-ready with Vercel deployment

## Tech Stack

- **Backend**: Django 5.0, Django REST Framework
- **Authentication**: JWT with SimpleJWT
- **Database**: PostgreSQL (production), SQLite (development)
- **Cache**: Redis
- **Task Queue**: Celery
- **Deployment**: Vercel, Docker support
- **Code Quality**: Black, Ruff, pre-commit hooks

## API Endpoints

### Authentication
- `POST /api/v1/auth/authorize/` - Request SMS verification code
- `POST /api/v1/auth/verify/` - Verify SMS code and register/login
- `POST /api/v1/auth/login/` - Login with phone and password
- `POST /api/v1/auth/logout/` - Logout and blacklist token
- `POST /api/v1/auth/token/refresh/` - Refresh access token
- `POST /api/v1/auth/forgot-password/` - Request password reset
- `POST /api/v1/auth/reset-password/` - Reset password
- `GET/PUT /api/v1/auth/profile/` - Get/update user profile

### Products
- `GET /api/v1/shop/products/` - List products with filtering
- `GET /api/v1/shop/products/{id}/` - Get product details
- `POST /api/v1/shop/products/{id}/like/` - Toggle product like

### Shopping Cart
- `GET /api/v1/shop/cart/` - View cart
- `POST /api/v1/shop/cart/` - Add to cart
- `DELETE /api/v1/shop/cart/{product_id}/` - Remove from cart

### Orders
- `GET /api/v1/shop/orders/` - List user orders
- `POST /api/v1/shop/orders/` - Create order from cart
- `GET /api/v1/shop/orders/{id}/` - Get order details

### Reviews
- `POST /api/v1/shop/products/{id}/review/` - Create product review

## Quick Start

### Development Setup

\`\`\`bash
# Clone the repository
git clone <repo-url>
cd ecommerce-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/development.txt

# Setup environment variables
cp .env.example .env
# Edit .env file with your settings

# Install pre-commit hooks
pre-commit install

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create sample data
python scripts/create_sample_data.py

# Start development server
./start.sh
\`\`\`

### Production Deployment

#### Vercel Deployment

1. Install Vercel CLI: `npm i -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel --prod`
4. Set environment variables in Vercel dashboard

#### Docker Deployment

\`\`\`bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individual container
docker build -t ecommerce-api .
docker run -p 8000:8000 ecommerce-api
\`\`\`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Django settings module | `config.settings.development` |
| `DEBUG` | Debug mode | `True` |
| `SECRET_KEY` | Django secret key | Required |
| `DATABASE_URL` | Database connection URL | `sqlite:///db.sqlite3` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `SMS_API_URL` | SMS service API URL | Required |
| `SMS_LOGIN` | SMS service login | Required |
| `SMS_PASSWORD` | SMS service password | Required |
| `SMS_SENDER_ID` | SMS sender ID | Required |

## Project Structure

\`\`\`
ecommerce-api/
├── apps/
│   ├── common/          # Shared utilities
│   ├── users/           # User management & auth
│   ├── products/        # Product catalog & cart
│   ├── orders/          # Order management
│   └── reviews/         # Product reviews
├── config/
│   ├── settings/        # Django settings
│   ├── urls.py         # URL configuration
│   └── wsgi.py         # WSGI application
├── requirements/        # Dependencies
├── scripts/            # Utility scripts
├── static/             # Static files
├── media/              # Media files
├── vercel.json         # Vercel configuration
├── Dockerfile          # Docker configuration
└── docker-compose.yml  # Docker Compose
\`\`\`

## API Documentation

The API follows OpenAPI 3.0 specification. Key features:

- **Consistent Response Format**: All responses follow `{success: boolean, data?: any, error?: object}` format
- **Pagination**: List endpoints support pagination with metadata
- **Filtering**: Products can be filtered by category, price, attributes
- **Search**: Full-text search on product title and description
- **Authentication**: JWT Bearer token authentication
- **Error Handling**: Detailed error messages with validation details

## Testing

\`\`\`bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
\`\`\`

## Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Fast Python linter
- **Pre-commit**: Git hooks for code quality
- **Django Debug Toolbar**: Development debugging

\`\`\`bash
# Format code
black .

# Lint code
ruff check .

# Run pre-commit hooks
pre-commit run --all-files
\`\`\`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.
