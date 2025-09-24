# Engine CLI Practical Examples

## Overview

This guide provides practical examples for using the Engine CLI in real-world scenarios. Each example includes the command, expected output, and explanations.

## Getting Started Examples

### 1. First Time Setup

```bash
# Initialize configuration
engine config init

# Verify installation
engine --version

# Get help
engine --help
```

### 2. Basic Status Check

```bash
# Quick system status
engine status

# Detailed health check
engine advanced health

# Show configuration
engine config show
```

## Agent Management Examples

### 3. Creating a Simple Agent

```bash
# Create a basic agent
engine agent create dev-agent \
  --model claude-3-5-sonnet \
  --stack python,react \
  --name "Development Assistant"

# Expected output:
# Agent 'dev-agent' created successfully
# ID: dev-agent
# Model: claude-3-5-sonnet
# Stack: python, react
```

### 4. Creating an Advanced Agent

```bash
# Create a senior developer agent
engine agent create senior-dev \
  --model gpt-4 \
  --name "Senior Developer" \
  --speciality "Full-Stack Development" \
  --persona "Experienced, methodical, quality-focused" \
  --stack python,typescript,postgresql,docker \
  --tools github,vscode,terminal \
  --protocol analysis-first \
  --workflow tdd-workflow \
  --book project-memory

# Expected output:
# Agent 'senior-dev' created successfully with full configuration
```

### 5. Listing and Inspecting Agents

```bash
# List all agents
engine agent list

# Show detailed agent info
engine agent show senior-dev

# List agents with filters
engine agent list --stack python --model gpt-4
```

### 6. Executing Agent Tasks

```bash
# Simple task execution
engine agent execute dev-agent "Create a hello world function in Python"

# Task with context
engine agent execute senior-dev "Refactor this legacy code for better performance" \
  --context-file ./legacy_code.py

# Interactive execution
engine agent execute dev-agent --interactive
```

## Team Management Examples

### 7. Creating a Development Team

```bash
# Create a team
engine team create dev-team \
  --name "Development Team" \
  --description "Full-stack development team"

# Add agents to team
engine team add-agent dev-team senior-dev --role lead-developer
engine team add-agent dev-team dev-agent --role junior-developer

# Set team protocol
engine team set-protocol dev-team code-review-protocol

# Expected output:
# Team 'dev-team' created
# Added senior-dev as lead-developer
# Added dev-agent as junior-developer
# Protocol set to code-review-protocol
```

### 8. Team Coordination

```bash
# Execute team task
engine team execute dev-team "Build a REST API for user management"

# Monitor team activity
engine team monitor dev-team

# Get team status
engine team status dev-team
```

## Workflow Management Examples

### 9. Creating a Development Workflow

```bash
# Create a TDD workflow
engine workflow create tdd-workflow \
  --name "Test-Driven Development" \
  --description "Analysis → Tests → Implementation → Refactor"

# Add vertices (steps)
engine workflow add-vertex tdd-workflow analysis \
  --agent senior-dev \
  --description "Analyze requirements"

engine workflow add-vertex tdd-workflow write-tests \
  --agent dev-agent \
  --description "Write failing tests"

engine workflow add-vertex tdd-workflow implement \
  --agent senior-dev \
  --description "Implement functionality"

engine workflow add-vertex tdd-workflow refactor \
  --agent senior-dev \
  --description "Refactor code"

# Add edges (flow)
engine workflow add-edge tdd-workflow analysis write-tests
engine workflow add-edge tdd-workflow write-tests implement
engine workflow add-edge tdd-workflow implement refactor
```

### 10. Running Workflows

```bash
# Execute workflow
engine workflow run tdd-workflow \
  --input "Create a user authentication system"

# Monitor execution
engine workflow run tdd-workflow \
  --input "Build a payment processing module" \
  --monitor

# Run with custom parameters
engine workflow run tdd-workflow \
  --input "Implement search functionality" \
  --timeout 3600 \
  --max-retries 3
```

## Tool Integration Examples

### 11. Managing Tools

```bash
# List available tools
engine tool list

# Install a tool
engine tool install github-integration

# Configure tool
engine tool configure github-integration \
  --api-key "your-github-token" \
  --repo "owner/repo"

# Test tool
engine tool test github-integration
```

### 12. Using Tools in Agents

```bash
# Create agent with tools
engine agent create devops-agent \
  --model claude-3-5-sonnet \
  --tools github,docker,kubernetes \
  --name "DevOps Engineer"

# Execute with tool usage
engine agent execute devops-agent \
  "Deploy the application to staging environment"
```

## Protocol Management Examples

### 13. Creating Custom Protocols

```bash
# Create a code review protocol
engine protocol create code-review-protocol \
  --name "Code Review Protocol" \
  --description "Structured code review process"

# Add commands
engine protocol add-command code-review-protocol analyze \
  --description "Analyze code for issues"

engine protocol add-command code-review-protocol suggest \
  --description "Suggest improvements"

engine protocol add-command code-review-protocol approve \
  --description "Approve changes"
```

### 14. Using Protocols

```bash
# Assign protocol to agent
engine agent set-protocol senior-dev code-review-protocol

# Execute with protocol
engine agent execute senior-dev \
  "Review this pull request" \
  --protocol code-review-protocol
```

## Book (Memory) Management Examples

### 15. Creating Memory Books

```bash
# Create project memory book
engine book create project-memory \
  --name "Project Documentation" \
  --description "Project knowledge base"

# Add chapters
engine book add-chapter project-memory architecture \
  --title "System Architecture"

engine book add-chapter project-memory development \
  --title "Development Guidelines"

# Add pages
engine book add-page project-memory architecture overview \
  --title "System Overview" \
  --content "High-level system description..."

engine book add-page project-memory development coding-standards \
  --title "Coding Standards" \
  --content "Code formatting and style guidelines..."
```

### 16. Using Memory in Agents

```bash
# Assign book to agent
engine agent set-book senior-dev project-memory

# Agent can now reference project knowledge
engine agent execute senior-dev \
  "Update the user API following our coding standards"

# Search memory
engine book search project-memory "authentication"

# Update memory
engine book update-page project-memory development coding-standards \
  --content "Updated coding standards..."
```

## Configuration Management Examples

### 17. Managing Configuration

```bash
# Show current config
engine config show

# Set configuration values
engine config set api.base_url "https://api.engine-framework.com"
engine config set api.timeout 30
engine config set database.url "postgresql://user:pass@localhost:5432/engine"

# Get specific values
engine config get api.base_url
engine config get agent_defaults.model

# Export configuration
engine config export my-config.yaml

# Import configuration
engine config import my-config.yaml
```

### 18. Environment Variables

```bash
# Set environment variables
export ENGINE_API_KEY="your-api-key"
export ENGINE_DATABASE_URL="postgresql://..."
export ENGINE_LOG_LEVEL="DEBUG"

# Use in commands
engine --config-env agent create test-agent --model gpt-4
```

## Advanced Usage Examples

### 19. Batch Operations

```bash
# Create multiple agents from file
engine agent create-batch agents.yaml

# Execute workflow on multiple inputs
engine workflow run-batch tdd-workflow inputs.txt

# Bulk configuration update
engine config update-batch config-updates.yaml
```

### 20. Monitoring and Logging

```bash
# Monitor system
engine advanced monitor

# View logs
engine advanced logs --lines 100

# Filter logs
engine advanced logs --level error --grep "agent"

# Export logs
engine advanced logs --export debug.log --since "1 hour ago"
```

### 21. Interactive Mode

```bash
# Start interactive session
engine interactive

# Interactive agent execution
engine agent interactive senior-dev

# Interactive workflow building
engine workflow interactive
```

### 22. Backup and Recovery

```bash
# Create backup
engine advanced backup create "pre-deployment-backup"

# List backups
engine advanced backup list

# Restore from backup
engine advanced backup restore "pre-deployment-backup"

# Export data
engine advanced export --format json --output data.json
```

## Real-World Scenarios

### 23. Full-Stack Development Project

```bash
# Set up development environment
engine config init
engine config set api.base_url "http://localhost:8000"

# Create specialized agents
engine agent create backend-dev --model gpt-4 --stack python,postgresql,fastapi
engine agent create frontend-dev --model claude-3-5-sonnet --stack react,typescript
engine agent create qa-engineer --model gpt-3.5-turbo --stack testing,cypress

# Create development team
engine team create fullstack-team
engine team add-agent fullstack-team backend-dev --role backend-lead
engine team add-agent fullstack-team frontend-dev --role frontend-lead
engine team add-agent fullstack-team qa-engineer --role qa-lead

# Create project workflow
engine workflow create fullstack-workflow
engine workflow add-vertex fullstack-workflow requirements --agent backend-dev
engine workflow add-vertex fullstack-workflow backend-api --agent backend-dev
engine workflow add-vertex fullstack-workflow frontend-ui --agent frontend-dev
engine workflow add-vertex fullstack-workflow integration --agent qa-engineer
engine workflow add-edge fullstack-workflow requirements backend-api
engine workflow add-edge fullstack-workflow backend-api frontend-ui
engine workflow add-edge fullstack-workflow frontend-ui integration

# Execute project
engine workflow run fullstack-workflow \
  --input "Build a task management application with user authentication"
```

### 24. DevOps Automation

```bash
# Create DevOps agent
engine agent create devops-agent \
  --model claude-3-5-sonnet \
  --tools docker,kubernetes,github,aws \
  --name "DevOps Engineer"

# Set up CI/CD workflow
engine workflow create cicd-workflow
engine workflow add-vertex cicd-workflow build --agent devops-agent
engine workflow add-vertex cicd-workflow test --agent devops-agent
engine workflow add-vertex cicd-workflow deploy --agent devops-agent
engine workflow add-edge cicd-workflow build test
engine workflow add-edge cicd-workflow test deploy

# Execute deployment
engine workflow run cicd-workflow \
  --input "Deploy version 2.1.0 to production environment"
```

### 25. Research and Analysis

```bash
# Create research agent
engine agent create research-agent \
  --model gpt-4 \
  --tools web-search,data-analysis \
  --name "Research Analyst"

# Create analysis workflow
engine workflow create research-workflow
engine workflow add-vertex research-workflow gather-data --agent research-agent
engine workflow add-vertex research-workflow analyze --agent research-agent
engine workflow add-vertex research-workflow report --agent research-agent
engine workflow add-edge research-workflow gather-data analyze
engine workflow add-edge research-workflow analyze report

# Execute research
engine workflow run research-workflow \
  --input "Analyze the current state of AI agent frameworks"
```

## Error Handling Examples

### 26. Handling Common Errors

```bash
# Command fails - get detailed error
engine --verbose agent create test-agent --model invalid-model

# Configuration error - validate config
engine config validate

# Connection error - check status
engine status
engine advanced health

# Permission error - check and fix
ls -la ~/.engine/
chmod 644 ~/.engine/config.yaml
```

### 27. Recovery Procedures

```bash
# Agent execution fails - retry with debug
engine agent execute failing-agent "task" --debug --retry 3

# Workflow fails - check intermediate results
engine workflow status failed-workflow-id
engine workflow logs failed-workflow-id

# System unstable - restart services
engine advanced services restart
```

## Performance Optimization Examples

### 28. Optimizing Performance

```bash
# Check system performance
engine advanced benchmark

# Optimize configuration
engine config set core.max_memory "2GB"
engine config set core.max_concurrent_agents 10

# Monitor resource usage
engine advanced monitor --continuous

# Clear caches
engine advanced cache clear
```

### 29. Scaling Operations

```bash
# Scale team operations
engine team scale dev-team --agents 5

# Parallel workflow execution
engine workflow run-parallel workflow1 workflow2 workflow3

# Batch processing
engine advanced batch-process --input tasks.json --workers 4
```

## Integration Examples

### 30. Integrating with External Systems

```bash
# GitHub integration
engine tool configure github \
  --token "ghp_..." \
  --repo "owner/repo"

# Slack notifications
engine tool configure slack \
  --webhook "https://hooks.slack.com/..." \
  --channel "#devops"

# Database integration
engine config set database.url "postgresql://user:pass@host:5432/db"
engine advanced database test-connection
```

---

## Command Reference Summary

| Category | Common Commands |
|----------|-----------------|
| **Setup** | `config init`, `status`, `--help` |
| **Agents** | `agent create`, `agent execute`, `agent list` |
| **Teams** | `team create`, `team add-agent`, `team execute` |
| **Workflows** | `workflow create`, `workflow run`, `workflow add-vertex` |
| **Tools** | `tool list`, `tool install`, `tool configure` |
| **Protocols** | `protocol create`, `protocol add-command` |
| **Memory** | `book create`, `book add-page`, `book search` |
| **Config** | `config show`, `config set`, `config export` |
| **Advanced** | `advanced health`, `advanced logs`, `advanced monitor` |

For more detailed information, see the [CLI Manual](README.md) or use `engine [command] --help`.
