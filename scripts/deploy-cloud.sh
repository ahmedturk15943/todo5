#!/bin/bash
set -e

# Configuration
CLOUD_PROVIDER=${1:-"gke"}  # gke, aks, or oke
CLUSTER_NAME=${2:-"todo-app-cluster"}
REGION=${3:-"us-central1"}
NAMESPACE="todo-app"

echo "🚀 Deploying Todo App to $CLOUD_PROVIDER..."

# Verify kubectl is configured
if ! kubectl cluster-info > /dev/null 2>&1; then
    echo "❌ kubectl is not configured. Please configure kubectl first."
    exit 1
fi

# Install cert-manager for TLS certificates
echo "🔒 Installing cert-manager..."
if ! kubectl get namespace cert-manager > /dev/null 2>&1; then
    kubectl create namespace cert-manager
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    helm upgrade --install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --version v1.13.0 \
        --set installCRDs=true \
        --wait
fi

# Install NGINX Ingress Controller
echo "🌐 Installing NGINX Ingress Controller..."
if ! helm list -n ingress-nginx | grep -q ingress-nginx; then
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer \
        --wait
fi

# Install Dapr
echo "🔧 Installing Dapr..."
if ! helm list -n dapr-system | grep -q dapr; then
    helm repo add dapr https://dapr.github.io/helm-charts/
    helm repo update
    helm upgrade --install dapr dapr/dapr \
        --version=1.12 \
        --namespace dapr-system \
        --create-namespace \
        --set global.ha.enabled=true \
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
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=600s -n kafka

# Create namespace
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Create secrets (you should replace these with actual values)
echo "🔐 Creating secrets..."
kubectl create secret generic postgres-credentials \
    --from-literal=username=todoapp \
    --from-literal=password=$(openssl rand -base64 32) \
    --from-literal=database=todoapp \
    --namespace $NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic redis-credentials \
    --from-literal=password=$(openssl rand -base64 32) \
    --namespace $NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

# Install Todo App
echo "📦 Installing Todo App..."
helm dependency update ../helm/todo-app/

helm upgrade --install todo-app ../helm/todo-app/ \
    --values ../helm/todo-app/values-cloud.yaml \
    --namespace $NAMESPACE \
    --wait \
    --timeout 15m

# Wait for all pods to be ready
echo "⏳ Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod --all -n $NAMESPACE --timeout=600s

# Get LoadBalancer IP
echo "🔍 Getting LoadBalancer IP..."
EXTERNAL_IP=""
while [ -z $EXTERNAL_IP ]; do
    echo "Waiting for external IP..."
    EXTERNAL_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    [ -z "$EXTERNAL_IP" ] && sleep 10
done

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 LoadBalancer IP: $EXTERNAL_IP"
echo ""
echo "📝 Next steps:"
echo "   1. Update your DNS records to point todoapp.com to $EXTERNAL_IP"
echo "   2. Wait for DNS propagation"
echo "   3. Access the application at https://todoapp.com"
echo ""
echo "🔍 Useful commands:"
echo "   kubectl get pods -n $NAMESPACE"
echo "   kubectl logs -f <pod-name> -n $NAMESPACE"
echo "   kubectl get ingress -n $NAMESPACE"
echo "   helm list -n $NAMESPACE"
echo ""
