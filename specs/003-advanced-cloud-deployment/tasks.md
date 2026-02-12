# Tasks: Advanced Cloud Deployment with Enhanced Task Management

**Input**: Design documents from `/specs/003-advanced-cloud-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Web app structure: `backend/src/`, `frontend/src/`, `services/`, `k8s/`, `helm/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and infrastructure setup

- [x] T001 Review existing Phase 2 and Phase 3 codebase structure
- [ ] T002 [P] Install Dapr CLI and initialize Dapr in local environment (USER ACTION REQUIRED)
- [ ] T003 [P] Install Strimzi operator for Kafka on Minikube (USER ACTION REQUIRED)
- [x] T004 [P] Update backend/pyproject.toml with new dependencies (aiokafka, dapr, websockets, APScheduler)
- [x] T005 [P] Update frontend/package.json with new dependencies (socket.io-client, @tanstack/react-query)
- [x] T006 Create k8s/base/ directory structure for Kubernetes manifests
- [x] T007 Create services/ directory for new microservices
- [x] T008 [P] Setup Prometheus and Grafana for monitoring in k8s/monitoring/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Create Alembic migration for Task table extensions in backend/alembic/versions/001_extend_tasks.py
- [ ] T010 [P] Create database migration for new tables (recurring_patterns, reminders, tags, task_tags, activity_logs, notification_preferences) in backend/alembic/versions/002_create_new_tables.py
- [ ] T011 [P] Create full-text search trigger migration in backend/alembic/versions/003_fulltext_search.py
- [ ] T012 Run database migrations to apply schema changes
- [ ] T013 [P] Deploy Kafka cluster using Strimzi in k8s/kafka/kafka-cluster.yaml
- [ ] T014 [P] Create Dapr Pub/Sub component for Kafka in k8s/dapr/pubsub-kafka.yaml
- [ ] T015 [P] Create Dapr state store component for PostgreSQL in k8s/dapr/statestore-postgres.yaml
- [ ] T016 [P] Create Dapr secrets component for Kubernetes in k8s/dapr/secretstore-k8s.yaml
- [ ] T017 [P] Create Dapr Jobs API configuration in k8s/dapr/jobs-scheduler.yaml
- [ ] T018 Create Kafka topics (task-events, reminders, task-updates) in k8s/kafka/topics.yaml
- [ ] T019 [P] Implement Dapr Pub/Sub client wrapper in backend/src/dapr/pubsub.py
- [ ] T020 [P] Implement Dapr State client wrapper in backend/src/dapr/state.py
- [ ] T021 [P] Implement Dapr Jobs API client wrapper in backend/src/dapr/jobs.py
- [ ] T022 [P] Implement Dapr Secrets client wrapper in backend/src/dapr/secrets.py
- [ ] T023 Create event schema base classes in backend/src/events/schemas/base.py
- [ ] T024 Update backend/src/main.py to initialize Dapr clients

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Recurring Task Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks that repeat automatically on a schedule (daily, weekly, monthly)

**Independent Test**: Create a recurring task (e.g., "Daily standup at 9 AM"), mark it complete, and verify the next occurrence is automatically created with the correct due date

### Implementation for User Story 1

- [ ] T025 [P] [US1] Create RecurringPattern model in backend/src/models/recurring_pattern.py
- [ ] T026 [P] [US1] Extend Task model with recurring fields (recurring_pattern_id, parent_task_id) in backend/src/models/task.py
- [ ] T027 [US1] Implement RecurringService for pattern management in backend/src/services/recurring_service.py
- [ ] T028 [US1] Implement next occurrence calculation logic in RecurringService
- [ ] T029 [US1] Create TaskEvent schema in backend/src/events/schemas/task_event.py
- [ ] T030 [US1] Implement task event producer in backend/src/events/producers/task_producer.py
- [ ] T031 [US1] Create recurring task API endpoints (POST /api/recurring, GET /api/recurring, PUT /api/recurring/{id}, DELETE /api/recurring/{id}) in backend/src/api/routes/recurring.py
- [ ] T032 [US1] Update task completion endpoint to publish task-events in backend/src/api/routes/tasks.py
- [ ] T033 [US1] Create Recurring Task Service microservice structure in services/recurring-service/
- [ ] T034 [US1] Implement recurring task consumer in services/recurring-service/src/consumer.py
- [ ] T035 [US1] Implement task spawner logic in services/recurring-service/src/spawner.py
- [ ] T036 [US1] Create Dockerfile for recurring service in services/recurring-service/Dockerfile
- [ ] T037 [P] [US1] Create RecurrenceSelector component in frontend/src/components/RecurrenceSelector.tsx
- [ ] T038 [P] [US1] Update TaskForm component to include recurrence options in frontend/src/components/TaskForm.tsx
- [ ] T039 [P] [US1] Update TaskList component to show recurring indicator in frontend/src/components/TaskList.tsx
- [ ] T040 [US1] Add recurring task API methods to frontend API client in frontend/src/lib/api.ts
- [ ] T041 [US1] Create recurring task management page in frontend/src/app/recurring/page.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create recurring tasks and see automatic spawning

---

## Phase 4: User Story 2 - Due Dates and Smart Reminders (Priority: P1)

**Goal**: Enable users to set due dates on tasks and receive timely notifications before tasks are due

**Independent Test**: Create a task with a due date 2 hours in the future, set a reminder for 1 hour before, and verify the notification is received at the correct time

### Implementation for User Story 2

- [ ] T042 [P] [US2] Create Reminder model in backend/src/models/reminder.py
- [ ] T043 [P] [US2] Create NotificationPreference model in backend/src/models/notification_preference.py
- [ ] T044 [US2] Implement ReminderService for scheduling in backend/src/services/reminder_service.py
- [ ] T045 [US2] Implement NotificationService for delivery in backend/src/services/notification_service.py
- [ ] T046 [US2] Create ReminderEvent schema in backend/src/events/schemas/reminder_event.py
- [ ] T047 [US2] Create reminder API endpoints (POST /api/reminders, GET /api/reminders, DELETE /api/reminders/{id}) in backend/src/api/routes/reminders.py
- [ ] T048 [US2] Implement Dapr Jobs API scheduling in ReminderService
- [ ] T049 [US2] Create job trigger callback endpoint in backend/src/api/routes/jobs.py
- [ ] T050 [US2] Create Notification Service microservice structure in services/notification-service/
- [ ] T051 [US2] Implement notification consumer in services/notification-service/src/consumer.py
- [ ] T052 [US2] Implement multi-channel notifier (web push, email, in-app) in services/notification-service/src/notifier.py
- [ ] T053 [US2] Create Dockerfile for notification service in services/notification-service/Dockerfile
- [ ] T054 [P] [US2] Create ReminderConfig component in frontend/src/components/ReminderConfig.tsx
- [ ] T055 [P] [US2] Update TaskForm to include due date and reminder options in frontend/src/components/TaskForm.tsx
- [ ] T056 [P] [US2] Update TaskList to show due date urgency indicators in frontend/src/components/TaskList.tsx
- [ ] T057 [US2] Implement web push notification subscription in frontend/src/lib/notifications.ts
- [ ] T058 [US2] Add reminder API methods to frontend API client in frontend/src/lib/api.ts

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - recurring tasks with reminders

---

## Phase 5: User Story 3 - Task Prioritization and Organization (Priority: P2)

**Goal**: Enable users to assign priority levels and organize tasks with tags

**Independent Test**: Create tasks with different priorities, add tags like "work", "personal", "urgent", and verify tasks can be filtered and sorted by these attributes

### Implementation for User Story 3

- [ ] T059 [P] [US3] Create Tag model in backend/src/models/tag.py
- [ ] T060 [P] [US3] Create TaskTag join model in backend/src/models/task_tag.py
- [ ] T061 [P] [US3] Add priority field to Task model in backend/src/models/task.py
- [ ] T062 [US3] Extend TaskService with priority and tag operations in backend/src/services/task_service.py
- [ ] T063 [US3] Create tag API endpoints (POST /api/tags, GET /api/tags, PUT /api/tags/{id}, DELETE /api/tags/{id}) in backend/src/api/routes/tags.py
- [ ] T064 [US3] Update task endpoints to support priority and tags in backend/src/api/routes/tasks.py
- [ ] T065 [P] [US3] Create priority selector component in frontend/src/components/PrioritySelector.tsx
- [ ] T066 [P] [US3] Create tag input component in frontend/src/components/TagInput.tsx
- [ ] T067 [P] [US3] Update TaskForm to include priority and tags in frontend/src/components/TaskForm.tsx
- [ ] T068 [P] [US3] Update TaskList to show priority badges and tag chips in frontend/src/components/TaskList.tsx
- [ ] T069 [US3] Add tag management API methods to frontend API client in frontend/src/lib/api.ts
- [ ] T070 [US3] Update task types to include priority and tags in frontend/src/types/task.ts

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Advanced Search and Filtering (Priority: P2)

**Goal**: Enable users to quickly find specific tasks using search and apply multiple filters simultaneously

**Independent Test**: Create 20+ tasks with various attributes, then search for a keyword and apply filters (e.g., "show incomplete high-priority tasks due this week")

### Implementation for User Story 4

- [ ] T071 [US4] Implement SearchService with PostgreSQL full-text search in backend/src/services/search_service.py
- [ ] T072 [US4] Create search API endpoint (GET /api/search) in backend/src/api/routes/search.py
- [ ] T073 [US4] Implement multi-filter query builder in SearchService
- [ ] T074 [US4] Add search vector indexing to Task model in backend/src/models/task.py
- [ ] T075 [P] [US4] Create SearchBar component in frontend/src/components/SearchBar.tsx
- [ ] T076 [P] [US4] Create FilterPanel component in frontend/src/components/FilterPanel.tsx
- [ ] T077 [US4] Implement useSearch hook in frontend/src/hooks/useSearch.ts
- [ ] T078 [US4] Add search API methods to frontend API client in frontend/src/lib/api.ts
- [ ] T079 [US4] Integrate search and filters into task list page in frontend/src/app/tasks/page.tsx

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Real-Time Multi-Device Sync (Priority: P2)

**Goal**: Enable instant synchronization of task changes across all user devices without manual refresh

**Independent Test**: Open the app on two devices, create a task on device A, and verify it appears on device B within 2 seconds without refresh

### Implementation for User Story 5

- [ ] T080 [US5] Create UpdateEvent schema in backend/src/events/schemas/update_event.py
- [ ] T081 [US5] Update task event producer to publish to task-updates topic in backend/src/events/producers/task_producer.py
- [ ] T082 [US5] Create WebSocket Service microservice structure in services/websocket-service/
- [ ] T083 [US5] Implement WebSocket server with Socket.io in services/websocket-service/src/server.py
- [ ] T084 [US5] Implement connection manager in services/websocket-service/src/connection_manager.py
- [ ] T085 [US5] Implement task-updates consumer in services/websocket-service/src/consumer.py
- [ ] T086 [US5] Implement broadcaster with Redis Pub/Sub in services/websocket-service/src/broadcaster.py
- [ ] T087 [US5] Create Dockerfile for websocket service in services/websocket-service/Dockerfile
- [ ] T088 [P] [US5] Implement WebSocket client in frontend/src/lib/websocket.ts
- [ ] T089 [P] [US5] Create useWebSocket hook in frontend/src/hooks/useWebSocket.ts
- [ ] T090 [P] [US5] Create useRealTimeSync hook in frontend/src/hooks/useRealTimeSync.ts
- [ ] T091 [US5] Integrate real-time sync into task list in frontend/src/app/tasks/page.tsx
- [ ] T092 [US5] Add optimistic locking (version field) to task updates in backend/src/services/task_service.py

**Checkpoint**: At this point, User Stories 1-5 should all work independently with real-time sync

---

## Phase 8: User Story 6 - Activity History and Audit Trail (Priority: P3)

**Goal**: Provide complete history of all task operations for accountability and troubleshooting

**Independent Test**: Perform various task operations (create, edit, complete, delete), then view the activity log and verify all actions are recorded with timestamps and user information

### Implementation for User Story 6

- [ ] T093 [P] [US6] Create ActivityLog model in backend/src/models/activity_log.py
- [ ] T094 [US6] Implement ActivityService for logging in backend/src/services/activity_service.py
- [ ] T095 [US6] Create activity API endpoints (GET /api/activity, GET /api/activity/task/{id}) in backend/src/api/routes/activity.py
- [ ] T096 [US6] Create Audit Service microservice structure in services/audit-service/
- [ ] T097 [US6] Implement audit consumer in services/audit-service/src/consumer.py
- [ ] T098 [US6] Implement activity logger in services/audit-service/src/logger.py
- [ ] T099 [US6] Create Dockerfile for audit service in services/audit-service/Dockerfile
- [ ] T100 [P] [US6] Create ActivityLog component in frontend/src/components/ActivityLog.tsx
- [ ] T101 [US6] Add activity API methods to frontend API client in frontend/src/lib/api.ts
- [ ] T102 [US6] Create activity history page in frontend/src/app/activity/page.tsx

**Checkpoint**: At this point, all user stories 1-6 should work independently

---

## Phase 9: User Story 7 - Reliable and Scalable Deployment (Priority: P1)

**Goal**: Deploy the system to Kubernetes (local Minikube and cloud) with high availability and auto-scaling

**Independent Test**: Deploy to local Minikube, verify all features work, then deploy to cloud (AKS/GKE/OKE) and run load tests with 1000+ concurrent users

### Implementation for User Story 7

- [ ] T103 [P] [US7] Create Helm chart structure in helm/todo-app/
- [ ] T104 [P] [US7] Create Chart.yaml with dependencies in helm/todo-app/Chart.yaml
- [ ] T105 [P] [US7] Create values.yaml with default configuration in helm/todo-app/values.yaml
- [ ] T106 [P] [US7] Create values-local.yaml for Minikube in helm/todo-app/values-local.yaml
- [ ] T107 [P] [US7] Create values-cloud.yaml for AKS/GKE/OKE in helm/todo-app/values-cloud.yaml
- [ ] T108 [P] [US7] Create backend deployment template with Dapr sidecar in helm/todo-app/templates/backend-deployment.yaml
- [ ] T109 [P] [US7] Create frontend deployment template in helm/todo-app/templates/frontend-deployment.yaml
- [ ] T110 [P] [US7] Create notification service deployment template in helm/todo-app/templates/notification-deployment.yaml
- [ ] T111 [P] [US7] Create recurring service deployment template in helm/todo-app/templates/recurring-deployment.yaml
- [ ] T112 [P] [US7] Create audit service deployment template in helm/todo-app/templates/audit-deployment.yaml
- [ ] T113 [P] [US7] Create websocket service deployment template in helm/todo-app/templates/websocket-deployment.yaml
- [ ] T114 [P] [US7] Create service templates for all deployments in helm/todo-app/templates/
- [ ] T115 [P] [US7] Create ingress template in helm/todo-app/templates/ingress.yaml
- [ ] T116 [P] [US7] Create HorizontalPodAutoscaler templates in helm/todo-app/templates/
- [ ] T117 [P] [US7] Create ConfigMap template in helm/todo-app/templates/configmap.yaml
- [ ] T118 [P] [US7] Create Secret template in helm/todo-app/templates/secrets.yaml
- [ ] T119 [US7] Update backend Dockerfile with Dapr annotations in backend/Dockerfile
- [ ] T120 [US7] Update frontend Dockerfile for production in frontend/Dockerfile
- [ ] T121 [US7] Create GitHub Actions workflow for testing in .github/workflows/test.yml
- [ ] T122 [US7] Create GitHub Actions workflow for building Docker images in .github/workflows/build.yml
- [ ] T123 [US7] Create GitHub Actions workflow for local deployment in .github/workflows/deploy-local.yml
- [ ] T124 [US7] Create GitHub Actions workflow for cloud deployment in .github/workflows/deploy-cloud.yml
- [ ] T125 [US7] Deploy to Minikube and validate all features
- [ ] T126 [US7] Deploy to cloud Kubernetes (AKS/GKE/OKE) and validate

**Checkpoint**: At this point, the entire system should be deployed and operational on Kubernetes

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T127 [P] Update MCP tools to support new task attributes (priority, tags, due dates, recurrence) in backend/src/mcp/tools/
- [ ] T128 [P] Extend AI chatbot agent for new features in backend/src/agents/todo_agent.py
- [ ] T129 [P] Add structured logging with JSON format across all services
- [ ] T130 [P] Add Prometheus metrics endpoints to all services
- [ ] T131 [P] Configure Jaeger tracing via Dapr
- [ ] T132 [P] Create Grafana dashboards for monitoring in k8s/monitoring/grafana-dashboards/
- [ ] T133 [P] Update README.md with Phase 5 features and deployment instructions
- [ ] T134 [P] Update quickstart.md with complete setup guide
- [ ] T135 [P] Add API documentation with OpenAPI/Swagger UI
- [ ] T136 Security audit: validate input sanitization and authentication
- [ ] T137 Performance optimization: add database query optimization and caching
- [ ] T138 Run end-to-end validation per quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Recurring Tasks) - Can start after Phase 2
  - US2 (Reminders) - Can start after Phase 2, integrates with US1
  - US3 (Priorities/Tags) - Can start after Phase 2
  - US4 (Search) - Can start after Phase 2, uses US3 attributes
  - US5 (Real-Time Sync) - Can start after Phase 2, syncs all features
  - US6 (Activity History) - Can start after Phase 2, logs all operations
  - US7 (Deployment) - Can start after Phase 2, deploys all services
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 for recurring reminders
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Uses US3 attributes for filtering
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Syncs all task changes
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - Logs all operations
- **User Story 7 (P1)**: Can start after Foundational (Phase 2) - Deploys all services

### Within Each User Story

- Models before services
- Services before API endpoints
- Backend before frontend
- Core implementation before microservices
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, multiple user stories can be worked on in parallel:
  - US1 + US3 (no conflicts)
  - US2 (after US1 models exist)
  - US4 (after US3 models exist)
  - US5, US6, US7 (can proceed independently)
- Models within a story marked [P] can run in parallel
- Frontend components marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task T025: "Create RecurringPattern model in backend/src/models/recurring_pattern.py"
Task T026: "Extend Task model with recurring fields in backend/src/models/task.py"

# Launch frontend components together:
Task T037: "Create RecurrenceSelector component in frontend/src/components/RecurrenceSelector.tsx"
Task T038: "Update TaskForm component in frontend/src/components/TaskForm.tsx"
Task T039: "Update TaskList component in frontend/src/components/TaskList.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 + 7)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Recurring Tasks)
4. Complete Phase 4: User Story 2 (Reminders)
5. Complete Phase 9: User Story 7 (Deployment)
6. **STOP and VALIDATE**: Test recurring tasks with reminders on Kubernetes
7. Deploy/demo MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Recurring) → Test independently → Deploy
3. Add US2 (Reminders) → Test independently → Deploy
4. Add US3 (Priorities/Tags) → Test independently → Deploy
5. Add US4 (Search) → Test independently → Deploy
6. Add US5 (Real-Time Sync) → Test independently → Deploy
7. Add US6 (Activity History) → Test independently → Deploy
8. Add US7 (Kubernetes) → Deploy to production
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Recurring Tasks)
   - Developer B: User Story 3 (Priorities/Tags)
   - Developer C: User Story 7 (Kubernetes setup)
3. After US1 complete:
   - Developer A: User Story 2 (Reminders)
4. After US3 complete:
   - Developer B: User Story 4 (Search)
5. Remaining stories (US5, US6) can proceed in parallel

---

## Summary

**Total Tasks**: 138 tasks across 10 phases

**Task Count by User Story**:
- Setup: 8 tasks
- Foundational: 16 tasks (BLOCKS all stories)
- US1 (Recurring Tasks): 17 tasks
- US2 (Reminders): 17 tasks
- US3 (Priorities/Tags): 12 tasks
- US4 (Search): 9 tasks
- US5 (Real-Time Sync): 13 tasks
- US6 (Activity History): 10 tasks
- US7 (Deployment): 24 tasks
- Polish: 12 tasks

**Parallel Opportunities**: 67 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Create recurring task, complete it, verify next occurrence spawns
- US2: Set reminder, verify notification arrives on time
- US3: Create tasks with priorities/tags, verify filtering works
- US4: Search 20+ tasks with filters, verify results in <1 second
- US5: Open on 2 devices, create task on one, verify sync in <2 seconds
- US6: Perform operations, verify activity log records all actions
- US7: Deploy to Minikube and cloud, verify all features work

**Suggested MVP Scope**: US1 (Recurring) + US2 (Reminders) + US7 (Deployment) = Core value proposition

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Phase 2 (Foundational) is CRITICAL - all user stories depend on it
- Tests are NOT included as they were not explicitly requested in the spec
