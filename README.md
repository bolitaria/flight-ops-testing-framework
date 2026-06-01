# Flight Ops Testing Framework

A professional portfolio project demonstrating a **scalable, automated testing framework** for a mission-critical flight operations platform. Built with a DevOps mindset, this system models three FastAPI microservices, orchestrated with Docker Compose, and validates them through a multi-layer testing strategy – all integrated into a CI/CD pipeline.

## 🎯 Why this project?
This framework was built to showcase the ability to:
- Design an **automated testing strategy** for cloud-native, distributed systems.
- Integrate tests seamlessly into **CI/CD pipelines** (Jenkins, GitHub Actions, etc.).
- Ensure **reliability and security** from day one (DevSecOps principles).
- Provide **observability** with health checks and clear test reporting.
- Communicate technical decisions clearly for cross-team collaboration.

## 🏗️ System Architecture
| Service              | Port | Description                          |
|----------------------|------|--------------------------------------|
| Flight Service       | 8000 | Manage flights and seat inventory    |
| Booking Service      | 8001 | Create bookings, validate flights    |
| Notification Service | 8002 | Record sent notifications (simulated) |

The Booking Service calls the Flight Service to check availability and then triggers a notification. All services are containerized and orchestrated with Docker Compose, with health checks ensuring readiness.

## 🧪 Testing Strategy
A **risk-based, multi-layer approach** ensures coverage across all integration points:

| Layer       | Focus                                     | Marker               |
|-------------|-------------------------------------------|----------------------|
| Unit        | Business logic, algorithms               | `@pytest.mark.unit`  |
| API         | REST contracts, status codes, schemas    | `@pytest.mark.api`   |
| Integration | Cross-service communication              | `@pytest.mark.integration` |
| Workflow    | End‑to‑end business scenarios            | `@pytest.mark.workflow` |

Tests are written in Python with **pytest** and async **httpx** clients. They are completely independent of the services, allowing the framework to evolve without touching the application code.

## ⚙️ CI/CD
A GitHub Actions pipeline automatically builds the Docker containers, runs all test layers, and publishes an HTML report on every push. The same logic can be migrated to Jenkins, GitLab CI, or any other CI system.

## ▶️ Quick Start
```bash
make up          # Start all services
make test-unit   # Run unit tests only
make test-all    # Run all tests and generate report.html
make down        # Stop services
📂 Repository Structure
text
.
├── src/                  # Microservices source code & Dockerfiles
├── tests/                # Testing framework (unit, api, integration, workflow)
├── docker-compose.yml    # Local orchestration
├── requirements.txt      # Python dependencies
├── Makefile              # Convenience commands
├── .github/workflows/    # CI/CD pipeline definition
└── README.md
💡 Key Design Decisions
FastAPI for high-performance async APIs.

pytest with markers enables selective test execution and clear reporting.

Docker Compose creates isolated, reproducible environments.

Health checks guarantee that dependent services are ready before testing.

Retry logic in the Booking Service demonstrates resilience patterns.

The framework is portable – it works locally, in CI, and on any cloud environment.

🚀 Future enhancements
Add performance tests with locust or k6.

Extend with contract testing using pact.

Deploy on a real Kubernetes cluster with Terraform.

Integrate security scanning (Trivy, Bandit) into the pipeline.

Add centralized logging with ELK or Grafana Loki.

Built with passion for quality, automation, and continuous improvement.

text

## 16. .gitignore
```bash
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.pytest_cache/
report.html
