"""Unit tests for interactive CLI module."""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completion

from engine_cli.interactive import (
    EngineCLICompleter,
    InteractiveCLI,
    start_interactive
)


class TestEngineCLICompleter:
    """Test cases for EngineCLICompleter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.completer = EngineCLICompleter()

    def test_init(self):
        """Test completer initialization."""
        assert self.completer.commands is not None
        assert 'agent' in self.completer.commands
        assert 'workflow' in self.completer.commands
        assert self.completer.agent_options == ['--model', '--speciality', '--stack']
        assert self.completer.workflow_options == ['--name', '--description', '--vertices', '--edges']

    def test_get_completions_empty_input(self):
        """Test completion with empty input."""
        document = Document(text='')
        complete_event = Mock()

        completions = list(self.completer.get_completions(document, complete_event))

        # Should complete all main commands
        command_names = [c.text for c in completions]
        assert 'agent' in command_names
        assert 'workflow' in command_names
        assert 'help' in command_names
        assert 'exit' in command_names

    def test_get_completions_partial_command(self):
        """Test completion with partial command input."""
        document = Document(text='ag')
        complete_event = Mock()

        completions = list(self.completer.get_completions(document, complete_event))

        # Should complete 'agent'
        assert len(completions) == 1
        assert completions[0].text == 'agent'
        assert completions[0].start_position == -2  # Replace 'ag'

    def test_get_completions_full_command_subcommands(self):
        """Test completion of subcommands for full command."""
        document = Document(text='agent ')
        complete_event = Mock()

        completions = list(self.completer.get_completions(document, complete_event))

        # Should complete agent subcommands
        subcommand_names = [c.text for c in completions]
        assert 'create' in subcommand_names
        assert 'delete' in subcommand_names
        assert 'list' in subcommand_names
        assert 'show' in subcommand_names

    def test_get_completions_agent_create_options(self):
        """Test completion of options for agent create."""
        document = Document(text='agent create ')
        complete_event = Mock()

        completions = list(self.completer.get_completions(document, complete_event))

        # Should complete agent options
        option_names = [c.text for c in completions]
        assert '--model' in option_names
        assert '--speciality' in option_names
        assert '--stack' in option_names

    def test_get_completions_workflow_create_options(self):
        """Test completion of options for workflow create."""
        document = Document(text='workflow create ')
        complete_event = Mock()

        completions = list(self.completer.get_completions(document, complete_event))

        # Should complete workflow options
        option_names = [c.text for c in completions]
        assert '--name' in option_names
        assert '--description' in option_names
        assert '--vertices' in option_names
        assert '--edges' in option_names

    def test_get_completions_option_already_used(self):
        """Test that options are not completed if already used."""
        document = Document(text='agent create --model gpt-4 ')
        complete_event = Mock()

        completions = list(self.completer.get_completions(document, complete_event))

        # Should not complete --model again
        option_names = [c.text for c in completions]
        assert '--model' not in option_names
        assert '--speciality' in option_names
        assert '--stack' in option_names

    def test_get_completions_unknown_command(self):
        """Test completion behavior with unknown command."""
        document = Document(text='unknown ')
        complete_event = Mock()

        completions = list(self.completer.get_completions(document, complete_event))

        # Should not complete anything for unknown command
        assert len(completions) == 0


class TestInteractiveCLI:
    """Test cases for InteractiveCLI class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.interactive = InteractiveCLI()

    @patch('pathlib.Path.home')
    def test_init(self, mock_home):
        """Test InteractiveCLI initialization."""
        mock_home.return_value = Path('/home/test')

        interactive = InteractiveCLI()

        assert interactive.history_file == Path('/home/test/.engine_cli_history')
        assert interactive.session is not None
        # Verify session has completer and history
        assert interactive.session.completer is not None
        assert interactive.session.history is not None

    def test_get_prompt(self):
        """Test prompt generation."""
        prompt = self.interactive.get_prompt()

        # Should return HTML formatted prompt
        assert 'engine' in str(prompt)
        assert '❯' in str(prompt)

    def test_execute_command_empty(self):
        """Test execution of empty command."""
        result = self.interactive.execute_command('')

        assert result is True  # Continue

    def test_execute_command_exit(self):
        """Test execution of exit commands."""
        with patch('engine_cli.interactive.success') as mock_success:
            result = self.interactive.execute_command('exit')
            assert result is False
            mock_success.assert_called_with("Goodbye! 👋")

        with patch('engine_cli.interactive.success') as mock_success:
            result = self.interactive.execute_command('quit')
            assert result is False
            mock_success.assert_called_with("Goodbye! 👋")

        with patch('engine_cli.interactive.success') as mock_success:
            result = self.interactive.execute_command('q')
            assert result is False
            mock_success.assert_called_with("Goodbye! 👋")

    @patch('os.system')
    def test_execute_command_clear(self, mock_system):
        """Test execution of clear command."""
        result = self.interactive.execute_command('clear')

        assert result is True  # Continue
        mock_system.assert_called_with('clear')

    @patch('os.system')
    def test_execute_command_clear_windows(self, mock_system):
        """Test execution of clear command on Windows."""
        with patch('os.name', 'nt'):
            result = self.interactive.execute_command('clear')

            assert result is True  # Continue
            mock_system.assert_called_with('cls')

    def test_execute_command_help(self):
        """Test execution of help commands."""
        with patch.object(self.interactive, 'show_help') as mock_show_help:
            result = self.interactive.execute_command('help')
            assert result is True
            mock_show_help.assert_called_once()

        with patch.object(self.interactive, 'show_help') as mock_show_help:
            result = self.interactive.execute_command('h')
            assert result is True
            mock_show_help.assert_called_once()

        with patch.object(self.interactive, 'show_help') as mock_show_help:
            result = self.interactive.execute_command('?')
            assert result is True
            mock_show_help.assert_called_once()

    @patch('engine_cli.main.cli')
    @patch('shlex.split')
    def test_execute_command_cli_success(self, mock_split, mock_cli):
        """Test successful execution of CLI command."""
        mock_split.return_value = ['agent', 'list']
        mock_cli.return_value = None

        result = self.interactive.execute_command('agent list')

        assert result is True
        mock_split.assert_called_with('agent list')
        mock_cli.assert_called_with(args=['agent', 'list'], standalone_mode=False)

    @patch('engine_cli.main.cli')
    @patch('shlex.split')
    def test_execute_command_cli_system_exit(self, mock_split, mock_cli):
        """Test CLI command that raises SystemExit."""
        mock_split.return_value = ['--help']
        mock_cli.side_effect = SystemExit(0)

        result = self.interactive.execute_command('--help')

        assert result is True  # Continue despite SystemExit
        mock_cli.assert_called_with(args=['--help'], standalone_mode=False)

    @patch('engine_cli.main.cli')
    @patch('shlex.split')
    @patch('engine_cli.interactive.error')
    def test_execute_command_cli_exception(self, mock_error, mock_split, mock_cli):
        """Test CLI command that raises exception."""
        mock_split.return_value = ['invalid', 'command']
        mock_cli.side_effect = Exception('Command failed')

        result = self.interactive.execute_command('invalid command')

        assert result is True  # Continue despite exception
        mock_error.assert_called_with('Command failed: Command failed')

    @patch('engine_cli.interactive.header')
    @patch('engine_cli.interactive.info')
    @patch('engine_cli.formatting.table')
    @patch('engine_cli.formatting.print_table')
    @patch('engine_cli.interactive.separator')
    def test_show_help(self, mock_separator, mock_print_table, mock_table, mock_info, mock_header):
        """Test help display functionality."""
        # Mock table creation
        mock_table_instance = Mock()
        mock_table.return_value = mock_table_instance

        self.interactive.show_help()

        # Verify header was called
        mock_header.assert_called_with("Engine CLI Interactive Mode", "Type commands or use Tab for auto-complete")

        # Verify info calls
        mock_info.assert_any_call("Available commands:")

        # Verify table creation and population
        mock_table.assert_called_with("Commands", ["Command", "Description"])
        assert mock_table_instance.add_row.call_count > 10  # Multiple commands added

        # Verify table printing
        mock_print_table.assert_called_with(mock_table_instance)

        # Verify tips
        mock_info.assert_any_call("Tips:")
        mock_info.assert_any_call("• Use Tab for auto-completion")
        mock_info.assert_any_call("• Use ↑/↓ for command history")
        mock_info.assert_any_call("• Use Ctrl+C to cancel current command")
        mock_info.assert_any_call("• Use Ctrl+D to exit")

    @patch('engine_cli.interactive.header')
    @patch('engine_cli.interactive.info')
    @patch('engine_cli.interactive.separator')
    @patch('engine_cli.interactive.success')
    def test_run_welcome_and_exit(self, mock_success, mock_separator, mock_info, mock_header):
        """Test run method with immediate exit."""
        with patch.object(self.interactive.session, 'prompt', side_effect=EOFError()):
            result = self.interactive.run()

            assert result == 0
            mock_header.assert_called_with("Welcome to Engine CLI Interactive Mode")
            mock_info.assert_called_with("Type 'help' for available commands or 'exit' to quit")
            mock_separator.assert_called_once()
            mock_success.assert_called_with("Goodbye! 👋")

    @patch('engine_cli.interactive.header')
    @patch('engine_cli.interactive.info')
    @patch('engine_cli.interactive.separator')
    @patch('engine_cli.interactive.success')
    def test_run_keyboard_interrupt(self, mock_success, mock_separator, mock_info, mock_header):
        """Test run method with keyboard interrupt."""
        call_count = 0
        def prompt_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise KeyboardInterrupt()
            else:
                raise EOFError()

        with patch.object(self.interactive.session, 'prompt', side_effect=prompt_side_effect):
            result = self.interactive.run()

            assert result == 0
            # Should continue after KeyboardInterrupt and exit on EOFError

    @patch('engine_cli.interactive.header')
    @patch('engine_cli.interactive.info')
    @patch('engine_cli.interactive.separator')
    @patch('engine_cli.interactive.error')
    def test_run_exception(self, mock_error, mock_separator, mock_info, mock_header):
        """Test run method with general exception."""
        with patch.object(self.interactive.session, 'prompt', side_effect=Exception('Test error')):
            result = self.interactive.run()

            assert result == 1
            mock_error.assert_called_with("Interactive mode error: Test error")


class TestStartInteractive:
    """Test cases for start_interactive function."""

    @patch('engine_cli.interactive.InteractiveCLI')
    def test_start_interactive_success(self, mock_interactive_class):
        """Test successful start_interactive execution."""
        mock_interactive_instance = Mock()
        mock_interactive_instance.run.return_value = 0
        mock_interactive_class.return_value = mock_interactive_instance

        result = start_interactive()

        assert result == 0
        mock_interactive_class.assert_called_once()
        mock_interactive_instance.run.assert_called_once()

    @patch('engine_cli.interactive.InteractiveCLI')
    @patch('engine_cli.interactive.success')
    def test_start_interactive_keyboard_interrupt(self, mock_success, mock_interactive_class):
        """Test start_interactive with keyboard interrupt."""
        mock_interactive_class.side_effect = KeyboardInterrupt()

        result = start_interactive()

        assert result == 0
        mock_success.assert_called_with("Goodbye! 👋")

    @patch('engine_cli.interactive.InteractiveCLI')
    @patch('engine_cli.interactive.error')
    def test_start_interactive_exception(self, mock_error, mock_interactive_class):
        """Test start_interactive with general exception."""
        mock_interactive_class.side_effect = Exception('Init failed')

        result = start_interactive()

        assert result == 1
        mock_error.assert_called_with("Failed to start interactive mode: Init failed")


if __name__ == "__main__":
    pytest.main([__file__])