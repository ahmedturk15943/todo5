# Technical Research: Advanced Cloud Deployment

**Feature**: Advanced Cloud Deployment with Enhanced Task Management
**Date**: 2026-02-10
**Status**: Complete

## Research Overview

This document captures technical research and decisions for implementing event-driven architecture with Kafka, Dapr, and Kubernetes deployment. All technical unknowns from the plan have been researched and resolved.

## 1. Kafka Deployment Strategy

### Research Question
Should we use Strimzi operator, Redpanda Cloud, or managed Kafka (Confluent Cloud)?

### Options Evaluated

| Option | Pros | Cons | Cost |
|--------|------|------|------|
| **Strimzi Operator** | Full control, runs in K8s, free (compute only), learning experience | More complex setup, requires Zookeeper, operational overhead | Free (K8s compute) |
| **Redpanda Cloud** | Kafka-compatible, no Zookeeper, fast, free tier available, simple setup | Newer ecosystem, less tooling | Free tier available |
| **Confluent Cloud** | Industry standard, Schema Registry, excellent docs, managed | $400 credit expires, ongoing cost | $400 trial credit |

### Decision: **Strimzi Operator (Primary) with Redpanda Cloud (Fallback)**

**Rationale**:
- Strimzi provides production-grade Kafka on Kubernetes with full control
- Best learning experience for hackathon (demonstrates K8s operator pattern)
- Free cost (only K8s compute resources)
- Dapr Pub/Sub makes Kafka swappable - can switch to Redpanda Cloud if needed
- Fits within cloud free tier budgets

**Implementation**:
```yaml
# Install Strimzi operator
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka

# Deploy Kafka cluster (1 broker for local, 3 for production)
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka
  namespace: kafka
spec:
  kafka:
    replicas: 1  # Local: 1, Cloud: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
      - name: tls
        port: 9093
        type: internal
        tls: true
    storage:
      type: ephemeral  # Local: ephemeral, Cloud: persistent-claim
  zookeeper:
    replicas: 1  # Local: 1, Cloud: 3
    storage:
      type: ephemeral
```

**Alternatives Considered**:
- Redpanda Cloud: Excellent fallback if Strimzi setup issues arise
- Confluent Cloud: Too expensive after trial, not sustainable for learning

---

## 2. Dapr Jobs API vs Cron Bindings

### Research Question
Should we use Dapr Jobs API for exact-time scheduling or cron bindings for periodic checks?

### Options Evaluated

| Approach | How It Works | Pros | Cons |
|----------|--------------|------|------|
| **Dapr Jobs API** | Schedule job at exact time, callback fires once | Exact timing, no polling, scales better, efficient | Newer API (alpha), less documentation |
| **Cron Bindings** | Poll every X minutes, check DB for due reminders | Simple, well-documented | Polling overhead, timing imprecise, DB load |

### Decision: **Dapr Jobs API**

**Rationale**:
- Exact timing (reminder fires at 10:00:00, not "within 5 minutes of 10:00")
- No polling overhead (no DB scans every minute)
- Scales better (no wasted cycles checking for work)
- Aligns with event-driven architecture (job fires → event published)
- Dapr Jobs API is production-ready despite alpha label

**Implementation**:
```python
# Schedule reminder using Dapr Jobs API
async def schedule_reminder(task_id: int, remind_at: datetime, user_id: str):
    """Schedule reminder at exact time."""
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://localhost:3500/v1.0-alpha1/jobs/reminder-task-{task_id}",
            json={
                "dueTime": remind_at.isoformat(),
                "data": {
                    "task_id": task_id,
                    "user_id": user_id,
                    "type": "reminder"
                }
            }
        )

# Handle callback when job fires
@app.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    """Dapr calls this at scheduled time."""
    job_data = await request.json()

    # Publish reminder event via Dapr Pub/Sub
    await publish_event("reminders", "reminder.due", job_data["data"])

    return {"status": "SUCCESS"}
```

**Alternatives Considered**:
- Cron bindings: Simpler but imprecise timing and polling overhead
- APScheduler: Requires in-memory state, doesn't scale horizontally

---

## 3. WebSocket Scaling

### Research Question
How to manage WebSocket connections for 1000+ concurrent users?

### Options Evaluated

| Approach | Pros | Cons |
|----------|------|------|
| **Dedicated WebSocket Service** | Scales independently, clear separation, can use Socket.io | Additional service to manage |
| **Backend API with WebSocket** | Fewer services, simpler deployment | Couples WebSocket scaling with API scaling |
| **Redis Pub/Sub for Broadcasting** | Scales horizontally, standard pattern | Requires Redis, additional dependency |

### Decision: **Dedicated WebSocket Service with Redis Pub/Sub**

**Rationale**:
- WebSocket connections are long-lived and stateful (different scaling needs than stateless API)
- Dedicated service can scale independently based on connection count
- Redis Pub/Sub enables broadcasting across multiple WebSocket service instances
- Standard pattern for production WebSocket applications
- Dapr Pub/Sub can abstract Redis (consistent with architecture)

**Implementation**:
```python
# WebSocket service consumes task-updates from Kafka
# Broadcasts to connected clients via Socket.io with Redis adapter

from socketio import AsyncServer, AsyncRedisManager

# Redis manager for multi-instance broadcasting
redis_manager = AsyncRedisManager('redis://redis:6379')
sio = AsyncServer(async_mode='asgi', client_manager=redis_manager)

# Consumer: Kafka → WebSocket broadcast
async def consume_task_updates():
    """Consume task-updates topic, broadcast to clients."""
    async for message in kafka_consumer:
        event = json.loads(message.value)

        # Broadcast to user's room (all their connected devices)
        await sio.emit(
            'task_update',
            event,
            room=f"user_{event['user_id']}"
        )

# Client connection management
@sio.event
async def connect(sid, environ, auth):
    """Client connects, join user's room."""
    user_id = auth.get('user_id')
    await sio.enter_room(sid, f"user_{user_id}")
```

**Scaling Strategy**:
- Horizontal scaling: Multiple WebSocket service pods
- Redis Pub/Sub: Broadcasts across all instances
- Sticky sessions: Not required (Socket.io handles reconnection)
- Connection limit: 10,000 connections per pod (adjust replicas accordingly)

**Alternatives Considered**:
- Backend API with WebSocket: Doesn't scale well, couples concerns
- Server-Sent Events (SSE): One-way only, no client→server messages

---

## 4. Event Schema Versioning

### Research Question
Should we use Avro, JSON Schema, or Protobuf for event schemas?

### Options Evaluated

| Format | Pros | Cons | Best For |
|--------|------|------|----------|
| **JSON Schema** | Human-readable, easy debugging, Python/JS native | Larger payload, no built-in evolution | Hackathon, rapid development |
| **Avro** | Compact, schema evolution, Kafka ecosystem | Binary format, harder debugging | Production, high throughput |
| **Protobuf** | Compact, fast, strong typing | Requires compilation, steeper learning curve | gRPC services, performance-critical |

### Decision: **JSON Schema with Versioning**

**Rationale**:
- Human-readable events simplify debugging during development
- Python and JavaScript have native JSON support (no compilation step)
- JSON Schema provides validation without binary complexity
- Event volume is moderate (10,000/min), payload size not critical
- Easier for hackathon demonstration and judging
- Can migrate to Avro later if needed (Dapr abstracts serialization)

**Implementation**:
```python
# Event schema with version field
class TaskEvent(BaseModel):
    """Task event schema (v1)."""
    schema_version: str = "1.0"
    event_type: Literal["created", "updated", "completed", "deleted"]
    task_id: int
    user_id: str
    timestamp: datetime
    task_data: dict  # Full task object
    metadata: dict = {}

# Schema evolution strategy
# v1.0: Initial schema
# v1.1: Add new optional fields (backward compatible)
# v2.0: Breaking changes (consumers must handle both v1 and v2)

# Consumer handles multiple versions
async def handle_task_event(event: dict):
    """Handle task event with version awareness."""
    version = event.get("schema_version", "1.0")

    if version.startswith("1."):
        # Handle v1.x events
        await process_v1_event(event)
    elif version.startswith("2."):
        # Handle v2.x events
        await process_v2_event(event)
    else:
        logger.warning(f"Unknown schema version: {version}")
```

**Alternatives Considered**:
- Avro: Better for production but adds complexity for hackathon
- Protobuf: Overkill for this use case, requires compilation

---

## 5. Conflict Resolution

### Research Question
How to handle offline sync conflicts when two devices edit the same task?

### Options Evaluated

| Strategy | How It Works | Pros | Cons |
|----------|--------------|------|------|
| **Last Write Wins (LWW)** | Most recent timestamp wins | Simple, no user intervention | Data loss possible |
| **Operational Transform (OT)** | Transform operations to converge | No data loss, real-time collab | Complex implementation |
| **Conflict-free Replicated Data Types (CRDTs)** | Mathematically guaranteed convergence | No conflicts, scales well | Requires CRDT library, learning curve |
| **Manual Resolution** | Show conflict, user chooses | User control, no data loss | Poor UX, requires UI |

### Decision: **Last Write Wins (LWW) with Conflict Detection**

**Rationale**:
- Simple to implement and understand
- Conflicts are rare (most users don't edit same task on multiple devices simultaneously)
- Timestamp-based resolution is predictable
- Detect conflicts and log them (can add manual resolution later if needed)
- Aligns with eventual consistency model

**Implementation**:
```python
# Task model with version tracking
class Task(SQLModel, table=True):
    id: int
    title: str
    updated_at: datetime  # Timestamp for LWW
    version: int = 1      # Optimistic locking

# Update with conflict detection
async def update_task(task_id: int, updates: dict, client_version: int):
    """Update task with conflict detection."""
    task = await get_task(task_id)

    if task.version != client_version:
        # Conflict detected - client has stale data
        logger.warning(f"Conflict detected for task {task_id}")

        # Log conflict for analysis
        await log_conflict(task_id, client_version, task.version)

        # LWW: Accept update anyway (most recent wins)
        # Alternative: Reject and return 409 Conflict

    task.version += 1
    task.updated_at = datetime.utcnow()
    # Apply updates...
    await session.commit()

    # Publish update event
    await publish_task_event("updated", task)
```

**Conflict Scenarios**:
1. **Offline edit + online edit**: LWW based on updated_at timestamp
2. **Simultaneous edits**: Database transaction ensures one wins
3. **Delete + edit conflict**: Delete wins (task no longer exists)

**Alternatives Considered**:
- CRDTs: Too complex for hackathon timeline
- Manual resolution: Poor UX, requires additional UI
- OT: Overkill for task management (not real-time collaborative editing)

---

## 6. Notification Delivery

### Research Question
Which push notification providers should we use?

### Options Evaluated

| Provider | Platform | Pros | Cons |
|----------|----------|------|------|
| **Firebase Cloud Messaging (FCM)** | Android, Web | Free, reliable, Google-backed | Requires Firebase project |
| **Apple Push Notification Service (APNs)** | iOS | Native iOS support | Requires Apple Developer account |
| **Web Push API** | Web browsers | Standard API, no third-party | Limited to web, requires HTTPS |
| **Email (SMTP)** | All platforms | Universal, no setup | Not real-time, can be spam-filtered |

### Decision: **Multi-Channel Approach (Web Push + Email)**

**Rationale**:
- Web Push API for real-time browser notifications (no third-party service needed)
- Email as fallback and for users who prefer email
- No mobile native apps in scope (Phase V focuses on web)
- Can add FCM/APNs later if mobile apps are built

**Implementation**:
```python
# Notification service with multiple channels
class NotificationService:
    """Multi-channel notification delivery."""

    async def send_reminder(self, user_id: str, task: Task, reminder: Reminder):
        """Send reminder via user's preferred channels."""
        user_prefs = await get_notification_preferences(user_id)

        # Web push notification
        if user_prefs.web_push_enabled:
            await self.send_web_push(user_id, {
                "title": "Task Reminder",
                "body": f"{task.title} is due soon",
                "data": {"task_id": task.id}
            })

        # Email notification
        if user_prefs.email_enabled:
            await self.send_email(
                to=user_prefs.email,
                subject=f"Reminder: {task.title}",
                body=self.render_email_template(task, reminder)
            )

        # In-app notification (stored in DB, shown when user opens app)
        await self.create_in_app_notification(user_id, task, reminder)

# Web Push implementation
async def send_web_push(self, user_id: str, payload: dict):
    """Send web push notification."""
    subscriptions = await get_push_subscriptions(user_id)

    for subscription in subscriptions:
        try:
            webpush(
                subscription_info=subscription,
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": f"mailto:{settings.ADMIN_EMAIL}"}
            )
        except WebPushException as e:
            logger.error(f"Web push failed: {e}")
            # Remove invalid subscription
            await remove_subscription(subscription)
```

**Notification Preferences**:
- Users can enable/disable each channel
- Users can set quiet hours (no notifications during sleep)
- Users can configure reminder timing (1 hour before, 1 day before, etc.)

**Alternatives Considered**:
- FCM only: Requires Firebase, doesn't support web well
- Email only: Not real-time enough for reminders
- SMS: Too expensive, not in scope

---

## 7. Search Performance

### Research Question
Should we use PostgreSQL full-text search or Elasticsearch?

### Options Evaluated

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **PostgreSQL Full-Text Search** | No additional service, built-in, good enough for 1000s of tasks | Limited features, slower for large datasets | <100K tasks per user |
| **Elasticsearch** | Powerful, fast, advanced features (fuzzy search, facets) | Additional service, operational overhead, cost | >100K tasks, complex queries |

### Decision: **PostgreSQL Full-Text Search**

**Rationale**:
- Users have <1000 tasks typically (success criteria: fast search for 1000+ tasks)
- PostgreSQL full-text search is sufficient for this scale
- No additional service to manage (reduces complexity)
- Can add Elasticsearch later if needed (search service abstraction)
- Fits within "simplest viable solution" principle

**Implementation**:
```python
# PostgreSQL full-text search with GIN index
class Task(SQLModel, table=True):
    id: int
    title: str
    description: str
    # ... other fields

    # Full-text search vector (auto-updated via trigger)
    search_vector: Optional[str] = Field(sa_column=Column(TSVECTOR))

# Create GIN index for fast full-text search
CREATE INDEX task_search_idx ON task USING GIN(search_vector);

# Auto-update search vector on insert/update
CREATE TRIGGER task_search_vector_update
BEFORE INSERT OR UPDATE ON task
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(
    search_vector, 'pg_catalog.english', title, description
);

# Search query
async def search_tasks(user_id: str, query: str, filters: dict):
    """Search tasks with full-text search and filters."""
    stmt = (
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.search_vector.match(query))  # Full-text search
    )

    # Apply filters
    if filters.get("priority"):
        stmt = stmt.where(Task.priority == filters["priority"])
    if filters.get("tags"):
        stmt = stmt.where(Task.tags.contains(filters["tags"]))
    if filters.get("due_date_range"):
        stmt = stmt.where(Task.due_date.between(*filters["due_date_range"]))

    # Order by relevance (ts_rank)
    stmt = stmt.order_by(
        func.ts_rank(Task.search_vector, func.to_tsquery(query)).desc()
    )

    results = await session.execute(stmt)
    return results.scalars().all()
```

**Performance Optimization**:
- GIN index on search_vector for fast full-text search
- Composite indexes on (user_id, priority), (user_id, due_date) for filters
- Query result caching for common searches (Redis)
- Pagination for large result sets

**Alternatives Considered**:
- Elasticsearch: Overkill for this scale, adds operational complexity
- Simple LIKE queries: Too slow, no relevance ranking

---

## 8. State Management

### Research Question
Should we use PostgreSQL or Redis for Dapr state store?

### Options Evaluated

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **PostgreSQL** | Already in use, persistent, ACID guarantees | Slower than Redis, not optimized for key-value | Persistent state, transactional data |
| **Redis** | Fast, optimized for key-value, low latency | Additional service, in-memory (data loss risk) | Caching, session state, temporary data |

### Decision: **PostgreSQL for Persistent State, Redis for Cache**

**Rationale**:
- PostgreSQL for conversation state (needs persistence across restarts)
- Redis for caching search results and session data (performance optimization)
- Dapr state store uses PostgreSQL (consistent with main database)
- Redis is optional enhancement (can add later if needed)

**Implementation**:
```yaml
# Dapr state store component (PostgreSQL)
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      value: "host=neon.db user=... password=... dbname=todo"
    - name: tableName
      value: "dapr_state"

# Optional: Redis cache component
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cache
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis:6379"
    - name: redisPassword
      secretKeyRef:
        name: redis-secret
        key: password
```

**Usage Pattern**:
```python
# Store conversation state via Dapr
async def save_conversation_state(conv_id: str, messages: list):
    """Save conversation state (persistent)."""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/state/statestore",
            json=[{
                "key": f"conversation-{conv_id}",
                "value": {"messages": messages}
            }]
        )

# Cache search results (optional, if Redis deployed)
async def cache_search_results(cache_key: str, results: list):
    """Cache search results for 5 minutes."""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/state/cache",
            json=[{
                "key": cache_key,
                "value": results,
                "metadata": {"ttlInSeconds": "300"}
            }]
        )
```

**Alternatives Considered**:
- Redis only: Data loss risk, not suitable for persistent state
- PostgreSQL only: Slower for caching, but acceptable for MVP

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Kafka Deployment** | Strimzi Operator | Full control, free, learning experience |
| **Reminder Scheduling** | Dapr Jobs API | Exact timing, no polling, efficient |
| **WebSocket Scaling** | Dedicated service + Redis Pub/Sub | Independent scaling, standard pattern |
| **Event Schemas** | JSON Schema | Human-readable, easy debugging, sufficient |
| **Conflict Resolution** | Last Write Wins | Simple, predictable, conflicts are rare |
| **Notifications** | Web Push + Email | Multi-channel, no third-party dependencies |
| **Search** | PostgreSQL Full-Text | Sufficient for scale, no additional service |
| **State Management** | PostgreSQL (persistent) + Redis (cache) | Balanced approach, optional Redis |

## Implementation Priorities

**Phase 1 (MVP)**:
1. Strimzi Kafka deployment
2. Dapr Jobs API for reminders
3. PostgreSQL full-text search
4. Web Push notifications
5. LWW conflict resolution
6. JSON event schemas
7. PostgreSQL state store

**Phase 2 (Enhancements)**:
1. Redis for caching
2. Email notifications
3. WebSocket service with Redis Pub/Sub
4. Advanced conflict detection and logging

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Strimzi setup complexity | Fallback to Redpanda Cloud, detailed documentation |
| Dapr Jobs API alpha status | Test thoroughly, fallback to APScheduler if needed |
| WebSocket scaling issues | Start with single instance, add Redis Pub/Sub when needed |
| Notification delivery failures | Multi-channel approach, retry logic, dead letter queue |
| Search performance degradation | GIN indexes, query optimization, Redis caching |

## References

- [Strimzi Documentation](https://strimzi.io/docs/)
- [Dapr Jobs API](https://docs.dapr.io/developing-applications/building-blocks/jobs/)
- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [Web Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [Socket.io Scaling](https://socket.io/docs/v4/using-multiple-nodes/)
