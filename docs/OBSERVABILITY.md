# Observability Stack - Logging, Monitoring & Distributed Tracing

This document describes the observability infrastructure for the Astro application, including structured logging, log aggregation, visualization, and distributed tracing.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Quick Start](#quick-start)
- [Structured Logging](#structured-logging)
- [Request Tracing](#request-tracing)
- [Dashboards](#dashboards)
- [Querying Logs](#querying-logs)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

The observability stack consists of:

- **Loguru**: Primary logging library with colorized console output (dev) and JSON logs (prod)
- **Structlog**: Advanced structured logging processors for context injection
- **Loki**: Horizontally-scalable log aggregation system (like Prometheus for logs)
- **Promtail**: Agent that ships logs from Docker containers to Loki
- **Grafana**: Visualization platform for creating dashboards and exploring logs

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────┐     ┌─────────┐
│ API Container│────▶│   Promtail   │────▶│  Loki   │◀────│ Grafana │
└─────────────┘     └──────────────┘     └─────────┘     └─────────┘
      │                     │                   │              │
      │                     │                   │              │
  JSON Logs          Docker Logs         Aggregates       Visualizes
   (stdout)          via Docker API      & Indexes         & Queries
```

**Flow:**

1. **API containers** output JSON structured logs to stdout
2. **Promtail** scrapes Docker container logs via Docker API
3. **Promtail** parses JSON, extracts fields, and ships to Loki
4. **Loki** aggregates, indexes, and stores logs
5. **Grafana** queries Loki and displays dashboards/logs

## Components

### 1. Loguru (Primary Logger)

**Location:** `apps/api/app/core/logging_config.py`

**Features:**
- Colorized console logs in development (DEBUG level)
- JSON structured logs in production (INFO level)
- Automatic log rotation (500 MB, 30 days retention, compressed)
- Integration with Uvicorn and standard library logging

**Configuration:**

```python
from loguru import logger

# Development: colorized console
logger.add(sys.stderr, format="...", level="DEBUG", colorize=True)

# Production: JSON logs with rotation
logger.add(
    "logs/astro_{time:YYYY-MM-DD}.log",
    rotation="500 MB",
    retention="30 days",
    compression="zip",
    serialize=True,  # JSON output
)
```

### 2. Structlog (Processors)

**Location:** `apps/api/app/core/logging_config.py`

**Purpose:** Add advanced processing capabilities on top of Loguru.

**Processors:**
- `merge_contextvars`: Merge context variables into log entries
- `add_logger_name`: Add logger name to logs
- `add_log_level`: Add log level to logs
- `TimeStamper`: Add ISO timestamps
- `add_request_context_processor`: Inject request_id, user_id, path, method, client_ip
- `StackInfoRenderer`: Render stack traces
- `format_exc_info`: Format exception information
- `JSONRenderer` (prod) / `ConsoleRenderer` (dev)

**Configuration:**

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_request_context_processor,  # Custom processor
        structlog.processors.JSONRenderer(),  # or ConsoleRenderer
    ],
)
```

### 3. Request Context (Distributed Tracing)

**Location:** `apps/api/app/core/context.py`

**Purpose:** Thread-safe request context propagation using Python's `contextvars`.

**Features:**
- Generate unique `request_id` (UUID v4) for each request
- Propagate `request_id`, `user_id`, `path`, `method`, `client_ip` across entire request lifecycle
- Automatic injection into all log entries
- Works with async/await and background tasks

**Usage:**

```python
from app.core.context import set_request_context, get_request_context, generate_request_id

# Set context (in middleware)
request_id = generate_request_id()
set_request_context(
    request_id=request_id,
    path="/api/v1/charts",
    method="POST",
    client_ip="192.168.1.1",
    user_id="user-123",
)

# Get context (anywhere in request)
context = get_request_context()
request_id = context.get("request_id")

# Logs automatically include context
logger.info("Chart created")
# Output: {"time": "2025-01-20T15:30:45.123", "level": "INFO", "message": "Chart created", "request_id": "abc-123", "user_id": "user-123"}
```

### 4. Request Logging Middleware

**Location:** `apps/api/app/core/middleware.py`

**Purpose:** Automatically log all HTTP requests with context.

**Features:**
- Generate `request_id` for each request
- Extract client IP (supports `X-Forwarded-For` header)
- Extract user agent
- Log incoming requests and responses
- Track request duration
- Add `X-Request-ID` header to responses
- Clear context after request to prevent leakage

**Example Logs:**

```json
{
  "time": "2025-01-20T15:30:45.123",
  "level": "INFO",
  "message": "Incoming request",
  "request_id": "a3f8b2c1-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "method": "POST",
  "path": "/api/v1/charts",
  "client_ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "query_params": "limit=10"
}

{
  "time": "2025-01-20T15:30:45.456",
  "level": "INFO",
  "message": "Request completed",
  "request_id": "a3f8b2c1-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "method": "POST",
  "path": "/api/v1/charts",
  "status_code": 201,
  "duration_ms": 123.45
}
```

### 5. Loki (Log Aggregation)

**Location:** `config/loki/loki-config.yml`

**Purpose:** Horizontally-scalable log aggregation and indexing.

**Features:**
- Stores logs with 30-day retention
- BoltDB-Shipper for index storage
- Filesystem for object storage
- Automatic compaction and retention deletion
- Query logs via LogQL (similar to PromQL)

**Ports:**
- `3100`: HTTP API (Promtail → Loki, Grafana ← Loki)
- `9096`: gRPC API

### 6. Promtail (Log Shipper)

**Location:** `config/promtail/promtail-config.yml`

**Purpose:** Scrape Docker container logs and ship to Loki.

**Features:**
- Auto-discover Docker containers on `astro-network`
- Parse JSON logs from API container
- Extract fields: `timestamp`, `level`, `message`, `request_id`, `user_id`, `path`, `method`, `client_ip`, `duration_ms`, `status_code`
- Add labels for filtering: `container`, `image`, `service`, `environment`
- Multiline log support (Python tracebacks)
- Drop healthcheck logs to reduce noise

**Labels:**
- `container`: Container name (e.g., `astro-api`)
- `service`: Service name (e.g., `api`, `celery_worker`)
- `environment`: `development` or `production`
- `level`: Log level (e.g., `INFO`, `ERROR`)
- `request_id`: Request ID for tracing
- `path`: API endpoint path
- `method`: HTTP method

### 7. Grafana (Visualization)

**Location:** `config/grafana/`

**Purpose:** Visualize logs, create dashboards, and explore data.

**Features:**
- Pre-configured Loki datasource
- Auto-provisioned dashboards
- LogQL query builder
- Alerting support
- User management

**Access:**
- URL: http://localhost:3000
- Username: `admin`
- Password: `admin` (change in production!)

## Quick Start

### 1. Start Observability Stack

```bash
# Start main services (db, redis, api, web)
docker-compose up -d

# Start observability stack (loki, promtail, grafana)
docker-compose -f docker-compose.observability.yml up -d

# View logs
docker-compose -f docker-compose.observability.yml logs -f
```

### 2. Access Grafana

1. Open http://localhost:3000
2. Login with `admin` / `admin`
3. Navigate to **Dashboards** → **Astro API Monitoring**

### 3. Explore Logs

1. Navigate to **Explore** (compass icon)
2. Select **Loki** datasource
3. Try queries:

```logql
# All API logs
{container="astro-api"}

# Logs for specific request
{container="astro-api"} |= "a3f8b2c1-4d5e-6f7a-8b9c-0d1e2f3a4b5c"

# Error logs only
{container="astro-api"} |~ "ERROR|CRITICAL"

# Logs for specific endpoint
{container="astro-api", path="/api/v1/charts"}

# Slow requests (> 1 second)
{container="astro-api"} | json | duration_ms > 1000
```

## Structured Logging

### Log Format (Production)

All logs are output as JSON with the following structure:

```json
{
  "time": "2025-01-20T15:30:45.123456+00:00",
  "level": "INFO",
  "name": "app.services.chart_service",
  "function": "create_chart",
  "line": 42,
  "message": "Chart created successfully",
  "extra": {
    "request_id": "a3f8b2c1-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
    "user_id": "user-123",
    "path": "/api/v1/charts",
    "method": "POST",
    "client_ip": "192.168.1.1",
    "chart_id": "chart-456"
  }
}
```

### Log Levels

- **DEBUG**: Detailed diagnostic information (dev only)
- **INFO**: General informational messages (default in prod)
- **WARNING**: Warning messages (unexpected but recoverable)
- **ERROR**: Error messages (recoverable errors)
- **CRITICAL**: Critical errors (unrecoverable, requires immediate attention)

### Adding Custom Fields

```python
from loguru import logger

# Simple logging
logger.info("Chart created")

# With extra fields
logger.bind(chart_id="chart-456", user_id="user-123").info("Chart created")

# Or using context (propagates to all logs in request)
from app.core.context import set_request_context

set_request_context(user_id="user-123")
logger.info("Chart created")  # Automatically includes user_id
```

## Request Tracing

### How It Works

1. **Middleware** generates unique `request_id` (UUID v4)
2. **Context** stores `request_id` and other metadata
3. **Structlog processor** injects context into every log entry
4. **Promtail** extracts `request_id` as a label
5. **Grafana** allows filtering by `request_id`

### Trace a Request

To trace all logs for a specific request:

```logql
# Find request_id in response headers
curl -I http://localhost:8000/api/v1/charts
# X-Request-ID: a3f8b2c1-4d5e-6f7a-8b9c-0d1e2f3a4b5c

# Query Loki for all logs with that request_id
{container="astro-api"} |= "a3f8b2c1-4d5e-6f7a-8b9c-0d1e2f3a4b5c"
```

This shows the complete lifecycle of the request:
- Incoming request
- Service calls
- Database queries
- Response
- Any errors

### User Activity Tracking

To see all activity for a specific user:

```logql
{container="astro-api"} | json | user_id="user-123"
```

## Dashboards

### Astro API Monitoring Dashboard

**Location:** `config/grafana/dashboards/api-monitoring.json`

**Panels:**

1. **Request Rate (req/s)**: Requests per second over time
2. **Average Response Time**: Average response time (ms) gauge
3. **HTTP Status Codes Distribution**: Pie chart of 2xx, 4xx, 5xx responses
4. **Log Levels Over Time**: Stacked bar chart of DEBUG, INFO, WARNING, ERROR, CRITICAL
5. **Top 10 Endpoints by Request Count**: Table of most-hit endpoints
6. **Error Rate**: Errors per second over time
7. **Recent API Logs**: Live log stream with filtering

**Auto-refresh:** 5 seconds

**Time range:** Last 1 hour (configurable)

### Creating Custom Dashboards

1. Navigate to **Dashboards** → **New** → **New Dashboard**
2. Click **Add visualization**
3. Select **Loki** datasource
4. Enter LogQL query
5. Configure visualization (time series, table, pie chart, etc.)
6. Save dashboard

## Querying Logs (LogQL)

LogQL is Loki's query language, inspired by PromQL.

### Basic Queries

```logql
# All logs from API container
{container="astro-api"}

# Logs containing text
{container="astro-api"} |= "Chart created"

# Logs NOT containing text
{container="astro-api"} != "healthcheck"

# Regex match
{container="astro-api"} |~ "ERROR|CRITICAL"

# Regex NOT match
{container="astro-api"} !~ "DEBUG|INFO"
```

### JSON Parsing

```logql
# Parse JSON and filter by field
{container="astro-api"} | json | level="ERROR"

# Filter by numeric field
{container="astro-api"} | json | duration_ms > 1000

# Multiple conditions
{container="astro-api"} | json | level="ERROR" | path="/api/v1/charts"
```

### Aggregations

```logql
# Count logs per minute
rate({container="astro-api"} [1m])

# Sum by label
sum by (level) (count_over_time({container="astro-api"} [5m]))

# Average response time
avg_over_time({container="astro-api"} | json | unwrap duration_ms [5m])

# Top 10 endpoints
topk(10, sum by (path) (count_over_time({container="astro-api"} | json [5m])))
```

### Time Ranges

```logql
# Last 5 minutes
{container="astro-api"} [5m]

# Last 1 hour
{container="astro-api"} [1h]

# Last 24 hours
{container="astro-api"} [24h]
```

## Troubleshooting

### Logs Not Appearing in Grafana

1. **Check Promtail is running:**
   ```bash
   docker-compose -f docker-compose.observability.yml ps promtail
   ```

2. **Check Promtail logs:**
   ```bash
   docker-compose -f docker-compose.observability.yml logs promtail
   ```

3. **Verify Promtail can reach Loki:**
   ```bash
   docker exec astro-promtail wget -O- http://loki:3100/ready
   ```

4. **Check Loki is receiving logs:**
   ```bash
   curl http://localhost:3100/loki/api/v1/label/container/values
   # Should return: ["astro-api", "astro-celery_worker", ...]
   ```

### Grafana Can't Connect to Loki

1. **Check Loki is running:**
   ```bash
   docker-compose -f docker-compose.observability.yml ps loki
   ```

2. **Check Loki health:**
   ```bash
   curl http://localhost:3100/ready
   # Should return: "ready"
   ```

3. **Check Grafana datasource configuration:**
   - Navigate to **Configuration** → **Data sources** → **Loki**
   - URL should be `http://loki:3100`
   - Click **Save & Test**

### API Logs Not Structured

1. **Check environment:** `DEBUG=false` in `.env` (prod mode)
2. **Restart API:** `docker-compose restart api`
3. **Check logs:** `docker logs astro-api` (should see JSON)

### High Loki Disk Usage

Loki retains logs for 30 days by default. To reduce retention:

1. Edit `config/loki/loki-config.yml`
2. Change `retention_period: 720h` to `168h` (7 days)
3. Restart Loki: `docker-compose -f docker-compose.observability.yml restart loki`

## Best Practices

### 1. Always Use Request Context

```python
# ❌ Bad: No context
logger.info("Chart created")

# ✅ Good: Context automatically included by middleware
from app.core.context import set_request_context

set_request_context(user_id=user.id, chart_id=chart.id)
logger.info("Chart created")
```

### 2. Use Appropriate Log Levels

```python
# ❌ Bad: Everything is INFO
logger.info("Starting calculation")
logger.info("Invalid input")  # Should be WARNING or ERROR

# ✅ Good: Appropriate levels
logger.debug("Starting calculation")  # Dev only
logger.info("Calculation completed")
logger.warning("API rate limit approaching")
logger.error("Failed to fetch geocoding data")
logger.critical("Database connection lost")
```

### 3. Include Relevant Context

```python
# ❌ Bad: No useful information
logger.error("Failed to create chart")

# ✅ Good: Includes details for debugging
logger.bind(
    user_id=user.id,
    birth_datetime=birth_datetime,
    latitude=latitude,
    longitude=longitude,
).error("Failed to create chart", exc_info=True)
```

### 4. Don't Log Sensitive Data

```python
# ❌ Bad: Logging passwords
logger.info(f"User logged in with password: {password}")

# ❌ Bad: Logging full request body with sensitive data
logger.info(f"Request: {request.json()}")

# ✅ Good: Log only non-sensitive fields
logger.info(
    "User logged in",
    user_id=user.id,
    email=user.email,
)
```

### 5. Use Exceptions Properly

```python
# ❌ Bad: No stack trace
try:
    result = calculate_chart()
except Exception as e:
    logger.error(f"Error: {e}")

# ✅ Good: Include stack trace
try:
    result = calculate_chart()
except Exception as e:
    logger.exception("Failed to calculate chart")
    # or
    logger.error("Failed to calculate chart", exc_info=True)
```

### 6. Drop Noisy Logs

Promtail is configured to drop healthcheck logs:

```yaml
# config/promtail/promtail-config.yml
- match:
    selector: '{path="/health"}'
    action: drop
```

Add more drop rules for other noisy endpoints.

### 7. Monitor Error Rates

Create alerts in Grafana for error spikes:

1. Navigate to **Alerting** → **Alert rules**
2. Create alert: "High Error Rate"
3. Condition: `rate({container="astro-api"} |~ "ERROR" [5m]) > 10`
4. Configure notification channel (email, Slack, etc.)

## References

- [Loguru Documentation](https://loguru.readthedocs.io/)
- [Structlog Documentation](https://www.structlog.org/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [LogQL Documentation](https://grafana.com/docs/loki/latest/logql/)
- [Promtail Documentation](https://grafana.com/docs/loki/latest/clients/promtail/)
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
