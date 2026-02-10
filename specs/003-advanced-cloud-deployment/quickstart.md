# Quickstart Guide: Phase 5 Advanced Cloud Deployment

**Feature**: Advanced Cloud Deployment with Enhanced Task Management
**Date**: 2026-02-10
**Version**: 1.0

## Overview

This guide provides step-by-step instructions for deploying the Phase 5 todo application with event-driven architecture, Kafka, Dapr, and Kubernetes. It covers both local development (Minikube) and cloud production deployment (AKS/GKE/OKE).

## Prerequisites

### Required Tools

- **Docker Desktop**: 24.0+ with Kubernetes enabled
- **Minikube**: 1.33+ (for local K8s cluster)
- **kubectl**: 1.28+ (Kubernetes CLI)
- **Helm**: 3.14+ (Kubernetes package manager)
- **Dapr CLI**: 1.14+ (Distributed application runtime)
- **Python**: 3.13+ (backend development)
- **Node.js**: 20+ (frontend development)
- **Git**: 2.40+ (version control)

### Optional Tools

- **k9s**: Terminal UI for Kubernetes
- **kubectx/kubens**: Context and namespace switching
- **stern**: Multi-pod log tailing

### Installation Commands

**Windows (WSL2)**:
```bash
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

**macOS**:
```bash
brew install minikube kubectl helm dapr/tap/dapr-cli
```

**Linux**:
```bash
# Use same commands as Windows (WSL2) above
```

---

## Part 1: Local Development Setup (Minikube)

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --driver=docker

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

### Step 2: Install Dapr on Minikube

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr installation
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
# dapr-sidecar-injector  dapr-system  True     Running  1         1.14.0   1m   2024-02-10 14:30:00
# dapr-sentry            dapr-system  True     Running  1         1.14.0   1m   2024-02-10 14:30:00
# dapr-operator          dapr-system  True     Running  1         1.14.0   1m   2024-02-10 14:30:00
# dapr-placement         dapr-system  True     Running  1         1.14.0   1m   2024-02-10 14:30:00
```

### Step 3: Install Kafka (Strimzi Operator)

```bash
# Create Kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator to be ready
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Deploy Kafka cluster (1 broker for local)
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.7.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
    storage:
      type: ephemeral
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

# Wait for Kafka to be ready (takes 2-3 minutes)
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka

# Verify Kafka is running
kubectl get kafka -n kafka
kubectl get pods -n kafka
```

### Step 4: Create Kafka Topics

```bash
# Create task-events topic
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824
EOF

# Create reminders topic
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000
EOF

# Create task-updates topic
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 86400000  # 1 day (real-time updates don't need long retention)
EOF

# Verify topics created
kubectl get kafkatopics -n kafka
```

### Step 5: Deploy Dapr Components

```bash
# Create Dapr components namespace
kubectl create namespace todo-app

# Deploy Kafka Pub/Sub component
cat <<EOF | kubectl apply -f -
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-service"
    - name: authType
      value: "none"
EOF

# Deploy PostgreSQL State Store component
cat <<EOF | kubectl apply -f -
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-secret
        key: connectionString
EOF

# Deploy Kubernetes Secrets Store component
cat <<EOF | kubectl apply -f -
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: todo-app
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
EOF

# Verify Dapr components
kubectl get components -n todo-app
```

### Step 6: Create Secrets

```bash
# Create PostgreSQL connection secret (use your Neon DB credentials)
kubectl create secret generic postgres-secret \
  --from-literal=connectionString="host=your-neon-host.neon.tech user=your-user password=your-password dbname=todo sslmode=require" \
  -n todo-app

# Verify secret created
kubectl get secrets -n todo-app
```

### Step 7: Deploy Application with Helm

```bash
# Navigate to project root
cd /path/to/todo_app/phase1

# Install Helm chart (local values)
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --values ./helm/todo-app/values-local.yaml \
  --create-namespace

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod --all -n todo-app --timeout=300s

# Verify deployment
kubectl get pods -n todo-app
kubectl get services -n todo-app
```

### Step 8: Access the Application

```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts (or C:\Windows\System32\drivers\etc\hosts on Windows)
echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts

# Enable Minikube tunnel (in separate terminal, keep running)
minikube tunnel

# Access application
# Frontend: http://todo-app.local
# Backend API: http://todo-app.local/api
# API Docs: http://todo-app.local/api/docs
```

### Step 9: Verify Event-Driven Architecture

```bash
# Check Kafka consumer groups
kubectl exec -it todo-kafka-kafka-0 -n kafka -- \
  bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --list

# View task-events topic messages
kubectl exec -it todo-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning

# Check Dapr sidecars
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'

# View Dapr logs
kubectl logs -l app=backend -c daprd -n todo-app
```

---

## Part 2: Cloud Deployment (AKS/GKE/OKE)

### Option A: Azure Kubernetes Service (AKS)

#### Prerequisites
- Azure account with $200 free credit
- Azure CLI installed

#### Step 1: Create AKS Cluster

```bash
# Login to Azure
az login

# Create resource group
az group create --name todo-app-rg --location eastus

# Create AKS cluster (2 nodes, Standard_B2s)
az aks create \
  --resource-group todo-app-rg \
  --name todo-app-cluster \
  --node-count 2 \
  --node-vm-size Standard_B2s \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group todo-app-rg --name todo-app-cluster

# Verify connection
kubectl get nodes
```

#### Step 2: Install Dapr on AKS

```bash
# Initialize Dapr
dapr init -k

# Verify
dapr status -k
```

#### Step 3: Install Kafka (Strimzi)

```bash
# Follow same steps as Minikube (Step 3-4 above)
# But use 3 replicas for production:

# Edit Kafka cluster spec:
# kafka.replicas: 3
# zookeeper.replicas: 3
# storage.type: persistent-claim (instead of ephemeral)
```

#### Step 4: Deploy Application

```bash
# Install Helm chart (cloud values)
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --values ./helm/todo-app/values-cloud.yaml \
  --create-namespace

# Wait for deployment
kubectl wait --for=condition=ready pod --all -n todo-app --timeout=600s
```

#### Step 5: Configure Ingress

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/cloud/deploy.yaml

# Get external IP
kubectl get service ingress-nginx-controller -n ingress-nginx

# Configure DNS (point your domain to external IP)
# Or use nip.io for testing: <external-ip>.nip.io
```

---

### Option B: Google Kubernetes Engine (GKE)

#### Prerequisites
- Google Cloud account with $300 free credit
- gcloud CLI installed

#### Step 1: Create GKE Cluster

```bash
# Login to Google Cloud
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Create GKE cluster (2 nodes, e2-medium)
gcloud container clusters create todo-app-cluster \
  --zone us-central1-a \
  --num-nodes 2 \
  --machine-type e2-medium \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 4

# Get credentials
gcloud container clusters get-credentials todo-app-cluster --zone us-central1-a

# Verify
kubectl get nodes
```

#### Step 2-5: Follow same steps as AKS

---

### Option C: Oracle Kubernetes Engine (OKE) - Recommended (Always Free)

#### Prerequisites
- Oracle Cloud account (always free tier)
- oci CLI installed

#### Step 1: Create OKE Cluster

```bash
# Login to Oracle Cloud Console
# Navigate to: Developer Services > Kubernetes Clusters (OKE)

# Create cluster:
# - Name: todo-app-cluster
# - Kubernetes version: Latest
# - Node pool: 2 nodes, VM.Standard.E2.1.Micro (always free)
# - Shape: 1 OCPU, 1GB RAM per node

# Download kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region us-ashburn-1

# Verify
kubectl get nodes
```

#### Step 2-5: Follow same steps as AKS

---

## Part 3: CI/CD Pipeline (GitHub Actions)

### Step 1: Create GitHub Secrets

Navigate to: Repository > Settings > Secrets and variables > Actions

Add secrets:
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password
- `KUBECONFIG`: Base64-encoded kubeconfig file
- `NEON_DB_URL`: PostgreSQL connection string

### Step 2: GitHub Actions Workflows

Workflows are already configured in `.github/workflows/`:
- `test.yml`: Run tests on PR
- `build.yml`: Build and push Docker images
- `deploy-local.yml`: Deploy to Minikube (for testing)
- `deploy-cloud.yml`: Deploy to AKS/GKE/OKE

### Step 3: Trigger Deployment

```bash
# Push to main branch triggers deployment
git push origin main

# Or manually trigger via GitHub Actions UI
```

---

## Part 4: Testing

### Unit Tests

```bash
# Backend tests
cd backend
pytest tests/unit/ -v

# Frontend tests
cd frontend
npm test
```

### Integration Tests

```bash
# Backend integration tests (requires Kafka and PostgreSQL)
cd backend
pytest tests/integration/ -v

# Frontend E2E tests
cd frontend
npm run test:e2e
```

### Load Tests

```bash
# Install Locust
pip install locust

# Run load test
cd backend/tests/load
locust -f locustfile.py --host http://todo-app.local
```

### Contract Tests

```bash
# Verify API contracts
cd backend
pytest tests/contract/ -v
```

---

## Part 5: Monitoring and Observability

### Install Prometheus and Grafana

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Login: admin / prom-operator
# URL: http://localhost:3000
```

### View Logs

```bash
# View all logs
kubectl logs -l app=backend -n todo-app --tail=100 -f

# View Dapr logs
kubectl logs -l app=backend -c daprd -n todo-app --tail=100 -f

# View Kafka logs
kubectl logs -l app.kubernetes.io/name=kafka -n kafka --tail=100 -f

# Use stern for multi-pod logs
stern backend -n todo-app
```

### Metrics

```bash
# Dapr metrics
kubectl port-forward -n todo-app svc/backend 9090:9090
curl http://localhost:9090/metrics

# Kafka metrics
kubectl port-forward -n kafka svc/todo-kafka-kafka-bootstrap 9404:9404
curl http://localhost:9404/metrics
```

---

## Part 6: Troubleshooting

### Common Issues

#### 1. Pods not starting

```bash
# Check pod status
kubectl get pods -n todo-app

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n todo-app
```

#### 2. Kafka connection issues

```bash
# Verify Kafka is running
kubectl get kafka -n kafka

# Check Kafka logs
kubectl logs -l app.kubernetes.io/name=kafka -n kafka

# Test Kafka connectivity from pod
kubectl run kafka-test --rm -it --restart=Never --image=confluentinc/cp-kafka:latest -- \
  kafka-broker-api-versions --bootstrap-server todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092
```

#### 3. Dapr component issues

```bash
# Check Dapr components
kubectl get components -n todo-app

# Describe component
kubectl describe component kafka-pubsub -n todo-app

# Check Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system
```

#### 4. Database connection issues

```bash
# Verify secret exists
kubectl get secret postgres-secret -n todo-app

# Check secret value
kubectl get secret postgres-secret -n todo-app -o jsonpath='{.data.connectionString}' | base64 -d

# Test connection from pod
kubectl run psql-test --rm -it --restart=Never --image=postgres:16 -- \
  psql "postgresql://user:password@host/dbname?sslmode=require"
```

#### 5. Ingress not working

```bash
# Check ingress
kubectl get ingress -n todo-app

# Describe ingress
kubectl describe ingress todo-app-ingress -n todo-app

# Check ingress controller logs
kubectl logs -l app.kubernetes.io/name=ingress-nginx -n ingress-nginx
```

### Debug Commands

```bash
# Get all resources
kubectl get all -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Execute shell in pod
kubectl exec -it <pod-name> -n todo-app -- /bin/bash

# Port forward for local access
kubectl port-forward -n todo-app svc/backend 8000:8000

# View resource usage
kubectl top pods -n todo-app
kubectl top nodes
```

---

## Part 7: Cleanup

### Local (Minikube)

```bash
# Delete Helm release
helm uninstall todo-app -n todo-app

# Delete Kafka
kubectl delete kafka todo-kafka -n kafka
kubectl delete namespace kafka

# Delete Dapr
dapr uninstall -k

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

### Cloud (AKS/GKE/OKE)

```bash
# Delete Helm release
helm uninstall todo-app -n todo-app

# Delete cluster
# AKS:
az aks delete --resource-group todo-app-rg --name todo-app-cluster --yes --no-wait
az group delete --name todo-app-rg --yes --no-wait

# GKE:
gcloud container clusters delete todo-app-cluster --zone us-central1-a --quiet

# OKE:
# Delete via Oracle Cloud Console
```

---

## Summary

This quickstart guide covered:
- ✅ Local development setup with Minikube, Dapr, and Kafka
- ✅ Cloud deployment to AKS/GKE/OKE
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Testing procedures (unit, integration, load, contract)
- ✅ Monitoring and observability setup
- ✅ Troubleshooting common issues

**Next Steps**:
1. Run `/sp.tasks` to generate implementation tasks
2. Run `/sp.implement` to execute tasks via Claude Code
3. Deploy to local Minikube for testing
4. Deploy to cloud for production

**Estimated Setup Time**:
- Local (Minikube): 30-45 minutes
- Cloud (AKS/GKE/OKE): 45-60 minutes
- CI/CD Pipeline: 15-30 minutes

**Support**:
- Documentation: `specs/003-advanced-cloud-deployment/`
- Issues: GitHub Issues
- Logs: `kubectl logs` commands above
