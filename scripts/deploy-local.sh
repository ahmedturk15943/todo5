#!/bin/bash
set -e

echo "🚀 Deploying Todo App to Minikube..."

# Check if minikube is running
if ! minikube status > /dev/null 2>&1; then
    echo "❌ Minikube is not running. Starting Minikube..."
    minikube start --cpus=4 --memory=8192 --driver=docker
fi

# Enable required addons
echo "📦 Enabling Minikube addons..."
minikube addons enable ingress
minikube addons enable metrics-server

# Install Dapr
echo "🔧 Installing Dapr..."
if ! helm list -n dapr-system | grep -q dapr; then
    helm repo add dapr https://dapr.github.io/helm-charts/
    helm repo update
    helm upgrade --install dapr dapr/dapr \
        --version=1.12 \
        --namespace dapr-system \
        --create-namespace \
        --wait
fi

# Install Strimzi Kafka Operator
echo "📨 Installing Strimzi Kafka Operator..."
if ! kubectl get namespace kafka > /dev/null 2>&1; then
    kubectl create namespace kafka
fi

if ! helm list -n kafka | grep -q strimzi-kafka-operator; then
    helm repo add strimzi https://strimzi.io/charts/
    helm repo update
    helm upgrade --install strimzi-kafka-operator strimzi/strimzi-kafka-operator \
        --namespace kafka \
        --wait
fi

# Deploy Kafka cluster
echo "🔧 Deploying Kafka cluster..."
kubectl apply -f ../k8s/kafka/kafka-cluster.yaml -n kafka
kubectl apply -f ../k8s/kafka/topics.yaml -n kafka

# Wait for Kafka to be ready
echo "⏳ Waiting for Kafka to be ready..."
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka

# Install Todo App
echo "📦 Installing Todo App..."
helm dependency update ../helm/todo-app/

helm upgrade --install todo-app ../helm/todo-app/ \
    --values ../helm/todo-app/values-local.yaml \
    --namespace todo-app \
    --create-namespace \
    --wait \
    --timeout 10m

# Wait for all pods to be ready
echo "⏳ Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod --all -n todo-app --timeout=300s

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Add entry to /etc/hosts
echo "📝 Adding entry to /etc/hosts..."
if ! grep -q "todoapp.local" /etc/hosts; then
    echo "$MINIKUBE_IP todoapp.local" | sudo tee -a /etc/hosts
fi

# Display access information
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Access the application at:"
echo "   http://todoapp.local"
echo ""
echo "🔍 Useful commands:"
echo "   kubectl get pods -n todo-app"
echo "   kubectl logs -f <pod-name> -n todo-app"
echo "   kubectl port-forward svc/backend 8000:8000 -n todo-app"
echo "   minikube dashboard"
echo ""
