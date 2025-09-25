"""Tests for AgentBookStorage integration with Book system."""

import json
import os
import tempfile
from unittest.mock import patch

from engine_cli.storage.agent_book_storage import AgentBookStorage


class TestAgentBookStorage:
    """Test AgentBookStorage functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = AgentBookStorage(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_get_agent(self):
        """Test saving and retrieving an agent."""
        agent_data = {
            "id": "test_agent",
            "name": "Test Agent",
            "model": "claude-3.5-sonnet",
            "speciality": "Testing",
            "persona": "Methodical tester",
            "stack": ["python", "pytest"],
            "tools": ["git", "docker"],
            "protocol": "test_protocol",
            "workflow": "test_workflow",
            "book": "test_book",
            "created_at": "2025-01-01T00:00:00",
        }

        # Save agent
        result = self.storage.save_agent(agent_data)
        assert result is True

        # Retrieve agent
        retrieved = self.storage.get_agent("test_agent")
        assert retrieved is not None
        assert retrieved["id"] == "test_agent"
        assert retrieved["name"] == "Test Agent"
        assert retrieved["model"] == "claude-3.5-sonnet"
        assert retrieved["stack"] == ["python", "pytest"]

    def test_get_nonexistent_agent(self):
        """Test retrieving a non-existent agent."""
        result = self.storage.get_agent("nonexistent")
        assert result is None

    def test_list_agents_empty(self):
        """Test listing agents when none exist."""
        agents = self.storage.list_agents()
        assert agents == []

    def test_list_agents(self):
        """Test listing multiple agents."""
        # Save multiple agents
        agent1 = {
            "id": "agent1",
            "name": "Agent One",
            "model": "claude-3.5-sonnet",
            "created_at": "2025-01-01T00:00:00",
        }
        agent2 = {
            "id": "agent2",
            "name": "Agent Two",
            "model": "gpt-4",
            "created_at": "2025-01-01T00:00:00",
        }

        self.storage.save_agent(agent1)
        self.storage.save_agent(agent2)

        # List agents
        agents = self.storage.list_agents()
        assert len(agents) == 2

        agent_ids = [a["id"] for a in agents]
        assert "agent1" in agent_ids
        assert "agent2" in agent_ids

    def test_delete_agent(self):
        """Test deleting an agent."""
        agent_data = {
            "id": "test_agent",
            "name": "Test Agent",
            "model": "claude-3.5-sonnet",
            "created_at": "2025-01-01T00:00:00",
        }

        # Save agent
        self.storage.save_agent(agent_data)

        # Verify it exists
        assert self.storage.get_agent("test_agent") is not None

        # Delete agent
        result = self.storage.delete_agent("test_agent")
        assert result is True

        # Verify it's gone
        assert self.storage.get_agent("test_agent") is None

    def test_delete_nonexistent_agent(self):
        """Test deleting a non-existent agent."""
        result = self.storage.delete_agent("nonexistent")
        assert result is False

    def test_agent_exists(self):
        """Test checking if agent exists."""
        agent_data = {
            "id": "test_agent",
            "name": "Test Agent",
            "model": "claude-3.5-sonnet",
            "created_at": "2025-01-01T00:00:00",
        }

        # Agent doesn't exist initially
        assert self.storage.agent_exists("test_agent") is False

        # Save agent
        self.storage.save_agent(agent_data)

        # Now it exists
        assert self.storage.agent_exists("test_agent") is True

    @patch("engine_cli.storage.agent_book_storage.BookBuilder")
    def test_book_builder_integration(self, mock_builder):
        """Test that BookBuilder is properly used."""
        # Mock the BookBuilder
        mock_book = mock_builder.return_value
        mock_book.with_id.return_value = mock_book
        mock_book.with_title.return_value = mock_book
        mock_book.with_description.return_value = mock_book
        mock_book.with_author.return_value = mock_book
        mock_book.with_project.return_value = mock_book
        mock_book.add_tags.return_value = mock_book
        mock_book.add_categories.return_value = mock_book
        mock_book.build.return_value = "mock_book"

        agent_data = {
            "id": "test_agent",
            "name": "Test Agent",
            "model": "claude-3.5-sonnet",
            "created_at": "2025-01-01T00:00:00",
        }

        # Save agent
        result = self.storage.save_agent(agent_data)
        assert result is True

        # Verify BookBuilder was called correctly
        mock_builder.assert_called_once()
        mock_book.with_id.assert_called_with("agent_test_agent")
        mock_book.with_title.assert_called_with("Agent: Test Agent")
        mock_book.build.assert_called_once()

    def test_backward_compatibility(self):
        """Test loading agents saved in old format."""
        # Create a file in old format (direct JSON)
        old_agent_data = {
            "id": "old_agent",
            "name": "Old Agent",
            "model": "claude-3.5-sonnet",
            "created_at": "2025-01-01T00:00:00",
        }

        old_file_path = os.path.join(self.temp_dir, "old_agent.json")
        with open(old_file_path, "w") as f:
            json.dump(old_agent_data, f)

        # Should be able to load it
        retrieved = self.storage.get_agent("old_agent")
        assert retrieved is not None
        assert retrieved["id"] == "old_agent"
        assert retrieved["name"] == "Old Agent"
