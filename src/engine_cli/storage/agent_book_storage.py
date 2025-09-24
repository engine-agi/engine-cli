"""Agent storage using Book system for persistence."""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from engine_core import BookBuilder


class AgentBookStorage:
    """Agent storage using Book system for persistence."""

    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize agent book storage.

        Args:
            storage_dir: Directory to store agent books. Defaults to ./agents
        """
        self.storage_dir = storage_dir or os.path.join(os.getcwd(), "agents")
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_book_path(self, agent_id: str) -> str:
        """Get the file path for an agent book."""
        return os.path.join(self.storage_dir, f"{agent_id}.json")

    def _agent_to_book_data(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert agent data to book format."""
        return {
            "book_id": f"agent_{agent_data['id']}",
            "title": f"Agent: {agent_data.get('name', agent_data['id'])}",
            "description": f"Agent configuration for {agent_data.get('name', agent_data['id'])}",
            "author": "Engine CLI",
            "project_id": "engine_cli_agents",
            "content": {
                "agent_config": agent_data,
                "metadata": {
                    "created_at": agent_data.get("created_at", str(datetime.now())),
                    "version": "1.0",
                    "type": "agent_configuration",
                },
            },
            "tags": ["agent", "configuration", agent_data.get("model", "unknown")],
            "categories": ["agents"],
        }

    def _book_data_to_agent(self, book_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert book data back to agent format."""
        if "content" in book_data and "agent_config" in book_data["content"]:
            agent_data = book_data["content"]["agent_config"]
            # Ensure created_at is present
            if "created_at" not in agent_data:
                agent_data["created_at"] = book_data.get(
                    "created_at", str(datetime.now())
                )
            return agent_data
        return book_data  # Fallback for old format

    def save_agent(self, agent_data: Dict[str, Any]) -> bool:
        """Save agent using Book system.

        Args:
            agent_data: Agent configuration data

        Returns:
            bool: True if saved successfully
        """
        try:
            # Create book data from agent data
            book_data = self._agent_to_book_data(agent_data)

            # Create book using BookBuilder
            builder = BookBuilder()
            book = (
                builder.with_id(book_data["book_id"])
                .with_title(book_data["title"])
                .with_description(book_data["description"])
                .with_author(book_data["author"])
                .with_project(book_data["project_id"])
                .add_tags(book_data["tags"])
                .add_categories(book_data["categories"])
                .build()
            )

            # Save book as JSON
            book_path = self._get_book_path(agent_data["id"])
            with open(book_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        **book_data,
                        "created_at": str(datetime.now()),
                        "book_object": (
                            book.to_dict() if hasattr(book, "to_dict") else str(book)
                        ),
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            return True

        except Exception as e:
            print(f"Error saving agent: {e}")
            return False

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID.

        Args:
            agent_id: Agent ID

        Returns:
            Agent data or None if not found
        """
        try:
            book_path = self._get_book_path(agent_id)
            if not os.path.exists(book_path):
                return None

            with open(book_path, "r", encoding="utf-8") as f:
                book_data = json.load(f)

            return self._book_data_to_agent(book_data)

        except Exception as e:
            print(f"Error loading agent {agent_id}: {e}")
            return None

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all saved agents.

        Returns:
            List of agent data
        """
        agents = []
        try:
            if os.path.exists(self.storage_dir):
                for file in os.listdir(self.storage_dir):
                    if file.endswith(".json"):
                        try:
                            agent_id = file.replace(".json", "")
                            agent_data = self.get_agent(agent_id)
                            if agent_data:
                                agents.append(agent_data)
                        except Exception:
                            continue
        except Exception as e:
            print(f"Error listing agents: {e}")

        return agents

    def delete_agent(self, agent_id: str) -> bool:
        """Delete agent by ID.

        Args:
            agent_id: Agent ID to delete

        Returns:
            bool: True if deleted successfully
        """
        try:
            book_path = self._get_book_path(agent_id)
            if os.path.exists(book_path):
                os.remove(book_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting agent {agent_id}: {e}")
            return False

    def agent_exists(self, agent_id: str) -> bool:
        """Check if agent exists.

        Args:
            agent_id: Agent ID to check

        Returns:
            bool: True if agent exists
        """
        book_path = self._get_book_path(agent_id)
        return os.path.exists(book_path)
