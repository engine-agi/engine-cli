"""
Performance Tests for Engine CLI
Benchmarks with 100+ agents and <100ms response times.
"""

import json
import os
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

import pytest

# Import core components for performance testing
from engine_core.core.agents.agent_builder import AgentBuilder  # type: ignore
from engine_core.core.teams.team_builder import TeamBuilder  # type: ignore
from engine_core.core.teams.team_builder import TeamMemberRole
from engine_core.core.workflows.workflow_builder import WorkflowBuilder  # type: ignore


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""

    operation: str
    count: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    p95_time: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PerformanceReporter:
    """Generate performance reports."""

    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.start_time = time.time()

    def add_metric(self, metric: PerformanceMetrics):
        """Add a performance metric."""
        self.metrics.append(metric)

    def generate_report(self) -> str:
        """Generate a comprehensive performance report."""
        total_duration = time.time() - self.start_time

        report = []
        report.append("# 🚀 Engine CLI Performance Report")
        report.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total Duration:** {total_duration:.2f}s")
        report.append("")

        # Summary table
        report.append("## 📊 Summary")
        report.append("| Operation | Count | Avg Time | P95 | Status |")
        report.append("|-----------|-------|----------|-----|--------|")

        for metric in self.metrics:
            status = "✅ <100ms" if metric.p95_time < 0.1 else "❌ >100ms"
            report.append(
                f"| {
    metric.operation} | {
        metric.count} | {
            metric.avg_time:.4f}s | {
                metric.p95_time:.4f}s | {status} |"
            )

        report.append("")

        # Detailed metrics
        report.append("## 📈 Detailed Metrics")
        for metric in self.metrics:
            report.append(f"### {metric.operation}")
            report.append(f"- **Count:** {metric.count}")
            report.append(f"- **Total Time:** {metric.total_time:.4f}s")
            report.append(f"- **Average:** {metric.avg_time:.4f}s")
            report.append(f"- **Min:** {metric.min_time:.4f}s")
            report.append(f"- **Max:** {metric.max_time:.4f}s")
            report.append(f"- **P95:** {metric.p95_time:.4f}s")
            report.append("")

        # Compliance check
        all_under_100ms = all(m.p95_time < 0.1 for m in self.metrics)
        report.append("## 🎯 Compliance Check")
        if all_under_100ms:
            report.append(
                "✅ **ALL OPERATIONS UNDER 100ms** - Performance requirements met!"
            )
        else:
            report.append(
                "❌ **PERFORMANCE ISSUES DETECTED** - Some operations exceed 100ms"
            )
            slow_ops = [m for m in self.metrics if m.p95_time >= 0.1]
            for op in slow_ops:
                report.append(f"   - {op.operation}: {op.p95_time:.4f}s")

        return "\n".join(report)

    def save_report(self, filepath: str):
        """Save report to file."""
        report = self.generate_report()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)


@pytest.fixture
def performance_reporter():
    """Fixture for performance reporting."""
    return PerformanceReporter()


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for performance testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        # Create necessary directories
        os.makedirs("agents", exist_ok=True)
        os.makedirs("teams", exist_ok=True)
        os.makedirs("workflows", exist_ok=True)
        os.makedirs("books", exist_ok=True)

        yield temp_dir

        os.chdir(original_cwd)


class TestPerformanceBenchmarks:
    """Performance benchmarks for Engine CLI operations."""

    def _measure_operation(
        self, operation_name: str, count: int, operation_func
    ) -> PerformanceMetrics:
        """Measure performance of an operation."""
        times = []

        for i in range(count):
            start_time = time.perf_counter()
            operation_func(i)
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        times.sort()
        total_time = sum(times)
        avg_time = total_time / count
        min_time = min(times)
        max_time = max(times)

        # Calculate P95 (95th percentile)
        p95_index = int(count * 0.95)
        p95_time = times[p95_index] if p95_index < count else times[-1]

        return PerformanceMetrics(
            operation=operation_name,
            count=count,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            p95_time=p95_time,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    @pytest.mark.performance
    def test_agent_creation_100_agents(self, temp_workspace, performance_reporter):
        """Benchmark creating 100 agents."""

        def create_agent(i):
            agent = (
                AgentBuilder()
                .with_id(f"perf-agent-{i:03d}")
                .with_model("claude-3.5-sonnet")
                .with_name(f"Performance Agent {i}")
                .with_speciality("Performance Testing")
                .with_stack(["python", "benchmarking"])
                .build()
            )

            # Simulate CLI storage
            agent_data = {
                "id": f"perf-agent-{i:03d}",
                "model": "claude-3.5-sonnet",
                "name": f"Performance Agent {i}",
                "speciality": "Performance Testing",
                "stack": ["python", "benchmarking"],
                "created_at": "2025-09-23T10:00:00.000000",
            }

            agent_file = Path(f"agents/perf-agent-{i:03d}.yaml")
            with open(agent_file, "w") as f:
                json.dump(agent_data, f)

            return agent

        metric = self._measure_operation(
            "Agent Creation (100 agents)", 100, create_agent
        )
        performance_reporter.add_metric(metric)

        # Verify all agents were created
        assert len(list(Path("agents").glob("*.yaml"))) == 100

        # Assert performance requirement: P95 < 100ms
        assert (
            metric.p95_time < 0.1
        ), f"Agent creation P95 time {metric.p95_time:.4f}s exceeds 100ms requirement"

    @pytest.mark.performance
    def test_agent_loading_100_agents(self, temp_workspace, performance_reporter):
        """Benchmark loading 100 agents from storage."""
        # First create 100 agents
        for i in range(100):
            agent_data = {
                "id": f"perf-agent-{i:03d}",
                "model": "claude-3.5-sonnet",
                "name": f"Performance Agent {i}",
                "speciality": "Performance Testing",
                "stack": ["python", "benchmarking"],
                "created_at": "2025-09-23T10:00:00.000000",
            }

            agent_file = Path(f"agents/perf-agent-{i:03d}.yaml")
            with open(agent_file, "w") as f:
                json.dump(agent_data, f)

        def load_agent(i):
            agent_file = Path(f"agents/perf-agent-{i:03d}.yaml")
            with open(agent_file, "r") as f:
                data = json.load(f)

            # Recreate agent from data
            agent = (
                AgentBuilder()
                .with_id(data["id"])
                .with_model(data["model"])
                .with_name(data["name"])
                .with_speciality(data.get("speciality", ""))
                .with_stack(data.get("stack", []))
                .build()
            )
            return agent

        metric = self._measure_operation("Agent Loading (100 agents)", 100, load_agent)
        performance_reporter.add_metric(metric)

        # Assert performance requirement: P95 < 100ms
        assert (
            metric.p95_time < 0.1
        ), f"Agent loading P95 time {metric.p95_time:.4f}s exceeds 100ms requirement"

    @pytest.mark.performance
    def test_team_creation_with_50_members(self, temp_workspace, performance_reporter):
        """Benchmark creating teams with 50 members each."""
        # Create 100 agents first
        agents = []
        for i in range(100):
            agent = (
                AgentBuilder()
                .with_id(f"team-agent-{i:03d}")
                .with_model("claude-3.5-sonnet")
                .with_name(f"Team Agent {i}")
                .build()
            )
            agents.append(agent)

        def create_team_with_members(i):
            # Create team with 50 members (2 teams total)
            team_size = 50
            start_idx = i * team_size
            end_idx = start_idx + team_size

            team_agents = agents[start_idx:end_idx]

            team_builder = (
                TeamBuilder()
                .with_id(f"perf-team-{i}")
                .with_name(f"Performance Team {i}")
            )

            # Add members with alternating roles
            for j, agent in enumerate(team_agents):
                role = TeamMemberRole.LEADER if j == 0 else TeamMemberRole.MEMBER
                team_builder = team_builder.add_member(agent.id, role)

            team = team_builder.build()

            # Simulate CLI storage
            team_data = {
                "id": f"perf-team-{i}",
                "name": f"Performance Team {i}",
                "members": [
                    {
                        "id": agent.id,
                        "role": ("leader" if j == 0 else "member"),
                        "name": agent.name,
                    }
                    for j, agent in enumerate(team_agents)
                ],
                "created_at": "2025-09-23T10:00:00.000000",
            }

            team_file = Path(f"teams/perf-team-{i}.yaml")
            with open(team_file, "w") as f:
                json.dump(team_data, f)

            return team

        metric = self._measure_operation(
            "Team Creation (50 members each)", 2, create_team_with_members
        )
        performance_reporter.add_metric(metric)

        # Verify teams were created
        assert len(list(Path("teams").glob("*.yaml"))) == 2

        # Assert performance requirement: P95 < 100ms
        assert (
            metric.p95_time < 0.1
        ), f"Team creation P95 time {metric.p95_time:.4f}s exceeds 100ms requirement"

    @pytest.mark.performance
    def test_workflow_creation_complex(self, temp_workspace, performance_reporter):
        """Benchmark creating complex workflows with multiple vertices."""
        # Create 10 agents for workflow vertices
        agents = []
        for i in range(10):
            agent = (
                AgentBuilder()
                .with_id(f"workflow-agent-{i}")
                .with_model("claude-3.5-sonnet")
                .with_name(f"Workflow Agent {i}")
                .build()
            )
            agents.append(agent)

        def create_complex_workflow(i):
            workflow = (
                WorkflowBuilder()
                .with_id(f"perf-workflow-{i}")
                .with_name(f"Performance Workflow {i}")
            )

            # Add 10 vertices with different agents
            for j in range(10):
                workflow = workflow.add_agent_vertex(
                    f"task-{j}", agents[j], f"Execute task {j} in workflow {i}"
                )

            # Add edges to create a complex graph
            for j in range(9):
                workflow = workflow.add_edge(f"task-{j}", f"task-{j+1}")

            # Add some parallel edges
            workflow = workflow.add_edge("task-0", "task-5")
            workflow = workflow.add_edge("task-2", "task-7")

            workflow = workflow.build()

            # Simulate CLI storage
            workflow_data = {
                "id": f"perf-workflow-{i}",
                "name": f"Performance Workflow {i}",
                "vertices": [
                    {
                        "id": f"task-{j}",
                        "agent_id": agents[j].id,
                        "task": f"Execute task {j} in workflow {i}",
                    }
                    for j in range(10)
                ],
                "edges": [{"from": f"task-{j}", "to": f"task-{j+1}"} for j in range(9)]
                + [
                    {"from": "task-0", "to": "task-5"},
                    {"from": "task-2", "to": "task-7"},
                ],
                "created_at": "2025-09-23T10:00:00.000000",
            }

            workflow_file = Path(f"workflows/perf-workflow-{i}.yaml")
            with open(workflow_file, "w") as f:
                json.dump(workflow_data, f)

            return workflow

        metric = self._measure_operation(
            "Complex Workflow Creation (10 vertices)",
            5,
            create_complex_workflow,
        )
        performance_reporter.add_metric(metric)

        # Verify workflows were created
        assert len(list(Path("workflows").glob("*.yaml"))) == 5

        # Assert performance requirement: P95 < 100ms
        assert (
    metric.p95_time < 0.1 ), f"Workflow creation P95 time {
        metric.p95_time:.4f}s exceeds 100ms requirement"

    @pytest.mark.performance
    def test_bulk_operations_1000_items(self, temp_workspace, performance_reporter):
        """Benchmark bulk operations with 1000 items."""

        def bulk_agent_creation(i):
            # Create 100 agents in each bulk operation (10 operations = 1000 total)
            agents_data = []
            for j in range(100):
                agent_data = {
                    "id": f"bulk-agent-{i*100 + j:04d}",
                    "model": "claude-3.5-sonnet",
                    "name": f"Bulk Agent {i*100 + j}",
                    "speciality": "Bulk Operations",
                    "stack": ["python", "bulk"],
                    "created_at": "2025-09-23T10:00:00.000000",
                }
                agents_data.append(agent_data)

            # Write all agents in bulk
            for agent_data in agents_data:
                agent_file = Path(f"agents/{agent_data['id']}.yaml")
                with open(agent_file, "w") as f:
                    json.dump(agent_data, f)

            return len(agents_data)

        metric = self._measure_operation(
            "Bulk Agent Creation (100 agents/batch)", 10, bulk_agent_creation
        )
        performance_reporter.add_metric(metric)

        # Verify all agents were created
        agent_files = list(Path("agents").glob("*.yaml"))
        assert len(agent_files) == 1000

        # Assert performance requirement: P95 < 100ms
        assert (
            metric.p95_time < 0.1
        ), f"Bulk operations P95 time {metric.p95_time:.4f}s exceeds 100ms requirement"

    @pytest.mark.performance
    def test_end_to_end_project_simulation_100_scale(
        self, temp_workspace, performance_reporter
    ):
        """Benchmark end-to-end project simulation at 100x scale."""

        def create_full_project(i):
            # Create 10 agents per project (100 agents total across 10 projects)
            project_agents = []
            for j in range(10):
                agent = (
                    AgentBuilder()
                    .with_id(f"project-{i}-agent-{j}")
                    .with_model("claude-3.5-sonnet" if j % 2 == 0 else "claude-3-haiku")
                    .with_name(f"Project {i} Agent {j}")
                    .with_speciality(f"Role {j}")
                    .with_stack(["python", f"skill-{j}"])
                    .build()
                )
                project_agents.append(agent)

            # Create team with all agents
            team_builder = (
                TeamBuilder()
                .with_id(f"project-{i}-team")
                .with_name(f"Project {i} Team")
            )

            for j, agent in enumerate(project_agents):
                role = TeamMemberRole.LEADER if j == 0 else TeamMemberRole.MEMBER
                team_builder = team_builder.add_member(agent.id, role)

            team = team_builder.build()

            # Create workflow
            workflow = (
                WorkflowBuilder()
                .with_id(f"project-{i}-workflow")
                .with_name(f"Project {i} Workflow")
            )

            # Add vertices for each agent
            for j, agent in enumerate(project_agents):
                workflow = workflow.add_agent_vertex(
                    f"step-{j}", agent, f"Execute step {j} for project {i}"
                )

            # Add sequential edges
            for j in range(len(project_agents) - 1):
                workflow = workflow.add_edge(f"step-{j}", f"step-{j+1}")

            workflow = workflow.build()

            # Simulate storage for all components
            # Save agents
            for agent in project_agents:
                agent_data = {
                    "id": agent.id,
                    "model": (
                        "claude-3.5-sonnet"
                        if "claude-3.5-sonnet" in str(agent)
                        else "claude-3-haiku"
                    ),
                    "name": agent.name,
                    "speciality": f"Role {project_agents.index(agent)}",
                    "stack": [
                        "python",
                        f"skill-{project_agents.index(agent)}",
                    ],
                    "created_at": "2025-09-23T10:00:00.000000",
                }
                agent_file = Path(f"agents/{agent.id}.yaml")
                with open(agent_file, "w") as f:
                    json.dump(agent_data, f)

            # Save team
            team_data = {
                "id": team.id,
                "name": team.name,
                "members": [
                    {
                        "id": agent.id,
                        "role": ("leader" if j == 0 else "member"),
                        "name": agent.name,
                    }
                    for j, agent in enumerate(project_agents)
                ],
                "created_at": "2025-09-23T10:00:00.000000",
            }
            team_file = Path(f"teams/{team.id}.yaml")
            with open(team_file, "w") as f:
                json.dump(team_data, f)

            # Save workflow
            workflow_data = {
                "id": workflow.id,
                "name": workflow.name,
                "vertices": [
                    {
                        "id": f"step-{j}",
                        "agent_id": agent.id,
                        "task": f"Execute step {j} for project {i}",
                    }
                    for j, agent in enumerate(project_agents)
                ],
                "edges": [
                    {"from": f"step-{j}", "to": f"step-{j+1}"}
                    for j in range(len(project_agents) - 1)
                ],
                "created_at": "2025-09-23T10:00:00.000000",
            }
            workflow_file = Path(f"workflows/{workflow.id}.yaml")
            with open(workflow_file, "w") as f:
                json.dump(workflow_data, f)

            return {
                "agents": project_agents,
                "team": team,
                "workflow": workflow,
            }

        metric = self._measure_operation(
            "End-to-End Project Creation (10 agents/project)",
            10,
            create_full_project,
        )
        performance_reporter.add_metric(metric)

        # Verify all components were created
        assert (
            len(list(Path("agents").glob("*.yaml"))) == 100
        )  # 10 projects * 10 agents
        assert len(list(Path("teams").glob("*.yaml"))) == 10  # 10 teams
        assert len(list(Path("workflows").glob("*.yaml"))) == 10  # 10 workflows

        # Assert performance requirement: P95 < 100ms
        assert (
            metric.p95_time < 0.1
        ), f"End-to-end project creation P95 time {metric.p95_time:.4f}s exceeds 100ms requirement"

    @pytest.mark.performance
    def test_generate_performance_report(self, temp_workspace, performance_reporter):
        """Generate and save performance report."""

        # Run a quick benchmark to have data for the report
        def quick_agent_creation(i):
            agent = (
                AgentBuilder()
                .with_id(f"report-agent-{i}")
                .with_model("claude-3.5-sonnet")
                .with_name(f"Report Agent {i}")
                .build()
            )
            return agent

        metric = self._measure_operation(
            "Quick Agent Creation Sample", 10, quick_agent_creation
        )
        performance_reporter.add_metric(metric)

        # Generate report
        report_path = Path("performance_report.md")
        performance_reporter.save_report(str(report_path))

        # Verify report was created
        assert report_path.exists()

        # Read and verify report content
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()

        assert "# 🚀 Engine CLI Performance Report" in report_content
        assert "Quick Agent Creation Sample" in report_content
        assert "10" in report_content  # Count
        assert "<100ms" in report_content or ">100ms" in report_content  # Status

        print(f"\n📊 Performance Report Generated: {report_path}")
        print("Sample Report Content:")
        print("=" * 50)
        print(
            report_content[:500] + "..."
            if len(report_content) > 500
            else report_content
        )
        print("=" * 50)
