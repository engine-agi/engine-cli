# Engine CLI Troubleshooting Guide

## Overview

This guide helps you troubleshoot common issues with the Engine CLI. Most problems can be resolved by following the steps below.

## Quick Diagnosis

### Check CLI Installation
```bash
# Verify installation
engine --version

# Check if CLI is in PATH
which engine

# Test basic functionality
engine --help
```

### Check Configuration
```bash
# Show current configuration
engine config show

# Validate configuration
engine config validate

# Check configuration file location
engine config paths
```

### Check System Status
```bash
# Overall system health
engine status

# Detailed health check
engine advanced health

# Monitor system resources
engine advanced monitor
```

## Common Issues and Solutions

### 1. "Command not found" Error

**Symptoms:**
- `engine: command not found`
- CLI not recognized in terminal

**Solutions:**

```bash
# Check if CLI is installed
pip list | grep engine-cli

# Reinstall CLI
pip install --upgrade engine-cli

# Or install from source
pip install -e .

# Verify PATH includes Python bin directory
echo $PATH
which python
python -m engine_cli.main --help
```

### 2. Configuration File Issues

**Symptoms:**
- "Configuration file not found"
- Settings not persisting
- Commands fail with config errors

**Solutions:**

```bash
# Initialize configuration
engine config init

# Force overwrite existing config
engine config init --force

# Specify custom config path
engine --config /path/to/config.yaml [command]

# Check file permissions
ls -la ~/.engine/
chmod 644 ~/.engine/config.yaml
```

### 3. Connection Refused Errors

**Symptoms:**
- API calls fail
- Database connection errors
- "Connection refused" messages

**Solutions:**

```bash
# Check API server status
engine advanced health

# Verify API configuration
engine config get api.base_url
engine config get api.timeout

# Test network connectivity
curl -I http://localhost:8000/health

# Update API URL
engine config set api.base_url "http://localhost:8000"
```

### 4. Database Connection Issues

**Symptoms:**
- Database-related command failures
- "Unable to connect to database" errors

**Solutions:**

```bash
# Check database configuration
engine config get database.url

# Test database connection (if available)
engine advanced health

# Update database URL
engine config set database.url "postgresql://user:pass@localhost:5432/engine"

# Verify PostgreSQL is running
sudo systemctl status postgresql
```

### 5. Permission Denied Errors

**Symptoms:**
- File access errors
- "Permission denied" when writing files
- Cannot create directories

**Solutions:**

```bash
# Check file permissions
ls -la ~/.engine/

# Fix permissions
chmod 755 ~/.engine
chmod 644 ~/.engine/config.yaml

# Change ownership if needed
sudo chown -R $USER:$USER ~/.engine

# Run with appropriate permissions
sudo engine [command]
```

### 6. Agent Execution Failures

**Symptoms:**
- Agent commands fail to execute
- "Agent not found" errors
- Model/API key issues

**Solutions:**

```bash
# List available agents
engine agent list

# Check agent configuration
engine agent show AGENT_ID

# Verify API keys and model access
engine config get api.key
engine config get agent_defaults.model

# Test agent execution with simple task
engine agent execute AGENT_ID "Hello world"
```

### 7. Workflow Execution Issues

**Symptoms:**
- Workflows fail to start
- Vertex/agent execution errors
- Workflow hangs or times out

**Solutions:**

```bash
# Check workflow definition
engine workflow show WORKFLOW_ID

# Validate workflow structure
engine workflow validate WORKFLOW_ID

# Test individual agents
engine agent execute AGENT_ID "test task"

# Monitor workflow execution
engine workflow run WORKFLOW_ID --monitor

# Check logs
engine advanced logs --level error
```

### Performance Issues

**Symptoms:**
- CLI is slow to respond
- Commands take longer than expected
- High CPU usage during startup

**Solutions:**

```bash
# Check startup performance
time engine --version

# Clear command cache to force reload
engine advanced cache clear

# Check cache status
engine advanced cache status

# View detailed cache information
engine advanced cache info

# Expected startup time: < 2 seconds
# Typical startup time: 0.3-0.5 seconds
# Benchmark results: Average 0.355s (5 runs)
```

### Cache Management

```bash
# View cache status
engine advanced cache status

# Clear all caches (use with caution)
engine advanced cache clear

# View cache contents
engine advanced cache info
```

## Debug Mode

### Enable Verbose Output

```bash
# Use verbose flag
engine --verbose [command]

# Set debug level
export ENGINE_LOG_LEVEL=DEBUG
engine [command]

# Enable all debug output
export ENGINE_DEBUG=true
engine [command]
```

### Log Analysis

```bash
# View recent logs
engine advanced logs --lines 50

# Filter by level
engine advanced logs --level error

# Search for specific terms
engine advanced logs --grep "error"

# Export logs for analysis
engine advanced logs --export debug.log
```

### Debug Configuration

```bash
# Show all configuration
engine config show --verbose

# Validate configuration syntax
engine config validate --strict

# Test configuration loading
engine config test-load
```

## Environment-Specific Issues

### Docker Environment

```bash
# Check container status
docker ps | grep engine

# View container logs
docker logs engine-cli

# Access container shell
docker exec -it engine-cli bash

# Check network connectivity
docker network ls
```

### Kubernetes Environment

```bash
# Check pod status
kubectl get pods | grep engine

# View pod logs
kubectl logs -f engine-cli-pod

# Check service endpoints
kubectl get services

# Test internal connectivity
kubectl exec -it engine-cli-pod -- engine status
```

### CI/CD Environment

```bash
# Verify environment variables
env | grep ENGINE_

# Check configuration paths
engine config paths

# Test with minimal config
ENGINE_CONFIG_MINIMAL=true engine [command]

# Disable interactive features
ENGINE_NON_INTERACTIVE=true engine [command]
```

## Advanced Troubleshooting

### Network Diagnostics

```bash
# Test API connectivity
curl -v http://localhost:8000/health

# Check DNS resolution
nslookup api.engine-framework.com

# Test with different timeouts
engine --timeout 60 [command]

# Use proxy settings
export HTTP_PROXY=http://proxy.company.com:8080
engine [command]
```

### Dependency Issues

```bash
# Check Python dependencies
pip check

# Reinstall dependencies
pip install --force-reinstall engine-cli

# Check for conflicting packages
pip list | grep -E "(click|rich|pydantic)"

# Use virtual environment
python -m venv debug-env
source debug-env/bin/activate
pip install engine-cli
```

### Plugin/Extension Issues

```bash
# List loaded plugins
engine plugin list

# Test plugin loading
engine plugin test PLUGIN_NAME

# Disable problematic plugins
engine config set plugins.disabled "problematic-plugin"

# Reinstall plugins
engine plugin reinstall
```

## Getting Help

### Built-in Help

```bash
# General help
engine --help

# Command-specific help
engine agent --help
engine config --help

# Interactive tutorial
engine interactive --tutorial
```

### Community Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the complete CLI manual
- **Discord**: Join our community for real-time help

### Professional Support

For enterprise deployments and critical issues:

- **Email**: support@engine-framework.com
- **Priority Support**: Available for commercial licenses
- **On-site Assistance**: Custom deployment support

## Prevention Best Practices

### Regular Maintenance

```bash
# Update CLI regularly
pip install --upgrade engine-cli

# Clean old logs
engine advanced logs --clean --older-than 30d

# Backup configuration
engine advanced config-ops export backup-$(date +%Y%m%d).yaml

# Run health checks weekly
engine advanced health --comprehensive
```

### Monitoring Setup

```bash
# Enable monitoring
engine config set monitoring.enabled true

# Set up alerts
engine config set monitoring.alerts.enabled true

# Configure log rotation
engine config set logging.rotation.enabled true
```

### Backup Strategy

```bash
# Regular configuration backups
crontab -e
# Add: 0 2 * * * engine advanced config-ops export /backups/config-$(date +%Y%m%d).yaml

# Database backups (if applicable)
# Add: 0 3 * * * pg_dump engine > /backups/db-$(date +%Y%m%d).sql

# Log archival
# Add: 0 4 * * 0 engine advanced logs --export /backups/logs-$(date +%W).log --clean
```

## Emergency Procedures

### Complete Reset

**⚠️ WARNING: This will delete all configuration and data**

```bash
# Stop all services
engine advanced services stop

# Backup important data first
engine advanced backup create emergency-backup

# Reset configuration
rm -rf ~/.engine
engine config init

# Reset database (if applicable)
# WARNING: This deletes all data
engine advanced database reset --confirm

# Restart services
engine advanced services start
```

### Recovery from Backup

```bash
# List available backups
engine advanced backup list

# Restore from backup
engine advanced backup restore latest

# Verify restoration
engine status
engine config show
```

## Diagnostic Commands

### System Information

```bash
# Complete system info
engine advanced system-info

# Environment details
engine advanced env-info

# Dependency versions
engine advanced deps-info
```

### Performance Diagnostics

```bash
# Performance benchmark
engine advanced benchmark

# Memory usage analysis
engine advanced memory-usage

# CPU profiling
engine advanced cpu-profile
```

### Network Diagnostics

```bash
# Network connectivity test
engine advanced network-test

# API endpoint validation
engine advanced api-test

# WebSocket connection test
engine advanced ws-test
```

---

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| Command not found | `pip install --upgrade engine-cli` |
| Config not found | `engine config init` |
| Connection refused | `engine config set api.base_url "http://localhost:8000"` |
| Permission denied | `chmod 644 ~/.engine/config.yaml` |
| Slow performance | `export ENGINE_LOG_LEVEL=INFO` |
| Debug mode | `engine --verbose [command]` |

For additional help, visit our [documentation](README.md) or create an issue on GitHub.