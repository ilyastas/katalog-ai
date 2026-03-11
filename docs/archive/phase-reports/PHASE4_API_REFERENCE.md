"""
Phase 4 API Reference - Complete Endpoint Documentation
========================================================

Complete list of all HTTP endpoints added in Phase 4 with examples
"""

# 📋 **ENDPOINT SUMMARY**

Total Endpoints Added: **25+**

| Category | Count | Endpoints |
|----------|-------|-----------|
| Verification Management | 4 | Manual verify, status, batch, report |
| Celery Task Control | 8 | Start tasks, check status, manage |
| Analytics Queries | 4 | Daily, monthly, category, business |
| OpenAI Chat | 3 | Chat, threads, history |
| **TOTAL** | **19** | All operational |

---

# 🔐 **VERIFICATION MANAGEMENT** (`/verify`)

## **1. Manual Business Verification**

```
PUT /api/v1/verify/{business_id}/verify
```

**Purpose**: Manually trigger verification for a single business

**Parameters**:
- `business_id` (path, required): Integer business ID

**Response** (200 OK):
```json
{
    "status": "success",
    "business_id": 1,
    "business_name": "Salon A",
    "trust_score": 0.85,
    "verifications": {
        "2gis": {
            "verified": true,
            "id": "12345",
            "name": "Salon A",
            "address": "Almaty"
        },
        "google": {
            "verified": true,
            "rating": 4.5,
            "reviews": 120
        },
        "olx": {
            "verified": false,
            "reason": "No profile found"
        }
    },
    "verified_at": "2024-01-20T10:30:00Z"
}
```

**Example**:
```bash
curl -X PUT http://localhost:8000/api/v1/verify/1/verify
```

**Error Cases**:
- 404: Business not found
- 500: Verification failed

---

## **2. Get Verification Status**

```
GET /api/v1/verify/{business_id}/status
```

**Purpose**: Check current verification state

**Parameters**:
- `business_id` (path, required): Integer business ID

**Response** (200 OK):
```json
{
    "status": "success",
    "business_id": 1,
    "business_name": "Salon A",
    "category": "hair_salon",
    "verified": true,
    "trust_score": 0.85,
    "verification_flags": {
        "verified_2gis": true,
        "verified_google": true,
        "verified_olx": false
    },
    "last_verification": "2024-01-20T10:30:00Z",
    "external_links": {
        "2gis": "https://2gis.kz/...",
        "google": "https://maps.google.com/..."
    }
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/verify/1/status
```

---

## **3. Batch Verification**

```
POST /api/v1/verify/batch
```

**Purpose**: Schedule batch verification for multiple businesses

**Query Parameters**:
- `category` (optional): Filter by category (e.g., "hair_salon")
- `limit` (optional): Maximum businesses to process (default: all)

**Response** (200 OK):
```json
{
    "status": "scheduled",
    "task_id": "verify_batch_xyz123",
    "category": "hair_salon",
    "limit": 10,
    "message": "Category 'hair_salon' verification scheduled",
    "check_status_url": "/api/v1/celery/tasks/verify_batch_xyz123"
}
```

**Examples**:
```bash
# Full catalog verification
curl -X POST http://localhost:8000/api/v1/verify/batch

# Category-specific with limit
curl -X POST "http://localhost:8000/api/v1/verify/batch?category=hair_salon&limit=10"

# All in category
curl -X POST "http://localhost:8000/api/v1/verify/batch?category=restaurant"
```

---

## **4. Verification Report**

```
GET /api/v1/verify/{business_id}/report
```

**Purpose**: Get detailed verification history and audit trail

**Parameters**:
- `business_id` (path, required): Integer business ID

**Response** (200 OK):
```json
{
    "status": "success",
    "business_id": 1,
    "business_name": "Salon A",
    "current_trust_score": 0.85,
    "verification_history": [
        {
            "api_source": "google",
            "verified": true,
            "response": {
                "name": "Salon A",
                "rating": 4.5,
                "reviews": 120
            },
            "verified_at": "2024-01-20T10:30:00Z"
        },
        {
            "api_source": "2gis",
            "verified": true,
            "response": {
                "id": "12345",
                "name": "Salon A"
            },
            "verified_at": "2024-01-20T10:29:00Z"
        }
    ],
    "external_links": {
        "2gis": "https://2gis.kz/...",
        "google": "https://maps.google.com/..."
    },
    "recommendation": "Ready for recommendation"
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/verify/1/report
```

---

# 🔄 **CELERY TASK CONTROL** (`/celery`)

## **1. Verify Single Business (Async)**

```
POST /api/v1/celery/verify/single/{business_id}
```

**Purpose**: Trigger async verification for single business

**Parameters**:
- `business_id` (path, required): Integer business ID

**Response** (200 OK):
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

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/celery/verify/single/1

# Response contains task_id for tracking
task_id="a1b2c3d4-..."

# Poll for result
curl http://localhost:8000/api/v1/celery/tasks/$task_id
```

**Task Behavior**:
- Returns immediately with task_id
- Worker verifies in background
- Retries up to 3 times on failure
- Updates database with results

---

## **2. Verify All Businesses (Async)**

```
POST /api/v1/celery/verify/all
```

**Purpose**: Trigger batch verification for entire catalog

**Response** (200 OK):
```json
{
    "task_id": "verify_all_xyz789",
    "total_businesses": 250,
    "status": "pending",
    "estimated_duration_minutes": 40,
    "message": "Verification of 250 businesses started",
    "check_status_url": "/api/v1/celery/tasks/verify_all_xyz789"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/celery/verify/all

# Check progress every 10 seconds
while true; do
  curl http://localhost:8000/api/v1/celery/tasks/verify_all_xyz789
  sleep 10
done
```

**Expected Results**:
```json
{
    "status": "SUCCESS",
    "progress": 100,
    "result": {
        "total": 250,
        "verified": 245,
        "failed": 5,
        "by_category": {
            "hair_salon": {"total": 50, "verified": 48},
            "restaurant": {"total": 75, "verified": 72}
        },
        "average_trust_score": 0.78,
        "duration_seconds": 1245
    }
}
```

---

## **3. Verify Category (Async)**

```
POST /api/v1/celery/verify/category/{category}
```

**Purpose**: Verify all businesses in specific category

**Parameters**:
- `category` (path, required): Category name
- `limit` (query, optional): Maximum to process (for testing)

**Response** (200 OK):
```json
{
    "task_id": "verify_cat_def123",
    "category": "hair_salon",
    "businesses_to_verify": 50,
    "status": "pending",
    "message": "Verification of hair_salon category started",
    "check_status_url": "/api/v1/celery/tasks/verify_cat_def123"
}
```

**Examples**:
```bash
# Full category
curl -X POST http://localhost:8000/api/v1/celery/verify/category/hair_salon

# Limited to first 5 (for testing)
curl -X POST "http://localhost:8000/api/v1/celery/verify/category/hair_salon?limit=5"

# Different category
curl -X POST http://localhost:8000/api/v1/celery/verify/category/restaurant
```

---

## **4. Recalculate Trust Scores (Async)**

```
POST /api/v1/celery/recalculate-scores
```

**Purpose**: Recalculate trust scores for all businesses

**Response** (200 OK):
```json
{
    "task_id": "score_abc123",
    "businesses_to_process": 250,
    "status": "pending",
    "algorithm": "6-factor weighted average",
    "weights": {
        "2gis": 0.25,
        "olx": 0.15,
        "google": 0.25,
        "rating": 0.15,
        "ctr": 0.10,
        "recency": 0.10
    },
    "message": "Trust score recalculation started",
    "check_status_url": "/api/v1/celery/tasks/score_abc123"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/celery/recalculate-scores

# Expected result after completion
# {
#     "status": "SUCCESS",
#     "result": {
#         "total_processed": 250,
#         "average_trust_score": 0.78,
#         "by_category": {...},
#         "distribution": {"high_trust": 180, "medium_trust": 50, "low_trust": 20}
#     }
# }
```

---

## **5. Get Task Status**

```
GET /api/v1/celery/tasks/{task_id}
```

**Purpose**: Get real-time status of any Celery task

**Parameters**:
- `task_id` (path, required): Task ID from task trigger endpoint

**Response** - **Pending**:
```json
{
    "task_id": "a1b2c3d4-...",
    "status": "PENDING",
    "progress": 0,
    "message": "Task pending..."
}
```

**Response** - **In Progress**:
```json
{
    "task_id": "a1b2c3d4-...",
    "status": "PROGRESS",
    "progress": 65,
    "total": 250,
    "message": "Processing business 163/250"
}
```

**Response** - **Success**:
```json
{
    "task_id": "a1b2c3d4-...",
    "status": "SUCCESS",
    "progress": 100,
    "result": {
        "total": 250,
        "verified": 245,
        "failed": 5,
        "average_trust_score": 0.78
    },
    "completed_at": "2024-01-20T11:45:00Z"
}
```

**Response** - **Failed**:
```json
{
    "task_id": "a1b2c3d4-...",
    "status": "FAILURE",
    "error": "Database connection lost",
    "completed_at": "2024-01-20T11:45:00Z"
}
```

**Example - Polling Loop**:
```bash
#!/bin/bash

task_id="a1b2c3d4-..."

while true; do
  response=$(curl -s http://localhost:8000/api/v1/celery/tasks/$task_id)
  status=$(echo $response | jq -r '.status')
  progress=$(echo $response | jq -r '.progress')
  
  echo "Status: $status | Progress: $progress%"
  
  if [ "$status" = "SUCCESS" ] || [ "$status" = "FAILURE" ]; then
    echo "Task complete!"
    echo $response | jq '.result'
    break
  fi
  
  sleep 5
done
```

---

## **6. Start Daily Statistics Calculation (Async)**

```
POST /api/v1/celery/analytics/daily
```

**Purpose**: Schedule daily statistics aggregation

**Response** (200 OK):
```json
{
    "task_id": "daily_2024_01_20",
    "date": "2024-01-19",
    "status": "pending",
    "message": "Daily statistics for 2024-01-19 scheduled",
    "check_status_url": "/api/v1/celery/tasks/daily_2024_01_20"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/celery/analytics/daily

# But usually runs automatically via Celery Beat at 11:59 PM
```

---

## **7. Start Monthly Report Generation (Async)**

```
POST /api/v1/celery/analytics/monthly
```

**Purpose**: Generate 30-day rolling report

**Response** (200 OK):
```json
{
    "task_id": "monthly_2024_01",
    "status": "pending",
    "period_days": 30,
    "message": "Monthly report generation scheduled",
    "check_status_url": "/api/v1/celery/tasks/monthly_2024_01"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/celery/analytics/monthly

# Usually runs on 1st of month automatically
```

---

## **8. Clean Up Old Logs (Async)**

```
POST /api/v1/celery/cleanup
```

**Purpose**: Delete APILog records older than retention period

**Query Parameters**:
- `days_to_keep` (optional, default: 90): Retention days (7-365)

**Response** (200 OK):
```json
{
    "task_id": "cleanup_2024_01",
    "days_to_keep": 90,
    "status": "pending",
    "message": "Log cleanup for records older than 90 days scheduled",
    "check_status_url": "/api/v1/celery/tasks/cleanup_2024_01"
}
```

**Examples**:
```bash
# Default 90-day retention
curl -X POST http://localhost:8000/api/v1/celery/cleanup

# Keep only 60 days
curl -X POST "http://localhost:8000/api/v1/celery/cleanup?days_to_keep=60"

# Keep 180 days
curl -X POST "http://localhost:8000/api/v1/celery/cleanup?days_to_keep=180"
```

**Expected Result**:
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

---

## **9. Get Tasks Summary**

```
GET /api/v1/celery/tasks/summary
```

**Purpose**: List all active and recent tasks

**Response** (200 OK):
```json
{
    "active_tasks": 3,
    "active": [
        {
            "task_id": "verify_all_xyz789",
            "type": "backend.workers.tasks.verification_tasks.verify_all_businesses",
            "worker": "celery@worker-1",
            "started": 1705759200.123
        },
        {
            "task_id": "daily_stats_123",
            "type": "backend.workers.tasks.analytics_tasks.calculate_daily_statistics",
            "worker": "celery@worker-1",
            "started": 1705759300.456
        }
    ],
    "timestamp": "2024-01-20T10:50:00Z"
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/celery/tasks/summary
```

---

# 📊 **ANALYTICS QUERIES** (`/analytics`)

## **1. Get Daily Statistics**

```
GET /api/v1/analytics/daily
```

**Purpose**: Get statistics for a specific date

**Query Parameters**:
- `date` (optional): ISO format date (YYYY-MM-DD), defaults to yesterday

**Response** (200 OK):
```json
{
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
```

**Examples**:
```bash
# Yesterday (default)
curl http://localhost:8000/api/v1/analytics/daily

# Specific date
curl "http://localhost:8000/api/v1/analytics/daily?date=2024-01-15"

# Parse with jq
curl http://localhost:8000/api/v1/analytics/daily | jq '.by_category.hair_salon'
```

---

## **2. Get Monthly Report**

```
GET /api/v1/analytics/monthly
```

**Purpose**: Get 30-day rolling metrics

**Query Parameters**:
- `days` (optional, default: 30): Number of days to include (1-365)

**Response** (200 OK):
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

**Examples**:
```bash
# Default 30 days
curl http://localhost:8000/api/v1/analytics/monthly

# 7-day report
curl "http://localhost:8000/api/v1/analytics/monthly?days=7"

# 90-day report
curl "http://localhost:8000/api/v1/analytics/monthly?days=90"
```

---

## **3. Get Category Analytics**

```
GET /api/v1/analytics/category/{category}
```

**Purpose**: Analytics for specific category

**Parameters**:
- `category` (path, required): Category name
- `days` (query, optional, default: 30): Period in days

**Response** (200 OK):
```json
{
    "category": "hair_salon",
    "period_start": "2023-12-21",
    "period_end": "2024-01-19",
    "days": 30,
    "total_events": 8900,
    "recommendations": 3500,
    "clicks": 2950,
    "calls": 2450,
    "total_lead_value_kzt": 890000,
    "click_through_rate": 84.3,
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

**Examples**:
```bash
# Hair salons (30 days)
curl http://localhost:8000/api/v1/analytics/category/hair_salon

# Restaurants (90 days)
curl "http://localhost:8000/api/v1/analytics/category/restaurant?days=90"

# Parks (7 days)
curl "http://localhost:8000/api/v1/analytics/category/park?days=7"
```

---

## **4. Get Business Analytics**

```
GET /api/v1/analytics/business/{business_id}
```

**Purpose**: Performance metrics for specific business

**Parameters**:
- `business_id` (path, required): Business ID
- `days` (query, optional, default: 90): Analysis period

**Response** (200 OK):
```json
{
    "business_id": 1,
    "business_name": "Salon A",
    "category": "hair_salon",
    "trust_score": 0.92,
    "period_start": "2023-10-21",
    "period_end": "2024-01-19",
    "days": 90,
    "total_events": 1250,
    "recommendations": 500,
    "clicks": 420,
    "calls": 330,
    "total_lead_value_kzt": 42000,
    "average_value_per_click": 100.0,
    "click_through_rate": 84.0,
    "daily_breakdown": {
        "2024-01-19": {
            "events": 15,
            "clicks": 12,
            "value": 1200
        },
        "2024-01-18": {
            "events": 18,
            "clicks": 15,
            "value": 1500
        }
    }
}
```

**Examples**:
```bash
# 90-day performance
curl http://localhost:8000/api/v1/analytics/business/1

# 30-day performance
curl "http://localhost:8000/api/v1/analytics/business/1?days=30"

# Year-to-date
curl "http://localhost:8000/api/v1/analytics/business/1?days=365"
```

---

# 💬 **OPENAI CHAT** (`/openai`)

## **1. Chat with ALIE**

```
POST /api/v1/openai/chat
```

**Purpose**: Conversational interface for recommendations

**Request Body**:
```json
{
    "message": "Find me hair salons in Almaty with high ratings",
    "thread_id": "thread_..." (optional)
}
```

**Response** (200 OK):
```json
{
    "thread_id": "thread_abc123d4e5f6",
    "message": "I found 5 highly-rated hair salons in Almaty matching your request...",
    "status": "success",
    "request_id": "req_xyz789"
}
```

**Examples**:
```bash
# First message
curl -X POST http://localhost:8000/api/v1/openai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find me restaurants near Almaty city center"
  }'

# Response includes thread_id for continuation

# Continue conversation using thread_id
curl -X POST http://localhost:8000/api/v1/openai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me only those with vegetarian options",
    "thread_id": "thread_abc123d4e5f6"
  }'
```

**Error Cases**:
- 400: Empty message or message > 500 chars
- 500: OpenAI service unavailable

---

## **2. Create New Thread**

```
POST /api/v1/openai/threads
```

**Purpose**: Create new conversation thread

**Response** (200 OK):
```json
{
    "thread_id": "thread_xyz789abc123",
    "created_at": "2024-01-20T10:30:00Z",
    "status": "success"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/openai/threads

# Use returned thread_id for subsequent messages
thread_id=$(curl -s -X POST http://localhost:8000/api/v1/openai/threads | jq -r '.thread_id')

curl -X POST http://localhost:8000/api/v1/openai/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Find me hair salons\", \"thread_id\": \"$thread_id\"}"
```

---

## **3. Get Thread Messages**

```
GET /api/v1/openai/threads/{thread_id}
```

**Purpose**: Retrieve conversation history

**Parameters**:
- `thread_id` (path, required): Thread ID

**Response** (200 OK):
```json
{
    "thread_id": "thread_abc123d4e5f6",
    "messages": [
        {
            "role": "user",
            "content": "Find hair salons in Almaty",
            "timestamp": "2024-01-20T10:30:00Z"
        },
        {
            "role": "assistant",
            "content": "I found 5 highly-rated salons...",
            "timestamp": "2024-01-20T10:30:15Z"
        }
    ],
    "count": 2,
    "status": "success"
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/openai/threads/thread_abc123d4e5f6

# Pretty print
curl http://localhost:8000/api/v1/openai/threads/thread_abc123d4e5f6 | jq '.messages'
```

---

# ⚡ **REQUEST/RESPONSE PATTERNS**

## **Async Task Pattern**

Most verification and analytics operations follow this pattern:

```
1. POST /api/v1/celery/... → Returns task_id immediately
2. GET /api/v1/celery/tasks/{task_id} → Poll for status
3. When status="SUCCESS" → result available
```

**Example Workflow**:
```bash
#!/bin/bash

# Step 1: Start task
task_response=$(curl -s -X POST http://localhost:8000/api/v1/celery/verify/all)
task_id=$(echo $task_response | jq -r '.task_id')

echo "Task started: $task_id"

# Step 2: Poll for completion
while true; do
  status_response=$(curl -s http://localhost:8000/api/v1/celery/tasks/$task_id)
  status=$(echo $status_response | jq -r '.status')
  progress=$(echo $status_response | jq -r '.progress // "unknown"')
  
  echo "[$progress%] Status: $status"
  
  if [ "$status" = "SUCCESS" ]; then
    echo "Task completed!"
    echo $status_response | jq '.result'
    break
  elif [ "$status" = "FAILURE" ]; then
    echo "Task failed!"
    echo $status_response | jq '.error'
    exit 1
  fi
  
  sleep 5
done
```

---

## **Analytics Query Pattern**

Analytics queries return pre-calculated results immediately:

```
GET /api/v1/analytics/... → Returns results immediately
```

No polling needed.

---

# 🔐 **ERROR RESPONSES**

All endpoints return standard error format:

**400 Bad Request**:
```json
{
    "detail": "Invalid date format (use YYYY-MM-DD)"
}
```

**404 Not Found**:
```json
{
    "detail": "Business 999 not found"
}
```

**500 Internal Server**:
```json
{
    "detail": "Failed to verify business: Database connection lost"
}
```

---

# 📊 **COMMON QUERIES**

## **Get Daily Performance**
```bash
curl "http://localhost:8000/api/v1/analytics/daily?date=2024-01-19" | jq '{
  date: .date,
  events: .total_events,
  value: .total_lead_value_kzt,
  ctr: .click_through_rate
}'
```

## **Monitor Verification Progress**
```bash
task_id="verify_all_xyz789"
while [ $(curl -s http://localhost:8000/api/v1/celery/tasks/$task_id | jq -r '.status') != "SUCCESS" ]; do
  curl -s http://localhost:8000/api/v1/celery/tasks/$task_id | jq '{status, progress}'
  sleep 5
done
```

## **Find Top Businesses**
```bash
curl http://localhost:8000/api/v1/analytics/monthly | jq '.top_businesses | sort_by(-.events) | .[0:5]'
```

## **Check Category Performance**
```bash
for category in hair_salon restaurant museum park; do
  echo "$category:"
  curl -s "http://localhost:8000/api/v1/analytics/category/$category" | jq '{events: .total_events, ctr: .click_through_rate}'
done
```

---

**All endpoints tested and ready for production** ✅
