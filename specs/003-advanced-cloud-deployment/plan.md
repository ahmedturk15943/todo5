# Implementation Plan: Advanced Cloud Deployment with Enhanced Task Management

**Branch**: `003-advanced-cloud-deployment` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-advanced-cloud-deployment/spec.md`

## Summary

This plan implements advanced task management features (recurring tasks, reminders, priorities, tags, search/filter) with event-driven architecture using Kafka and Dapr, deployed on Kubernetes (local Minikube and cloud AKS/GKE/OKE). The system evolves from Phase 2's web application and Phase 3's AI chatbot to a distributed, event-driven architecture with real-time synchronization, automated task spawning, and intelligent notifications.

**Primary Requirements**:
- Recurring tasks with automatic next occurrence creation
- Due dates with scheduled reminder notifications
- Priority levels and tag-based organization
- Advanced search and filtering capabilities
- Real-time multi-device synchronization
- Activity history and audit trail
- Event-driven architecture with Kafka topics (task-events, reminders, task-updates)
- Dapr integration for distributed runtime (Pub/Sub, State, Jobs API, Secrets, Service Invocation)
- Kubernetes deployment (Minikube local, AKS/GKE/OKE cloud)
- CI/CD pipeline with GitHub Actions
- Monitoring and logging infrastructure

**Technical Approach**:
- Extend existing PostgreSQL schema with new tables for recurring patterns, reminders, tags, priorities, and activity logs
- Implement event-driven architecture where task operations publish events to Kafka
- Create specialized microservices: Notification Service (consumes reminders), Recurring Task Service (auto-spawns tasks), Audit Service (logs all operations), WebSocket Service (real-time sync)
- Use Dapr sidecars to abstract Kafka, state management, and scheduled jobs
- Deploy Kafka using Strimzi operator on Kubernetes or use Redpanda Cloud
- Implement WebSocket connections for real-time client updates
- Use Dapr Jobs API for exact-time reminder scheduling (not cron polling)
- Deploy with Helm charts extending Phase 4 infrastructure
- Implement CI/CD pipeline for automated testing and deployment

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Node.js 20+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.115+, SQLModel 0.0.22+, aiokafka 0.11+ (Kafka client), dapr 1.14+ (Dapr SDK), websockets 13.0+, APScheduler 3.10+ (fallback scheduling)
- Frontend: Next.js 16+, React 19+, Socket.io-client 4.7+ (WebSocket), TanStack Query 5.0+ (state management)
- Infrastructure: Kafka 3.7+ (Strimzi operator or Redpanda Cloud), Dapr 1.14+, Kubernetes 1.28+, Helm 3.14+

**Storage**:
- Primary: Neon Serverless PostgreSQL (existing from Phase 2) - extended schema
- Event Stream: Kafka topics (task-events, reminders, task-updates)
- State: Dapr state store (PostgreSQL or Redis) for conversation state
- Cache: Redis (optional) for search/filter performance

**Testing**:
- Backend: pytest 8.0+, pytest-asyncio 0.23+, testcontainers 4.0+ (Kafka/PostgreSQL containers)
- Frontend: Vitest 2.0+, React Testing Library 16.0+, Playwright 1.45+ (E2E)
- Integration: Contract tests with Pact, load tests with Locust
- Infrastructure: Helm chart validation, Kubernetes manifest linting

**Target Platform**:
- Local: Minikube 1.33+ on Windows/WSL2, macOS, or Linux
- Cloud: Azure Kubernetes Service (AKS), Google Kubernetes Engine (GKE), or Oracle Kubernetes Engine (OKE)
- Container Runtime: Docker 24.0+, containerd 1.7+

**Project Type**: Web application (backend + frontend) with microservices architecture

**Performance Goals**:
- API response time: <2 seconds for all operations under normal load
- Real-time sync latency: <2 seconds from event to client update
- Reminder delivery: within 30 seconds of scheduled time
- Search/filter: <1 second for 1000+ tasks
- Concurrent users: 1000+ without degradation
- Event throughput: 10,000 events/minute

**Constraints**:
- Must maintain backward compatibility with Phase 2 and Phase 3 features
- Must fit within cloud free tier/trial credits (Azure $200, GCP $300, Oracle free tier)
- Zero downtime deployments (rolling updates)
- All operations must complete within 2 seconds under normal load
- Notification delivery within 30 seconds of scheduled time
- Activity logs retained for 90 days minimum
- Must support both local (Minikube) and cloud (AKS/GKE/OKE) with identical functionality

**Scale/Scope**:
- Users: 1000+ concurrent, 10,000+ total
- Tasks per user: 1000+ with fast search/filter
- Events: 10,000/minute sustained, 50,000/minute peak
- Services: 6 microservices (Backend API, Notification, Recurring Task, Audit, WebSocket, Frontend)
- Kafka topics: 3 (task-events, reminders, task-updates)
- Database tables: 8 new tables (recurring_patterns, reminders, tags, task_tags, priorities, activity_logs, notification_preferences, websocket_connections)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-Driven Development ✅ PASS
- [x] Specification written and approved (spec.md complete)
- [x] Plan being generated from specification (this document)
- [x] Tasks will be broken down from plan (/sp.tasks next)
- [x] Implementation will be generated by Claude Code (/sp.implement)
- [x] No manual coding planned

**Status**: COMPLIANT - Following strict spec-driven workflow

### II. Test-First ✅ PASS
- [x] Tests will be written before implementation
- [x] Red-Green-Refactor cycle will be enforced
- [x] Contract tests for API changes
- [x] Integration tests for event-driven flows
- [x] E2E tests for user scenarios

**Status**: COMPLIANT - TDD approach planned for all components

### III. Incremental Evolution ✅ PASS
- [x] Phase V builds on Phase II (web app) and Phase III (AI chatbot)
- [x] Maintains backward compatibility with existing features
- [x] Extends existing database schema (no breaking changes)
- [x] Adds new services without modifying existing core services
- [x] Independently deployable (can deploy Phase V features incrementally)

**Status**: COMPLIANT - Evolutionary architecture maintained

### IV. Reusable Intelligence ✅ PASS
- [x] Dapr components are reusable across services
- [x] Kafka event schemas are versioned and documented
- [x] Helm charts extend Phase IV charts (reusable deployment patterns)
- [x] MCP tools from Phase III extended for new task attributes
- [x] CI/CD pipeline templates reusable for future phases

**Status**: COMPLIANT - Reusable patterns throughout

### V. Clean Code Architecture ✅ PASS
- [x] Clear separation: models (entities), services (business logic), API (controllers), consumers (event handlers)
- [x] Single Responsibility: each service has one purpose (Notification, Recurring Task, Audit, WebSocket)
- [x] Dependency Inversion: services depend on Dapr abstractions, not concrete Kafka/Redis implementations
- [x] Clear project structure maintained from Phase II
- [x] Self-documenting code with necessary comments for complex event flows

**Status**: COMPLIANT - Clean architecture principles followed

### VI. Cloud-Native Standards ✅ PASS
- [x] Containerization: All services run in Docker containers
- [x] Declarative configuration: Kubernetes manifests and Helm charts
- [x] Immutable infrastructure: No manual configuration
- [x] Observability: Structured logs (JSON), metrics (Prometheus), traces (Jaeger via Dapr)
- [x] Infrastructure as Code: All deployment artifacts versioned in repository

**Status**: COMPLIANT - Cloud-native best practices applied

### VII. AI-Native Integration ✅ PASS
- [x] Phase III AI chatbot extended to support new task attributes (priority, tags, due dates, recurrence)
- [x] MCP tools updated for recurring task creation and reminder scheduling
- [x] Natural language processing for complex queries ("show high-priority work tasks due this week")
- [x] AI-assisted operations with kubectl-ai for Kubernetes management

**Status**: COMPLIANT - AI capabilities extended

### Constitution Check Summary
**Overall Status**: ✅ ALL GATES PASSED

No violations detected. All constitutional principles are followed. Architecture maintains clean separation, evolutionary approach, and cloud-native standards while extending existing functionality.

## Project Structure

### Documentation (this feature)

```text
specs/003-advanced-cloud-deployment/
├── spec.md                    # Feature specification (complete)
├── plan.md                    # This file - architectural plan
├── research.md                # Phase 0 - technical research (to be created)
├── data-model.md              # Phase 1 - entity definitions (to be created)
├── quickstart.md              # Phase 1 - setup instructions (to be created)
├── contracts/                 # Phase 1 - API contracts (to be created)
│   ├── openapi.yaml          # REST API specification
│   ├── events.yaml           # Kafka event schemas
│   └── websocket.yaml        # WebSocket message schemas
├── checklists/
│   └── requirements.md       # Spec quality checklist (complete)
└── tasks.md                   # Phase 2 - implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
# Existing structure from Phase II + Phase III (maintained)
backend/
├── src/
│   ├── models/                      # SQLModel entities
│   │   ├── user.py                 # Existing
│   │   ├── task.py                 # Extended with new fields
│   │   ├── recurring_pattern.py    # NEW - recurrence definitions
│   │   ├── reminder.py             # NEW - scheduled reminders
│   │   ├── tag.py                  # NEW - task tags
│   │   ├── priority.py             # NEW - priority enum
│   │   ├── activity_log.py         # NEW - audit trail
│   │   └── notification_preference.py # NEW - user notification settings
│   ├── services/                    # Business logic
│   │   ├── task_service.py         # Extended with priority, tags, search
│   │   ├── recurring_service.py    # NEW - recurring task logic
│   │   ├── reminder_service.py     # NEW - reminder scheduling
│   │   ├── search_service.py       # NEW - advanced search/filter
│   │   ├── activity_service.py     # NEW - activity logging
│   │   └── notification_service.py # NEW - notification delivery
│   ├── api/
│   │   └── routes/
│   │       ├── tasks.py            # Extended with new endpoints
│   │       ├── recurring.py        # NEW - recurring task endpoints
│   │       ├── reminders.py        # NEW - reminder endpoints
│   │       ├── search.py           # NEW - search/filter endpoints
│   │       ├── activity.py         # NEW - activity log endpoints
│   │       ├── auth.py             # Existing
│   │       └── chat.py             # Extended for new task attributes
│   ├── agents/                      # AI agents
│   │   └── todo_agent.py           # Extended with new MCP tools
│   ├── mcp/                         # Model Context Protocol
│   │   ├── server.py               # Extended with new tools
│   │   └── tools/
│   │       ├── add_task.py         # Extended with priority, tags, due date, recurrence
│   │       ├── list_tasks.py       # Extended with search/filter
│   │       ├── set_reminder.py     # NEW - reminder scheduling
│   │       └── manage_recurrence.py # NEW - recurrence management
│   ├── events/                      # NEW - Event-driven components
│   │   ├── producers/
│   │   │   └── task_producer.py    # Publishes task events to Kafka
│   │   ├── consumers/
│   │   │   ├── recurring_consumer.py # Consumes task-events, spawns next occurrence
│   │   │   ├── notification_consumer.py # Consumes reminders, sends notifications
│   │   │   └── audit_consumer.py   # Consumes task-events, logs to activity_logs
│   │   └── schemas/
│   │       ├── task_event.py       # Task event schema
│   │       ├── reminder_event.py   # Reminder event schema
│   │       └── update_event.py     # Real-time update event schema
│   ├── websocket/                   # NEW - Real-time sync
│   │   ├── server.py               # WebSocket server
│   │   ├── connection_manager.py   # Manages active connections
│   │   └── handlers.py             # Message handlers
│   ├── dapr/                        # NEW - Dapr integration
│   │   ├── pubsub.py               # Dapr Pub/Sub client
│   │   ├── state.py                # Dapr State client
│   │   ├── jobs.py                 # Dapr Jobs API client
│   │   └── secrets.py              # Dapr Secrets client
│   └── main.py                      # FastAPI app (extended)
├── tests/
│   ├── unit/
│   │   ├── test_recurring_service.py
│   │   ├── test_reminder_service.py
│   │   ├── test_search_service.py
│   │   └── test_activity_service.py
│   ├── integration/
│   │   ├── test_event_flow.py      # Test Kafka event flows
│   │   ├── test_websocket.py       # Test real-time sync
│   │   └── test_dapr_integration.py
│   └── contract/
│       ├── test_api_contracts.py
│       └── test_event_schemas.py
├── Dockerfile                       # Extended with new dependencies
└── pyproject.toml                   # Extended with new packages

frontend/
├── src/
│   ├── app/
│   │   ├── tasks/
│   │   │   └── page.tsx            # Extended with priority, tags, search UI
│   │   ├── recurring/
│   │   │   └── page.tsx            # NEW - recurring task management
│   │   └── chat/
│   │       └── page.tsx            # Extended for new task attributes
│   ├── components/
│   │   ├── TaskList.tsx            # Extended with priority badges, tag chips
│   │   ├── TaskForm.tsx            # Extended with priority, tags, due date, recurrence
│   │   ├── SearchBar.tsx           # NEW - advanced search
│   │   ├── FilterPanel.tsx         # NEW - multi-filter UI
│   │   ├── RecurrenceSelector.tsx  # NEW - recurrence pattern picker
│   │   ├── ReminderConfig.tsx      # NEW - reminder configuration
│   │   └── ActivityLog.tsx         # NEW - activity history display
│   ├── hooks/
│   │   ├── useWebSocket.ts         # NEW - WebSocket connection hook
│   │   ├── useRealTimeSync.ts      # NEW - real-time sync hook
│   │   └── useSearch.ts            # NEW - search/filter hook
│   ├── lib/
│   │   ├── api.ts                  # Extended with new endpoints
│   │   └── websocket.ts            # NEW - WebSocket client
│   └── types/
│       ├── task.ts                 # Extended with new fields
│       ├── recurring.ts            # NEW - recurrence types
│       └── reminder.ts             # NEW - reminder types
├── tests/
│   ├── unit/
│   │   └── components/
│   ├── integration/
│   │   └── test_realtime_sync.spec.ts
│   └── e2e/
│       ├── recurring-tasks.spec.ts
│       ├── reminders.spec.ts
│       └── search-filter.spec.ts
├── Dockerfile                       # Extended
└── package.json                     # Extended with new packages

# NEW - Microservices
services/
├── notification-service/            # NEW - Notification delivery
│   ├── src/
│   │   ├── main.py                 # Service entry point
│   │   ├── consumer.py             # Consumes reminder events
│   │   ├── notifier.py             # Sends notifications (email, push, in-app)
│   │   └── dapr_client.py          # Dapr integration
│   ├── Dockerfile
│   └── requirements.txt
├── recurring-service/               # NEW - Recurring task spawning
│   ├── src/
│   │   ├── main.py
│   │   ├── consumer.py             # Consumes task-events
│   │   ├── spawner.py              # Creates next occurrence
│   │   └── dapr_client.py
│   ├── Dockerfile
│   └── requirements.txt
├── audit-service/                   # NEW - Activity logging
│   ├── src/
│   │   ├── main.py
│   │   ├── consumer.py             # Consumes task-events
│   │   ├── logger.py               # Writes to activity_logs
│   │   └── dapr_client.py
│   ├── Dockerfile
│   └── requirements.txt
└── websocket-service/               # NEW - Real-time sync
    ├── src/
    │   ├── main.py
    │   ├── server.py               # WebSocket server
    │   ├── consumer.py             # Consumes task-updates
    │   ├── broadcaster.py          # Broadcasts to connected clients
    │   └── dapr_client.py
    ├── Dockerfile
    └── requirements.txt

# Infrastructure
k8s/                                 # Kubernetes manifests
├── base/                            # Base configurations
│   ├── namespace.yaml
│   ├── configmap.yaml
│   └── secrets.yaml
├── dapr/                            # NEW - Dapr components
│   ├── pubsub-kafka.yaml           # Kafka Pub/Sub component
│   ├── statestore-postgres.yaml    # PostgreSQL state store
│   ├── secretstore-k8s.yaml        # Kubernetes secret store
│   └── jobs-scheduler.yaml         # Jobs API configuration
├── kafka/                           # NEW - Kafka deployment
│   ├── strimzi-operator.yaml       # Strimzi operator
│   └── kafka-cluster.yaml          # Kafka cluster definition
└── monitoring/                      # NEW - Observability
    ├── prometheus.yaml
    ├── grafana.yaml
    └── jaeger.yaml

helm/                                # Helm charts (extends Phase IV)
├── todo-app/
│   ├── Chart.yaml                  # Extended version
│   ├── values.yaml                 # Extended with new services
│   ├── values-local.yaml           # Minikube configuration
│   ├── values-cloud.yaml           # AKS/GKE/OKE configuration
│   └── templates/
│       ├── backend-deployment.yaml # Extended with Dapr sidecar
│       ├── frontend-deployment.yaml
│       ├── notification-deployment.yaml # NEW
│       ├── recurring-deployment.yaml    # NEW
│       ├── audit-deployment.yaml        # NEW
│       ├── websocket-deployment.yaml    # NEW
│       ├── kafka-topics.yaml       # NEW - Kafka topic definitions
│       ├── dapr-components.yaml    # NEW - Dapr component configs
│       └── ingress.yaml            # Extended with new routes

.github/
└── workflows/                       # NEW - CI/CD pipeline
    ├── test.yml                    # Run tests on PR
    ├── build.yml                   # Build and push Docker images
    ├── deploy-local.yml            # Deploy to Minikube
    └── deploy-cloud.yml            # Deploy to AKS/GKE/OKE
```

**Structure Decision**: Web application with microservices architecture. Extends existing Phase II backend and frontend with new microservices for event-driven capabilities. Maintains clean separation between core API (backend), specialized services (notification, recurring, audit, websocket), and client (frontend). All services communicate via Kafka events and Dapr abstractions.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitutional principles are followed.

## Phase 0: Research & Technical Decisions

### Research Tasks

The following technical unknowns require research before design:

1. **Kafka Deployment Strategy**: Strimzi operator vs Redpanda Cloud vs managed Kafka
2. **Dapr Jobs API**: Exact-time scheduling vs cron bindings for reminders
3. **WebSocket Scaling**: Connection management for 1000+ concurrent users
4. **Event Schema Versioning**: Avro vs JSON Schema vs Protobuf
5. **Conflict Resolution**: Offline sync conflict resolution strategies
6. **Notification Delivery**: Push notification providers (FCM, APNs, web push)
7. **Search Performance**: PostgreSQL full-text search vs Elasticsearch
8. **State Management**: Dapr state store (PostgreSQL vs Redis)

### Research Output

See [research.md](./research.md) for detailed findings on each topic.

## Phase 1: Design Artifacts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions, relationships, and validation rules.

**Summary of New Entities**:
- RecurringPattern: Defines recurrence rules (frequency, interval, end condition)
- Reminder: Scheduled notifications with delivery status
- Tag: Task categorization labels
- Priority: Enum (high, medium, low)
- ActivityLog: Audit trail of all operations
- NotificationPreference: User notification settings

### API Contracts

See [contracts/](./contracts/) for complete API specifications:
- `openapi.yaml`: REST API endpoints for tasks, recurring, reminders, search, activity
- `events.yaml`: Kafka event schemas (TaskEvent, ReminderEvent, UpdateEvent)
- `websocket.yaml`: WebSocket message schemas for real-time sync

### Quickstart Guide

See [quickstart.md](./quickstart.md) for:
- Local development setup (Minikube, Dapr, Kafka)
- Cloud deployment (AKS/GKE/OKE)
- Testing procedures
- Troubleshooting guide

## Architecture Diagrams

### System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              KUBERNETES CLUSTER                                       │
│                                                                                       │
│  ┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐        │
│  │    Frontend Pod     │   │    Backend Pod      │   │  Notification Pod   │        │
│  │ ┌───────┐ ┌───────┐ │   │ ┌───────┐ ┌───────┐ │   │ ┌───────┐ ┌───────┐ │        │
│  │ │ Next  │ │ Dapr  │ │   │ │FastAPI│ │ Dapr  │ │   │ │Notif  │ │ Dapr  │ │        │
│  │ │  App  │◀┼▶Sidecar│ │   │ │+ MCP  │◀┼▶Sidecar│ │   │ │Service│◀┼▶Sidecar│ │        │
│  │ └───────┘ └───────┘ │   │ └───────┘ └───────┘ │   │ └───────┘ └───────┘ │        │
│  └──────────┬──────────┘   └──────────┬──────────┘   └──────────┬──────────┘        │
│             │                         │                         │                    │
│  ┌──────────┴──────────┐   ┌──────────┴──────────┐   ┌──────────┴──────────┐        │
│  │  WebSocket Pod      │   │  Recurring Pod      │   │    Audit Pod        │        │
│  │ ┌───────┐ ┌───────┐ │   │ ┌───────┐ ┌───────┐ │   │ ┌───────┐ ┌───────┐ │        │
│  │ │WebSock│ │ Dapr  │ │   │ │Recur  │ │ Dapr  │ │   │ │ Audit │ │ Dapr  │ │        │
│  │ │Service│◀┼▶Sidecar│ │   │ │Service│◀┼▶Sidecar│ │   │ │Service│◀┼▶Sidecar│ │        │
│  │ └───────┘ └───────┘ │   │ └───────┘ └───────┘ │   │ └───────┘ └───────┘ │        │
│  └─────────────────────┘   └─────────────────────┘   └─────────────────────┘        │
│                                       │                                              │
│                          ┌────────────▼────────────┐                                 │
│                          │    DAPR COMPONENTS      │                                 │
│                          │  ┌──────────────────┐   │                                 │
│                          │  │ pubsub.kafka     │───┼────▶ Kafka Cluster             │
│                          │  ├──────────────────┤   │      (Strimzi/Redpanda)        │
│                          │  │ state.postgresql │───┼────▶ Neon DB                    │
│                          │  ├──────────────────┤   │                                 │
│                          │  │ jobs.scheduler   │   │  (Dapr Jobs API)               │
│                          │  ├──────────────────┤   │                                 │
│                          │  │ secretstore.k8s  │   │  (API keys, credentials)        │
│                          │  └──────────────────┘   │                                 │
│                          └─────────────────────────┘                                 │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### Event Flow

```
Task Operation (Create/Update/Complete/Delete)
    │
    ▼
Backend API
    │
    ├─▶ Write to PostgreSQL (immediate)
    │
    └─▶ Publish to Kafka via Dapr Pub/Sub
            │
            ├─▶ task-events topic
            │       │
            │       ├─▶ Recurring Service (if task completed & recurring)
            │       │       └─▶ Create next occurrence
            │       │
            │       └─▶ Audit Service
            │               └─▶ Write to activity_logs
            │
            ├─▶ reminders topic (if due date set)
            │       │
            │       └─▶ Notification Service
            │               └─▶ Schedule via Dapr Jobs API
            │                   └─▶ Send notification at scheduled time
            │
            └─▶ task-updates topic
                    │
                    └─▶ WebSocket Service
                            └─▶ Broadcast to all connected clients
```

## Next Steps

1. **Phase 0 Complete**: Create `research.md` with technical decisions
2. **Phase 1 Complete**: Create `data-model.md`, `contracts/`, and `quickstart.md`
3. **Phase 2 Ready**: Run `/sp.tasks` to generate implementation tasks
4. **Implementation**: Run `/sp.implement` to execute tasks via Claude Code

## Notes

- All services use Dapr sidecars for infrastructure abstraction
- Kafka provides event backbone for decoupled microservices
- WebSocket service enables real-time sync without polling
- Dapr Jobs API provides exact-time scheduling (superior to cron polling)
- Helm charts enable consistent deployment across local and cloud
- CI/CD pipeline automates testing and deployment
- Monitoring stack (Prometheus, Grafana, Jaeger) provides observability
