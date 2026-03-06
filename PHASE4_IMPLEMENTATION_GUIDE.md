"""
Phase 4 Implementation Guide - Using Celery Tasks with ALIE
===========================================================

This guide explains how to use the Phase 4 Celery task system in the ALIE platform.
"""

# 📚 **TABLE OF CONTENTS**

1. [Quick Start](#quick-start)
2. [Celery Architecture](#celery-architecture)
3. [Verification Tasks](#verification-tasks)
4. [Analytics Tasks](#analytics-tasks)
5. [API Endpoints](#api-endpoints)
6. [Task Monitoring](#task-monitoring)
7. [Error Handling](#error-handling)
8. [Advanced Usage](#advanced-usage)
9. [Troubleshooting](#troubleshooting)

---

# 🚀 **QUICK START**

## **1. Prerequisites**

```bash
# Install Celery and Redis
pip install celery[redis]==5.3.4
pip install redis==7.0+

# Start Redis (Docker recommended)
docker run -d -p 6379:6379 redis:7.0

# OR install locally and start
redis-server
```

## **2. Start Celery Worker**

```bash
# Terminal 1 - Start worker
celery -A backend.workers.celery_app worker -l info --queues verification,analytics

# Output:
# [tasks]
# - backend.workers.tasks.verification_tasks.verify_single_business
# - backend.workers.tasks.verification_tasks.verify_all_businesses
# - backend.workers.tasks.analytics_tasks.calculate_daily_statistics
```

## **3. Start Celery Beat (Optional - for scheduling)**

```bash
# Terminal 2 - Start scheduler
celery -A backend.workers.celery_app beat -l info

# Output:
# Scheduler: Celery Beat v5.3.4
# [tasks]
#   Scheduled 'verify-all-businesses' for 2024-01-21 02:00:00
#   Scheduled 'daily-statistics' for 2024-01-20 23:59:00
```

## **4. Start FastAPI Server**

```bash
# Terminal 3 - Start API
cd backend
uvicorn main:app --reload

# Visit http://localhost:8000/api/docs
```

## **5. Trigger a Task**

```bash
# Manual trigger
curl -X POST http://localhost:8000/api/v1/celery/verify/single/1

# Response:
{
    "task_id": "abc123def456",
    "business_id": 1,
    "status": "pending",
    "message": "Verification started in background"
}

# Check status
curl http://localhost:8000/api/v1/celery/tasks/abc123def456
# Returns: progress, result, or error
```

---

# 🏗️ **CELERY ARCHITECTURE**

## **Component Diagram**

```
┌─────────────────────┐
│   FastAPI Server    │
│  (API Endpoints)    │
└──────────┬──────────┘
           │ POST /celery/verify/all
           ↓
┌─────────────────────┐      ┌──────────────┐
│   Redis Message     │←────→│   Celery     │
│   Broker (6379)     │      │   Worker     │
└─────────────────────┘      └──────┬───────┘
           ↓                         │
┌─────────────────────┐             │
│   Redis Results     │             │
│   Backend (6379/2)  │←────────────┘
└─────────────────────┘   task results
           ↑
           └─── GET /celery/tasks/{id}
```

## **Message Flow**

1. **API Request**
   ```
   POST /api/v1/celery/verify/all
   → Returns task_id immediately
   ```

2. **Task Queuing**
   ```
   Task placed in Redis queue
   Worker picks it up when available
   Status: PENDING
   ```

3. **Execution**
   ```
   Worker processes task
   Status: PROGRESS (with percentage)
   Interim results stored in memory
   ```

4. **Completion**
   ```
   Task finishes
   Results stored in Redis
   Status: SUCCESS / FAILURE
   ```

5. **Retrieval**
   ```
   GET /api/v1/celery/tasks/{task_id}
   Returns results from Redis
   ```

## **Configuration**

File: `backend/workers/celery_app.py`

```python
from celery import Celery
from kombu import Queue, Exchange

app = Celery('alie')

# Broker configuration
app.conf.broker_url = 'redis://localhost:6379/1'
app.conf.result_backend = 'redis://localhost:6379/2'

# Task configuration
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.task_track_started = True
app.conf.task_time_limit = 30 * 60  # 30 minutes hard limit

# Queue configuration
app.conf.task_queues = (
    Queue('verification', Exchange('verification'), routing_key='verification'),
    Queue('analytics', Exchange('analytics'), routing_key='analytics'),
)

# Routing
app.conf.task_routes = {
    'backend.workers.tasks.verification_tasks.*': {'queue': 'verification'},
    'backend.workers.tasks.analytics_tasks.*': {'queue': 'analytics'},
}
```

---

# ✅ **VERIFICATION TASKS**

## **Task 1: verify_single_business(business_id)**

Verifies a single business across all APIs.

### **Endpoint**
```
POST /api/v1/celery/verify/single/{business_id}
```

### **Request**
```bash
curl -X POST http://localhost:8000/api/v1/celery/verify/single/1
```

### **Response**
```json
{
    "task_id": "a1b2c3d4-e5f6-7890-abcd",
    "business_id": 1,
    "business_name": "Salon A",
    "status": "pending",
    "message": "Verification started in background",
    "check_status_url": "/api/v1/celery/tasks/a1b2c3d4-..."
}
```

### **Task Details**

Task Definition:
```python
@app.task(bind=True, max_retries=3)
def verify_single_business(self, business_id: int) -> Dict:
    """Verify single business"""
    db = SessionLocal()
    try:
        business = db.query(Business).get(business_id)
        if not business:
            return {"error": "Business not found", "business_id": business_id}
        
        # Use VerificationCoordinator
        coordinator = VerificationCoordinator(...)
        result = asyncio.run(coordinator.verify_business(business, db))
        
        db.commit()
        return {"status": "success", "trust_score": result["trust_score"]}
    
    except Exception as e:
        db.rollback()
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=300 * (self.request.retries + 1))
    
    finally:
        db.close()
```

### **How It Works**

1. Get business from database
2. Initialize VerificationCoordinator
3. Call verify_business (async) using asyncio.run()
4. APIs called:
   - 2ГИС (Kazakhstan)
   - Google Places
   - OLX (if available)
5. Update Business.trust_score
6. Return results
7. On error: Retry up to 3 times with 300-second delays

### **Tracking Status**

```bash
# While running
curl http://localhost:8000/api/v1/celery/tasks/{task_id}
# Response:
{
    "task_id": "a1b2c3d4-...",
    "status": "PROGRESS",
    "progress": 45,
    "message": "Verifying with APIs..."
}

# When complete
curl http://localhost:8000/api/v1/celery/tasks/{task_id}
# Response:
{
    "task_id": "a1b2c3d4-...",
    "status": "SUCCESS",
    "progress": 100,
    "result": {
        "business_id": 1,
        "trust_score": 0.85,
        "verified_2gis": true,
        "verified_google": true,
        "verified_olx": false,
        "updated_at": "2024-01-20T10:30:00Z"
    }
}
```

---

## **Task 2: verify_all_businesses()**

Batch verification for all businesses in catalog.

### **Endpoint**
```
POST /api/v1/celery/verify/all
```

### **Request**
```bash
curl -X POST http://localhost:8000/api/v1/celery/verify/all
```

### **Response**
```json
{
    "task_id": "x1y2z3a4-b5c6-d7e8-f9a0",
    "total_businesses": 250,
    "status": "pending",
    "estimated_duration_minutes": 40,
    "message": "Verification of 250 businesses started"
}
```

### **Progress Tracking**

```bash
# Track real-time
for i in {1..60}; do
  curl http://localhost:8000/api/v1/celery/tasks/x1y2z3a4-...
  sleep 10  # Check every 10 seconds
done
```

### **Results**

```json
{
    "status": "SUCCESS",
    "result": {
        "total": 250,
        "verified": 245,
        "failed": 5,
        "by_category": {
            "hair_salon": {"total": 50, "verified": 48},
            "restaurant": {"total": 75, "verified": 72},
            "museum": {"total": 60, "verified": 58},
            "park": {"total": 65, "verified": 67}
        },
        "average_trust_score": 0.78,
        "duration_seconds": 1245
    }
}
```

---

## **Task 3: verify_category(category, limit)**

Verify businesses in a specific category.

### **Endpoint**
```
POST /api/v1/celery/verify/category/{category}?limit=10
```

### **Request**
```bash
# Verify all hair salons
curl -X POST http://localhost:8000/api/v1/celery/verify/category/hair_salon

# Verify only first 10 (for testing)
curl -X POST "http://localhost:8000/api/v1/celery/verify/category/hair_salon?limit=10"
```

### **Response**
```json
{
    "task_id": "cat123abc456",
    "category": "hair_salon",
    "businesses_to_verify": 50,
    "status": "pending",
    "check_status_url": "/api/v1/celery/tasks/cat123abc456"
}
```

### **Use Cases**

1. **Testing**: Run on limited subset
   ```bash
   curl -X POST "http://localhost:8000/api/v1/celery/verify/category/hair_salon?limit=5"
   ```

2. **Incremental Updates**: Verify one category daily
   ```bash
   # Schedule in cron
   0 2 * * MON  curl -X POST .../verify/category/hair_salon
   0 2 * * TUE  curl -X POST .../verify/category/restaurant
   0 2 * * WED  curl -X POST .../verify/category/museum
   ```

3. **Manual Refresh**: Update after new data import
   ```bash
   curl -X POST "http://localhost:8000/api/v1/celery/verify/category/restaurant"
   ```

---

## **Task 4: recalculate_trust_scores()**

Recalculate trust scores for all businesses using 6-factor algorithm.

### **Endpoint**
```
POST /api/v1/celery/recalculate-scores
```

### **Request**
```bash
curl -X POST http://localhost:8000/api/v1/celery/recalculate-scores
```

### **Response**
```json
{
    "task_id": "score123abc456",
    "businesses_to_process": 250,
    "algorithm": "6-factor weighted average",
    "weights": {
        "2gis": 0.25,
        "olx": 0.15,
        "google": 0.25,
        "rating": 0.15,
        "ctr": 0.10,
        "recency": 0.10
    },
    "status": "pending"
}
```

### **Algorithm Details**

Each business trust score = weighted average of:

| Factor | Weight | Source | Range |
|--------|--------|--------|-------|
| 2ГИС | 25% | verified_2gis flag | 0.0 - 1.0 |
| OLX | 15% | verified_olx flag | 0.0 - 1.0 |
| Google | 25% | verified_google flag | 0.0 - 1.0 |
| Rating | 15% | business.rating / 5 | 0.0 - 1.0 |
| CTR | 10% | clicks / recommendations | 0.0 - 1.0 |
| Recency | 10% | 1 - (days_old / 365) | 0.0 - 1.0 |

### **Example Calculation**

Business properties:
```json
{
    "verified_2gis": true,              // 1.0
    "verified_olx": false,               // 0.0
    "verified_google": true,             // 1.0
    "rating": 4.3,                       // 0.86 (4.3/5)
    "clicks": 380,                       // CTR
    "recommendations": 450,              // CTR calc
    "last_verification": "2024-01-10"    // 10 days ago
}
```

Trust Score Calculation:
```
CTR = 380 / 450 = 0.844
Recency = 1 - (10 / 365) = 0.973

Trust Score = (1.0 × 0.25) +
              (0.0 × 0.15) +
              (1.0 × 0.25) +
              (0.86 × 0.15) +
              (0.844 × 0.10) +
              (0.973 × 0.10)
            = 0.25 + 0 + 0.25 + 0.129 + 0.0844 + 0.0973
            = 0.81
```

### **Results**

```json
{
    "status": "SUCCESS",
    "result": {
        "total_processed": 250,
        "average_trust_score": 0.78,
        "by_category": {
            "hair_salon": 0.82,
            "restaurant": 0.76,
            "museum": 0.80,
            "park": 0.74
        },
        "distribution": {
            "high_trust": 180,      // >= 0.75
            "medium_trust": 50,     // 0.50 - 0.75
            "low_trust": 20         // < 0.50
        }
    }
}
```

---

# 📊 **ANALYTICS TASKS**

## **Task 5: calculate_daily_statistics()**

Aggregates statistics for a specific day.

### **Endpoint**
```
POST /api/v1/celery/analytics/daily
```

### **Request**
```bash
curl -X POST http://localhost:8000/api/v1/celery/analytics/daily
```

### **Response**
```json
{
    "task_id": "daily123abc456",
    "date": "2024-01-19",
    "status": "pending",
    "message": "Daily statistics for 2024-01-19 scheduled",
    "check_status_url": "/api/v1/celery/tasks/daily123abc456"
}
```

### **Task Details**

Aggregates previous day's LeadEvent records by:
- Event type (recommendation, click, call)
- Category
- Individual business
- Lead value

### **Results**

```json
{
    "status": "SUCCESS",
    "result": {
        "date": "2024-01-19",
        "total_events": 1245,
        "recommendations": 450,
        "clicks": 380,
        "calls": 415,
        "total_lead_value_kzt": 125000,
        "average_value_per_lead": 100.40,
        "click_through_rate": 84.4,
        "by_category": {
            "hair_salon": {
                "events": 245,
                "recommendations": 100,
                "clicks": 95,
                "calls": 50,
                "value": 25000
            },
            "restaurant": {
                "events": 340,
                "recommendations": 120,
                "clicks": 110,
                "calls": 110,
                "value": 38000
            }
        }
    }
}
```

### **Querying Results**

```bash
# Get yesterday's stats
curl "http://localhost:8000/api/v1/analytics/daily"

# Get specific date
curl "http://localhost:8000/api/v1/analytics/daily?date=2024-01-19"

# Response includes all pre-calculated statistics
```

---

## **Task 6: calculate_monthly_report()**

Generates comprehensive 30-day rolling report.

### **Endpoint**
```
POST /api/v1/celery/analytics/monthly
```

### **Request**
```bash
curl -X POST http://localhost:8000/api/v1/celery/analytics/monthly
```

### **Results**

```json
{
    "period_start": "2023-12-21",
    "period_end": "2024-01-19",
    "days": 30,
    "total_events": 35250,
    "recommendations": 14000,
    "clicks": 11500,
    "calls": 9750,
    "total_lead_value_kzt": 3500000,
    "average_daily_value": 116666.67,
    "click_through_rate": 82.3,
    "businesses_verified": 185,
    "total_businesses": 250,
    "verification_rate": 74.0,
    "api_response_time_ms": 245.3,
    "top_categories": [
        {
            "category": "hair_salon",
            "events": 8900,
            "value": 890000,
            "ctr": 84.5
        },
        {
            "category": "restaurant",
            "events": 12000,
            "value": 1200000,
            "ctr": 81.0
        }
    ],
    "top_businesses": [
        {
            "business_id": 1,
            "name": "Salon A",
            "events": 450,
            "clicks": 380,
            "value": 38000,
            "trust_score": 0.92
        }
    ]
}
```

### **Scheduled Execution**

Default schedule (runs monthly):
```python
'monthly-report': {
    'task': 'backend.workers.tasks.analytics_tasks.calculate_monthly_report',
    'schedule': crontab(day_of_month=1, hour=0, minute=0),
}
```

Query via API anytime:
```bash
curl "http://localhost:8000/api/v1/analytics/monthly?days=30"
```

---

## **Task 7: cleanup_old_logs(days_to_keep)**

Deletes old APILog records per retention policy.

### **Endpoint**
```
POST /api/v1/celery/cleanup?days_to_keep=90
```

### **Request**
```bash
# Delete logs older than 90 days (default)
curl -X POST http://localhost:8000/api/v1/celery/cleanup

# Delete logs older than 60 days
curl -X POST "http://localhost:8000/api/v1/celery/cleanup?days_to_keep=60"
```

### **Response**
```json
{
    "task_id": "cleanup123abc456",
    "days_to_keep": 90,
    "status": "pending",
    "message": "Log cleanup for records older than 90 days scheduled"
}
```

### **Results**

```json
{
    "status": "SUCCESS",
    "result": {
        "deleted_records": 12450,
        "cutoff_date": "2023-10-21",
        "freed_space_mb": 245.5,
        "remaining_records": 18950
    }
}
```

### **Scheduled Execution**

Default schedule (weekly):
```python
'cleanup-logs': {
    'task': 'backend.workers.tasks.analytics_tasks.cleanup_old_logs',
    'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Sundays 3 AM
}
```

---

# 🔌 **API ENDPOINTS REFERENCE**

## **Verification Endpoints**

### **Manual Verification**
```
PUT /api/v1/verify/{business_id}/verify
```
Manually trigger verification for single business.

### **Verification Status**
```
GET /api/v1/verify/{business_id}/status
```
Check current verification state and trust score.

### **Verification Report**
```
GET /api/v1/verify/{business_id}/report
```
Get detailed verification history and audit trail.

### **Batch Verification**
```
POST /api/v1/verify/batch?category=hair_salon&limit=10
```
Schedule batch verification (returns task_id).

---

## **Celery Task Endpoints**

### **Check Task Status**
```
GET /api/v1/celery/tasks/{task_id}
```
Get progress, results, or errors for any task.

### **List Active Tasks**
```
GET /api/v1/celery/tasks/summary
```
Get summary of currently running and recent tasks.

---

## **Analytics Query Endpoints**

### **Daily Stats**
```
GET /api/v1/analytics/daily?date=2024-01-19
```
Get statistics for specific date (pre-calculated).

### **Monthly Report**
```
GET /api/v1/analytics/monthly?days=30
```
Get rolling 30-day metrics.

### **Category Analytics**
```
GET /api/v1/analytics/category/{category}?days=30
```
Get analytics for specific category.

### **Business Analytics**
```
GET /api/v1/analytics/business/{business_id}?days=90
```
Get detailed performance metrics for business.

---

# 👀 **TASK MONITORING**

## **Monitor via WebUI**

```bash
# Flower (Celery monitoring)
pip install flower
celery -A backend.workers.celery_app --broker=redis://localhost:6379/1 flower

# Visit http://localhost:5555
```

Flower shows:
- Active tasks in real-time
- Task history
- Worker status
- Queue lengths
- Task execution times
- Error logs

## **Monitor via CLI**

```bash
# Check queue status
celery -A backend.workers.celery_app inspect active

# Check registered tasks
celery -A backend.workers.celery_app inspect registered

# Show worker stats
celery -A backend.workers.celery_app inspect stats

# Details on specific task
celery -A backend.workers.celery_app inspect query_task {task_id}
```

## **Monitor via API**

```python
# Get Celery stats programmatically
import requests

# Get active tasks
response = requests.get('http://localhost:8000/api/v1/celery/tasks/summary')
print(response.json())

# Monitor specific task
task_id = 'abc123...'
response = requests.get(f'http://localhost:8000/api/v1/celery/tasks/{task_id}')
print(response.json())
```

---

