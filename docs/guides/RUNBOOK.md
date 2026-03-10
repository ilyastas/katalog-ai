# ALIE Platform - Production Runbook

## 🎯 Overview

This runbook provides operational procedures for running ALIE in production.

---

## 📞 On-Call Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| Primary On-Call | DevOps Team | Slack #alie-alerts |
| Backend Lead | Backend Team | Slack #backend |
| Database Admin | DBA Team | Slack #database |
| Security Lead | Security Team | Slack #security |

---

## 🚨 Incident Response

### Severity Levels

**SEV-1 (Critical)**: Complete service outage
- Response time: 15 minutes
- Resolution time: 1 hour

**SEV-2 (High)**: Partial service degradation
- Response time: 30 minutes
- Resolution time: 4 hours

**SEV-3 (Medium)**: Minor issues
- Response time: 2 hours
- Resolution time: 24 hours

### Incident Response Steps

1. **Acknowledge** the alert in monitoring system
2. **Assess** the impact and severity
3. **Communicate** in #alie-incidents Slack channel
4. **Investigate** using monitoring and logs
5. **Mitigate** the immediate issue
6. **Resolve** the root cause
7. **Document** in incident postmortem

---

## 📊 Monitoring & Alerts

### Key Metrics

| Metric | Normal Range | Alert Threshold |
|--------|--------------|-----------------|
| API Response Time | < 200ms | > 500ms |
| Error Rate | < 0.1% | > 1% |
| CPU Usage | < 60% | > 80% |
| Memory Usage | < 70% | > 85% |
| Database Connections | < 50 | > 80 |
| Queue Length | < 100 | > 1000 |

### Monitoring Endpoints

```bash
# Health check
curl https://api.alie.kz/health

# Metrics
curl https://api.alie.kz/metrics

# Database status
kubectl exec -n alie-prod deployment/postgres -- pg_isready
```

---

## 🔍 Common Issues

### Issue 1: API Pods Crashing

**Symptoms:**
- API pods in CrashLoopBackOff
- 502/503 errors from ingress

**Investigation:**
```bash
# Check pod status
kubectl get pods -n alie-prod -l app=alie-api

# Check recent logs
kubectl logs -n alie-prod -l app=alie-api --tail=100

# Check previous logs
kubectl logs -n alie-prod <pod-name> --previous

# Describe pod for events
kubectl describe pod -n alie-prod <pod-name>
```

**Common Causes:**
- Database connection failure
- Missing environment variables
- Out of memory
- Failed health checks

**Resolution:**
```bash
# Case 1: Database connection issues
# Check if PostgreSQL is running
kubectl get pods -n alie-prod -l app=postgres

# Test connection
kubectl exec -n alie-prod deployment/alie-api -- \
  psql -h postgres-service -U $POSTGRES_USER -c "SELECT 1"

# Case 2: Missing secrets
# Verify secrets exist
kubectl get secrets -n alie-prod
kubectl describe secret alie-secrets -n alie-prod

# Case 3: Resource limits
# Increase memory/CPU limits in k8s/api-deployment.yaml
# Then apply changes
kubectl apply -f k8s/api-deployment.yaml

# Case 4: Rollback to previous version
kubectl rollout undo deployment/alie-api -n alie-prod
```

---

### Issue 2: High API Latency

**Symptoms:**
- Response times > 500ms
- Timeout errors
- User complaints

**Investigation:**
```bash
# Check pod resource usage
kubectl top pods -n alie-prod

# Check HPA status
kubectl get hpa -n alie-prod

# Check database performance
kubectl exec -n alie-prod deployment/postgres -- \
  psql -U $POSTGRES_USER -c "SELECT * FROM pg_stat_activity"

# Check Redis latency
kubectl exec -n alie-prod deployment/redis -- \
  redis-cli --latency
```

**Common Causes:**
- Insufficient pod replicas
- Database slow queries
- Redis cache misses
- External API timeouts

**Resolution:**
```bash
# Case 1: Scale up API pods
kubectl scale deployment alie-api --replicas=10 -n alie-prod

# Case 2: Analyze slow queries
kubectl exec -n alie-prod deployment/postgres -- \
  psql -U $POSTGRES_USER -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10"

# Case 3: Clear Redis cache
kubectl exec -n alie-prod deployment/redis -- \
  redis-cli -a $REDIS_PASSWORD FLUSHDB

# Case 4: Increase timeout for external APIs
# Edit backend/config/settings.py and redeploy
```

---

### Issue 3: Celery Workers Not Processing Tasks

**Symptoms:**
- Tasks stuck in pending state
- Queue length increasing
- No task results

**Investigation:**
```bash
# Check worker pods
kubectl get pods -n alie-prod -l app=alie-worker

# Check worker logs
kubectl logs -n alie-prod -l app=alie-worker --tail=100

# Check Redis queues
kubectl exec -n alie-prod deployment/redis -- \
  redis-cli -a $REDIS_PASSWORD LLEN celery

# Check beat scheduler
kubectl logs -n alie-prod -l app=alie-beat --tail=100
```

**Common Causes:**
- Workers crashed
- Redis connection issues
- Tasks exceeding retry limit
- Long-running tasks blocking queue

**Resolution:**
```bash
# Case 1: Restart workers
kubectl rollout restart deployment/alie-worker -n alie-prod

# Case 2: Scale up workers
kubectl scale deployment alie-worker --replicas=8 -n alie-prod

# Case 3: Purge stuck tasks
kubectl exec -n alie-prod deployment/redis -- \
  redis-cli -a $REDIS_PASSWORD DEL celery

# Case 4: Restart beat scheduler
kubectl rollout restart deployment/alie-beat -n alie-prod
```

---

### Issue 4: Database Connection Pool Exhausted

**Symptoms:**
- "Too many connections" errors
- API timeout errors
- Database CPU at 100%

**Investigation:**
```bash
# Check active connections
kubectl exec -n alie-prod deployment/postgres -- \
  psql -U $POSTGRES_USER -c "SELECT count(*) FROM pg_stat_activity"

# Check connections by application
kubectl exec -n alie-prod deployment/postgres -- \
  psql -U $POSTGRES_USER -c "SELECT application_name, count(*) FROM pg_stat_activity GROUP BY application_name"

# Check max connections
kubectl exec -n alie-prod deployment/postgres -- \
  psql -U $POSTGRES_USER -c "SHOW max_connections"
```

**Resolution:**
```bash
# Case 1: Kill idle connections
kubectl exec -n alie-prod deployment/postgres -- \
  psql -U $POSTGRES_USER -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < NOW() - INTERVAL '5 minutes'"

# Case 2: Increase max_connections
# Edit k8s/postgres-deployment.yaml
# Add: -c max_connections=200
# Then apply
kubectl apply -f k8s/postgres-deployment.yaml

# Case 3: Optimize pool size
# Edit backend/config/database.py
# Reduce DB_POOL_SIZE and DB_MAX_OVERFLOW
# Redeploy API
```

---

### Issue 5: SSL Certificate Expired

**Symptoms:**
- HTTPS errors
- Browser warnings
- Certificate validation failures

**Investigation:**
```bash
# Check certificate status
kubectl get certificate -n alie-prod

# Check certificate details
kubectl describe certificate alie-api-cert -n alie-prod

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager
```

**Resolution:**
```bash
# Trigger certificate renewal
kubectl delete certificate alie-api-cert -n alie-prod
kubectl apply -f k8s/ingress.yaml

# Check renewal status
kubectl get certificate -n alie-prod -w

# Manual verification
openssl s_client -connect api.alie.kz:443 -servername api.alie.kz < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

---

## 🔄 Routine Maintenance

### Daily Tasks

```bash
# Check pod health
kubectl get pods -n alie-prod

# Check resource usage
kubectl top pods -n alie-prod
kubectl top nodes

# Review error logs
kubectl logs -n alie-prod -l app=alie-api --tail=100 | grep ERROR
```

### Weekly Tasks

```bash
# Database vacuum
kubectl exec -n alie-prod deployment/postgres -- \
  vacuumdb -U $POSTGRES_USER -d alie --analyze

# Check disk usage
kubectl exec -n alie-prod deployment/postgres -- df -h

# Review HPA metrics
kubectl describe hpa -n alie-prod

# Check for pending updates
kubectl get pods -n alie-prod -o jsonpath='{.items[*].spec.containers[*].image}' | tr ' ' '\n' | sort -u
```

### Monthly Tasks

```bash
# Backup database
kubectl exec -n alie-prod deployment/postgres -- \
  pg_dump -U $POSTGRES_USER alie > backup_$(date +%Y%m%d).sql

# Rotate secrets
kubectl create secret generic alie-secrets-new --from-literal=... -n alie-prod
kubectl patch deployment alie-api -n alie-prod -p '{"spec":{"template":{"spec":{"containers":[{"name":"api","envFrom":[{"secretRef":{"name":"alie-secrets-new"}}]}]}}}}'
kubectl delete secret alie-secrets -n alie-prod
kubectl create secret generic alie-secrets --from-literal=... -n alie-prod

# Review and update certificates
kubectl get certificate -n alie-prod

# Analyze cost and resource usage
kubectl cost -n alie-prod

# Update dependencies
# Review requirements.txt for CVEs
# Update and redeploy
```

---

## 🛠 Operational Procedures

### Procedure 1: Deploying New Version

```bash
# 1. Build and push new images
docker build -t ghcr.io/YOUR_USERNAME/alie-api:v1.2.0 .
docker push ghcr.io/YOUR_USERNAME/alie-api:v1.2.0

# 2. Update deployment
kubectl set image deployment/alie-api \
  api=ghcr.io/YOUR_USERNAME/alie-api:v1.2.0 \
  -n alie-prod

# 3. Monitor rollout
kubectl rollout status deployment/alie-api -n alie-prod

# 4. Verify health
curl https://api.alie.kz/health

# 5. If issues, rollback
kubectl rollout undo deployment/alie-api -n alie-prod
```

### Procedure 2: Scaling for Load

```bash
# Scale API pods
kubectl scale deployment alie-api --replicas=10 -n alie-prod

# Scale workers
kubectl scale deployment alie-worker --replicas=15 -n alie-prod

# Monitor resource usage
watch kubectl top pods -n alie-prod

# After load decreases, scale down
kubectl scale deployment alie-api --replicas=3 -n alie-prod
kubectl scale deployment alie-worker --replicas=2 -n alie-prod
```

### Procedure 3: Database Migration

```bash
# 1. Backup database
kubectl exec -n alie-prod deployment/postgres -- \
  pg_dump -U $POSTGRES_USER alie > backup_pre_migration_$(date +%Y%m%d_%H%M%S).sql

# 2. Run migration in test mode
kubectl exec -n alie-prod deployment/alie-api -- \
  alembic upgrade head --sql > migration.sql

# 3. Review SQL
cat migration.sql

# 4. Apply migration
kubectl exec -n alie-prod deployment/alie-api -- \
  alembic upgrade head

# 5. Verify
kubectl exec -n alie-prod deployment/alie-api -- \
  alembic current

# 6. If issues, rollback
kubectl exec -n alie-prod deployment/alie-api -- \
  alembic downgrade -1
```

### Procedure 4: Emergency Maintenance

```bash
# 1. Put API in maintenance mode
kubectl scale deployment alie-api --replicas=0 -n alie-prod

# 2. Display maintenance page (via ingress)
kubectl apply -f k8s/maintenance-page.yaml

# 3. Perform maintenance
# ... your maintenance tasks ...

# 4. Restore service
kubectl scale deployment alie-api --replicas=3 -n alie-prod
kubectl delete -f k8s/maintenance-page.yaml

# 5. Verify
curl https://api.alie.kz/health
```

---

## 📈 Performance Tuning

### Database Optimization

```sql
-- Find slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan 
FROM pg_stat_user_indexes 
WHERE idx_scan = 0;

-- Vacuum and analyze
VACUUM ANALYZE;

-- Update statistics
ANALYZE;
```

### Redis Optimization

```bash
# Check memory usage
kubectl exec -n alie-prod deployment/redis -- \
  redis-cli -a $REDIS_PASSWORD INFO memory

# Check cache hit rate
kubectl exec -n alie-prod deployment/redis -- \
  redis-cli -a $REDIS_PASSWORD INFO stats | grep keyspace

# Evict expired keys
kubectl exec -n alie-prod deployment/redis -- \
  redis-cli -a $REDIS_PASSWORD --scan --pattern "expired:*" | xargs redis-cli DEL
```

---

## 📝 Documentation Links

- Deployment Guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- API Documentation: https://api.alie.kz/docs
- Architecture Overview: [PHASE4_COMPLETION.md](PHASE4_COMPLETION.md)
- Monitoring Dashboard: https://grafana.alie.kz

---

**Last Updated:** March 2026  
**Version:** 1.0.0  
**Owner:** DevOps Team
