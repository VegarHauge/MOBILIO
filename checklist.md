# Project Evaluation Checklist

The group earn points by completing items from the categories below.
You are not expected to complete all items.
Focus on areas that align with your project goals and interests.

The core deliverables are required.
This means that you must get at least 2 points for each item in this category.

Try to be honest with yourself and us in your self-assessment, to avoid disappointment later on.
Many cloud providers, command line tools, and libraries provide solutions that require only a few clicks or commands to implement some of the items below.
You should not expect to earn full points for simply clicking a few buttons, following a simple tutorial, or adding a few lines of code.
Please support your self-assessment with a comment and/or **references to** relevant documentation, code snippets, or screenshots.

| **Category**                     | **Item**                                | **Max Points** | **Points**       | **Comment** |
| -------------------------------- | --------------------------------------- | -------------- | ---------------- | ----------- |
| **Core Deliverables (Required)** |                                         |                |                  |             |
| Codebase & Organization          | Well-organized project structure        | 5              | 5                | Clear separation: backend/, frontend/, recomendation/, db/, monitoring/ with proper sub-modules |
|                                  | Clean, readable code                    | 5              | 4                | Good structure each main component has it's own folder, backend split into, services, models, apis, utils. Frontend split into pages, components, centralised api calls.  |
|                                  | Use planning tool (e.g., GitHub issues) | 5              | 2                | GitHub issues used to some extend |
|                                  | Proper version control usage            | 5              | 5                | Git repository with structured commits, , minus one point for bad commit messages from Vegar :( |
|                                  | Complete source code                    | 5              | 5                | All components present |
| Documentation                    | Comprehensive reproducibility report    | 10             | 10                |  |
|                                  | Updated design document                 | 5              | 5                | design.md v1.0 complete with architecture diagrams, ERD, tech stack, security, cost analysis |
|                                  | Clear build/deployment instructions     | 5              | 5               | Detailed local Docker Compose instructions, env setup, verification steps;  |
|                                  | Troubleshooting guide                   | 5              | 3                | There are some guides in the report|
|                                  | Completed self-assessment table         | 5              | 5                | This document! |
|                                  | Hour sheets for all members             | 5              | 5               | Hour sheets in report.md  |
| Presentation Video               | Project demonstration                   | 5              | 5                | see video  |
|                                  | Code walk-through                       | 5              | 5                | see video |
|                                  | Deployment showcase                     | 5              | 5                | see video |
| **Technical Implementation**     |                                         |                |                  |             |
| Application Functionality        | Basic functionality works               | 10             | 10                | Complete e-commerce: CRUD products, cart management, order processing, Stripe payments; assumes works based on code quality |
|                                  | Advanced features implemented           | 10             | 10                | ML recommendations with train/sync endpoints, S3 image uploads |
|                                  | Error handling & robustness             | 10             | 7                | HTTPException throughout API layer (auth.py, cart.py, products.py), logging in health_service.py & product_service.py, try-catch blocks, validation with Pydantic |
|                                  | User-friendly interface                 | 5              | 5                | React 19 + Material-UI, context state management, ProductCard.test.jsx shows component testing |
| Backend & Architecture           | Stateless web server                    | 5              | 5                | FastAPI backend with JWT stateless auth, REST endpoints, can scale horizontally |
|                                  | Stateful application                    | 10             | 10               | User sessions via JWT, cart persists in MySQL, order history, product inventory - proper stateful design with DB |
|                                  | Database integration                    | 10             | 10               | MySQL main DB + separate analytics DB, SQLAlchemy ORM with models (cart.py, user.py, order.py, product.py), health checks verify connections |
|                                  | API design                              | 5              | 5                | RESTful with clear namespaces (/api/auth, /api/cart, /api/products, /api/orders, /api/payment), OpenAPI docs, proper HTTP methods |
|                                  | Microservices architecture              | 10             | 8                | Separate services (backend, recommendation, frontend) with independent codebases, inter-service communication, shared DBs (could be more decoupled) |
| Cloud Integration                | Basic cloud deployment                  | 10             | 10                | deployed visit http://34.88.175.32/  |
|                                  | Cloud APIs usage                        | 10             | 10               | AWS S3 via Boto3 (s3_service.py), Stripe API for payments (stripe_service.py), proper SDK integration |
|                                  | Serverless components                   | 10             | 0                | |
|                                  | Advanced cloud services                 | 5              | 5               | Every cloud service is advanced for us, since we are new to it :)  |
| **DevOps & Deployment**          |                                         |                |                  |             |
| Containerization                 | Basic Dockerfile                        | 5              | 5                | All services: backend/Dockerfile, frontend/Dockerfile, recomendation/Dockerfile, db dockerfiles |
|                                  | Optimized Dockerfile                    | 5              | 4                | Multi-stage build in frontend/Dockerfile (node build → nginx), alpine images (redis:7-alpine, nginx:1.25-alpine), good layer caching |
|                                  | Docker Compose                          | 5              | 5                | Comprehensive docker-compose.yml: 11 services, depends_on with health conditions, volume mounts, proper networking, health checks |
|                                  | Persistent storage                      | 5              | 5                | Named volumes: mysql_data, analytics_data; proper MySQL data persistence across container restarts |
| Deployment & Scaling             | Manual deployment                       | 5              | 5                | docker-compose up -d documented and functional |
|                                  | Automated deployment                    | 5              | 0                | No CI/CD pipeline , no automated testing/deployment |
|                                  | Multiple replicas                       | 5              | 0                | docker-compose.yml has no replica config |
|                                  | Kubernetes deployment                   | 10             | 10               | http://34.88.175.32/ |
| **Quality Assurance**            |                                         |                |                  |             |
| Testing                          | Unit tests                              | 5              | 5                | 6 backend tests: test_auth.py, test_cart.py, test_orders.py, test_products.py , test_payment.py, pytest with SQLite in-memory |
|                                  | Integration tests                       | 5              | 5                | test_integration.py  with @pytest.mark.integration, full e-commerce flow tests (register→login→cart→checkout→payment), conftest.py with fixtures |
|                                  | End-to-end tests                        | 5              | 0                | |
|                                  | Performance testing                     | 5              | 0                | |
| Monitoring & Operations          | Health checks                           | 5              | 5                | /api/health/detailed endpoint in health_service.py, checks DB/S3/Stripe, Docker healthchecks in compose (mysql, analyticsdb) |
|                                  | Logging                                 | 5              | 4                | logging.getLogger() in health_service.py, product_service.py with info/warning/error levels, structured but could use centralized log aggregation |
|                                  | Metrics/Monitoring                      | 2              | 2                | Prometheus (port 9090) + Grafana (port 3001) in docker-compose.yml, custom dashboards in monitoring/grafana/ |
|                                  | Custom Metrics for your project         | 3              | 3                | product_requests_total Counter in metrics.py with middleware for /api/products endpoint tracking |
| Security                         | HTTPS/TLS                               | 5              | 0                | HTTP only  no TLS certificates, no nginx SSL config |
|                                  | Authentication                          | 5              | 5                | JWT tokens via PyJWT in auth_service.py, Argon2 password hashing , token expiry, proper verify_token() |
|                                  | Authorization                           | 5              | 5                | Role-based (admin/customer) with get_admin_user() dependency in auth_utils.py, endpoints protected by role checks |
| **Innovation & Excellence**      |                                         |                |                  |             |
| Advanced Features and            | AI/ML Integration                       | 10             | 10               | Full ML service: scikit-learn in ml_recommendation_service.py (771 lines), similarity matrix, co-purchase matrix, model training via POST /train, pickle model persistence, data sync from production→analytics |
| Technical Excellence             | Real-time features                      | 10             | 0                | |
|                                  | Creative problem solving                | 10             | 8                | Separate analytics DB for ML (avoids production load), S3 for image offload, health checks for external services. |
|                                  | Performance optimization                | 5              | 1                | Redis declared in docker-compose but no usage found in codebase (grep for "redis|cache" found no Python code), multi-stage Docker builds |
|                                  | Exceptional user experience             | 5              | 5             | Material-UI React frontend, admin panel, API docs|
| **Total**                        |                                         | **255**        | **202**          |    |

## Grading Scale

- **Minimum Required: 100 points**
- **Maximum: 200+ points**

| Grade | Points   |
| ----- | -------- |
| A     | 180-200+ |
| B     | 160-179  |
| C     | 140-159  |
| D     | 120-139  |
| E     | 100-119  |
| F     | 0-99     |
