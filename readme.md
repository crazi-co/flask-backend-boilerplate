# Flask PostgreSQL Stripe Backend Boilerplate

A production-ready Flask backend boilerplate with JWT authentication, PostgreSQL database, Google OAuth, Stripe payments, and Azure deployment scripts.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Technology Stack

- **Language:** Python 3.11
- **Web Framework:** Flask
- **Authentication:** JWT (PyJWT) with bcrypt password hashing
- **Database:** PostgreSQL with SQLModel and Pydantic for ORM and validation
- **OAuth:** Google OAuth integration
- **Payments:** Stripe integration
- **Email:** AWS SES for transactional emails
- **Deployment:** Docker containers with Azure App Service support
- **Other:** Flask-CORS, Flask-Limiter, Werkzeug, Uvicorn

## Project Structure

```
flask-postgres-stripe-backend-boilerplate/
├── app/                          # Main application package
│   ├── data/                    # Static data and email templates
│   │   └── email_templates/     # HTML email templates (OTP, welcome, password reset)
│   ├── error_handing/           # Custom error handlers (AWS, Stripe, base errors)
│   ├── logs/                    # Application log files
│   ├── routes/                  # Flask route handlers (auth, users, stripe, transactions, misc)
│   ├── schemas/                 # Pydantic schemas and database models
│   │   ├── api/                 # API response schemas
│   │   └── database/            # SQLModel database models (user, session, transaction, OTP)
│   ├── services/                # Business logic services (auth, user, email, OTP, stripe, transaction, database)
│   └── utils/                   # Utility functions (API responses, logging configuration)
├── creds/                       # Credentials directory (gitignored - contains OAuth secrets, AWS keys)
├── docs/                        # Documentation (deployment guides and API spec)
│   ├── APP_SERVICE_GUIDE.md     # Azure App Service deployment guide
│   ├── CONTAINER_APPS_GUIDE.md  # Azure Container Apps deployment guide (legacy)
│   └── Boilerplate.openapi.json # OpenAPI 3.0 specification for all API endpoints
├── scripts/                     # Utility scripts
│   └── generate_keys.py        # Key generation utilities
├── tests/                       # Test suite
├── docker-compose.yml           # Docker Compose configuration for local development
├── Dockerfile                   # Docker image definition
├── Makefile                     # Deployment and management commands
├── flask_app.py                # Main Flask application entry point
├── run.py                      # Production runner script
├── run_debug.py                # Development/debug runner script
├── start.sh                    # Production startup script (gunicorn)
├── setup.py                    # Application setup and initialization
├── requirements.txt            # Python dependencies
└── .env.example                 # Environment variables template

```

## Prerequisites

- **Python 3.11** (required)
- **PostgreSQL** database (local or remote)
- **Azure account** (for deployment)
- **Stripe account** (for payments)
- **Google OAuth credentials** (for OAuth)
- **AWS SES credentials** (for email)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd flask-postgres-stripe-backend-boilerplate
```

### 2. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and fill in all required variables:
# - Database connection (DATABASE_DSN)
# - JWT secret key (JWT_SECRET_KEY)
# - API keys (PUBLIC_API_KEY, PRIVATE_API_KEY)
# - AWS SES credentials (SES_AWS_ACCESS_KEY_ID, SES_AWS_SECRET_ACCESS_KEY)
# - Stripe keys (STRIPE_SECRET_KEY, STRIPE_PRICE_ID)
# - Google OAuth (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
# - Azure deployment config (RESOURCE_GROUP, LOCATION, etc.)
```

### 3. Install Dependencies

```bash
# Create virtual environment (recommended)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 4. Run the Application

**Development Mode (with debug):**
```bash
python run_debug.py
```

**Production Mode:**
```bash
python run.py
```

The application will start on the port specified in `API_PORT` (default: 5000).

### 5. Verify Installation

```bash
# Health check endpoint
curl http://localhost:5000/api/v1/health
```

## Deployment

### Docker Container Deployment

Deploy as a Docker container to Azure App Service (~$13/month):

```bash
# 1. Install Azure CLI and login
make install
make login

# 2. Create infrastructure (resource group, App Service Plan, ACR if using ACR)
make setup

# 3. Build Docker image and deploy
make deploy
```

**For more details:** See [docs/APP_SERVICE_GUIDE.md](docs/APP_SERVICE_GUIDE.md)

### Azure App Service Deployment

Quick deployment commands:

```bash
# First-time deployment
make setup      # Create infrastructure
make deploy     # Build and deploy Docker container

# Update code
make redeploy   # Rebuild and redeploy

# Update environment variables only
make deploy-env-vars

# View logs
make logs

# Get app URL
make url
```

**For more details:** See [docs/APP_SERVICE_GUIDE.md](docs/APP_SERVICE_GUIDE.md)

### Alternative: Source Code Deployment

Deploy directly from source code (no Docker required):

```bash
make setup          # Create infrastructure
make deploy-source  # Deploy from source code
```

**Note:** Docker container deployment is recommended for production.

## Environment Variables

All environment variables are defined in `.env.example`. Key variables include:

- **API Configuration:** `API_PORT`, `API_BASE`
- **Database:** `DATABASE_DSN`
- **Authentication:** `JWT_SECRET_KEY`, `JWT_ALGORITHM`
- **AWS SES:** `SES_AWS_ACCESS_KEY_ID`, `SES_AWS_SECRET_ACCESS_KEY`, `SES_AWS_REGION`
- **Stripe:** `STRIPE_SECRET_KEY`, `STRIPE_PRICE_ID`, `CLIENT_URL`, `STRIPE_RETURN_URL`
- **Google OAuth:** `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
- **Azure Deployment:** `RESOURCE_GROUP`, `LOCATION`, `APP_NAME`, `REGISTRY_TYPE`, etc.

See `.env.example` for the complete list.

## Features

- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **User Management** - User registration, login, profile management
- ✅ **Google OAuth** - Social authentication integration
- ✅ **Stripe Payments** - Payment processing integration
- ✅ **Email Service** - AWS SES integration for transactional emails
- ✅ **OTP System** - One-time password for email verification
- ✅ **Database Models** - SQLModel ORM with Pydantic validation
- ✅ **Error Handling** - Custom error handlers for AWS, Stripe, and general errors
- ✅ **Logging** - Structured logging configuration
- ✅ **CORS Support** - Cross-origin resource sharing enabled
- ✅ **Rate Limiting** - Flask-Limiter integration
- ✅ **Azure Deployment** - Ready-to-deploy with Docker and App Service

## API Endpoints

The application exposes REST API endpoints for:

- **Authentication:** `/api/v1/auth/*` - Login, register, OAuth, OTP
- **Users:** `/api/v1/user/*` - User profile management
- **Stripe:** `/api/v1/stripe/*` - Payment processing
- **Transactions:** `/api/v1/transaction/*` - Transaction management
- **Misc:** `/api/v1/misc/*` - Health check and utilities

See **[OpenAPI Specification](docs/Boilerplate.openapi.json)** for complete API documentation including request/response schemas, authentication methods, and example requests.

## Development

### Running Tests

```bash
# Run test suite (when implemented)
python -m pytest tests/
```

### Code Style

The project uses pylint for code quality. Run:

```bash
pylint app/
```

## Documentation

- **[OpenAPI Specification](docs/Boilerplate.openapi.json)** - Complete API documentation (OpenAPI 3.0 format)
- **[Azure App Service Guide](docs/APP_SERVICE_GUIDE.md)** - Complete deployment guide for Azure App Service
- **[Container Apps Guide](docs/CONTAINER_APPS_GUIDE.md)** - Legacy Container Apps deployment guide

### Viewing the OpenAPI Specification

You can view the OpenAPI spec using:

- **Swagger UI:** Import `docs/Boilerplate.openapi.json` into [Swagger Editor](https://editor.swagger.io/)
- **Postman:** Import the OpenAPI file directly into Postman
- **VS Code:** Use the "OpenAPI Preview" extension to view the spec
- **Any OpenAPI-compatible tool:** The spec follows OpenAPI 3.0.1 standard


## Support

For issues and questions, please open an issue in the repository.
