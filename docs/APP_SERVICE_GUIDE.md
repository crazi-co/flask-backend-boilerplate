# Crazi Co - Azure App Service Deployment Guide

**Deploy to Azure App Service for ~$13/month** 💰 (vs $76/month with Container Apps)

---

## 🐳 Deployment Methods

This guide supports **two deployment methods** for Azure App Service:

### 1. Docker Container Deployment (Recommended) 🐳

**Best for:** Production, consistent environments, faster subsequent deployments

- ✅ Supports multiple container registries (ACR, Docker Hub, GitHub Container Registry)
- ✅ **Free options available** (Docker Hub, GitHub Container Registry)
- ✅ Consistent environment across deployments
- ✅ Faster updates (cached layers)
- ✅ Better for CI/CD pipelines

**Registry Options:**
- **Docker Hub** (FREE) - Default, no Azure costs
- **GitHub Container Registry** (FREE) - Integrated with GitHub
- **Azure Container Registry** (ACR) - Paid, but integrated with Azure

**Commands:**
```bash
make setup      # Creates App Service Plan (ACR only if using ACR)
make deploy     # Builds Docker image and deploys
make redeploy   # Rebuilds and redeploys
```

### 2. Source Code Deployment 📦

**Best for:** Quick testing, development, simpler setup

- ✅ No Docker required
- ✅ Builds directly from source code
- ✅ Uses Oryx build system
- ✅ Automatic dependency installation

**Commands:**
```bash
make setup          # Creates App Service Plan (no ACR)
make deploy-source  # Deploys from source code
make redeploy-source # Redeploys from source
```

**This guide focuses on Docker Container Deployment as the primary method.**

---

## Why App Service?

| Feature | App Service | Container Apps |
|---------|------------|----------------|
| **Cost** | ✅ **$13/month** (B1 tier) | ❌ $76/month |
| **Use Case** | ✅ Single web apps | Microservices |
| **Complexity** | ✅ Simple | Complex |
| **Setup Time** | ✅ 5 minutes | 20 minutes |
| **Auto-scaling** | Basic | Advanced |

**Perfect for:** Flask/Django apps, REST APIs, single-service applications

---

## ⚡ Quick Start (5 minutes)

### Prerequisites

1. **Azure CLI installed**:
   ```bash
   make install
   ```

2. **Login to Azure**:
   ```bash
   make login
   ```

3. **Create `.env` file** with your configuration (see below)

### Deploy in 3 Steps (Docker Container Method - Recommended)

**First, configure your registry in `.env`:**

For **Azure Container Registry** (ACR - Recommended, Default):
```bash
REGISTRY_TYPE=acr
ACR_NAME=crazicoregistry
```
✅ **Benefits:** No architecture issues, builds in Azure cloud, better integration

For **Docker Hub** (FREE):
```bash
REGISTRY_TYPE=dockerhub
DOCKERHUB_USERNAME=your-dockerhub-username
DOCKERHUB_PASSWORD=your-dockerhub-password
```

For **GitHub Container Registry** (FREE):
```bash
REGISTRY_TYPE=ghcr
GHCR_USERNAME=your-github-username
GHCR_REPO=crazi-co
GHCR_TOKEN=your-github-personal-access-token  # Needs package:write permission
```

**Then deploy:**
```bash
# 1. Create resource group and App Service Plan
#    (ACR created automatically only if REGISTRY_TYPE=acr)
make setup

# 2. Build Docker image and deploy (includes env vars)
make deploy
```

**Done!** Your app is live at `https://crazi-co.azurewebsites.net` 🎉

### Alternative: Deploy from Source Code

If you prefer to deploy from source code instead of Docker:

```bash
# 1. Create resource group and App Service Plan
make setup

# 2. Deploy from source code
make deploy-source
```

---

## 📋 Environment Variables

Create a `.env` file in your project root. See `.env.example` for a complete template.

### Required Configuration

```bash
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
# Options: acr, dockerhub, ghcr (default: acr)
REGISTRY_TYPE=acr

# For Docker Hub (FREE)
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
```

**Note:** Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
# Then edit .env with your actual values
```

---

## 🎯 Common Workflows

### First-Time Deployment (Docker Container)

```bash
# 1. Install and login
make install
make login

# 2. Create infrastructure (creates ACR, resource group, App Service Plan)
make setup

# 3. Build Docker image and deploy (automatically includes env vars)
make deploy

# 4. Your URL will be shown automatically!
```

**What happens:**
- ✅ Creates App Service Plan (ACR only if `REGISTRY_TYPE=acr`)
- ✅ Builds Docker image (locally for Docker Hub/GitHub, or in Azure Cloud for ACR)
- ✅ Pushes image to your chosen registry
- ✅ Configures App Service to use Docker container
- ✅ Deploys all environment variables
- ✅ App starts automatically

### Update Code (Docker Container)

```bash
# When you change your Flask app code
make redeploy
```

This will:
- ✅ Prompt for new version (or keep current)
- ✅ Rebuild Docker image locally (Docker Hub/GitHub) or in Azure Cloud (ACR)
- ✅ Push image to your registry
- ✅ Update App Service with new image
- ✅ Restart the app

### Alternative: Source Code Deployment

If you prefer deploying from source code:

```bash
# First-time deployment
make deploy-source

# Update code
make redeploy-source
```

**Source code deployment:**
- ✅ Packages your code as a zip file
- ✅ Uploads to App Service
- ✅ Builds using Oryx build system
- ✅ Installs dependencies automatically

### Update Environment Variables Only

```bash
# When you only change .env file
make deploy-env-vars
```

### Check Status

```bash
make status    # View app state
make logs      # View recent logs
make url       # Get app URL
```

---

## 📊 Available Commands

### Essential Commands (Docker Container Deployment)

| Command | Description | Time |
|---------|-------------|------|
| `make help` | Show all commands | instant |
| `make install` | Install Azure CLI | 2 min |
| `make login` | Login to Azure | 1 min |
| `make setup` | Create resource group & plan (ACR only if using ACR) | 3 min |
| `make build-docker` | Build and push Docker image to registry | 5-15 min* |
| `make deploy` | Build Docker image and deploy web app + env vars (prompts for version) | 10-20 min* |
| `make redeploy` | Rebuild Docker image and update app (prompts for version) | 5-15 min* |

\* *Times vary: Docker Hub/GitHub (5-10 min), ACR (10-15 min)*
| `make deploy-env-vars` | Update environment variables only | 30 sec |
| `make url` | Get app URL | instant |

### Alternative: Source Code Deployment Commands

| Command | Description | Time |
|---------|-------------|------|
| `make deploy-source` | Deploy from source code (no Docker) | 5 min |
| `make redeploy-source` | Redeploy from source code | 3 min |

### Monitoring & Management

| Command | Description |
|---------|-------------|
| `make logs` | View app logs in real-time |
| `make status` | Show app status |
| `make restart` | Restart the app |

### Cleanup

| Command | Description |
|---------|-------------|
| `make clean` | Delete web app only |
| `make clean-all` | Delete everything (DANGEROUS!) |

---

## 💰 Pricing Tiers

Choose your tier by setting `WEBAPP_SKU` in `.env`:

| Tier | SKU | vCPU | Memory | Cost/month | Best For |
|------|-----|------|--------|------------|----------|
| **Free** | F1 | Shared | 1 GB | **$0** | Testing only (60min/day limit) |
| **Basic B1** | B1 | 1 | 1.75 GB | **~$13** | ✅ **Development & small apps** |
| **Basic B2** | B2 | 2 | 3.5 GB | **~$26** | Medium traffic |
| **Standard S1** | S1 | 1 | 1.75 GB | **~$69** | Production (auto-scaling) |
| **Premium P1v2** | P1v2 | 1 | 3.5 GB | **~$95** | High performance |

**Recommendation:** Start with **B1** ($13/month). Upgrade to S1 if you need:
- Auto-scaling
- Custom domains with SSL
- Deployment slots (staging/production)

### Change Tier

```bash
# In .env file, change:
WEBAPP_SKU=B2  # or S1, P1v2, etc.

# Then run:
make setup
```

---

## 🔄 Version Management

Every time you run `make redeploy`, you'll be prompted to update your app version:

```bash
📌 Current Version: 1.0.0
Enter new version (or press Enter to keep current): 1.1.0
✅ Version updated to 1.1.0 in .env
```

- **Keep same version**: Just press Enter
- **Update version**: Type new version (e.g., `1.1.0`, `2.0.0`)
- The version is automatically saved in `.env` and deployed to Azure
- Access in your Flask app: `os.getenv("VERSION")`

You can also manually update version without deploying:
```bash
make update-version
```

---

## 🚀 Advanced Features

### Enable Continuous Deployment from GitHub

```bash
# Link your GitHub repo
az webapp deployment source config \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --repo-url https://github.com/youruser/yourrepo \
  --branch main \
  --manual-integration
```

### Enable Application Insights (Monitoring)

```bash
# Enable App Insights
az webapp log config \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --application-logging filesystem \
  --level information
```

### Add Custom Domain

```bash
# 1. Add custom domain
az webapp config hostname add \
  --webapp-name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --hostname yourdomain.com

# 2. Enable HTTPS
az webapp config ssl bind \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --certificate-thumbprint YOUR_CERT_THUMBPRINT \
  --ssl-type SNI
```

### Scale Out (Add More Instances)

```bash
# Scale to 3 instances (requires Standard tier or higher)
az appservice plan update \
  --name $WEBAPP_PLAN \
  --resource-group $RESOURCE_GROUP \
  --number-of-workers 3
```

---

## 🐛 Troubleshooting

### App Not Starting

```bash
# Check logs
make logs

# Common issues:
# 1. Missing environment variables
# 2. Wrong startup command
# 3. Port mismatch (App Service uses 5000)
# 4. Docker image not found (check ACR)
```

### Docker Container Issues

**For Azure Container Registry (ACR):**
```bash
# Check if ACR exists
az acr list --resource-group $RESOURCE_GROUP

# Check if image exists
az acr repository show-tags --name $ACR_NAME --repository $APP_NAME
```

**For Docker Hub:**
```bash
# Check if image exists (replace with your username)
docker pull your-username/crazi-co:latest

# Or check on Docker Hub website
# https://hub.docker.com/r/your-username/crazi-co
```

**For GitHub Container Registry:**
```bash
# Check if image exists (replace with your username)
docker pull ghcr.io/your-username/crazi-co:latest

# Or check on GitHub Packages
# https://github.com/your-username?tab=packages
```

**View container logs:**
```bash
make logs

# Restart the app
make restart
```

### Container Registry Authentication

**If you see authentication errors, verify your registry credentials:**

**For Azure Container Registry (ACR):**
```bash
# Verify ACR credentials
az acr credential show --name $ACR_NAME

# Re-authenticate App Service
az webapp config container set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --docker-registry-server-url https://$ACR_NAME.azurecr.io \
  --docker-registry-server-user $(az acr credential show --name $ACR_NAME --query username -o tsv) \
  --docker-registry-server-password $(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
```

**For Docker Hub:**
```bash
# Test login locally
docker login -u $DOCKERHUB_USERNAME

# Re-authenticate App Service (run make deploy-env-vars to update)
make deploy-env-vars
```

**For GitHub Container Registry:**
```bash
# Test login locally
echo $GHCR_TOKEN | docker login ghcr.io -u $GHCR_USERNAME --password-stdin

# Re-authenticate App Service (run make deploy-env-vars to update)
make deploy-env-vars
```

### "Application Error" Page

```bash
# Enable detailed error messages
az webapp config set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "gunicorn --bind=0.0.0.0:5000 --timeout=900 --log-level debug flask_app:app"

# Then check logs
make logs
```

### Environment Variables Not Loading

```bash
# Verify they're set
az webapp config appsettings list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP

# If missing, run:
make deploy-env-vars
```

### Slow Deployment

**Docker Container Deployment:**
- **Docker Hub/GitHub:** First build: 5-10 minutes (local build + push)
- **ACR:** First build: 10-15 minutes (building image in Azure Cloud)
- Subsequent builds: 3-8 minutes (cached layers)
- **Speed up:** Use multi-stage builds, minimize dependencies

**Source Code Deployment:**
- First deploy: 5-10 minutes (Oryx build system installing packages)
- **Speed up:** Use a `requirements.txt` with pinned versions (no version resolution needed)

---

## 📈 Monitoring & Logs

### View Real-Time Logs

```bash
make logs
# Or directly:
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP
```

### View Metrics in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your resource group → Your app
3. Click "Metrics" to see:
   - Response time
   - HTTP requests
   - CPU/Memory usage
   - Errors

### Set Up Alerts

```bash
# Alert if app is down
az monitor metrics alert create \
  --name "App Down Alert" \
  --resource-group $RESOURCE_GROUP \
  --scopes $(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query id -o tsv) \
  --condition "avg Http5xx > 5" \
  --window-size 5m \
  --evaluation-frequency 1m
```

---

## 🔒 Security Best Practices

### 1. Use Managed Identity (No Passwords!)

```bash
# Enable system-assigned managed identity
az webapp identity assign \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP
```

### 2. Store Secrets in Azure Key Vault

```bash
# Create Key Vault
az keyvault create \
  --name "crazi-co-vault" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Store secret
az keyvault secret set \
  --vault-name "crazi-co-vault" \
  --name "DatabasePassword" \
  --value "your-secure-password"

# Reference in app settings
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings DATABASE_DSN="@Microsoft.KeyVault(SecretUri=https://crazi-co-vault.vault.azure.net/secrets/DatabasePassword/)"
```

### 3. Restrict Network Access

```bash
# Allow only specific IPs
az webapp config access-restriction add \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --rule-name "Office IP" \
  --action Allow \
  --ip-address 203.0.113.0/24 \
  --priority 100
```

---

## 🐳 Docker Container Configuration

### Container Details

When deploying with Docker containers, your configuration depends on your registry:

**Common Settings:**
- **Port:** `5000`
- **Startup Command:** `gunicorn --bind=0.0.0.0:$PORT --timeout=600 --workers=4 --access-logfile - --error-logfile - flask_app:app`

**Registry-Specific Image Names:**
- **Docker Hub:** `your-username/crazi-co:latest`
- **GitHub Container Registry:** `ghcr.io/your-username/crazi-co:latest`
- **Azure Container Registry:** `crazicoregistry.azurecr.io/crazi-co:latest`

### View Container Information

```bash
# View container configuration
az webapp config container show --name $APP_NAME --resource-group $RESOURCE_GROUP

# For ACR only - List all images
az acr repository list --name $ACR_NAME

# For ACR only - View image tags
az acr repository show-tags --name $ACR_NAME --repository $APP_NAME
```

### Manual Docker Build (Local)

**For Docker Hub:**
```bash
# Login to Docker Hub
docker login -u $DOCKERHUB_USERNAME

# Build and push
docker build -t $DOCKERHUB_USERNAME/$APP_NAME:latest .
docker push $DOCKERHUB_USERNAME/$APP_NAME:latest

# Update App Service
make deploy-env-vars
```

**For GitHub Container Registry:**
```bash
# Login to GitHub Container Registry
echo $GHCR_TOKEN | docker login ghcr.io -u $GHCR_USERNAME --password-stdin

# Build and push
docker build -t ghcr.io/$GHCR_USERNAME/$GHCR_REPO:latest .
docker push ghcr.io/$GHCR_USERNAME/$GHCR_REPO:latest

# Update App Service
make deploy-env-vars
```

**For Azure Container Registry:**
```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build and push
docker build -t $ACR_NAME.azurecr.io/$APP_NAME:latest .
docker push $ACR_NAME.azurecr.io/$APP_NAME:latest

# Update App Service
make deploy-env-vars
```

## 🔄 Migration from Container Apps

If you were previously using Container Apps:

### 1. Delete Container Apps Resources

```bash
make docker-clean-all
```

This will delete:
- ✅ Container Apps environment
- ✅ Container Registry (ACR) - **Note:** Only needed if using ACR
- ✅ All images
- ✅ Resource group

### 2. Deploy to App Service (Docker Method)

**Option A: Using Free Registry (Docker Hub or GitHub)**
```bash
make install
make login
# Configure .env with REGISTRY_TYPE=dockerhub or REGISTRY_TYPE=ghcr
make setup  # Creates App Service Plan (no ACR needed)
make deploy # Builds locally and deploys Docker container
```

**Option B: Using Azure Container Registry**
```bash
make install
make login
# Configure .env with REGISTRY_TYPE=acr
make setup  # Creates ACR + App Service Plan
make deploy # Builds in Azure Cloud and deploys Docker container
```

### 3. Update Your DNS (if using custom domain)

Point your domain from:
```
old: crazi-co.agreeabledune-939d87ff.canadacentral.azurecontainerapps.io
new: crazi-co.azurewebsites.net
```

---

## 📚 Additional Resources

- [Azure App Service Documentation](https://learn.microsoft.com/azure/app-service/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/latest/deploying/)
- [Azure CLI Reference](https://learn.microsoft.com/cli/azure/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)

---

## 💡 Tips & Tricks

### 1. Speed Up Docker Builds

```bash
# Use ACR build cache
az acr build \
  --registry $ACR_NAME \
  --image $APP_NAME:latest \
  --resource-group $RESOURCE_GROUP \
  --file Dockerfile \
  --no-logs \
  .

# Build with specific platform (faster)
az acr build \
  --registry $ACR_NAME \
  --image $APP_NAME:latest \
  --platform linux/amd64 \
  .
```

### 2. Speed Up Source Code Deployments

```bash
# Use local cache for pip
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings ENABLE_ORYX_BUILD=true SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### 3. Zero-Downtime Deployment (Standard tier+)

```bash
# Create staging slot
az webapp deployment slot create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --slot staging

# Deploy to staging
az webapp deployment source config-zip \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --slot staging \
  --src deploy.zip

# Swap to production
az webapp deployment slot swap \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --slot staging
```

### 4. Monitor Costs

```bash
# View current costs
az consumption usage list \
  --start-date $(date -d "1 month ago" +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d)
```

### 5. Backup Your App

```bash
# Create backup
az webapp config backup create \
  --resource-group $RESOURCE_GROUP \
  --webapp-name $APP_NAME \
  --backup-name "manual-backup-$(date +%Y%m%d)" \
  --container-url "YOUR_STORAGE_ACCOUNT_URL"
```

---

## 🎉 Success!

Your Flask app is now running on Azure App Service!

**Next Steps:**
1. ✅ Test your app: `curl $(make url)/api/v1/health`
2. ✅ Verify Docker container is running: `make logs`
3. ✅ Set up monitoring and alerts
4. ✅ Configure custom domain (optional)
5. ✅ Enable auto-scaling (Standard tier+)
6. ✅ Set up CI/CD from GitHub

**Questions?** Check the [troubleshooting section](#-troubleshooting) or [Azure docs](https://learn.microsoft.com/azure/app-service/)

**Happy Deploying!** 🚀

---

## 📞 Support

- **Azure Portal**: https://portal.azure.com
- **Azure Support**: https://azure.microsoft.com/support/
- **GitHub Issues**: Report bugs or request features in your repo

