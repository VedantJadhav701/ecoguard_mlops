#!/bin/bash

# EcoGuard MLOps Setup Script
# This script helps set up the MLOps environment

set -e

echo "╔═══════════════════════════════════════════════╗"
echo "║  EcoGuard MLOps Setup                         ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is required but not installed. Please install it."
        exit 1
    fi
    echo "✅ $1 found"
}

check_command "docker"
check_command "docker-compose"
check_command "git"

# Get deployment choice
echo ""
echo "Select deployment option:"
echo "1. Local Docker Compose (development)"
echo "2. Kubernetes (production)"
read -p "Enter choice (1-2): " choice

# Setup environment
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env created. Please update it with your values."
else
    echo "✅ .env already exists"
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt --upgrade
echo "✅ Dependencies installed"

# Run tests
echo ""
read -p "Run tests? (y/n): " run_tests
if [ "$run_tests" == "y" ]; then
    echo "Running tests..."
    pip install -r requirements-dev.txt
    pytest tests/ -v --cov=. || true
fi

# Deployment choice
if [ "$choice" == "1" ]; then
    echo ""
    echo "Starting Docker Compose stack..."
    docker-compose build
    docker-compose up -d
    
    echo ""
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  Docker Compose is running                   ║"
    echo "╠═══════════════════════════════════════════════╣"
    echo "║  API:        http://localhost:8000             ║"
    echo "║  MLflow:     http://localhost:5000             ║"
    echo "║  Prometheus: http://localhost:9090             ║"
    echo "║  Grafana:    http://localhost:3000             ║"
    echo "║  (Grafana password: admin/admin)              ║"
    echo "╚═══════════════════════════════════════════════╝"

elif [ "$choice" == "2" ]; then
    echo ""
    echo "Kubernetes deployment..."
    
    check_command "kubectl"
    
    read -p "Enter your container registry (e.g., ghcr.io/username): " registry
    
    echo "Building Docker image..."
    docker build -t ${registry}/ecoguard:latest .
    
    read -p "Push image to registry? (y/n): " push_image
    if [ "$push_image" == "y" ]; then
        docker push ${registry}/ecoguard:latest
        echo "✅ Image pushed"
    fi
    
    echo ""
    echo "Updating Kubernetes manifests..."
    sed -i.bak "s|image: ghcr.io/yourusername/ecoguard:latest|image: ${registry}/ecoguard:latest|g" k8s/01-deployment.yml
    
    echo "Applying Kubernetes manifests..."
    kubectl apply -f k8s/
    
    echo ""
    echo "Waiting for deployment..."
    kubectl rollout status deployment/ecoguard-api -n ecoguard
    
    echo ""
    echo "╔═══════════════════════════════════════════════╗"
    echo "║  Kubernetes deployment complete               ║"
    echo "╠═══════════════════════════════════════════════╣"
    echo "║  To access services:                           ║"
    echo "║  kubectl port-forward -n ecoguard svc/ecoguard-api 8000:8000"
    echo "║  kubectl port-forward -n ecoguard svc/grafana 3000:3000"
    echo "╚═══════════════════════════════════════════════╝"
fi

echo ""
echo "Setup complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Check MLOPS_IMPLEMENTATION_SUMMARY.md for detailed information"
echo "2. Update .env with your configuration"
echo "3. Add GitHub secrets for CI/CD (see GITHUB_SECRETS_SETUP.md)"
echo "4. Review and update Kubernetes manifests with your values"
echo ""
echo "For more information, see MLOPS_DEPLOYMENT_GUIDE.md"
