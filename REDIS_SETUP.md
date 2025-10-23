# Redis Setup Guide

## Overview

This project uses Redis as its primary data store for caching stock market data and analysis results. Redis provides fast in-memory data storage with persistence capabilities.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed on your system

### Starting Redis

1. **Start the Redis service:**
   ```bash
   docker-compose up -d
   ```

2. **Verify Redis is running:**
   ```bash
   docker ps | grep stock-analyzer-redis
   ```

3. **Test Redis connection:**
   ```bash
   docker exec stock-analyzer-redis redis-cli ping
   ```
   Expected output: `PONG`

### Stopping Redis

```bash
docker-compose down
```

To stop and remove all data:
```bash
docker-compose down -v
```

## Redis Configuration

The `docker-compose.yml` file includes:
- **Image:** Redis 7 Alpine (lightweight)
- **Port:** 6379 (mapped to host)
- **Data Persistence:** Volume mounted at `/data` with AOF (Append Only File) enabled
- **Health Check:** Automatic health monitoring
- **Auto-restart:** Container restarts automatically unless manually stopped

## Connection Details

- **Host:** `localhost`
- **Port:** `6379`
- **Database:** `0` (default)

These settings are used in `src/utils/database_adapters/redis_adapter.py`:
```python
RedisAdapter(host='localhost', port=6379, db=0)
```

## Monitoring Redis

### View Redis logs
```bash
docker logs stock-analyzer-redis
```

### Connect to Redis CLI
```bash
docker exec -it stock-analyzer-redis redis-cli
```

### Common Redis CLI commands
```bash
# Check all keys
KEYS *

# Get a specific value
GET <key>

# Check database size
DBSIZE

# Get Redis info
INFO

# Monitor all commands in real-time
MONITOR
```

## Data Persistence

Redis data is persisted in a Docker volume named `stock-analyzer-backend_redis-data`. This ensures data survives container restarts.

To backup Redis data:
```bash
docker exec stock-analyzer-redis redis-cli BGSAVE
docker cp stock-analyzer-redis:/data/dump.rdb ./redis-backup.rdb
```

To restore from backup:
```bash
docker cp ./redis-backup.rdb stock-analyzer-redis:/data/dump.rdb
docker restart stock-analyzer-redis
```

## Troubleshooting

### Error: Connection refused (Error 111)
- **Cause:** Redis service is not running
- **Solution:** Run `docker-compose up -d`

### Error: Port 6379 already in use
- **Cause:** Another Redis instance or service is using port 6379
- **Solution:** 
  - Stop the conflicting service
  - Or modify `docker-compose.yml` to use a different port (e.g., `"6380:6379"`)
  - Update Redis connection settings in the application accordingly

### Container keeps restarting
- **Check logs:** `docker logs stock-analyzer-redis`
- **Check disk space:** Redis needs sufficient space for data persistence
- **Check memory:** Ensure adequate memory is available

## Production Considerations

For production deployments, consider:

1. **Password Protection:**
   Add password authentication to `docker-compose.yml`:
   ```yaml
   command: redis-server --appendonly yes --requirepass your_secure_password
   ```

2. **Memory Limits:**
   Add resource constraints:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 512M
   ```

3. **Network Security:**
   Don't expose Redis port directly; use a private network

4. **Monitoring:**
   Integrate with monitoring tools like Redis Exporter for Prometheus

5. **Backup Strategy:**
   Implement automated backup scripts

## Alternative: Local Redis Installation

If you prefer not to use Docker:

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### macOS
```bash
brew install redis
brew services start redis
```

### Windows
Use Windows Subsystem for Linux (WSL) or Redis for Windows port

## Testing Redis Connection

Use the test script:
```python
import redis

client = redis.StrictRedis(host='localhost', port=6379, db=0)
client.ping()  # Should return True
```

Or run the project examples:
```bash
python examples/example_data_fetch_and_stash_into_redis.py
```
