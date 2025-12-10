# Crazi Co - Azure Container Apps Deployment Guide (OLD - $76/month)

⚠️ **DEPRECATED: Use App Service instead (~$13/month)** - See `APP_SERVICE_GUIDE.md`

This guide is kept for reference. All commands have been renamed to `docker-*` prefix.

---

## ⚡ Quick Start (20 minutes)

### Step 1: Create `.env` file

Create a `.env` file in your project root with **ALL** your configuration:

```bash
# Copy this template and fill in your values
cat > .env << 'EOF'
# ============================================================================
# API Configuration
# ============================================================================
API_PORT=5000
API_BASE=/api/v1

# ============================================================================
# Database Configuration (REQUIRED)
# ============================================================================
DATABASE_DSN=postgresql://user:password@host:5432/database

# ============================================================================
# Authorization Configuration
# ============================================================================
AUTHORIZATION_HEADER=Authorization

# ============================================================================
# Role Configuration
# ============================================================================
PUBLIC_ROLE=public
PRIVATE_ROLE=private
USER_ROLE=user

# ============================================================================
# API Keys
# ============================================================================
PUBLIC_API_KEY=your-public-api-key
PRIVATE_API_KEY=your-private-api-key

# ============================================================================
# JWT/Authentication Configuration (REQUIRED)
# ============================================================================
JWT_SECRET_KEY=your-secret-key-here-minimum-32-characters
JWT_ALGORITHM=HS256

# ============================================================================
# AWS SES (Email Service) Configuration
# ============================================================================
SES_AWS_ACCESS_KEY_ID=your-aws-access-key-id
SES_AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
SES_AWS_REGION=us-east-1

# ============================================================================
# OTP Configuration
# ============================================================================
OTP_EXPIRY_IN_MINUTES=10
SESSION_EXPIRY_IN_DAYS=30

# ============================================================================
# Azure Resources Configuration
# ============================================================================
RESOURCE_GROUP=Crazi-Co
LOCATION=canadacentral
ACR_NAME=crazicoregistry
APP_NAME=crazi-co
ENV_NAM=crazi-co-env
WEBAPP_PLAN=crazi-co-plan
WEBAPP_SKU=B1

# ============================================================================
# Application Version
# ============================================================================
VERSION=1.0.0

# ============================================================================
# Container Registry Configuration
# ============================================================================
# Registry Type: acr, dockerhub, or ghcr (default: dockerhub)
REGISTRY_TYPE=dockerhub

# For Docker Hub - needed if REGISTRY_TYPE=dockerhub
DOCKERHUB_USERNAME=your-dockerhub-username
DOCKERHUB_PASSWORD=your-dockerhub-password-or-token

# ============================================================================
# Application Configuration
# ============================================================================
ENVIRONMENT=production
RATE_LIMIT=100

# ============================================================================
# Stripe Configuration
# ============================================================================
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PRICE_ID=your-stripe-price-id
CLIENT_URL=https://your-client-url.com
STRIPE_RETURN_URL=https://your-client-url.com/return

# ============================================================================
# Google OAuth Configuration
# ============================================================================
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://your-app-url.com/auth/google/callback
EOF
```

> **Note:** All variables from `.env` are automatically deployed as encrypted secrets in Azure!

### Step 2: Configure Registry

Choose your container registry (FREE options available!):

**Option A: Docker Hub (FREE - Recommended)**
```bash
REGISTRY_TYPE=dockerhub
DOCKERHUB_USERNAME=your-dockerhub-username
DOCKERHUB_PASSWORD=your-dockerhub-password
```

**Option B: GitHub Container Registry (FREE)**
```bash
REGISTRY_TYPE=ghcr
GHCR_USERNAME=your-github-username
GHCR_REPO=crazi-co
GHCR_TOKEN=your-github-personal-access-token  # Needs package:write permission
```

**Option C: Azure Container Registry (Paid)**
```bash
REGISTRY_TYPE=acr
ACR_NAME=crazicoregistry
```

### Step 3: Deploy Everything

```bash
make install        # Install Azure CLI (one-time)
make login          # Login to Azure
make docker-deploy  # Deploy everything (~15-20 min)
```

**Note:** Deployment time varies:
- **Docker Hub/GitHub:** ~15 minutes (local build + push)
- **ACR:** ~20 minutes (Azure Cloud build)

### Step 3: Get Your URL

```bash
make docker-url
```

**🎉 Done!** Test it: `curl https://YOUR_URL/api/v1/health`

---

## 📋 Daily Workflow Cheat Sheet

| What Changed? | Command | Time |
|---------------|---------|------|
| 💻 **Code files** | `make docker-redeploy` | ~15 min |
| 📦 **requirements.txt** | `make docker-redeploy` | ~15 min |
| 🔑 **.env file** | `make docker-deploy-env-vars` | ~1 min |

**Remember:** Your code is baked into the Docker image, so ANY code change requires `make docker-redeploy`!

---

## Common Commands

```bash
make help             # Show all commands
make docker-redeploy         # Rebuild image + redeploy (code/requirements.txt changes) ~15min
make docker-deploy-env-vars  # Deploy latest image + sync env vars (env changes only) ~1min
make docker-logs             # View logs
make docker-status           # App status
make docker-restart          # Restart app
```

> **⚡ Important:** Code is baked into the Docker image - use `make docker-redeploy` for ANY code changes!

### Version Management

When you run `make deploy` or `make docker-redeploy`, you'll be prompted to update your app version:

```bash
📌 Current Version: 1.0.0
Enter new version (or press Enter to keep current): 1.1.0
✅ Version updated to 1.1.0 in .env
```

- **Keep same version**: Just press Enter
- **Update version**: Type new version (e.g., `1.1.0`, `2.0.0`)
- The version is automatically updated in `.env` and deployed to Azure
- You can also manually run `make update-version` to change version without deploying

---

## Table of Contents

1. [Quick Start (20 minutes)](#quick-start)
2. [Makefile Commands Reference](#makefile-commands)
3. [Manual Deployment (Alternative)](#manual-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Troubleshooting](#troubleshooting)
6. [Cost Estimation](#cost-estimation)
7. [Advanced Topics](#advanced-topics)

---

## Quick Start

### Prerequisites

- Mac with Homebrew installed
- Azure account with active subscription
- Your `.env` file configured (see below)

### 1. Configure Environment (2 minutes)

Create/update your `.env` file in the project root with **all** required variables (see Step 1 above for complete list).

**Minimum required for deployment:**

```bash
# API Configuration
API_PORT=5000
API_BASE=/api/v1

# Database (REQUIRED)
DATABASE_DSN=postgresql://user:password@host:5432/database

# Authorization
AUTHORIZATION_HEADER=Authorization

# Roles
PUBLIC_ROLE=public
PRIVATE_ROLE=private
USER_ROLE=user

# API Keys
PUBLIC_API_KEY=your-public-key
PRIVATE_API_KEY=your-private-key

# JWT (REQUIRED)
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# AWS SES
SES_AWS_ACCESS_KEY_ID=your-aws-access-key-id
SES_AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
SES_AWS_REGION=us-east-1

# OTP
OTP_EXPIRY_IN_MINUTES=10
SESSION_EXPIRY_IN_DAYS=30

# Azure Resources
RESOURCE_GROUP=Crazi-Co
LOCATION=canadacentral
ACR_NAME=crazicoregistry
APP_NAME=crazi-co
ENV_NAM=crazi-co-env
WEBAPP_PLAN=crazi-co-plan
WEBAPP_SKU=B1

# Application Version
VERSION=1.0.0

# Container Registry
REGISTRY_TYPE=dockerhub
DOCKERHUB_USERNAME=your-dockerhub-username
DOCKERHUB_PASSWORD=your-dockerhub-password

# Application Configuration
ENVIRONMENT=production
RATE_LIMIT=100

# Stripe Configuration
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PRICE_ID=your-stripe-price-id
CLIENT_URL=https://your-client-url.com
STRIPE_RETURN_URL=https://your-client-url.com/return

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://your-app-url.com/auth/google/callback
```

> **🔒 Security:** Sensitive values (keys, secrets) are automatically stored as encrypted Azure secrets!

### 2. Install Azure CLI (2 minutes)

```bash
make install
```

This installs Azure CLI and Container Apps extension.

### 3. Login to Azure (1 minute)

```bash
make login
```

Your browser will open for authentication.

### 4. Complete Deployment (15 minutes)

```bash
# One command to deploy everything!
make deploy
```

This will:
1. ✅ Create resource group
2. ✅ Register Azure providers
3. ✅ Create Azure Container Registry (only if `REGISTRY_TYPE=acr`)
4. ✅ Build your Docker image (locally for Docker Hub/GitHub, or in Azure Cloud for ACR)
5. ✅ Push image to your chosen registry
6. ✅ Create Container Apps environment
7. ✅ Deploy your app

### 5. Get Your App URL

```bash
make docker-url
```

Test it:
```bash
curl https://YOUR_APP_URL/api/v1/health
```

**Done! 🎉** Your app is live on Azure!

---

## Makefile Commands

### Essential Commands

| Command | Description | Time |
|---------|-------------|------|
| `make help` | Show all available commands | instant |
| `make install` | Install Azure CLI and extensions | 2 min |
| `make login` | Login to Azure | 1 min |
| `make docker-deploy` | Complete deployment from scratch (prompts for version) | 15-20 min* |
| `make docker-redeploy` | **Rebuild image + redeploy (prompts for version)** | 10-15 min* |

\* *Times vary: Docker Hub/GitHub (10-15 min), ACR (15-20 min)*
| `make docker-deploy-env-vars` | **Deploy latest image + sync env vars (env changes only)** | 1 min |
| `make update-version` | Update VERSION in .env (without deploying) | instant |
| `make docker-build` | Build and push Docker image to registry | 5-15 min* |

\* *Times vary: Docker Hub/GitHub (5-10 min), ACR (10-15 min)*
| `make docker-url` | Get app URL | instant |

> **💡 Tip:** Use `make docker-redeploy` for code changes, `make docker-deploy-env-vars` for env var changes!

### Monitoring & Management

| Command | Description |
|---------|-------------|
| `make docker-logs` | View last 100 log lines |
| `make docker-logs-follow` | Follow logs in real-time |
| `make docker-status` | Show app status |
| `make docker-restart` | Restart the app |
| `make list-images` | List all Docker images in registry |

### Scaling

```bash
# Scale to 2-10 replicas
make docker-scale MIN=2 MAX=10
```

### Cleanup

| Command | Description |
|---------|-------------|
| `make clean` | Delete container app (keeps images) |
| `make docker-clean-all` | **DANGER**: Delete everything |

---

## Deployment Workflows

### First Time Deployment

```bash
# 1. Install and login
make install
make login

# 2. Deploy everything
make deploy

# 3. Get URL and test
make docker-url
curl https://YOUR_APP_URL/api/v1/health
```

### Update Existing App

After making code changes:

```bash
# Rebuild and redeploy
make docker-redeploy

# Or step by step:
make docker-build            # Build new image
make docker-deploy-env-vars  # Deploy new image + env vars
```

### View Logs

```bash
# Last 100 lines
make docker-logs

# Follow in real-time
make docker-logs-follow
```

---

## Manual Deployment (Alternative)

If you prefer not to use Make:

### Step 1: Install Azure CLI

```bash
brew install azure-cli
az extension add --name containerapp --upgrade
az login
```

### Step 2: Set Variables

```bash
export RESOURCE_GROUP="Crazi-Co"
export LOCATION="canadacentral"
export ACR_NAME="crazicoregistry"
export APP_NAME="crazi-co"
export ENV_NAME="crazi-co-env"
export DATABASE_DSN="your-db-connection"
export API_BASE="/api/v1"
```

### Step 3: Create Resources

```bash
# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Register providers
az provider register -n Microsoft.App --wait
az provider register -n Microsoft.OperationalInsights --wait

# Create ACR (only if using ACR)
if [ "$REGISTRY_TYPE" = "acr" ]; then
  az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --location $LOCATION \
    --admin-enabled true
fi
```

### Step 4: Build Image

**For Azure Container Registry:**
```bash
# Build in Azure Cloud
az acr build \
  --registry $ACR_NAME \
  --image $APP_NAME:latest \
  --resource-group $RESOURCE_GROUP \
  .
```

**For Docker Hub:**
```bash
# Build locally and push
docker build -t $DOCKERHUB_USERNAME/$APP_NAME:latest .
docker push $DOCKERHUB_USERNAME/$APP_NAME:latest
```

**For GitHub Container Registry:**
```bash
# Build locally and push
docker build -t ghcr.io/$GHCR_USERNAME/$GHCR_REPO:latest .
docker push ghcr.io/$GHCR_USERNAME/$GHCR_REPO:latest
```

### Step 5: Create Container Environment

```bash
az containerapp env create \
  --name $ENV_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 6: Deploy App

**For Azure Container Registry:**
```bash
# Get ACR credentials
REGISTRY_URL=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
REGISTRY_USER=$(az acr credential show --name $ACR_NAME --query username -o tsv)
REGISTRY_PASS=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
IMAGE_NAME="$REGISTRY_URL/$APP_NAME:latest"
```

**For Docker Hub:**
```bash
REGISTRY_URL="docker.io"
REGISTRY_USER="$DOCKERHUB_USERNAME"
REGISTRY_PASS="$DOCKERHUB_PASSWORD"
IMAGE_NAME="$DOCKERHUB_USERNAME/$APP_NAME:latest"
```

**For GitHub Container Registry:**
```bash
REGISTRY_URL="ghcr.io"
REGISTRY_USER="$GHCR_USERNAME"
REGISTRY_PASS="$GHCR_TOKEN"
IMAGE_NAME="ghcr.io/$GHCR_USERNAME/$GHCR_REPO:latest"
```

**Deploy:**
```bash
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image $IMAGE_NAME \
  --registry-server $REGISTRY_URL \
  --registry-username $REGISTRY_USER \
  --registry-password $REGISTRY_PASS \
  --target-port 5000 \
  --ingress external \
  --cpu 1.0 \
  --memory 2.0Gi \
  --min-replicas 1 \
  --max-replicas 5 \
  --secrets database-dsn="$DATABASE_DSN" \
  --env-vars \
    DATABASE_DSN=secretref:database-dsn \
    API_BASE="$API_BASE" \
    API_PORT=5000
```

---

## Environment Variables Management

### How It Works

All environment variables from your `.env` file are automatically:
1. **🔒 Encrypted** - Sensitive values (keys, secrets) stored as Azure secrets
2. **🔄 Synced** - Deployed on every `make docker-deploy-env-vars`
3. **🚀 Applied** - New revision created with updated config

### Day-to-Day Workflow

**When you change code or requirements.txt:**
```bash
# Rebuilds entire Docker image with your changes
make docker-redeploy  # Takes ~15 min
```

**When you only change .env file:**
```bash
# Updates latest image + environment variables (no rebuild)
make docker-deploy-env-vars  # Takes ~1 min
```

**Option 3: Manual (Advanced)**
```bash
# Update specific variables
az containerapp update \
  --name crazi-co \
  --resource-group Crazi Co \
  --set-env-vars "API_BASE=/api/v2"
```

### Required Environment Variables

See [Step 1](#step-1-create-env-file) above for the complete list. **Minimum required:**

- `DATABASE_DSN` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret for JWT tokens
- Authorization keys (`PRIVATE_API_KEY`, `PUBLIC_API_KEY`)
- `SES_AWS_ACCESS_KEY_ID` and `SES_AWS_SECRET_ACCESS_KEY` - For email service

### Security Best Practices

✅ **DO:**
- Keep `.env` file in `.gitignore`
- Use strong, random keys for `JWT_SECRET_KEY`
- Rotate API keys regularly
- Use Azure Key Vault for production secrets

❌ **DON'T:**
- Commit `.env` to git
- Share API keys in chat/email
- Use default/example values in production

---

## Environment Configuration

### Required Environment Variables

Your `.env` file must include:

```bash
# API Configuration
API_PORT=5000
API_BASE=/api/v1

# Database Configuration
DATABASE_DSN=postgresql://user:pass@host:5432/db

# Authorization
AUTHORIZATION_HEADER=Authorization

# Roles
PUBLIC_ROLE=public
PRIVATE_ROLE=private
USER_ROLE=user

# API Keys
PUBLIC_API_KEY=your-public-key
PRIVATE_API_KEY=your-private-key

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# AWS SES Configuration
SES_AWS_ACCESS_KEY_ID=your-aws-access-key-id
SES_AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
SES_AWS_REGION=us-east-1

# OTP Configuration
OTP_EXPIRY_IN_MINUTES=10
SESSION_EXPIRY_IN_DAYS=30

# Azure Resources
RESOURCE_GROUP=Crazi-Co
LOCATION=canadacentral
ACR_NAME=crazicoregistry
APP_NAME=crazi-co
ENV_NAM=crazi-co-env
WEBAPP_PLAN=crazi-co-plan
WEBAPP_SKU=B1

# Application Version
VERSION=1.0.0

# Container Registry
REGISTRY_TYPE=dockerhub
DOCKERHUB_USERNAME=your-dockerhub-username
DOCKERHUB_PASSWORD=your-dockerhub-password

# Application Configuration
ENVIRONMENT=production
RATE_LIMIT=100

# Stripe Configuration
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PRICE_ID=your-stripe-price-id
CLIENT_URL=https://your-client-url.com
STRIPE_RETURN_URL=https://your-client-url.com/return

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://your-app-url.com/auth/google/callback
```

### Getting Your Database Connection String

For Azure Database for PostgreSQL:

```bash
# Format:
DATABASE_DSN=postgresql://username:password@servername.postgres.database.azure.com:5432/database?sslmode=require
```

---

## Troubleshooting

### Common Issues

#### Azure CLI not found
```bash
# Install
brew install azure-cli

# Verify
az --version
```

#### Container won't start
```bash
# View logs
make docker-logs

# Or check status
make docker-status

# Try restart
make docker-restart
```

#### Build failing
```bash
# Check if ACR exists
az acr show --name crazicoregistry --resource-group Crazi-Co

# Rebuild with Make
make docker-build
```

#### Environment variables not set
```bash
# Make sure .env file exists in project root
cat .env

# Make automatically loads .env when using make commands
```

#### Provider registration errors
```bash
# Register manually
az provider register -n Microsoft.App --wait
az provider register -n Microsoft.OperationalInsights --wait

# Check status
az provider show -n Microsoft.App --query "registrationState"
```

#### "Resource group not found"
```bash
# Create it
az group create --name Crazi Co --location canadacentral

# Or use Make
make setup
```

### View Detailed Logs

```bash
# Container Apps logs
make docker-logs

# Follow in real-time
make docker-logs-follow

# Azure deployment logs
az containerapp revision list \
  --name crazi-co \
  --resource-group Crazi Co \
  --output table
```

### Health Check Failing

```bash
# Test health endpoint
curl https://YOUR_APP_URL/api/v1/health

# Should return:
# {"status":"healthy","service":"crazi-co"}

# Check app is running
make docker-status
```

---

## Cost Estimation

### Monthly Costs (Approximate)

| Resource | Tier | Est. Cost |
|----------|------|-----------|
| **Container Registry** | Docker Hub/GitHub (FREE) or ACR Basic (~$5/month) | **$0** or ~$5/month |
| **Container Apps** | Consumption (1 replica, always on) | ~$15-25/month |
| **Log Analytics Workspace** | Pay-as-you-go | ~$2-5/month |
| **Total** | | **~$17-30/month** (with free registry) or **~$22-35/month** (with ACR) |

**💡 Cost Savings:** Use Docker Hub or GitHub Container Registry to save ~$5/month!

### Cost Optimization Tips

1. **Use free registries**: Docker Hub or GitHub Container Registry (saves ~$5/month)
2. **Use auto-scaling**: Set `MIN_REPLICAS=0` to scale to zero when idle
2. **Review logs retention**: Adjust Log Analytics retention period
3. **Use consumption plan**: Only pay for actual CPU/memory usage

---

## Advanced Topics

### GitHub Actions Auto-Deployment

The project includes a GitHub Actions workflow for automatic deployment on push.

**Setup:**

1. Ensure `.github/workflows/deploy-container-apps.yml` exists
2. Your GitHub Actions will use the same ACR
3. Push to main branch triggers automatic redeploy and deployment

**Workflow:**
```yaml
git add .
git commit -m "Update app"
git push origin main
# GitHub Actions automatically builds and deploys!
```

### Custom Domain Setup

```bash
# Add custom domain
az containerapp hostname add \
  --name crazi-co \
  --resource-group Crazi Co \
  --hostname api.yourdomain.com

# Get certificate validation info
az containerapp hostname list \
  --name crazi-co \
  --resource-group Crazi-Co
```

### Environment Variables Update

```bash
# Update environment variables
az containerapp update \
  --name crazi-co \
  --resource-group Crazi Co \
  --set-env-vars \
    API_BASE=/api/v2 \
    NEW_VAR=value
```

### Monitoring with Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app crazi-co-insights \
  --location canadacentral \
  --resource-group Crazi-Co

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app crazi-co-insights \
  --resource-group Crazi Co \
  --query instrumentationKey -o tsv)

# Add to your app
az containerapp update \
  --name crazi-co \
  --resource-group Crazi Co \
  --set-env-vars \
    APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

### Database Connection from Container Apps

Your app automatically connects using the `DATABASE_DSN` secret. To update:

```bash
# Update database connection
az containerapp secret set \
  --name crazi-co \
  --resource-group Crazi Co \
  --secrets database-dsn="new-connection-string"

# Restart app
make docker-restart
```

---

## Deployment Timeline

| Task | Time | Note |
|------|------|------|
| Install Azure CLI | 2 min | One-time setup |
| Azure login | 1 min | Browser authentication |
| Create resource group | 1 min | One-time setup |
| Create ACR (if using) | 2 min | One-time setup, skip if using Docker Hub/GitHub |
| First image build | 5-15 min* | Docker Hub/GitHub: 5-10 min, ACR: 10-15 min |
| Create Container Environment | 3 min | One-time setup |
| Deploy app | 3-5 min | |
| **Total First Deploy** | **~15-25 min*** | *Faster with Docker Hub/GitHub |
| **Subsequent Updates** | **~5-8 min** | Just redeploy + update |

---

## Key Benefits

✅ **Free registry options** - Use Docker Hub or GitHub Container Registry (no Azure costs)  
✅ **Fast deployments** - 5-8 minutes after first build  
✅ **Auto-scaling** - Scale from 0 to many instances  
✅ **Pay-per-use** - Only pay when container runs  
✅ **Built-in HTTPS** - Free SSL certificates  
✅ **Simple commands** - Use `make docker-deploy`, `make docker-redeploy`, etc.  
✅ **Health monitoring** - Automatic health checks  
✅ **Flexible registries** - Choose Docker Hub, GitHub, or Azure Container Registry  
✅ **Easy rollback** - Revision-based deployments  

---

## Quick Reference

### Most Used Commands

```bash
# Deploy for first time
make deploy

# Update after code changes
make docker-redeploy

# View logs
make docker-logs

# Get app URL
make docker-url

# Check status
make docker-status

# Restart app
make docker-restart
```

### Environment File Example

```bash
# Azure Configuration
RESOURCE_GROUP=Crazi-Co
LOCATION=canadacentral
ACR_NAME=crazicoregistry
APP_NAME=crazi-co
ENV_NAME=crazi-co-env

# Application Configuration
VERSION=1.0.0
API_BASE=/api/v1
API_PORT=5000
DATABASE_DSN=postgresql://user:pass@host.postgres.database.azure.com:5432/db?sslmode=require
```

---

## Support

- **GitHub Issues**: Report bugs or request features
- **Azure Documentation**: https://learn.microsoft.com/azure/container-apps/
- **Flask Documentation**: https://flask.palletsprojects.com/

## Next Steps

1. ✅ Deploy your app: `make deploy`
2. ✅ Test health endpoint: `curl https://YOUR_URL/api/v1/health`
3. ✅ Set up custom domain (optional)
4. ✅ Configure auto-scaling rules
5. ✅ Enable Application Insights monitoring
6. ✅ Set up GitHub Actions for CI/CD

**Happy Deploying! 🚀**
