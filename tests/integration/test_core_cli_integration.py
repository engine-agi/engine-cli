"""
Core-CLI Integration Tests
End-to-end tests simulating complete usage flows between CLI and Engine Core.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest
import yaml

# Import core components for validation
from engine_core.core.agents.agent_builder import AgentBuilder
from engine_core.core.teams.team_builder import TeamBuilder, TeamMemberRole
from engine_core.core.workflows.workflow_builder import WorkflowBuilder


class TestCoreCLIIntegration:
    """Integration tests for complete CLI-Core workflows."""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            # Create necessary directories
            os.makedirs("agents", exist_ok=True)
            os.makedirs("teams", exist_ok=True)
            os.makedirs("workflows", exist_ok=True)
            os.makedirs("books", exist_ok=True)

            yield temp_dir

            # Restore original directory
            os.chdir(original_cwd)


import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Import core components for validation
from engine_core.core.agents.agent_builder import AgentBuilder
from engine_core.core.teams.team_builder import TeamBuilder, TeamMemberRole
from engine_core.core.workflows.workflow_builder import WorkflowBuilder


class TestCoreCLIIntegration:
    """Integration tests for complete CLI-Core workflows."""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            # Create necessary directories
            os.makedirs("agents", exist_ok=True)
            os.makedirs("teams", exist_ok=True)
            os.makedirs("workflows", exist_ok=True)
            os.makedirs("books", exist_ok=True)

            yield temp_dir

            # Restore original directory
            os.chdir(original_cwd)

    @pytest.mark.integration
    def test_agent_builder_to_storage_integration(self, temp_workspace):
        """Test integration between AgentBuilder and storage persistence."""
        # Create agent using core builder
        agent = (
            AgentBuilder()
            .with_id("integration-agent")
            .with_model("claude-3.5-sonnet")
            .with_name("Integration Test Agent")
            .with_speciality("Integration Testing")
            .with_stack(["python", "pytest"])
            .build()
        )

        assert agent is not None

        # Simulate CLI storage format (YAML)
        agent_data = {
            "id": "integration-agent",
            "model": "claude-3.5-sonnet",
            "name": "Integration Test Agent",
            "speciality": "Integration Testing",
            "stack": ["python", "pytest"],
            "created_at": "2025-09-23T10:00:00.000000",
        }

        # Save to file (simulating CLI storage)
        agent_file = Path("agents/integration-agent.yaml")
        with open(agent_file, "w") as f:
            yaml.dump(agent_data, f)

        # Verify file was created
        assert agent_file.exists()

        # Load and verify data integrity
        with open(agent_file, "r") as f:
            loaded_data = yaml.safe_load(f)

        assert loaded_data["id"] == "integration-agent"
        assert loaded_data["model"] == "claude-3.5-sonnet"
        assert loaded_data["name"] == "Integration Test Agent"
        assert "python" in loaded_data["stack"]
        assert "pytest" in loaded_data["stack"]

        # Test that core can recreate agent from stored data
        recreated_agent = (
            AgentBuilder()
            .with_id(loaded_data["id"])
            .with_model(loaded_data["model"])
            .with_name(loaded_data["name"])
            .with_speciality(loaded_data.get("speciality", ""))
            .with_stack(loaded_data.get("stack", []))
            .build()
        )

        assert recreated_agent is not None

    @pytest.mark.integration
    def test_team_builder_with_agents_integration(self, temp_workspace):
        """Test team builder integration with multiple agents."""
        # Create agents first
        agent1 = (
            AgentBuilder()
            .with_id("team-agent-1")
            .with_model("claude-3.5-sonnet")
            .with_name("Team Agent 1")
            .build()
        )

        agent2 = (
            AgentBuilder()
            .with_id("team-agent-2")
            .with_model("claude-3-haiku")
            .with_name("Team Agent 2")
            .build()
        )

        assert agent1 is not None
        assert agent2 is not None

        # Create team using core builder
        team = (
            TeamBuilder()
            .with_id("integration-team")
            .with_name("Integration Test Team")
            .add_member("team-agent-1", TeamMemberRole.LEADER)
            .add_member("team-agent-2", TeamMemberRole.MEMBER)
            .build()
        )

        assert team is not None

        # Simulate CLI storage format
        team_data = {
            "id": "integration-team",
            "name": "Integration Test Team",
            "description": "Team for integration testing",
            "members": [
                {
                    "id": "team-agent-1",
                    "role": "leader",
                    "name": "Team Agent 1",
                },
                {
                    "id": "team-agent-2",
                    "role": "member",
                    "name": "Team Agent 2",
                },
            ],
            "created_at": "2025-09-23T10:00:00.000000",
        }

        # Save team data
        team_file = Path("teams/integration-team.yaml")
        with open(team_file, "w") as f:
            yaml.dump(team_data, f)

        # Save agent data
        for agent_data in [
            {
                "id": "team-agent-1",
                "model": "claude-3.5-sonnet",
                "name": "Team Agent 1",
            },
            {
                "id": "team-agent-2",
                "model": "claude-3-haiku",
                "name": "Team Agent 2",
            },
        ]:
            agent_file = Path(f"agents/{agent_data['id']}.yaml")
            with open(agent_file, "w") as f:
                yaml.dump(agent_data, f)

        # Verify all files exist
        assert team_file.exists()
        assert Path("agents/team-agent-1.yaml").exists()
        assert Path("agents/team-agent-2.yaml").exists()

        # Load and verify team-agent relationship
        with open(team_file, "r") as f:
            loaded_team = yaml.safe_load(f)

        assert len(loaded_team["members"]) == 2
        member_ids = [m["id"] for m in loaded_team["members"]]
        assert "team-agent-1" in member_ids
        assert "team-agent-2" in member_ids

        # Verify leader role
        leader_member = next(m for m in loaded_team["members"] if m["role"] == "leader")
        assert leader_member["id"] == "team-agent-1"

    @pytest.mark.integration
    def test_workflow_with_agents_integration(self, temp_workspace):
        """Test workflow integration with agent execution."""
        # Create agent for workflow
        workflow_agent = (
            AgentBuilder()
            .with_id("workflow-executor")
            .with_model("claude-3.5-sonnet")
            .with_name("Workflow Executor Agent")
            .build()
        )

        assert workflow_agent is not None

        # Create workflow using core builder
        workflow = (
            WorkflowBuilder()
            .with_id("integration-workflow")
            .with_name("Integration Test Workflow")
            .add_agent_vertex("analyze", workflow_agent, "Analyze requirements")
            .add_agent_vertex("implement", workflow_agent, "Implement solution")
            .add_edge("analyze", "implement")
            .build()
        )

        assert workflow is not None

        # Simulate CLI storage format
        workflow_data = {
            "id": "integration-workflow",
            "name": "Integration Test Workflow",
            "description": "Workflow for integration testing",
            "vertices": [
                {
                    "id": "analyze",
                    "agent_id": "workflow-executor",
                    "task": "Analyze requirements",
                },
                {
                    "id": "implement",
                    "agent_id": "workflow-executor",
                    "task": "Implement solution",
                },
            ],
            "edges": [{"from": "analyze", "to": "implement"}],
            "created_at": "2025-09-23T10:00:00.000000",
        }

        # Save workflow data
        workflow_file = Path("workflows/integration-workflow.yaml")
        with open(workflow_file, "w") as f:
            yaml.dump(workflow_data, f)

        # Save agent data
        agent_data = {
            "id": "workflow-executor",
            "model": "claude-3.5-sonnet",
            "name": "Workflow Executor Agent",
        }
        agent_file = Path("agents/workflow-executor.yaml")
        with open(agent_file, "w") as f:
            yaml.dump(agent_data, f)

        # Verify files exist
        assert workflow_file.exists()
        assert agent_file.exists()

        # Load and verify workflow structure
        with open(workflow_file, "r") as f:
            loaded_workflow = yaml.safe_load(f)

        assert len(loaded_workflow["vertices"]) == 2
        assert len(loaded_workflow["edges"]) == 1

        # Verify vertex-agent relationships
        vertex_agent_ids = [v["agent_id"] for v in loaded_workflow["vertices"]]
        assert all(agent_id == "workflow-executor" for agent_id in vertex_agent_ids)

        # Verify edge connectivity
        edge = loaded_workflow["edges"][0]
        assert edge["from"] == "analyze"
        assert edge["to"] == "implement"

    @pytest.mark.integration
    def test_end_to_end_project_simulation(self, temp_workspace):
        """Simulate complete end-to-end project workflow."""
        # Phase 1: Project Setup - Create all components

        # Create agents
        senior_dev = (
            AgentBuilder()
            .with_id("senior-dev")
            .with_model("claude-3.5-sonnet")
            .with_name("Senior Developer")
            .with_speciality("Full-Stack Development")
            .with_stack(["python", "react", "postgresql"])
            .build()
        )

        qa_engineer = (
            AgentBuilder()
            .with_id("qa-engineer")
            .with_model("claude-3-haiku")
            .with_name("QA Engineer")
            .with_speciality("Quality Assurance")
            .with_stack(["selenium", "pytest"])
            .build()
        )

        # Create team
        dev_team = (
            TeamBuilder()
            .with_id("dev-team")
            .with_name("Development Team")
            .add_member("senior-dev", TeamMemberRole.LEADER)
            .add_member("qa-engineer", TeamMemberRole.MEMBER)
            .build()
        )

        # Create workflow
        dev_workflow = (
            WorkflowBuilder()
            .with_id("dev-workflow")
            .with_name("Development Workflow")
            .add_agent_vertex(
                "analysis",
                senior_dev,
                "Analyze requirements and design solution",
            )
            .add_agent_vertex("implementation", senior_dev, "Implement the solution")
            .add_agent_vertex("testing", qa_engineer, "Test the implementation")
            .add_agent_vertex("review", senior_dev, "Review and approve changes")
            .add_edge("analysis", "implementation")
            .add_edge("implementation", "testing")
            .add_edge("testing", "review")
            .build()
        )

        # Verify all core objects created successfully
        assert senior_dev is not None
        assert qa_engineer is not None
        assert dev_team is not None
        assert dev_workflow is not None

        # Phase 2: Persistence Simulation - Save all data

        # Save agents
        agents_data = [
            {
                "id": "senior-dev",
                "model": "claude-3.5-sonnet",
                "name": "Senior Developer",
                "speciality": "Full-Stack Development",
                "stack": ["python", "react", "postgresql"],
            },
            {
                "id": "qa-engineer",
                "model": "claude-3-haiku",
                "name": "QA Engineer",
                "speciality": "Quality Assurance",
                "stack": ["selenium", "pytest"],
            },
        ]

        for agent_data in agents_data:
            agent_file = Path(f"agents/{agent_data['id']}.yaml")
            with open(agent_file, "w") as f:
                yaml.dump(agent_data, f)

        # Save team
        team_data = {
            "id": "dev-team",
            "name": "Development Team",
            "members": [
                {
                    "id": "senior-dev",
                    "role": "leader",
                    "name": "Senior Developer",
                },
                {"id": "qa-engineer", "role": "member", "name": "QA Engineer"},
            ],
        }
        team_file = Path("teams/dev-team.yaml")
        with open(team_file, "w") as f:
            yaml.dump(team_data, f)

        # Save workflow
        workflow_data = {
            "id": "dev-workflow",
            "name": "Development Workflow",
            "vertices": [
                {
                    "id": "analysis",
                    "agent_id": "senior-dev",
                    "task": "Analyze requirements and design solution",
                },
                {
                    "id": "implementation",
                    "agent_id": "senior-dev",
                    "task": "Implement the solution",
                },
                {
                    "id": "testing",
                    "agent_id": "qa-engineer",
                    "task": "Test the implementation",
                },
                {
                    "id": "review",
                    "agent_id": "senior-dev",
                    "task": "Review and approve changes",
                },
            ],
            "edges": [
                {"from": "analysis", "to": "implementation"},
                {"from": "implementation", "to": "testing"},
                {"from": "testing", "to": "review"},
            ],
        }
        workflow_file = Path("workflows/dev-workflow.yaml")
        with open(workflow_file, "w") as f:
            yaml.dump(workflow_data, f)

        # Phase 3: Verification - Load and validate all data

        # Verify all files exist
        assert Path("agents/senior-dev.yaml").exists()
        assert Path("agents/qa-engineer.yaml").exists()
        assert Path("teams/dev-team.yaml").exists()
        assert Path("workflows/dev-workflow.yaml").exists()

        # Load and validate agents
        with open("agents/senior-dev.yaml", "r") as f:
            senior_data = yaml.safe_load(f)
        assert senior_data["speciality"] == "Full-Stack Development"
        assert "python" in senior_data["stack"]

        # Load and validate team
        with open("teams/dev-team.yaml", "r") as f:
            team_loaded = yaml.safe_load(f)
        assert len(team_loaded["members"]) == 2
        assert any(m["role"] == "leader" for m in team_loaded["members"])

        # Load and validate workflow
        with open("workflows/dev-workflow.yaml", "r") as f:
            workflow_loaded = yaml.safe_load(f)
        assert len(workflow_loaded["vertices"]) == 4
        assert len(workflow_loaded["edges"]) == 3

        # Verify workflow topology
        vertex_ids = [v["id"] for v in workflow_loaded["vertices"]]
        assert "analysis" in vertex_ids
        assert "implementation" in vertex_ids
        assert "testing" in vertex_ids
        assert "review" in vertex_ids

        # Phase 4: Cross-reference validation
        # Ensure all agent references in team and workflow are valid
        team_agent_ids = [m["id"] for m in team_loaded["members"]]
        workflow_agent_ids = list(
            set(v["agent_id"] for v in workflow_loaded["vertices"])
        )

        # All agents referenced in team should exist
        for agent_id in team_agent_ids:
            assert Path(f"agents/{agent_id}.yaml").exists()

        # All agents referenced in workflow should exist
        for agent_id in workflow_agent_ids:
            assert Path(f"agents/{agent_id}.yaml").exists()

    @pytest.mark.integration
    def test_data_consistency_across_formats(self, temp_workspace):
        """Test data consistency when converting between formats."""
        # Create original agent data
        original_data = {
            "id": "consistency-agent",
            "model": "claude-3.5-sonnet",
            "name": "Consistency Test Agent",
            "speciality": "Data Consistency Testing",
            "stack": ["python", "testing"],
            "metadata": {"version": "1.0", "created_by": "test"},
        }

        # Save as YAML
        yaml_file = Path("agents/consistency-agent.yaml")
        with open(yaml_file, "w") as f:
            yaml.dump(original_data, f)

        # Load YAML and convert to JSON
        with open(yaml_file, "r") as f:
            yaml_data = yaml.safe_load(f)

        json_str = json.dumps(yaml_data, indent=2, sort_keys=True)
        json_data = json.loads(json_str)

        # Convert back to YAML
        yaml_from_json = yaml.dump(json_data, sort_keys=True)
        yaml_from_json_data = yaml.safe_load(yaml_from_json)

        # Verify data consistency through conversions
        assert yaml_data == json_data == yaml_from_json_data

        # Verify specific fields maintain integrity
        assert json_data["id"] == "consistency-agent"
        assert json_data["model"] == "claude-3.5-sonnet"
        assert json_data["stack"] == ["python", "testing"]
        assert json_data["metadata"]["version"] == "1.0"

        # Test that core builder can handle the converted data
        core_agent = (
            AgentBuilder()
            .with_id(json_data["id"])
            .with_model(json_data["model"])
            .with_name(json_data["name"])
            .with_speciality(json_data.get("speciality", ""))
            .with_stack(json_data.get("stack", []))
            .build()
        )

        assert core_agent is not None

    @pytest.mark.integration
    def test_bulk_operations_data_integrity(self, temp_workspace):
        """Test bulk operations maintain data integrity."""
        # Create multiple agents in bulk
        agents_data = []
        for i in range(5):
            agent_data = {
                "id": f"bulk-agent-{i}",
                "model": ("claude-3.5-sonnet" if i % 2 == 0 else "claude-3-haiku"),
                "name": f"Bulk Agent {i}",
                "speciality": f"Speciality {i}",
                "stack": ["python", f"skill-{i}"],
            }
            agents_data.append(agent_data)

            # Save each agent
            agent_file = Path(f"agents/bulk-agent-{i}.yaml")
            with open(agent_file, "w") as f:
                yaml.dump(agent_data, f)

        # Create team with all agents
        team_members = []
        for i, agent_data in enumerate(agents_data):
            role = TeamMemberRole.LEADER if i == 0 else TeamMemberRole.MEMBER
            team_members.append((agent_data["id"], role))

        # Build team using core
        bulk_team = TeamBuilder().with_id("bulk-team").with_name("Bulk Operations Team")

        for agent_id, role in team_members:
            bulk_team = bulk_team.add_member(agent_id, role)

        bulk_team = bulk_team.build()
        assert bulk_team is not None

        # Save team data
        team_data = {
            "id": "bulk-team",
            "name": "Bulk Operations Team",
            "members": [
                {"id": agent_id, "role": role.value, "name": f"Bulk Agent {i}"}
                for i, (agent_id, role) in enumerate(team_members)
            ],
        }

        team_file = Path("teams/bulk-team.yaml")
        with open(team_file, "w") as f:
            yaml.dump(team_data, f)

        # Verify bulk integrity
        # All agent files exist
        for i in range(5):
            assert Path(f"agents/bulk-agent-{i}.yaml").exists()

        # Team file exists
        assert team_file.exists()

        # Load team and verify all members
        with open(team_file, "r") as f:
            loaded_team = yaml.safe_load(f)

        assert len(loaded_team["members"]) == 5

        # Verify member data integrity
        for member in loaded_team["members"]:
            agent_file = Path(f"agents/{member['id']}.yaml")
            assert agent_file.exists()

            with open(agent_file, "r") as f:
                agent_data = yaml.safe_load(f)

            assert agent_data["name"] == member["name"]

    @pytest.mark.integration
    def test_error_recovery_and_data_integrity(self, temp_workspace):
        """Test error recovery maintains data integrity."""
        # Create valid agent
        valid_agent_data = {
            "id": "valid-agent",
            "model": "claude-3.5-sonnet",
            "name": "Valid Agent",
        }

        # Save valid agent
        valid_file = Path("agents/valid-agent.yaml")
        with open(valid_file, "w") as f:
            yaml.dump(valid_agent_data, f)

        # Attempt to create invalid agent data (simulate error)
        invalid_agent_data = {
            "id": "",  # Invalid: empty ID
            "model": "invalid-model",
            "name": "Invalid Agent",
        }

        # This would normally fail, but we'll save it to test recovery
        invalid_file = Path("agents/invalid-agent.yaml")
        with open(invalid_file, "w") as f:
            yaml.dump(invalid_agent_data, f)

        # Verify valid agent still exists and is intact
        assert valid_file.exists()
        with open(valid_file, "r") as f:
            loaded_valid = yaml.safe_load(f)
        assert loaded_valid["id"] == "valid-agent"
        assert loaded_valid["model"] == "claude-3.5-sonnet"

        # Invalid file exists but would be rejected by core validation
        assert invalid_file.exists()

        # Test that core validation catches the invalid data
        with pytest.raises(ValueError):
            # This should fail due to empty ID
            (
                AgentBuilder()
                .with_id(invalid_agent_data["id"])
                .with_model(invalid_agent_data["model"])
                .with_name(invalid_agent_data["name"])
                .build()
            )

        # Verify valid agent can still be recreated
        valid_core_agent = (
            AgentBuilder()
            .with_id(valid_agent_data["id"])
            .with_model(valid_agent_data["model"])
            .with_name(valid_agent_data["name"])
            .build()
        )

        assert valid_core_agent is not None
