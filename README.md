# Todo Application - Phase 5 (Advanced Cloud Deployment)

**Version**: 5.0.0
**Phase**: Phase 5 - Event-Driven Architecture with Cloud Deployment
**Status**: Production-Ready Microservices Application

---

## Overview

Enterprise-grade todo application with event-driven architecture, real-time synchronization, and cloud-native deployment. Features recurring tasks, smart reminders, advanced search, activity history, and multi-device sync.

**Core Features**:
- User authentication (signup, signin, signout)
- Multi-user support with complete data isolation
- Task CRUD operations with priorities and tags
- Recurring tasks (daily, weekly, monthly patterns)
- Smart reminders with exact-time scheduling
- Advanced search with full-text indexing
- Real-time multi-device synchronization
- Activity history and audit trail
- Responsive design (mobile to desktop)

**Technology Stack**:
- **Frontend**: Next.js 16+ with App Router, TypeScript, Tailwind CSS, Socket.io
- **Backend**: Python FastAPI with SQLModel ORM, Dapr
- **Database**: PostgreSQL with full-text search
- **Message Broker**: Apache Kafka with Strimzi operator
- **Cache**: Redis for WebSocket scaling
- **Event-Driven**: Dapr Pub/Sub, State Store, Jobs API, Secrets
- **Microservices**: WebSocket, Notification, Recurring, Audit services
- **Orchestration**: Kubernetes with Helm charts
- **Architecture**: Event-driven microservices with CQRS patterns

---

## Prerequisites

### Local Development Requirements
- Python 3.11+
- Node.js 18+
- Docker Desktop (for Kafka, Redis, PostgreSQL)
- Minikube (for local Kubernetes testing)
- Helm 3.x
- kubectl

### Cloud Deployment Requirements
- Kubernetes cluster (GKE, AKS, or OKE)
- kubectl configured for your cluster
- Helm 3.x
- Container registry (Docker Hub, GCR, ACR)

---

## Quick Start (Local Development)

### 1. Start Infrastructure Services

```bash
# Start PostgreSQL, Redis, and Kafka with Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env and configure:
# - DATABASE_URL=postgresql://todoapp:todoapp@localhost:5432/todoapp
# - KAFKA_BOOTSTRAP_SERVERS=localhost:9092
# - REDIS_URL=redis://localhost:6379

# Run database migrations
cd backend
alembic upgrade head

# Start backend server
uvicorn src.main:app --reload --port 8000
```

### 3. Start Microservices

```bash
# Terminal 1: WebSocket Service
cd services/websocket-service
pip install -r requirements.txt
python -m src.server

# Terminal 2: Notification Service
cd services/notification-service
pip install -r requirements.txt
python -m src.main

# Terminal 3: Recurring Service
cd services/recurring-service
pip install -r requirements.txt
python -m src.main

# Terminal 4: Audit Service
cd services/audit-service
pip install -r requirements.txt
python -m src.main
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local:
# - NEXT_PUBLIC_API_URL=http://localhost:8000
# - NEXT_PUBLIC_WS_URL=http://localhost:8001

# Start frontend server
npm run dev
```

Frontend will start at `http://localhost:3000`

---

## Usage

### 1. Create Account & Sign In

1. Visit `http://localhost:3000`
2. Click "Sign Up" and create an account
3. Sign in with your credentials

### 2. Manage Tasks

**Create Task**:
- Click "+ Add Task"
- Enter title (required)
- Add description (optional)
- Set priority (high, medium, low)
- Add tags for organization
- Set due date (optional)
- Configure recurrence pattern (optional)
- Add reminder (optional)
- Click "Create Task"

**View and Filter Tasks**:
- View all tasks on main page
- Use search bar for full-text search
- Filter by status (incomplete/complete)
- Filter by priority (high/medium/low)
- Filter by tags
- Sort by various fields

**Update Task**:
- Click "Edit" on any task
- Modify any field
- Changes sync in real-time across all devices

**Mark Complete**:
- Click checkbox next to task
- Task marked as complete
- If recurring, next occurrence is automatically created

**Delete Task**:
- Click "Delete" on any task
- Task permanently removed

### 3. Recurring Tasks

**Create Recurring Task**:
- Select recurrence pattern: Daily, Weekly, Monthly, or Custom
- Set interval (e.g., every 2 days)
- For weekly: select days of week
- For monthly: select day of month
- Set end condition: Never, After N occurrences, or By date

**How It Works**:
- When you complete a recurring task, the next occurrence is automatically created
- Original task is marked complete and linked to parent
- Recurring service monitors task-events topic via Kafka
- Next occurrence calculated based on pattern

### 4. Smart Reminders

**Set Reminder**:
- Add due date to task first
- Click "Add Reminder"
- Choose preset (15min, 30min, 1hr, 1day before) or custom time
- Reminder scheduled via Dapr Jobs API

**Notification Delivery**:
- Web push notifications (if enabled)
- Email notifications (if configured)
- In-app notifications
- Respects quiet hours preferences

### 5. Real-Time Sync

**Multi-Device Sync**:
- Open app on multiple devices
- Changes sync instantly (< 2 seconds)
- WebSocket connection with automatic reconnection
- Connection status indicator in UI
- Optimistic locking prevents conflicts

### 6. Activity History

**View Activity Log**:
- Click "Activity" in navigation
- See all task operations (created, updated, completed, deleted)
- Filter by action type
- View changes made to each task
- Audit trail for accountability

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer / Ingress                  │
└────────────┬────────────────────────────────────┬────────────────┘
             │                                    │
    ┌────────▼────────┐                  ┌───────▼────────┐
    │    Frontend     │                  │  WebSocket     │
    │   (Next.js)     │                  │   Service      │
    └────────┬────────┘                  └───────┬────────┘
             │                                    │
    ┌────────▼────────────────────────────────────▼────────┐
    │              Backend API (FastAPI + Dapr)            │
    └────────┬─────────────────────────────────┬───────────┘
             │                                 │
    ┌────────▼────────┐              ┌────────▼────────────┐
    │   PostgreSQL    │              │   Apache Kafka      │
    │   (Database)    │              │  (Message Broker)   │
    └─────────────────┘              └────────┬────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────┐
                    │                         │                     │
           ┌────────▼────────┐    ┌──────────▼──────┐   ┌─────────▼────────┐
           │  Notification   │    │   Recurring     │   │     Audit        │
           │    Service      │    │    Service      │   │    Service       │
           └─────────────────┘    └─────────────────┘   └──────────────────┘
```

### Event Flow

1. **Task Created/Updated** → Backend publishes to `task-events` and `task-updates` topics
2. **task-events** → Consumed by Recurring Service (spawns next occurrence) and Audit Service (logs activity)
3. **task-updates** → Consumed by WebSocket Service → Broadcasts to connected clients
4. **Reminder Due** → Dapr Jobs API triggers → Backend publishes to `reminders` topic → Notification Service sends notifications

### Microservices

- **Backend API**: Main REST API, task management, authentication
- **WebSocket Service**: Real-time synchronization, Socket.io server, Redis Pub/Sub for scaling
- **Notification Service**: Multi-channel notifications (web push, email, in-app)
- **Recurring Service**: Spawns next occurrence when recurring tasks completed
- **Audit Service**: Activity logging and audit trail

### Data Stores

- **PostgreSQL**: Primary database with full-text search
- **Redis**: WebSocket connection state and Pub/Sub for horizontal scaling
- **Kafka**: Event streaming and message broker (3 topics: task-events, task-updates, reminders)

### Dapr Components

- **Pub/Sub**: Kafka integration for event publishing/subscribing
- **State Store**: PostgreSQL for distributed state management
- **Jobs API**: Exact-time reminder scheduling (no polling)
- **Secrets Store**: Kubernetes secrets integration

---

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### API Endpoints

**Authentication**:
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/signin` - Authenticate and get JWT token

**Tasks**:
- `GET /api/users/{user_id}/tasks` - List all tasks
- `POST /api/users/{user_id}/tasks` - Create task
- `GET /api/users/{user_id}/tasks/{task_id}` - Get task
- `PUT /api/users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/users/{user_id}/tasks/{task_id}` - Delete task
- `PATCH /api/users/{user_id}/tasks/{task_id}/complete` - Toggle completion

**Recurring Tasks**:
- `POST /api/recurring` - Create recurring pattern
- `GET /api/recurring` - List patterns
- `GET /api/recurring/{id}` - Get pattern
- `DELETE /api/recurring/{id}` - Deactivate pattern

**Reminders**:
- `POST /api/reminders` - Create reminder
- `GET /api/reminders` - List reminders
- `DELETE /api/reminders/{id}` - Cancel reminder

**Tags**:
- `GET /api/tags` - List tags
- `POST /api/tags` - Create tag
- `PUT /api/tags/{id}` - Update tag
- `DELETE /api/tags/{id}` - Delete tag
- `POST /api/tasks/{task_id}/tags/{tag_id}` - Add tag to task
- `DELETE /api/tasks/{task_id}/tags/{tag_id}` - Remove tag from task

**Search**:
- `GET /api/search` - Search and filter tasks
- `GET /api/search/count` - Get task counts

**Activity**:
- `GET /api/activity` - Get user activities
- `GET /api/activity/task/{task_id}` - Get task activities
- `GET /api/activity/recent` - Get recent activities

---

## Project Structure

```
phase1/
├── backend/
│   ├── src/
│   │   ├── models/              # SQLModel entities
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   ├── recurring_pattern.py
│   │   │   ├── reminder.py
│   │   │   ├── tag.py
│   │   │   └── activity_log.py
│   │   ├── services/            # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── task_service.py
│   │   │   ├── recurring_service.py
│   │   │   ├── reminder_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── search_service.py
│   │   │   └── activity_service.py
│   │   ├── api/
│   │   │   ├── routes/          # API endpoints
│   │   │   │   ├── auth.py
│   │   │   │   ├── tasks.py
│   │   │   │   ├── recurring.py
│   │   │   │   ├── reminders.py
│   │   │   │   ├── tags.py
│   │   │   │   ├── search.py
│   │   │   │   └── activity.py
│   │   │   ├── middleware/      # JWT auth, error handling
│   │   │   └── dependencies.py
│   │   ├── events/              # Event schemas and producers
│   │   │   ├── schemas/
│   │   │   │   ├── base.py
│   │   │   │   ├── task_event.py
│   │   │   │   ├── reminder_event.py
│   │   │   │   └── update_event.py
│   │   │   └── producers/
│   │   │       └── task_producer.py
│   │   ├── dapr/                # Dapr clients
│   │   │   ├── pubsub.py
│   │   │   ├── state.py
│   │   │   ├── jobs.py
│   │   │   └── secrets.py
│   │   ├── database.py          # Database connection
│   │   ├── config.py            # Configuration
│   │   └── main.py              # FastAPI app entry point
│   ├── alembic/                 # Database migrations
│   │   └── versions/
│   ├── pyproject.toml
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   │   ├── (auth)/          # Auth pages
│   │   │   ├── (dashboard)/     # Protected pages
│   │   │   └── activity/        # Activity history
│   │   ├── components/
│   │   │   ├── auth/            # Auth forms
│   │   │   ├── tasks/           # Task components
│   │   │   ├── RecurrenceSelector.tsx
│   │   │   ├── ReminderConfig.tsx
│   │   │   ├── PrioritySelector.tsx
│   │   │   ├── TagInput.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   ├── FilterPanel.tsx
│   │   │   ├── ActivityLog.tsx
│   │   │   └── Navigation.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useRealTimeSync.ts
│   │   │   └── useSearch.ts
│   │   ├── lib/
│   │   │   ├── api.ts           # API client
│   │   │   ├── auth.ts          # Auth utilities
│   │   │   └── websocket.ts     # WebSocket client
│   │   ├── types/               # TypeScript types
│   │   │   ├── task.ts
│   │   │   ├── recurring.ts
│   │   │   ├── reminder.ts
│   │   │   └── tag.ts
│   │   └── styles/              # Global styles
│   ├── package.json
│   └── README.md
├── services/
│   ├── websocket-service/       # Real-time sync service
│   │   ├── src/
│   │   │   ├── server.py
│   │   │   ├── connection_manager.py
│   │   │   ├── consumer.py
│   │   │   └── broadcaster.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── notification-service/    # Notification delivery
│   │   ├── src/
│   │   │   ├── main.py
│   │   │   ├── consumer.py
│   │   │   └── notifier.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── recurring-service/       # Recurring task spawning
│   │   ├── src/
│   │   │   ├── main.py
│   │   │   └── consumer.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── audit-service/           # Activity logging
│       ├── src/
│       │   ├── consumer.py
│       │   └── logger.py
│       ├── Dockerfile
│       └── requirements.txt
├── helm/
│   └── todo-app/                # Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-local.yaml
│       ├── values-cloud.yaml
│       └── templates/
│           ├── backend-deployment.yaml
│           ├── frontend-deployment.yaml
│           ├── websocket-deployment.yaml
│           ├── notification-deployment.yaml
│           ├── recurring-deployment.yaml
│           ├── audit-deployment.yaml
│           ├── services.yaml
│           ├── ingress.yaml
│           ├── hpa.yaml
│           ├── secrets.yaml
│           └── dapr-components.yaml
├── k8s/
│   ├── kafka/                   # Kafka manifests
│   │   ├── kafka-cluster.yaml
│   │   └── topics.yaml
│   └── dapr/                    # Dapr components
│       ├── pubsub-kafka.yaml
│       ├── statestore-postgres.yaml
│       ├── secretstore-k8s.yaml
│       └── jobs-scheduler.yaml
├── scripts/
│   ├── deploy-local.sh          # Minikube deployment
│   └── deploy-cloud.sh          # Cloud deployment
├── specs/                       # Feature specifications
├── history/                     # Prompt history records
└── README.md                    # This file
```

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m contract

# Run with coverage
pytest --cov=src --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm test -- --coverage
```

---

## Deployment

### Local Kubernetes Deployment (Minikube)

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Run deployment script
chmod +x scripts/deploy-local.sh
./scripts/deploy-local.sh

# Access application
# Add to /etc/hosts: <minikube-ip> todoapp.local
# Visit: http://todoapp.local
```

### Cloud Deployment (GKE/AKS/OKE)

```bash
# Configure kubectl for your cluster
# For GKE:
gcloud container clusters get-credentials <cluster-name> --region <region>

# For AKS:
az aks get-credentials --resource-group <rg> --name <cluster-name>

# For OKE:
oci ce cluster create-kubeconfig --cluster-id <cluster-id>

# Build and push Docker images
docker build -t <registry>/todoapp/backend:5.0.0 ./backend
docker build -t <registry>/todoapp/frontend:5.0.0 ./frontend
docker build -t <registry>/todoapp/websocket-service:5.0.0 ./services/websocket-service
docker build -t <registry>/todoapp/notification-service:5.0.0 ./services/notification-service
docker build -t <registry>/todoapp/recurring-service:5.0.0 ./services/recurring-service
docker build -t <registry>/todoapp/audit-service:5.0.0 ./services/audit-service

docker push <registry>/todoapp/backend:5.0.0
docker push <registry>/todoapp/frontend:5.0.0
docker push <registry>/todoapp/websocket-service:5.0.0
docker push <registry>/todoapp/notification-service:5.0.0
docker push <registry>/todoapp/recurring-service:5.0.0
docker push <registry>/todoapp/audit-service:5.0.0

# Update values-cloud.yaml with your registry and domain

# Run deployment script
chmod +x scripts/deploy-cloud.sh
./scripts/deploy-cloud.sh gke todo-app-cluster us-central1

# Get LoadBalancer IP
kubectl get svc ingress-nginx-controller -n ingress-nginx

# Update DNS records to point your domain to the LoadBalancer IP
# Wait for DNS propagation
# Access: https://todoapp.com
```

### Helm Commands

```bash
# Install/Upgrade
helm upgrade --install todo-app ./helm/todo-app/ \
  --values ./helm/todo-app/values-local.yaml \
  --namespace todo-app \
  --create-namespace

# Uninstall
helm uninstall todo-app -n todo-app

# View status
helm status todo-app -n todo-app

# View values
helm get values todo-app -n todo-app
```

---

## Troubleshooting

### Backend Issues

**Database Connection Error**:
- Verify `DATABASE_URL` in `.env` is correct
- Ensure Neon database is accessible
- Check connection string includes `sslmode=require`

**JWT Authentication Error**:
- Verify `BETTER_AUTH_SECRET` matches frontend
- Check token expiry (default 7 days)
- Ensure Authorization header format: `Bearer <token>`

### Frontend Issues

**API Connection Error**:
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check backend server is running
- Verify CORS is configured correctly

**Authentication Issues**:
- Clear browser localStorage and cookies
- Verify `BETTER_AUTH_SECRET` matches backend
- Check browser console for errors

---

## Security Notes

- Passwords are hashed with bcrypt (10+ rounds)
- JWT tokens expire after 7 days
- All API endpoints require authentication (except signup/signin)
- User data is completely isolated (users can only access their own tasks)
- HTML is escaped to prevent XSS attacks
- CORS is configured to allow only specified origins

---

## Phase Comparison

**Phase I** (Console App):
- In-memory storage
- Single user
- CLI interface
- No authentication
- Data lost on exit

**Phase II** (Web App):
- PostgreSQL persistence
- Multi-user support
- Web interface
- JWT authentication
- Data persists across sessions

---

## Next Steps (Future Phases)

**Phase III**: AI-Native Features
- Natural language task creation
- Smart task suggestions
- Conversational interface

**Phase IV**: Cloud-Native Deployment
- Kubernetes deployment
- Infrastructure as Code
- Observability and monitoring
- CI/CD pipelines

---

## License

Copyright (c) 2025 Evolution of Todo Project. All rights reserved.
