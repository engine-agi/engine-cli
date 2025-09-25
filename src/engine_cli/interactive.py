"""Interactive CLI mode with REPL, auto-complete, and command history."""

import os
import sys
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from engine_cli.formatting import error, header, info, separator, success


class EngineCLICompleter(Completer):
    """Auto-completer for Engine CLI commands."""

    def __init__(self):
        self.commands = {
            "version": [],
            "status": [],
            "agent": ["create", "delete", "list", "show"],
            "team": [
                "create",
                "delete",
                "list",
                "show",
                "add-agent",
                "remove-agent",
            ],
            "workflow": ["create", "delete", "list", "show", "run", "status"],
            "tool": ["create", "delete", "list", "show", "execute"],
            "protocol": ["create", "delete", "list", "show"],
            "book": ["create", "delete", "list", "show", "search", "add-page"],
            "project": ["create", "delete", "list", "show", "init"],
            "examples": ["list", "run", "create"],
            "monitoring": ["status", "logs", "metrics"],
            "help": [],
            "exit": [],
            "quit": [],
            "clear": [],
        }

        self.agent_options = ["--model", "--speciality", "--stack"]
        self.team_options = ["--name", "--description", "--agents"]
        self.workflow_options = [
            "--name",
            "--description",
            "--vertices",
            "--edges",
        ]
        self.tool_options = ["--name", "--type", "--config"]
        self.protocol_options = ["--name", "--commands"]
        self.book_options = ["--name", "--description", "--chapters"]

    def get_completions(self, document, complete_event):
        """Get completions for the current input."""
        text = document.text_before_cursor
        words = text.strip().split()

        if not words:
            # Complete main commands
            for cmd in self.commands.keys():
                yield Completion(cmd, start_position=0)
            return

        # Complete subcommands and options
        if len(words) == 1:
            cmd = words[0]
            if cmd in self.commands:
                for subcmd in self.commands[cmd]:
                    yield Completion(subcmd, start_position=-len(cmd))
            else:
                # Complete partial command names
                for full_cmd in self.commands.keys():
                    if full_cmd.startswith(cmd):
                        yield Completion(full_cmd, start_position=-len(cmd))
        elif len(words) >= 2:
            cmd = words[0]
            subcmd = words[1]

            # Complete options based on command
            if cmd == "agent" and subcmd == "create":
                for option in self.agent_options:
                    if not any(option in word for word in words):
                        yield Completion(option, start_position=0)
            elif cmd == "team" and subcmd == "create":
                for option in self.team_options:
                    if not any(option in word for word in words):
                        yield Completion(option, start_position=0)
            elif cmd == "workflow" and subcmd == "create":
                for option in self.workflow_options:
                    if not any(option in word for word in words):
                        yield Completion(option, start_position=0)
            elif cmd == "tool" and subcmd == "create":
                for option in self.tool_options:
                    if not any(option in word for word in words):
                        yield Completion(option, start_position=0)
            elif cmd == "protocol" and subcmd == "create":
                for option in self.protocol_options:
                    if not any(option in word for word in words):
                        yield Completion(option, start_position=0)
            elif cmd == "book" and subcmd == "create":
                for option in self.book_options:
                    if not any(option in word for word in words):
                        yield Completion(option, start_position=0)


class InteractiveCLI:
    """Interactive CLI REPL mode."""

    def __init__(self):
        self.history_file = Path.home() / ".engine_cli_history"
        self.session = PromptSession(
            history=FileHistory(str(self.history_file)),
            completer=EngineCLICompleter(),
            style=Style.from_dict(
                {
                    "prompt": "ansicyan bold",
                    "": "ansiwhite",
                }
            ),
        )

    def get_prompt(self) -> HTML:
        """Get the interactive prompt."""
        return HTML("<prompt>engine</prompt> <white>❯ </white>")

    def execute_command(self, command_line: str) -> bool:
        """Execute a command line. Returns False if should exit."""
        command_line = command_line.strip()

        if not command_line:
            return True

        # Handle special commands
        if command_line.lower() in ["exit", "quit", "q"]:
            success("Goodbye! 👋")
            return False

        if command_line.lower() == "clear":
            os.system("clear" if os.name == "posix" else "cls")
            return True

        if command_line.lower() in ["help", "h", "?"]:
            self.show_help()
            return True

        # Execute CLI command
        try:
            # Split command line into arguments
            import shlex

            args = shlex.split(command_line)

            # Execute using Click CLI
            from engine_cli.main import cli

            cli(args=args, standalone_mode=False)

        except SystemExit:
            # Click uses SystemExit for --help etc., ignore it
            pass
        except Exception as e:
            error(f"Command failed: {e}")

        return True

    def show_help(self):
        """Show interactive help."""
        header(
            "Engine CLI Interactive Mode",
            "Type commands or use Tab for auto-complete",
        )

        info("Available commands:")
        commands = [
            ("version", "Show version information"),
            ("status", "Show system status"),
            ("agent", "Manage AI agents"),
            ("team", "Manage agent teams"),
            ("workflow", "Manage workflows"),
            ("tool", "Manage tools"),
            ("protocol", "Manage protocols"),
            ("book", "Manage memory books"),
            ("project", "Manage projects"),
            ("examples", "Browse examples"),
            ("monitoring", "System monitoring"),
            ("help/h/?", "Show this help"),
            ("clear", "Clear screen"),
            ("exit/quit/q", "Exit interactive mode"),
        ]

        from engine_cli.formatting import print_table, table

        help_table = table("Commands", ["Command", "Description"])
        for cmd, desc in commands:
            help_table.add_row(cmd, desc)
        print_table(help_table)

        info("Tips:")
        info("• Use Tab for auto-completion")
        info("• Use ↑/↓ for command history")
        info("• Use Ctrl+C to cancel current command")
        info("• Use Ctrl+D to exit")

    def run(self):
        """Run the interactive CLI loop."""
        # Welcome message
        header("Welcome to Engine CLI Interactive Mode")
        info("Type 'help' for available commands or 'exit' to quit")
        separator()

        try:
            while True:
                try:
                    # Get user input
                    command_line = self.session.prompt(self.get_prompt())

                    # Execute command
                    if not self.execute_command(command_line):
                        break

                except KeyboardInterrupt:
                    # Ctrl+C - new line
                    print()
                    continue
                except EOFError:
                    # Ctrl+D - exit
                    print()
                    success("Goodbye! 👋")
                    break

        except Exception as e:
            error(f"Interactive mode error: {e}")
            return 1

        return 0


def start_interactive():
    """Start the interactive CLI mode."""
    try:
        interactive = InteractiveCLI()
        return interactive.run()
    except KeyboardInterrupt:
        print()
        success("Goodbye! 👋")
        return 0
    except Exception as e:
        error(f"Failed to start interactive mode: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(start_interactive())
