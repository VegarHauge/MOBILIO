# Project Report
This was a group project be me and two other students for the course DAT515 at UiS.
I was responsible for the Backend, recommendation engine, and some integration between frontend and backend.

## Project Overview

**Project Name**: Mobilio

[Design file can be found here](design.md)

**Group Members**:

- Vegar Kleiva Hauge, VegarHauge
- Matthias Starck, mstarckgh
- Fredrik Nilsen Låder, fredriklader

**Brief Description**:

Mobilio is a modern e-commerce platform for selling mobile phones and accessories. The application features a user-friendly React interface, secure JWT authentication, and Stripe payment integration. Admin users can manage product inventory, while customers can browse products with ML-powered recommendations, add items to their cart, and complete purchases securely. The platform is deployed on Google Kubernetes Engine (GKE) with comprehensive monitoring via Prometheus and Grafana.

## Architecture Overview

### High-Level Architecture

Below is the high-level architecture diagram for the application:

![High-Level Architecture](images/highlevel.png)

_Figure: High-level architecture showing client (browser/mobile), frontend, backend API, database, payment gateway (Stripe), and optional container/cloud deployment._

### Components

- **React Frontend**: UI, request data from the two web servers, and sends data to the E-Commerse backend service.
- **E-Commerse backend**: Serves all necessary endpoints for the webapp to work
- **S3 Bucket**: Object storage that stores all images.
- **Recomendation Service**: Gives recomendations based on one product, can give simillar products, or products often bought togheter with the product.
- **main db**: Where all the data is stored
- **analytic db**: Fetches necessary Data from main db, that the recomendation service trains on.

### Technologies Used

- **Frontend**: React 19, Material-UI, React Router, Axios
- **Backend**: Python FastAPI, SQLAlchemy, Pydantic
- **Databases**: MySQL 8 (Main + Analytics)
- **Cache**: Redis 7
- **ML/Recommendations**: scikit-learn, NumPy
- **Cloud Services**: AWS S3 (image storage), Google Cloud Platform (GKE)
- **Payment**: Stripe API
- **Monitoring**: Prometheus, Grafana
- **Container Orchestration**: Docker, Kubernetes (GKE)
- **Web Server**: Nginx (reverse proxy and ingress controller)

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows (with WSL2 recommended for Windows)
- **Minimum RAM**: 8GB (16GB recommended for running all services)
- **Storage**: 20GB free space (for Docker images, containers, and volumes)
- **Network**: Internet connection for pulling Docker images and external services (Stripe, S3)

### Required Software for Deployment

**For Docker Compose Deployment (Recommended):**

```bash
Docker Engine 20.10+
Docker Compose 2.0+
```

**For Kubernetes/GKE Deployment:**

```bash
kubectl (Kubernetes CLI)
gcloud CLI (for GKE)
Docker Engine 20.10+ (for building images)
```

**Optional (for development without Docker):**

```bash
Python 3.11+ (for backend development)
Node.js 18+ (for frontend development)
MySQL 8+ (for local database)
Redis 7+ (for caching)
```

### Application Dependencies (Handled by Docker)

These are installed automatically within Docker containers:

**Backend (FastAPI):**

- Python 3.11+
- FastAPI, SQLAlchemy, Pydantic
- PyMySQL, Redis client
- Stripe SDK, Boto3 (AWS S3)
- JWT libraries (PyJWT, passlib)
- Prometheus instrumentation
- See `backend/requirements.txt` for full list

**Frontend (React):**

- Node.js 18+
- React 19, Material-UI
- Axios, React Router
- See `frontend/package.json` for full list

**Recommendation Service:**

- Python 3.11+
- FastAPI, scikit-learn, NumPy
- PyMySQL
- See `recomendation/requirements.txt` for full list

**Infrastructure:**

- MySQL 8 (Main database)
- MySQL 8 (Analytics database)
- Redis 7 (Cache)
- Nginx (Reverse proxy)
- Prometheus (Metrics)
- Grafana (Visualization)

### External Service Accounts Required

- **Stripe Account**: For payment processing (test mode sufficient)
- **AWS Account**: For S3 bucket (free tier sufficient)
- **Google Cloud Account** (for GKE deployment): Free credits available for new accounts

## Build Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/dat515-2025/Group-7.git
cd Group-7/7Project
```

### 2. Install Dependencies

**Note**: If using Docker Compose (recommended), you can skip to section 3. Dependencies are only needed for local development without Docker.

**Backend Dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

**Recommendation Service Dependencies:**

```bash
cd recomendation
pip install -r requirements.txt
```

**Frontend Dependencies:**

```bash
cd frontend
npm install
```

### 3. Build the Application

**For Docker Compose Deployment (Recommended):**

Docker will automatically build all images when you run `docker-compose up`. No manual build needed.

### 4. Configuration

**Backend Configuration:**

```bash
cd backend
cp .env.example .env
```

Edit `.env` file with your credentials:

```bash
# Database Configuration
DATABASE_URL=mysql+pymysql://dat515user:admin123@mysql:3306/DAT515
ANALYTICS_DATABASE_URL=mysql+pymysql://analytics_user:analytics_pass@analyticsdb:3306/analytics_db
REDIS_URL=redis://redis:6379/0

# JWT Secret (generate a secure random string)
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# CORS (adjust for production)
CORS_ORIGINS=http://localhost:3000,http://localhost
```

**Recommendation Service Configuration:**

```bash
cd recomendation
cp .env.example .env
```

Edit `.env` file (default values usually work):

```bash
DATABASE_URL=mysql+pymysql://dat515user:admin123@mysql:3306/DAT515
ANALYTICS_DB_URL=mysql+pymysql://analytics_user:analytics_pass@analyticsdb:3306/analytics_db
```

## Deployment Instructions

### Local Deployment

**Step 1: Ensure Docker and Docker Compose are installed**

```bash
docker --version
docker-compose --version
```

**Step 2: Start all services**

```bash
docker-compose up -d
```

This will start 11 containers:

- `backend` - FastAPI backend (port 8000)
- `frontend` - React app (port 3000)
- `recommendation` - ML recommendation service (port 8080)
- `mysql` - Main database (port 3306)
- `analyticsdb` - Analytics database (port 3307)
- `redis` - Cache (port 6379)
- `nginx` - Reverse proxy (port 80)
- `prometheus` - Metrics collection (port 9090)
- `grafana` - Monitoring dashboard (port 3001)
- `seed` - Database seeding (runs once and stops)
- `cadvisor` - Container monitoring (port 8082)

**Step 3: Wait for services to be healthy**

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f backend
```

Wait for:

- MySQL healthcheck to pass (may take 30-60 seconds)
- Database seeding to complete (might take some time)
- Backend to start accepting connections

**Step 4: Access the application**

- **Frontend**: http://localhost
- **Backend API Docs**: http://localhost/api/docs
- **Recommendation API Docs**: http://localhost/api/recommendation/docs
- **Grafana Dashboard**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

### Cloud Deployment (GKE)

#### Prerequisites

1. Google Cloud Account with billing enabled
2. Install Requiered Tools:
   - gcloud CLI
   - kubectl
   - Docker Desktop
   - Google Cloud Code VsCode Extension (optional but recommended)

```bash
# Install gcloud CLI (macOS example)
brew install --cask google-cloud-sdk

# Install kubectl
gcloud components install kubectl

# Install Docker Desktop
```

3. Set up Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing one)

# Option 1: Create project via CLI
gcloud projects create YOUR-PROJECT-ID --name="YOUR-PROJECT-NAME"
# Example: gcloud projects create dat515 --name="Mobilio E-Commerce"

# use an existing project
gcloud config set project YOUR-PROJECT-ID
# Example: gcloud config set project

# Option 2: Create project via browser
# Go to https://console.cloud.google.com/projectcreate
# Create project and note the Project ID

# Set your project ID
export PROJECT_ID=YOUR-PROJECT-ID
gcloud config set project $PROJECT_ID

# Enable billing for the project
# This must be done in the browser: https://console.cloud.google.com/billing
# Link your project to a billing account

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Configure Docker to use gcloud for authentication
gcloud auth configure-docker
```

#### Deployment Steps

1. Create GKE cluster

```bash
cd 7project

# Create cluster (can take several minutes)
gcloud container clusters create shop-app-cluster \
  --zone=europe-north1-a \
  --num-nodes=3 \
  --machine-type=e2-small \
  --disk-size=10GB \
  --enable-autorepair \
  --enable-autoupgrade

# Get cluster credentials and configure kubectl to use them
gcloud container clusters get-credentials shop-app-cluster --zone=europe-north1
```

2. Configure Environment Variables

Edit the kubernetes manifests in `k8s/` to set your environment variables, secrets, and configmaps. Make a copy of `k8s/backend/secret-example.yaml` to `k8s/backend/secret.yaml` and fill in AWS credentials and Stripe Keys.

3. Deploy application

```bash
# Make scripts executable (if not already)
chmod +x ./scripts/*.sh

# Run the complete deployment script
./scripts/deploy.sh
```

This deploy script will:

- Build Docker images for backend, frontend, and recommendation service
- Push images to Google Container Registry
- Deploy all Kubernetes resources (MySQL, Redis, backend, frontend, etc.)
- Set up Prometheus and Grafana monitoring
- Initialize the database

4. Seed the Database (with test data)

```bash
./scripts/seed-db.sh
```

5. Get the application URL

```bash
# Wait for LoadBalancer IP (may take a few minutes)
kubectl get service nginx -n shop-app -w

# Once EXTERNAL-IP appears, access the app at:
# http://<EXTERNAL-IP>
```

#### Post-Deployment

Access Services:

- Application: `http://<EXTERNAL-IP>`
- Grafana: `http://<EXTERNAL-IP>/grafana/` (admin/admin)
- Admin Panel: Login with `admin@mail.com / admin123`

Update Services:

```bash
# Update specific service after code changes
./scripts/update.sh backend   # Updates backend
./scripts/update.sh frontend  # Updates frontend
./scripts/update.sh recommendation  # Updates recommendation service

# Quick restart without rebuild
./scripts/restart.sh backend
```

Monitor Resources:

```bash
# Check all pods
kubectl get pods -n shop-app

# Check logs
kubectl logs -f deployment/backend -n shop-app
kubectl logs -f deployment/frontend -n shop-app

# View resource usage
kubectl top pods -n shop-app
kubectl top nodes
```

Cleanup

```bash
# Delete just the namespace (keeps cluster)
./scripts/cleanup.sh namespace

# Delete entire cluster
./scripts/cleanup.sh cluster
```

### Verification

**Check service health:**

```bash
# Local deployment
curl http://localhost/api/health/detailed
```

**Check recommendation service:**

```bash
curl http://localhost/api/recommendation/docs
```

**View all containers (local):**

```bash
docker-compose ps
```

**Interactive API Documentation:**

Visit these URLs to explore and test all API endpoints:

- **Main Backend API**: http://localhost/api/docs (Swagger UI)
- **Main Backend API**: http://localhost/api/redoc (ReDoc)
- **Recommendation API**: http://localhost/api/recommendation/docs

**Check logs:**

```bash
# Local
docker-compose logs backend
docker-compose logs recommendation

# GKE
kubectl logs -l app=backend --namespace=mobilio
kubectl logs -l app=recommendation --namespace=mobilio
```

## Testing Instructions

### Unit Tests

The backend includes comprehensive unit tests using pytest with test coverage reporting.

**Run all unit tests:**

```bash
cd backend
pytest
```

**Run specific test modules:**

```bash
# Test authentication
pytest tests/test_auth.py

# Test products
pytest tests/test_products.py

# Test cart functionality
pytest tests/test_cart.py

# Test orders
pytest tests/test_orders.py

# Test payment integration
pytest tests/test_payment.py
```

**Current Test Coverage:**

The project includes tests for:

- Authentication (registration, login, JWT tokens)
- Product CRUD operations
- Shopping cart management
- Order creation and history
- Stripe payment integration
- API validation and error handling

### Integration Tests

Integration tests verify the interaction between multiple components.

**Run integration tests:**

```bash
cd backend
pytest tests/test_integration.py -v
```

These tests cover:

- Complete user registration → login → cart → checkout flow
- Database transactions and rollbacks
- External service mocking (Stripe, S3)

---

## Presentation Video

**YouTube Link**: https://www.youtube.com/watch?v=P2dnaQGxtPw

**Duration**: [11 minutes 15 seconds]

**Video Includes**:

- [ ] Project overview and architecture
- [ ] Live demonstration of key features
- [ ] Code walkthrough
- [ ] Build and deployment showcase

## Troubleshooting

### Common Issues

#### Issue 1: MySQL port issue

**Symptoms**: MySQL server not starting, or can't get connection with the main db

**Solution**: Check if you have MySQL running as a background service, as it might use the same port (3306) as our containerized database.

**Debug Commands:**

**Linux:**

```bash
# Check if port 3306 is in use
sudo lsof -i :3306
sudo netstat -tlnp | grep 3306

# Check MySQL service status
sudo systemctl status mysql
sudo systemctl status mariadb

# Stop MySQL service if running
sudo systemctl stop mysql
sudo systemctl stop mariadb

# Prevent MySQL from starting on boot (optional)
sudo systemctl disable mysql
```

**macOS:**

```bash
# Check if port 3306 is in use
sudo lsof -i :3306
netstat -an | grep 3306

# Check MySQL service status
brew services list | grep mysql

# Stop MySQL service if running
brew services stop mysql

# Alternative: Check launchd services
launchctl list | grep mysql
launchctl unload ~/Library/LaunchAgents/homebrew.mxcl.mysql.plist

# Kill process using port 3306 (if needed)
sudo lsof -t -i:3306 | xargs kill -9
```

**Windows (PowerShell):**

```powershell
# Check if port 3306 is in use
Get-NetTCPConnection -LocalPort 3306 -State Listen -ErrorAction SilentlyContinue

# More detailed port information
netstat -ano | findstr :3306

# Find process using port 3306
$processId = (Get-NetTCPConnection -LocalPort 3306 -ErrorAction SilentlyContinue).OwningProcess
Get-Process -Id $processId

# Check MySQL service status
Get-Service -Name "*mysql*"

# Stop MySQL service if running
Stop-Service -Name "MySQL80" -Force
# Or for other versions:
Stop-Service -Name "MySQL" -Force

# Disable MySQL service (optional)
Set-Service -Name "MySQL80" -StartupType Disabled

# Kill process using port 3306 (if needed - use PID from netstat command)
Stop-Process -Id <PID> -Force
```

#### Issue 2: S3 bucket uploading images

**Symptoms**: When trying to upload an image to S3 via the admin dashboard, you might get internal server error 500

**Solution**: This is typically caused by missing AWS credentials or incorrect S3 bucket CORS configuration.

**Step 1: Verify AWS credentials are set in backend/.env:**

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

**Step 2: Configure S3 Bucket CORS Policy**

In the AWS S3 Console, go to your bucket → Permissions → Cross-origin resource sharing (CORS), and add this JSON configuration:

```json
[
	{
		"AllowedHeaders": ["*"],
		"AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
		"AllowedOrigins": [
			"http://localhost",
			"http://localhost:3000",
			"http://localhost:80",
			"https://your-production-domain.com"
		],
		"ExposeHeaders": ["ETag"],
		"MaxAgeSeconds": 3000
	}
]
```

**Step 3: Verify S3 Bucket Policy (Permissions → Bucket Policy)**

Ensure your bucket policy allows uploads:

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "PublicReadGetObject",
			"Effect": "Allow",
			"Principal": "*",
			"Action": "s3:GetObject",
			"Resource": "arn:aws:s3:::your-bucket-name/*"
		}
	]
}
```

**Step 4: Verify IAM User Permissions**

Your AWS IAM user needs these permissions:

- `s3:PutObject`
- `s3:GetObject`
- `s3:DeleteObject`
- `s3:ListBucket`

---

#### Issue 3: Stripe payment integration errors

**Symptoms**: Payment checkout fails, returns error 500, or Stripe webhook events not working

**Solution**: Verify that all Stripe API keys are correctly configured in your backend `.env` file.

**Step 1: Check Stripe credentials in backend/.env:**

```bash
# Required Stripe keys
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

**Step 2: Get your Stripe keys**

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Navigate to **Developers → API keys**
3. Copy your **Secret key** (starts with `sk_test_` for test mode)

