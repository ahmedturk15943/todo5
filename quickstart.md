# Todo App - Quick Start Guide

This guide will help you get the Todo App running locally or deploy it to Kubernetes.

---

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Kubernetes Deployment (Minikube)](#kubernetes-deployment-minikube)
3. [Cloud Deployment](#cloud-deployment)
4. [Testing the Application](#testing-the-application)
5. [Troubleshooting](#troubleshooting)

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop
- Git

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd todo_app/phase1
```

### Step 2: Start Infrastructure Services

```bash
# Create docker-compose.yml if not exists
cat > docker-compose.yml <<EOF
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: todoapp
      POSTGRES_PASSWORD: todoapp123
      POSTGRES_DB: todoapp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  kafka:
    image: bitnami/kafka:3.5
    environment:
      KAFKA_CFG_NODE_ID: 0
      KAFKA_CFG_PROCESS_ROLES: controller,broker
      KAFKA_CFG_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CFG_CONTROLLER_QUORUM_VOTERS: 0@kafka:9093
      KAFKA_CFG_CONTROLLER_LISTENER_NAMES: CONTROLLER
    ports:
      - "9092:9092"

volumes:
  postgres_data:
EOF

# Start services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Step 3: Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Create .env file
cat > .env <<EOF
DATABASE_URL=postgresql://todoapp:todoapp123@localhost:5432/todoapp
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
BETTER_AUTH_SECRET=$(openssl rand -base64 32)
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=7
EOF

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn src.main:app --reload --port 8000
```

Backend is now running at `http://localhost:8000`

### Step 4: Setup Microservices

Open 4 new terminal windows:

**Terminal 1 - WebSocket Service:**
```bash
cd services/websocket-service
pip install -r requirements.txt

# Create .env
cat > .env <<EOF
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
REDIS_URL=redis://localhost:6379
REDIS_ENABLED=false
PORT=8001
EOF

python -m src.server
```

**Terminal 2 - Notification Service:**
```bash
cd services/notification-service
pip install -r requirements.txt

# Create .env
cat > .env <<EOF
DATABASE_URL=postgresql://todoapp:todoapp123@localhost:5432/todoapp
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
EOF

python -m src.main
```

**Terminal 3 - Recurring Service:**
```bash
cd services/recurring-service
pip install -r requirements.txt

# Create .env
cat > .env <<EOF
DATABASE_URL=postgresql://todoapp:todoapp123@localhost:5432/todoapp
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
EOF

python -m src.main
```

**Terminal 4 - Audit Service:**
```bash
cd services/audit-service
pip install -r requirements.txt

# Create .env
cat > .env <<EOF
DATABASE_URL=postgresql://todoapp:todoapp123@localhost:5432/todoapp
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
EOF

python -m src.main
```

### Step 5: Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=http://localhost:8001
BETTER_AUTH_SECRET=<same-as-backend>
BETTER_AUTH_URL=http://localhost:3000
EOF

# Start frontend
npm run dev
```

Frontend is now running at `http://localhost:3000`

### Step 6: Verify Setup

1. Visit `http://localhost:3000`
2. Create an account
3. Create a task
4. Open the app in another browser/tab
5. Verify real-time sync works

---

## Kubernetes Deployment (Minikube)

### Prerequisites

- Minikube
- kubectl
- Helm 3.x
- Docker

### Step 1: Start Minikube

```bash
# Start with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### Step 2: Install Dependencies

```bash
# Install Dapr
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
helm upgrade --install dapr dapr/dapr \
  --version=1.12 \
  --namespace dapr-system \
  --create-namespace \
  --wait

# Install Strimzi Kafka Operator
kubectl create namespace kafka
helm repo add strimzi https://strimzi.io/charts/
helm upgrade --install strimzi-kafka-operator strimzi/strimzi-kafka-operator \
  --namespace kafka \
  --wait

# Deploy Kafka cluster
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka
kubectl apply -f k8s/kafka/topics.yaml -n kafka

# Wait for Kafka to be ready
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=600s -n kafka
```

### Step 3: Build Docker Images

```bash
# Build all images
docker build -t todoapp/backend:5.0.0 ./backend
docker build -t todoapp/frontend:5.0.0 ./frontend
docker build -t todoapp/websocket-service:5.0.0 ./services/websocket-service
docker build -t todoapp/notification-service:5.0.0 ./services/notification-service
docker build -t todoapp/recurring-service:5.0.0 ./services/recurring-service
docker build -t todoapp/audit-service:5.0.0 ./services/audit-service

# Load images into Minikube
minikube image load todoapp/backend:5.0.0
minikube image load todoapp/frontend:5.0.0
minikube image load todoapp/websocket-service:5.0.0
minikube image load todoapp/notification-service:5.0.0
minikube image load todoapp/recurring-service:5.0.0
minikube image load todoapp/audit-service:5.0.0
```

### Step 4: Deploy Application

```bash
# Update Helm dependencies
cd helm/todo-app
helm dependency update

# Install application
helm upgrade --install todo-app . \
  --values values-local.yaml \
  --namespace todo-app \
  --create-namespace \
  --wait \
  --timeout 10m

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod --all -n todo-app --timeout=600s
```

### Step 5: Access Application

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Add to /etc/hosts (Linux/Mac)
echo "$MINIKUBE_IP todoapp.local" | sudo tee -a /etc/hosts

# Windows: Add to C:\Windows\System32\drivers\etc\hosts
# <minikube-ip> todoapp.local

# Access application
open http://todoapp.local
```

---

## Cloud Deployment

### Prerequisites

- Kubernetes cluster (GKE, AKS, or OKE)
- kubectl configured
- Helm 3.x
- Container registry access

### Step 1: Configure kubectl

**For GKE:**
```bash
gcloud container clusters get-credentials <cluster-name> --region <region>
```

**For AKS:**
```bash
az aks get-credentials --resource-group <rg> --name <cluster-name>
```

**For OKE:**
```bash
oci ce cluster create-kubeconfig --cluster-id <cluster-id>
```

### Step 2: Build and Push Images

```bash
# Set your registry
REGISTRY="gcr.io/your-project"  # or docker.io/username, azurecr.io/registry

# Build and push all images
docker build -t $REGISTRY/todoapp/backend:5.0.0 ./backend
docker push $REGISTRY/todoapp/backend:5.0.0

docker build -t $REGISTRY/todoapp/frontend:5.0.0 ./frontend
docker push $REGISTRY/todoapp/frontend:5.0.0

docker build -t $REGISTRY/todoapp/websocket-service:5.0.0 ./services/websocket-service
docker push $REGISTRY/todoapp/websocket-service:5.0.0

docker build -t $REGISTRY/todoapp/notification-service:5.0.0 ./services/notification-service
docker push $REGISTRY/todoapp/notification-service:5.0.0

docker build -t $REGISTRY/todoapp/recurring-service:5.0.0 ./services/recurring-service
docker push $REGISTRY/todoapp/recurring-service:5.0.0

docker build -t $REGISTRY/todoapp/audit-service:5.0.0 ./services/audit-service
docker push $REGISTRY/todoapp/audit-service:5.0.0
```

### Step 3: Update Configuration

```bash
# Edit helm/todo-app/values-cloud.yaml
# Update:
# - image.registry to your registry
# - global.domain to your domain
# - postgresql.auth.existingSecret (create secret first)
# - redis.auth.existingSecret (create secret first)
```

### Step 4: Run Deployment Script

```bash
chmod +x scripts/deploy-cloud.sh
./scripts/deploy-cloud.sh gke todo-app-cluster us-central1
```

### Step 5: Configure DNS

```bash
# Get LoadBalancer IP
kubectl get svc ingress-nginx-controller -n ingress-nginx

# Update your DNS records:
# A record: todoapp.com -> <LoadBalancer-IP>
# A record: www.todoapp.com -> <LoadBalancer-IP>

# Wait for DNS propagation (can take up to 48 hours)
# Access: https://todoapp.com
```

---

## Testing the Application

### 1. Create Account

1. Visit the application URL
2. Click "Sign Up"
3. Enter email and password
4. Click "Sign Up"

### 2. Create Tasks

1. Click "+ Add Task"
2. Enter task details:
   - Title: "Test Task"
   - Priority: High
   - Tags: "work", "urgent"
   - Due Date: Tomorrow
3. Click "Create Task"

### 3. Test Recurring Tasks

1. Create a task with recurrence:
   - Pattern: Daily
   - Interval: 1 day
   - End: Never
2. Mark the task as complete
3. Verify next occurrence is created automatically

### 4. Test Reminders

1. Create a task with due date
2. Add reminder (15 minutes before)
3. Wait for reminder notification

### 5. Test Real-Time Sync

1. Open app in two browser windows
2. Create/update task in one window
3. Verify changes appear in other window within 2 seconds

### 6. Test Search and Filters

1. Create multiple tasks with different priorities and tags
2. Use search bar to find tasks
3. Apply filters (status, priority, tags)
4. Verify results are correct

### 7. View Activity History

1. Click "Activity" in navigation
2. Verify all operations are logged
3. Filter by action type
4. Verify changes are tracked

---

## Troubleshooting

### Backend Issues

**Database Connection Error:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
psql postgresql://todoapp:todoapp123@localhost:5432/todoapp

# Check migrations
cd backend
alembic current
alembic upgrade head
```

**Kafka Connection Error:**
```bash
# Check Kafka is running
docker-compose ps kafka

# Test Kafka
docker exec -it <kafka-container> kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Frontend Issues

**API Connection Error:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS configuration
# Ensure CORS_ORIGINS in backend .env includes frontend URL
```

**WebSocket Connection Error:**
```bash
# Verify WebSocket service is running
curl http://localhost:8001/

# Check browser console for errors
# Verify NEXT_PUBLIC_WS_URL is correct
```

### Kubernetes Issues

**Pods Not Starting:**
```bash
# Check pod status
kubectl get pods -n todo-app

# View pod logs
kubectl logs <pod-name> -n todo-app

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app
```

**Kafka Not Ready:**
```bash
# Check Kafka status
kubectl get kafka -n kafka

# View Kafka logs
kubectl logs -l app.kubernetes.io/name=kafka -n kafka

# Restart Kafka
kubectl delete pod -l app.kubernetes.io/name=kafka -n kafka
```

**Ingress Not Working:**
```bash
# Check ingress status
kubectl get ingress -n todo-app

# View ingress controller logs
kubectl logs -l app.kubernetes.io/name=ingress-nginx -n ingress-nginx

# Verify DNS resolution
nslookup todoapp.local
```

### Common Issues

**Port Already in Use:**
```bash
# Find process using port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

**Docker Compose Issues:**
```bash
# Stop all services
docker-compose down

# Remove volumes and restart
docker-compose down -v
docker-compose up -d
```

**Minikube Issues:**
```bash
# Restart Minikube
minikube stop
minikube delete
minikube start --cpus=4 --memory=8192

# Check Minikube status
minikube status
minikube logs
```

---

## Next Steps

1. **Customize Configuration**: Update environment variables for your needs
2. **Enable Monitoring**: Set up Prometheus and Grafana
3. **Configure Notifications**: Add email/SMS providers
4. **Set Up CI/CD**: Automate builds and deployments
5. **Scale Services**: Adjust replica counts based on load
6. **Enable TLS**: Configure SSL certificates for production

---

## Support

For issues and questions:
- Check the main README.md
- Review API documentation at `/docs`
- Check logs for error messages
- Verify all prerequisites are installed

---

## Summary

You now have a fully functional Todo App with:
- ✅ Event-driven architecture
- ✅ Real-time synchronization
- ✅ Recurring tasks and reminders
- ✅ Advanced search and filtering
- ✅ Activity history and audit trail
- ✅ Kubernetes deployment

Enjoy using the Todo App!
