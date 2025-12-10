.PHONY: help install login update-version \
	docker-setup docker-build docker-create-env docker-deploy-app docker-deploy-env-vars docker-update docker-url docker-logs docker-logs-follow docker-status docker-list-images docker-restart docker-scale docker-clean docker-clean-all docker-deploy docker-redeploy \
	setup deploy deploy-env-vars redeploy url logs logs-follow status restart clean clean-all

# Load environment variables from .env file
include .env
export

# Default variables (override in .env)
# API Configuration
API_PORT ?= 5000
API_BASE ?= /api/v1

# Database Configuration
DATABASE_DSN ?=

# Authorization Configuration
AUTHORIZATION_HEADER ?= Authorization

# Role Configuration
PUBLIC_ROLE ?= public
PRIVATE_ROLE ?= private
USER_ROLE ?= user

# API Keys
PUBLIC_API_KEY ?=
PRIVATE_API_KEY ?=

# JWT/Authentication Configuration
JWT_SECRET_KEY ?=
JWT_ALGORITHM ?= HS256

# AWS SES Configuration
SES_AWS_ACCESS_KEY_ID ?=
SES_AWS_SECRET_ACCESS_KEY ?=
SES_AWS_REGION ?= us-east-1

# OTP Configuration
OTP_EXPIRY_IN_MINUTES ?= 10
SESSION_EXPIRY_IN_DAYS ?= 30

# Azure Resources Configuration
RESOURCE_GROUP ?= Crazi-Co
LOCATION ?= canadacentral
ACR_NAME ?= crazicoregistry
APP_NAME ?= crazi-co
ENV_NAM ?= crazi-co-env
ENV_NAME ?= $(ENV_NAM)  # Backward compatibility
WEBAPP_PLAN ?= $(APP_NAME)-plan
WEBAPP_SKU ?= B1

# Application Version
VERSION ?= 1.0.0

# Container Registry Configuration
# Options: acr, dockerhub, ghcr
REGISTRY_TYPE ?= acr
# For Docker Hub
DOCKERHUB_USERNAME ?= your-dockerhub-username
DOCKERHUB_PASSWORD ?=
# For GitHub Container Registry (not in .env.example but needed for deployment)
GHCR_USERNAME ?= your-github-username
GHCR_REPO ?= $(APP_NAME)
GHCR_TOKEN ?=

# Application Configuration
ENVIRONMENT ?=
RATE_LIMIT ?=

# Stripe Configuration
STRIPE_SECRET_KEY ?=
STRIPE_PRICE_ID ?=
CLIENT_URL ?=
STRIPE_RETURN_URL ?=

# Google OAuth Configuration
GOOGLE_CLIENT_ID ?=
GOOGLE_CLIENT_SECRET ?=
GOOGLE_REDIRECT_URI ?=

help: ## Show this help message
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║        Azure Deployment Commands (App Service)            ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🐳 Docker Container Deployment (Recommended):"
	@echo "   make setup          - Create resource group and App Service Plan"
	@echo "                        (ACR created only if REGISTRY_TYPE=acr)"
	@echo "   make build-docker   - Build and push Docker image to registry"
	@echo "                        (Supports: acr, dockerhub, ghcr)"
	@echo "   make deploy         - Deploy App Service from Docker container"
	@echo "   make redeploy       - Rebuild and redeploy Docker container"
	@echo ""
	@echo "📦 Registry Configuration (set in .env):"
	@echo "   REGISTRY_TYPE       - Options: acr, dockerhub, ghcr (default: acr)"
	@echo "   For Docker Hub:     DOCKERHUB_USERNAME, DOCKERHUB_PASSWORD"
	@echo "   For GitHub:         GHCR_USERNAME, GHCR_REPO, GHCR_TOKEN"
	@echo "   For ACR:            ACR_NAME (default: analytiqregistry)"
	@echo ""
	@echo "📦 Source Code Deployment (Alternative):"
	@echo "   make deploy-source  - Deploy App Service from source code"
	@echo "   make redeploy-source - Redeploy from source code"
	@echo ""
	@echo "🚀 App Service Commands (Recommended - \$$13/month):"
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v docker | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🐳 Container Apps Commands (Old - \$$76/month):"
	@grep -E '^docker-[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[90m%-25s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# Shared Commands (Used by both deployment methods)
# ============================================================================

install: ## Install Azure CLI
	@echo "Installing Azure CLI..."
	brew install azure-cli
	@echo "✅ Installation complete!"

login: ## Login to Azure
	@echo "Logging into Azure..."
	az login
	@echo "✅ Logged in!"

update-version: ## Update VERSION in .env file
	@echo "📌 Current Version: $(VERSION)"
	@read -p "Enter new version (or press Enter to keep current): " NEW_VERSION; \
	if [ -n "$$NEW_VERSION" ]; then \
		if grep -q "^VERSION=" .env 2>/dev/null; then \
			sed -i.bak "s/^VERSION=.*/VERSION=$$NEW_VERSION/" .env && rm -f .env.bak; \
		else \
			echo "VERSION=$$NEW_VERSION" >> .env; \
		fi; \
		echo "✅ Version updated to $$NEW_VERSION in .env"; \
	else \
		echo "✅ Keeping current version: $(VERSION)"; \
	fi

# ============================================================================
# App Service Commands (NEW - $13/month!)
# ============================================================================

setup: ## Create resource group, ACR (if using), and App Service Plan
	@echo "Creating resource group..."
	az group create --name $(RESOURCE_GROUP) --location $(LOCATION)
	@if [ "$(REGISTRY_TYPE)" = "acr" ]; then \
		echo "Creating Azure Container Registry..."; \
		az acr create \
			--resource-group $(RESOURCE_GROUP) \
			--name $(ACR_NAME) \
			--sku Basic \
			--location $(LOCATION) \
			--admin-enabled true; \
	fi
	@echo "Creating App Service Plan ($(WEBAPP_SKU))..."
	az appservice plan create \
		--name $(WEBAPP_PLAN) \
		--resource-group $(RESOURCE_GROUP) \
		--location $(LOCATION) \
		--is-linux \
		--sku $(WEBAPP_SKU)
	@echo "✅ Setup complete!"

build-docker: ## Build and push Docker image to registry
	@echo "Building Docker image for linux/amd64 (Azure App Service)..."
	@if [ "$(REGISTRY_TYPE)" = "acr" ]; then \
		echo "Building in Azure Container Registry (takes ~10-15 minutes)..."; \
		az acr build \
			--registry $(ACR_NAME) \
			--image $(APP_NAME):latest \
			--resource-group $(RESOURCE_GROUP) \
			--platform linux/amd64 \
			.; \
	elif [ "$(REGISTRY_TYPE)" = "dockerhub" ]; then \
		echo "Setting up Docker buildx for cross-platform builds..."; \
		docker buildx create --use --name multiplatform-builder 2>/dev/null || docker buildx use multiplatform-builder 2>/dev/null || true; \
		echo "Building locally and pushing to Docker Hub..."; \
		docker buildx build --platform linux/amd64 -t $(DOCKERHUB_USERNAME)/$(APP_NAME):latest --load .; \
		docker push $(DOCKERHUB_USERNAME)/$(APP_NAME):latest; \
	elif [ "$(REGISTRY_TYPE)" = "ghcr" ]; then \
		echo "Setting up Docker buildx for cross-platform builds..."; \
		docker buildx create --use --name multiplatform-builder 2>/dev/null || docker buildx use multiplatform-builder 2>/dev/null || true; \
		echo "Building locally and pushing to GitHub Container Registry..."; \
		docker buildx build --platform linux/amd64 -t ghcr.io/$(GHCR_USERNAME)/$(GHCR_REPO):latest --load .; \
		docker push ghcr.io/$(GHCR_USERNAME)/$(GHCR_REPO):latest; \
	else \
		echo "❌ Unknown registry type: $(REGISTRY_TYPE)"; \
		echo "Supported: acr, dockerhub, ghcr"; \
		exit 1; \
	fi
	@echo "✅ Build complete!"

deploy: update-version build-docker ## Deploy App Service from Docker container (includes env vars, prompts for version)
	@echo "Getting registry credentials..."
	@if [ "$(REGISTRY_TYPE)" = "acr" ]; then \
		REGISTRY_URL=$$(az acr show --name $(ACR_NAME) --query loginServer -o tsv); \
		REGISTRY_USER=$$(az acr credential show --name $(ACR_NAME) --query username -o tsv); \
		REGISTRY_PASS=$$(az acr credential show --name $(ACR_NAME) --query "passwords[0].value" -o tsv); \
		IMAGE_NAME="$$REGISTRY_URL/$(APP_NAME):latest"; \
	elif [ "$(REGISTRY_TYPE)" = "dockerhub" ]; then \
		REGISTRY_URL="docker.io"; \
		REGISTRY_USER="$(DOCKERHUB_USERNAME)"; \
		REGISTRY_PASS='$(DOCKERHUB_PASSWORD)'; \
		IMAGE_NAME="$(DOCKERHUB_USERNAME)/$(APP_NAME):latest"; \
	elif [ "$(REGISTRY_TYPE)" = "ghcr" ]; then \
		REGISTRY_URL="ghcr.io"; \
		REGISTRY_USER="$(GHCR_USERNAME)"; \
		REGISTRY_PASS='$(GHCR_TOKEN)'; \
		IMAGE_NAME="ghcr.io/$(GHCR_USERNAME)/$(GHCR_REPO):latest"; \
	else \
		echo "❌ Unknown registry type: $(REGISTRY_TYPE)"; \
		exit 1; \
	fi; \
	echo "Creating Web App with Docker container..."; \
	az webapp create \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--plan $(WEBAPP_PLAN) \
		--deployment-container-image-name $$IMAGE_NAME 2>/dev/null || \
	echo "Web App already exists, updating configuration..."; \
	echo "Configuring Web App to use Docker container..."; \
	az webapp config container set \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--container-image-name $$IMAGE_NAME \
		--container-registry-url https://$$REGISTRY_URL \
		--container-registry-user $$REGISTRY_USER \
		--container-registry-password $$REGISTRY_PASS
	@echo "Enabling container logging..."
	@az webapp log config \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--docker-container-logging filesystem \
		--level verbose 2>/dev/null || true
	@echo "Deploying environment variables..."
	@make deploy-env-vars
	@echo "✅ Deployment complete!"
	@echo ""
	@echo "📋 To view container logs, run: make logs"
	@make url

deploy-source: update-version ## Deploy App Service from source code (alternative method)
	@echo "Creating Web App with Python runtime..."
	@az webapp create \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--plan $(WEBAPP_PLAN) \
		--runtime "PYTHON|3.11" 2>/dev/null || \
	echo "Web App already exists, updating configuration..."
	@echo "Configuring Web App..."
	@az webapp config set \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--startup-file "gunicorn --bind=0.0.0.0:5000 --timeout=900 flask_app:app"
	@echo "Enabling build during deployment..."
	@az webapp config appsettings set \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
	@echo "Deploying code..."
	@zip -r deploy.zip . -x "*.git*" "*__pycache__*" "*.pyc" "*venv*" "*antenv*" "*.env" "deploy.zip" "*.zip" 2>/dev/null || true
	@az webapp deployment source config-zip \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--src deploy.zip
	@rm -f deploy.zip
	@echo "Deploying environment variables..."
	@make deploy-env-vars
	@echo "✅ Deployment complete!"
	@make url

deploy-env-vars: ## Deploy/update ALL environment variables from .env
	@echo "Deploying environment variables and secrets..."
	@echo "Getting registry credentials..."
	@if [ "$(REGISTRY_TYPE)" = "acr" ]; then \
		REGISTRY_URL=$$(az acr show --name $(ACR_NAME) --query loginServer -o tsv); \
		REGISTRY_USER=$$(az acr credential show --name $(ACR_NAME) --query username -o tsv); \
		REGISTRY_PASS=$$(az acr credential show --name $(ACR_NAME) --query "passwords[0].value" -o tsv); \
		IMAGE_NAME="$$REGISTRY_URL/$(APP_NAME):latest"; \
	elif [ "$(REGISTRY_TYPE)" = "dockerhub" ]; then \
		REGISTRY_URL="docker.io"; \
		REGISTRY_USER="$(DOCKERHUB_USERNAME)"; \
		REGISTRY_PASS='$(DOCKERHUB_PASSWORD)'; \
		IMAGE_NAME="$(DOCKERHUB_USERNAME)/$(APP_NAME):latest"; \
	elif [ "$(REGISTRY_TYPE)" = "ghcr" ]; then \
		REGISTRY_URL="ghcr.io"; \
		REGISTRY_USER="$(GHCR_USERNAME)"; \
		REGISTRY_PASS='$(GHCR_TOKEN)'; \
		IMAGE_NAME="ghcr.io/$(GHCR_USERNAME)/$(GHCR_REPO):latest"; \
	else \
		echo "❌ Unknown registry type: $(REGISTRY_TYPE)"; \
		exit 1; \
	fi; \
	echo "Updating image and environment variables..."; \
	az webapp config container set \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--container-image-name $$IMAGE_NAME \
		--container-registry-url https://$$REGISTRY_URL \
		--container-registry-user $$REGISTRY_USER \
		--container-registry-password $$REGISTRY_PASS 2>/dev/null || true
	@echo "Setting startup command..."
	@az webapp config set \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--startup-file "gunicorn --bind=0.0.0.0:5000 --timeout=600 --workers=4 --access-logfile - --error-logfile - flask_app:app" 2>/dev/null || true
	@echo "Setting environment variables..."
	@az webapp config appsettings set \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--settings \
			VERSION="$${VERSION:-1.0.0}" \
			API_PORT=$${API_PORT:-5000} \
			WEBSITES_PORT=$${API_PORT:-5000} \
			PORT=$${API_PORT:-5000} \
			API_BASE="$${API_BASE:-/api/v1}" \
			ENVIRONMENT="$${ENVIRONMENT:-}" \
			RATE_LIMIT="$${RATE_LIMIT:-}" \
			DATABASE_DSN="$${DATABASE_DSN:-}" \
			AUTHORIZATION_HEADER="$${AUTHORIZATION_HEADER:-Authorization}" \
			PUBLIC_ROLE="$${PUBLIC_ROLE:-public}" \
			PRIVATE_ROLE="$${PRIVATE_ROLE:-private}" \
			USER_ROLE="$${USER_ROLE:-user}" \
			API_KEY_ROLE="$${API_KEY_ROLE:-api_key}" \
			PUBLIC_API_KEY="$${PUBLIC_API_KEY:-}" \
			PRIVATE_API_KEY="$${PRIVATE_API_KEY:-}" \
			JWT_SECRET_KEY="$${JWT_SECRET_KEY:-}" \
			JWT_ALGORITHM="$${JWT_ALGORITHM:-HS256}" \
			SES_AWS_ACCESS_KEY_ID="$${SES_AWS_ACCESS_KEY_ID:-}" \
			SES_AWS_SECRET_ACCESS_KEY="$${SES_AWS_SECRET_ACCESS_KEY:-}" \
			SES_AWS_REGION="$${SES_AWS_REGION:-us-east-1}" \
			OTP_EXPIRY_IN_MINUTES="$${OTP_EXPIRY_IN_MINUTES:-10}" \
			SESSION_EXPIRY_IN_DAYS="$${SESSION_EXPIRY_IN_DAYS:-30}" \
			OPENAI_API_KEY="$${OPENAI_API_KEY:-}" \
			AZURE_OPENAI_API_KEY="$${AZURE_OPENAI_API_KEY:-}" \
			AZURE_OPENAI_API_VERSION="$${AZURE_OPENAI_API_VERSION:-2024-02-15-preview}" \
			AZURE_OPENAI_ENDPOINT="$${AZURE_OPENAI_ENDPOINT:-}" \
			AZURE_OPENAI_DEPLOYMENT_NAME="$${AZURE_OPENAI_DEPLOYMENT_NAME:-gpt-4}" \
			WHISPER_API_KEY="$${WHISPER_API_KEY:-}" \
			WHISPER_API_VERSION="$${WHISPER_API_VERSION:-}" \
			WHISPER_ENDPOINT="$${WHISPER_ENDPOINT:-}" \
			WHISPER_DEPLOYMENT_NAME="$${WHISPER_DEPLOYMENT_NAME:-}" \
			AZURE_CONTENT_UNDERSTANDING_ENDPOINT="$${AZURE_CONTENT_UNDERSTANDING_ENDPOINT:-}" \
			AZURE_CONTENT_UNDERSTANDING_KEY="$${AZURE_CONTENT_UNDERSTANDING_KEY:-}" \
			AZURE_CONTENT_UNDERSTANDING_VERSION="$${AZURE_CONTENT_UNDERSTANDING_VERSION:-}" \
			AZURE_CONTENT_UNDERSTANDING_ANALYSER_ID="$${AZURE_CONTENT_UNDERSTANDING_ANALYSER_ID:-}" \
			AZURE_CONTENT_UNDERSTANDING_4_1_MODEL="$(AZURE_CONTENT_UNDERSTANDING_4_1_MODEL)" \
			AZURE_CONTENT_UNDERSTANDING_4_1_MINI_MODEL="$(AZURE_CONTENT_UNDERSTANDING_4_1_MINI_MODEL)" \
			AZURE_CONTENT_UNDERSTANDING_TEXT_EMBEDDING_3_LARGE_MODEL="$${AZURE_CONTENT_UNDERSTANDING_TEXT_EMBEDDING_3_LARGE_MODEL:-}" \
			BRIGHTDATA_API_KEY="$${BRIGHTDATA_API_KEY:-}" \
			RAPIDAPI_KEY="$${RAPIDAPI_KEY:-}" \
			STRIPE_SECRET_KEY="$${STRIPE_SECRET_KEY:-}" \
			STRIPE_PRICE_ID="$${STRIPE_PRICE_ID:-}" \
			CLIENT_URL="$${CLIENT_URL:-}" \
			STRIPE_RETURN_URL="$${STRIPE_RETURN_URL:-}" \
			GOOGLE_CLIENT_ID="$${GOOGLE_CLIENT_ID:-}" \
			GOOGLE_CLIENT_SECRET="$${GOOGLE_CLIENT_SECRET:-}" \
			GOOGLE_REDIRECT_URI="$${GOOGLE_REDIRECT_URI:-}" \
			MAX_IMAGE_ATTACHMENT_SIZE="$${MAX_IMAGE_ATTACHMENT_SIZE:-}" \
			MAX_AUDIO_ATTACHMENT_SIZE="$${MAX_AUDIO_ATTACHMENT_SIZE:-}" \
			MAX_VIDEO_ATTACHMENT_SIZE="$${MAX_VIDEO_ATTACHMENT_SIZE:-}" \
			MAX_DOCUMENT_ATTACHMENT_SIZE="$${MAX_DOCUMENT_ATTACHMENT_SIZE:-}" \
			MAX_PDF_ATTACHMENT_SIZE="$${MAX_PDF_ATTACHMENT_SIZE:-$${MAX_DOCUMENT_ATTACHMENT_SIZE:-}}" \
			MAX_ATTACHMENTS="$${MAX_ATTACHMENTS:-}" \
			MAX_AUDIO_ATTACHMENT_DURATION="$${MAX_AUDIO_ATTACHMENT_DURATION:-}" \
			MAX_VIDEO_ATTACHMENT_DURATION="$${MAX_VIDEO_ATTACHMENT_DURATION:-}" \
			SUPPORTED_IMAGE_EXTENSIONS="$${SUPPORTED_IMAGE_EXTENSIONS:-}" \
			SUPPORTED_VIDEO_EXTENSIONS="$${SUPPORTED_VIDEO_EXTENSIONS:-}" \
			SUPPORTED_AUDIO_EXTENSIONS="$${SUPPORTED_AUDIO_EXTENSIONS:-}" \
			SUPPORTED_PDF_EXTENSIONS="$${SUPPORTED_PDF_EXTENSIONS:-}" \
		--output none 2>/dev/null || true
	@if [ "$(REGISTRY_TYPE)" = "acr" ]; then \
		REGISTRY_URL=$$(az acr show --name $(ACR_NAME) --query loginServer -o tsv); \
		REGISTRY_USER=$$(az acr credential show --name $(ACR_NAME) --query username -o tsv); \
		REGISTRY_PASS=$$(az acr credential show --name $(ACR_NAME) --query "passwords[0].value" -o tsv); \
		IMAGE_NAME="$$REGISTRY_URL/$(APP_NAME):latest"; \
		az webapp config appsettings set \
			--name $(APP_NAME) \
			--resource-group $(RESOURCE_GROUP) \
			--settings \
				DOCKER_REGISTRY_SERVER_URL="https://$$REGISTRY_URL" \
				DOCKER_REGISTRY_SERVER_USERNAME="$$REGISTRY_USER" \
				DOCKER_REGISTRY_SERVER_PASSWORD="$$REGISTRY_PASS" \
				DOCKER_CUSTOM_IMAGE_NAME="DOCKER|$$IMAGE_NAME" \
			--output none 2>/dev/null || true; \
	elif [ "$(REGISTRY_TYPE)" = "dockerhub" ]; then \
		IMAGE_NAME="$(DOCKERHUB_USERNAME)/$(APP_NAME):latest"; \
		az webapp config appsettings set \
			--name $(APP_NAME) \
			--resource-group $(RESOURCE_GROUP) \
			--settings \
				DOCKER_REGISTRY_SERVER_URL="https://docker.io" \
				DOCKER_REGISTRY_SERVER_USERNAME="$(DOCKERHUB_USERNAME)" \
				DOCKER_REGISTRY_SERVER_PASSWORD='$(DOCKERHUB_PASSWORD)' \
				DOCKER_CUSTOM_IMAGE_NAME="DOCKER|$$IMAGE_NAME" \
			--output none 2>/dev/null || true; \
	elif [ "$(REGISTRY_TYPE)" = "ghcr" ]; then \
		IMAGE_NAME="ghcr.io/$(GHCR_USERNAME)/$(GHCR_REPO):latest"; \
		az webapp config appsettings set \
			--name $(APP_NAME) \
			--resource-group $(RESOURCE_GROUP) \
			--settings \
				DOCKER_REGISTRY_SERVER_URL="https://ghcr.io" \
				DOCKER_REGISTRY_SERVER_USERNAME="$(GHCR_USERNAME)" \
				DOCKER_REGISTRY_SERVER_PASSWORD='$(GHCR_TOKEN)' \
				DOCKER_CUSTOM_IMAGE_NAME="DOCKER|$$IMAGE_NAME" \
			--output none 2>/dev/null || true; \
	fi
	@echo "✅ Deployment complete!"

redeploy: update-version build-docker ## Redeploy Docker container (rebuilds image and updates app, prompts for version)
	@echo "Updating image and environment variables..."
	@make deploy-env-vars
	@echo "Restarting Web App..."
	@az webapp restart --name $(APP_NAME) --resource-group $(RESOURCE_GROUP)
	@echo "✅ Redeployment complete!"
	@make url

redeploy-source: update-version ## Redeploy app from source code (alternative method, prompts for version)
	@echo "Redeploying from local code..."
	@cd .. && zip -r Analytiq/deploy.zip Analytiq -x "*.git*" "*__pycache__*" "*.pyc" "*venv*" "*antenv*" "*.env" 2>/dev/null || true
	@az webapp deployment source config-zip \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--src deploy.zip
	@rm -f deploy.zip
	@make deploy-env-vars
	@echo "✅ Redeployment complete!"

url: ## Get app URL
	@echo ""
	@echo "🚀 Your app URL:"
	@az webapp show \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--query defaultHostName -o tsv | awk '{print "https://" $$1}'
	@echo ""

logs: ## View app logs (last 100 lines)
	@echo "Enabling container logging..."
	@az webapp log config \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--docker-container-logging filesystem 2>/dev/null || true
	@echo "Viewing logs..."
	@az webapp log tail \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP)

logs-follow: ## Follow app logs in real-time
	@echo "Enabling container logging..."
	@az webapp log config \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--docker-container-logging filesystem 2>/dev/null || true
	@echo "Following logs..."
	@az webapp log tail \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--follow

logs-container: ## View container logs directly
	@az webapp log download \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--log-file container-logs.zip
	@echo "✅ Logs downloaded to container-logs.zip"

status: ## Show app status
	@echo "App Service Status:"
	@az webapp show \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--query "{Name:name, State:state, URL:defaultHostName}" \
		-o table

restart: ## Restart the app
	@echo "Restarting app..."
	@az webapp restart \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP)
	@echo "✅ Restart complete!"

clean: ## Delete web app (keeps plan and resource group)
	@echo "⚠️  This will delete the web app!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		az webapp delete \
			--name $(APP_NAME) \
			--resource-group $(RESOURCE_GROUP); \
		echo "✅ App deleted!"; \
	fi

clean-all: ## Delete everything (DANGEROUS!)
	@echo "⚠️  This will delete EVERYTHING (resource group, plan, app)!"
	@read -p "Are you ABSOLUTELY sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		az group delete \
			--name $(RESOURCE_GROUP) \
			--yes; \
		echo "✅ Everything deleted!"; \
	fi

# ============================================================================
# Container Apps Commands (OLD - Keep for reference/migration)
# ============================================================================

docker-setup: ## [DOCKER] Create resource group and ACR (if using ACR)
	@echo "Creating resource group..."
	az group create --name $(RESOURCE_GROUP) --location $(LOCATION)
	@echo "Registering resource providers..."
	az provider register -n Microsoft.App --wait
	az provider register -n Microsoft.OperationalInsights --wait
	@if [ "$(REGISTRY_TYPE)" = "acr" ]; then \
		echo "Creating Azure Container Registry..."; \
		az acr create \
			--resource-group $(RESOURCE_GROUP) \
			--name $(ACR_NAME) \
			--sku Basic \
			--location $(LOCATION) \
			--admin-enabled true; \
	fi
	@echo "✅ Setup complete!"

docker-build: ## [DOCKER] Build and push Docker image to registry
	@echo "Building Docker image for linux/amd64 (Azure App Service)..."
	@if [ "$(REGISTRY_TYPE)" = "acr" ]; then \
		echo "Building in Azure Container Registry (takes ~10-15 minutes)..."; \
		az acr build \
			--registry $(ACR_NAME) \
			--image $(APP_NAME):latest \
			--resource-group $(RESOURCE_GROUP) \
			--platform linux/amd64 \
			.; \
	elif [ "$(REGISTRY_TYPE)" = "dockerhub" ]; then \
		echo "Setting up Docker buildx for cross-platform builds..."; \
		docker buildx create --use --name multiplatform-builder 2>/dev/null || docker buildx use multiplatform-builder 2>/dev/null || true; \
		echo "Building locally and pushing to Docker Hub..."; \
		docker buildx build --platform linux/amd64 -t $(DOCKERHUB_USERNAME)/$(APP_NAME):latest --load .; \
		docker push $(DOCKERHUB_USERNAME)/$(APP_NAME):latest; \
	elif [ "$(REGISTRY_TYPE)" = "ghcr" ]; then \
		echo "Setting up Docker buildx for cross-platform builds..."; \
		docker buildx create --use --name multiplatform-builder 2>/dev/null || docker buildx use multiplatform-builder 2>/dev/null || true; \
		echo "Building locally and pushing to GitHub Container Registry..."; \
		docker buildx build --platform linux/amd64 -t ghcr.io/$(GHCR_USERNAME)/$(GHCR_REPO):latest --load .; \
		docker push ghcr.io/$(GHCR_USERNAME)/$(GHCR_REPO):latest; \
	else \
		echo "❌ Unknown registry type: $(REGISTRY_TYPE)"; \
		echo "Supported: acr, dockerhub, ghcr"; \
		exit 1; \
	fi
	@echo "✅ Build complete!"

docker-create-env: ## [DOCKER] Create Container Apps environment
	@echo "Creating Container Apps environment..."
	az containerapp env create \
		--name $(ENV_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--location $(LOCATION)
	@echo "✅ Environment created!"

docker-deploy-app: ## [DOCKER] Deploy container app (initial)
	@echo "Getting registry credentials..."
	@if [ "$(REGISTRY_TYPE)" = "acr" ]; then \
		REGISTRY_URL=$$(az acr show --name $(ACR_NAME) --query loginServer -o tsv); \
		REGISTRY_USER=$$(az acr credential show --name $(ACR_NAME) --query username -o tsv); \
		REGISTRY_PASS=$$(az acr credential show --name $(ACR_NAME) --query "passwords[0].value" -o tsv); \
		IMAGE_NAME="$$REGISTRY_URL/$(APP_NAME):latest"; \
	elif [ "$(REGISTRY_TYPE)" = "dockerhub" ]; then \
		REGISTRY_URL="docker.io"; \
		REGISTRY_USER="$(DOCKERHUB_USERNAME)"; \
		REGISTRY_PASS='$(DOCKERHUB_PASSWORD)'; \
		IMAGE_NAME="$(DOCKERHUB_USERNAME)/$(APP_NAME):latest"; \
	elif [ "$(REGISTRY_TYPE)" = "ghcr" ]; then \
		REGISTRY_URL="ghcr.io"; \
		REGISTRY_USER="$(GHCR_USERNAME)"; \
		REGISTRY_PASS='$(GHCR_TOKEN)'; \
		IMAGE_NAME="ghcr.io/$(GHCR_USERNAME)/$(GHCR_REPO):latest"; \
	else \
		echo "❌ Unknown registry type: $(REGISTRY_TYPE)"; \
		exit 1; \
	fi; \
	echo "Deploying container app..."; \
	az containerapp create \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--environment $(ENV_NAME) \
		--image $$IMAGE_NAME \
		--registry-server $$REGISTRY_URL \
		--registry-username $$REGISTRY_USER \
		--registry-password $$REGISTRY_PASS \
		--target-port 5000 \
		--ingress external \
		--cpu 1.0 \
		--memory 2.0Gi \
		--min-replicas 1 \
		--max-replicas 5 \
		--secrets database-dsn="$(DATABASE_DSN)" \
		--env-vars \
			VERSION="$(VERSION)" \
			DATABASE_DSN=secretref:database-dsn \
			API_BASE="$(API_BASE)" \
			API_PORT=5000
	@echo "✅ Deployment complete!"
	@make docker-url

docker-deploy-env-vars: ## [DOCKER] Deploy/update ALL environment variables
	@echo "Deploying environment variables and secrets..."
	@echo "Getting registry credentials..."
	@if [ "$(REGISTRY_TYPE)" = "acr" ]; then \
		REGISTRY_URL=$$(az acr show --name $(ACR_NAME) --query loginServer -o tsv); \
		IMAGE_NAME="$$REGISTRY_URL/$(APP_NAME):latest"; \
	elif [ "$(REGISTRY_TYPE)" = "dockerhub" ]; then \
		IMAGE_NAME="$(DOCKERHUB_USERNAME)/$(APP_NAME):latest"; \
	elif [ "$(REGISTRY_TYPE)" = "ghcr" ]; then \
		IMAGE_NAME="ghcr.io/$(GHCR_USERNAME)/$(GHCR_REPO):latest"; \
	else \
		echo "❌ Unknown registry type: $(REGISTRY_TYPE)"; \
		exit 1; \
	fi; \
	echo "Setting secrets (encrypted)..."; \
	az containerapp secret set \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--secrets \
			database-dsn="$${DATABASE_DSN:-}" \
			jwt-secret-key="$${JWT_SECRET_KEY:-}" \
			private-api-key="$${PRIVATE_API_KEY:-}" \
			public-api-key="$${PUBLIC_API_KEY:-}" \
			ses-aws-access-key-id="$${SES_AWS_ACCESS_KEY_ID:-}" \
			ses-aws-secret-access-key="$${SES_AWS_SECRET_ACCESS_KEY:-}" \
			azure-openai-api-key="$${AZURE_OPENAI_API_KEY:-}" \
			cdp-api-key-id="$${CDP_API_KEY_ID:-}" \
			cdp-api-key-secret="$${CDP_API_KEY_SECRET:-}" \
			payment-client-private-key="$${PAYMENT_CLIENT_PRIVATE_KEY:-}" \
			rapidapi-key="$${RAPIDAPI_KEY:-}" \
			brightdata-api-key="$${BRIGHTDATA_API_KEY:-}" \
			coingecko-api-key="$${COINGECKO_API_KEY:-}" 2>/dev/null || true; \
	echo "Updating image and environment variables..."; \
	az containerapp update \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--image $$IMAGE_NAME \
		--revision-suffix $$(date +%s) \
		--set-env-vars \
			"VERSION=$${VERSION:-1.0.0}" \
			"API_BASE=$${API_BASE:-/api/v1}" \
			"API_PORT=$${API_PORT:-5000}" \
			"DATABASE_DSN=secretref:database-dsn" \
			"JWT_SECRET_KEY=secretref:jwt-secret-key" \
			"JWT_ALGORITHM=$${JWT_ALGORITHM:-HS256}" \
			"SESSION_EXPIRY_IN_DAYS=$${SESSION_EXPIRY_IN_DAYS:-30}" \
			"USER_ROLE=$${USER_ROLE:-user}" \
			"API_KEY_ROLE=$${API_KEY_ROLE:-api_key}" \
			"PRIVATE_ROLE=$${PRIVATE_ROLE:-private}" \
			"PUBLIC_ROLE=$${PUBLIC_ROLE:-public}" \
			"AUTHORIZATION_HEADER=$${AUTHORIZATION_HEADER:-Authorization}" \
			"PRIVATE_API_KEY=secretref:private-api-key" \
			"PUBLIC_API_KEY=secretref:public-api-key" \
			"SES_AWS_REGION=$${SES_AWS_REGION:-us-east-1}" \
			"SES_AWS_ACCESS_KEY_ID=secretref:ses-aws-access-key-id" \
			"SES_AWS_SECRET_ACCESS_KEY=secretref:ses-aws-secret-access-key" \
			"AZURE_OPENAI_API_KEY=secretref:azure-openai-api-key" \
			"AZURE_OPENAI_API_VERSION=$${AZURE_OPENAI_API_VERSION:-2024-02-15-preview}" \
			"AZURE_OPENAI_ENDPOINT=$${AZURE_OPENAI_ENDPOINT:-}" \
			"AZURE_OPENAI_DEPLOYMENT_NAME=$${AZURE_OPENAI_DEPLOYMENT_NAME:-gpt-4}" \
			"CDP_API_KEY_ID=secretref:cdp-api-key-id" \
			"CDP_API_KEY_SECRET=secretref:cdp-api-key-secret" \
			"PAY_TO_ADDRESS=$${PAY_TO_ADDRESS:-}" \
			"PAYMENT_NETWORK=$${PAYMENT_NETWORK:-base-sepolia}" \
			"PAYMENT_CLIENT_PRIVATE_KEY=secretref:payment-client-private-key" \
			"RAPIDAPI_KEY=secretref:rapidapi-key" \
			"BRIGHTDATA_API_KEY=secretref:brightdata-api-key" \
			"COINGECKO_API_KEY=secretref:coingecko-api-key" \
			"OTP_EXPIRY_IN_MINUTES=$${OTP_EXPIRY_IN_MINUTES:-10}"
	@echo "✅ Deployment complete!"

docker-url: ## [DOCKER] Get container app URL
	@echo ""
	@echo "🚀 Your app URL:"
	@az containerapp show \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--query properties.configuration.ingress.fqdn -o tsv
	@echo ""

docker-logs: ## [DOCKER] View container app logs
	az containerapp logs show \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--tail 100

docker-logs-follow: ## [DOCKER] Follow container app logs
	az containerapp logs show \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--follow

docker-status: ## [DOCKER] Show container app status
	@echo "Container App Status:"
	@az containerapp show \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--query "{Name:name, Status:properties.provisioningState, URL:properties.configuration.ingress.fqdn}" \
		-o table

docker-list-images: ## [DOCKER] List all images in ACR
	@az acr repository list --name $(ACR_NAME) --output table

docker-restart: ## [DOCKER] Restart container app
	@echo "Restarting app..."
	az containerapp restart \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP)
	@echo "✅ Restart complete!"

docker-scale: ## [DOCKER] Scale app (usage: make docker-scale MIN=2 MAX=10)
	@echo "Scaling app..."
	az containerapp update \
		--name $(APP_NAME) \
		--resource-group $(RESOURCE_GROUP) \
		--min-replicas $(MIN) \
		--max-replicas $(MAX)
	@echo "✅ Scaled to $(MIN)-$(MAX) replicas!"

docker-clean: ## [DOCKER] Delete container app only
	@echo "⚠️  This will delete the container app!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		az containerapp delete \
			--name $(APP_NAME) \
			--resource-group $(RESOURCE_GROUP) \
			--yes; \
		echo "✅ App deleted!"; \
	fi

docker-clean-all: ## [DOCKER] Delete everything (ACR, Container Apps, etc.)
	@echo "⚠️  This will delete EVERYTHING (resource group, ACR, images, app)!"
	@read -p "Are you ABSOLUTELY sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		az group delete \
			--name $(RESOURCE_GROUP) \
			--yes; \
		echo "✅ Everything deleted!"; \
	fi

docker-deploy: update-version login docker-setup docker-build docker-create-env docker-deploy-app docker-deploy-env-vars ## [DOCKER] Complete Container Apps deployment
docker-redeploy: update-version docker-build docker-deploy-env-vars ## [DOCKER] Rebuild and redeploy Container Apps
