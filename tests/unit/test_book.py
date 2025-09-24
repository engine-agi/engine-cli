import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner


# Mock classes for engine-core dependencies
class MockBookMetadata:
    def __init__(self):
        self.status = MagicMock(value="active")
        self.created_at = datetime.now()
        self.version = "1.0.0"


class MockBookStatistics:
    def __init__(self):
        self.chapter_count = 2
        self.page_count = 5
        self.section_count = 10
        self.word_count = 1500


class MockBook:
    def __init__(self, book_id="test_book", title="Test Book"):
        self.book_id = book_id
        self.title = title
        self.description = "A test book"
        self.author = "Test Author"
        self.metadata = MockBookMetadata()
        self.chapters = []

    def get_statistics(self):
        return {
            "chapter_count": 2,
            "page_count": 5,
            "section_count": 10,
            "word_count": 1500,
        }


class MockChapter:
    def __init__(self, chapter_id="test_chapter", title="Test Chapter"):
        self.chapter_id = chapter_id
        self.title = title

    def to_dict(self):
        return {"statistics": {"page_count": 3, "section_count": 5, "word_count": 750}}


class MockSearchResult:
    def __init__(self):
        self.content_type = "page"
        self.title = "Test Page"
        self.content_id = "test_page_1"
        self.relevance_score = 0.85
        self.content_snippet = "This is a test content snippet for search results"
        self.highlights = ["test", "content", "search"]


class MockBookService:
    def __init__(self):
        self.books = {}

    async def create_book(self, book_id, title, description="", author=None):
        book = MockBook(book_id, title)
        book.description = description
        book.author = author
        self.books[book_id] = book
        return book

    async def get_book(self, book_id):
        return self.books.get(book_id)

    async def list_books(self):
        return list(self.books.values())

    async def delete_book(self, book_id):
        if book_id in self.books:
            del self.books[book_id]
            return True
        return False

    async def add_chapter(self, book_id, chapter_id, title, description=""):
        if book_id in self.books:
            chapter = MockChapter(chapter_id, title)
            self.books[book_id].chapters.append(chapter)
            return chapter_id
        return None

    async def search_books(self, search_query):
        return [MockSearchResult()]


class MockContentType:
    PAGE = "page"
    CHAPTER = "chapter"
    SECTION = "section"


class MockAccessLevel:
    PUBLIC = "public"
    PRIVATE = "private"


class MockContentStatus:
    ACTIVE = "active"
    DRAFT = "draft"


class MockSearchScope:
    GLOBAL = "global"
    BOOK = "book"


class MockSearchQuery:
    def __init__(self, query_text, scope, max_results, semantic_search):
        self.query_text = query_text
        self.scope = scope
        self.max_results = max_results
        self.semantic_search = semantic_search


# Mock the engine-core imports
@pytest.fixture
def mock_book_enums():
    # Import enums directly from engine_core instead of using _get_book_enums
    try:
        from engine_core import (
            AccessLevel,
            ContentStatus,
            ContentType,
            SearchQuery,
            SearchScope,
        )

        yield ContentType, AccessLevel, ContentStatus, SearchScope, SearchQuery
    except ImportError:
        # Fallback for when engine_core is not available
        yield None, None, None, None, None


@pytest.fixture
def mock_book_service():
    """Mock BookService"""
    service = MockBookService()
    with patch("engine_cli.commands.book.BookService", return_value=service):
        with patch("engine_cli.commands.book.get_book_service", return_value=service):
            yield service


@pytest.fixture
def mock_imports():
    """Mock all external imports"""
    with patch.dict(
        "sys.modules",
        {
            "engine_core": MagicMock(),
            "engine_core.services": MagicMock(),
            "engine_core.services.book_service": MagicMock(),
            "engine_core.core": MagicMock(),
            "engine_core.core.book": MagicMock(),
            "engine_core.core.book.book_builder": MagicMock(),
        },
    ):
        yield


@pytest.fixture
def cli_runner():
    return CliRunner()


class TestBookServiceIntegration:
    """Test BookService integration"""

    @pytest.mark.asyncio
    async def test_get_book_service(self, mock_book_service):
        """Test getting book service instance"""
        from engine_cli.commands.book import get_book_service

        service = get_book_service()
        assert service is not None
        assert isinstance(service, MockBookService)

    @pytest.mark.asyncio
    async def test_book_service_not_available(self):
        """Test when BookService is not available"""
        with patch("engine_cli.commands.book.BOOK_SERVICE_AVAILABLE", False):
            import click

            from engine_cli.commands.book import get_book_service

            with pytest.raises(click.ClickException, match="BookService not available"):
                get_book_service()


class TestBookCLICommands:
    """Test CLI commands for book management"""

    def test_create_book_basic(self, cli_runner, mock_book_service, mock_imports):
        """Test creating a basic book"""
        from engine_cli.commands.book import create

        result = cli_runner.invoke(
            create,
            [
                "test_book_1",
                "Test Book Title",
                "--description",
                "A test book description",
            ],
        )

        assert result.exit_code == 0
        assert "Book 'test_book_1' created successfully" in result.output

    def test_create_book_with_author(self, cli_runner, mock_book_service, mock_imports):
        """Test creating a book with author"""
        from engine_cli.commands.book import create

        result = cli_runner.invoke(
            create,
            [
                "test_book_2",
                "Test Book with Author",
                "--description",
                "Book with author",
                "--author",
                "Test Author",
            ],
        )

        assert result.exit_code == 0
        assert "Book 'test_book_2' created successfully" in result.output

    def test_show_book(self, cli_runner, mock_book_service, mock_imports):
        """Test showing book information"""
        # First create a book
        from engine_cli.commands.book import create

        cli_runner.invoke(create, ["test_book_show", "Book to Show"])

        # Then show it
        from engine_cli.commands.book import show

        result = cli_runner.invoke(show, ["test_book_show"])

        assert result.exit_code == 0
        assert "Book: Book to Show" in result.output
        assert "ID" in result.output
        assert "Title" in result.output
        assert "Statistics" in result.output

    def test_show_book_not_found(self, cli_runner, mock_book_service, mock_imports):
        """Test showing a non-existent book"""
        from engine_cli.commands.book import show

        result = cli_runner.invoke(show, ["nonexistent_book"])

        assert result.exit_code == 0
        assert "Book 'nonexistent_book' not found" in result.output

    def test_list_books(self, cli_runner, mock_book_service, mock_imports):
        """Test listing books"""
        # Create some books first
        from engine_cli.commands.book import create

        cli_runner.invoke(create, ["book1", "Book One"])
        cli_runner.invoke(create, ["book2", "Book Two"])

        # Then list them
        from engine_cli.commands.book import list

        result = cli_runner.invoke(list)

        assert result.exit_code == 0
        assert "Books" in result.output

    def test_list_books_empty(self, cli_runner, mock_book_service, mock_imports):
        """Test listing books when none exist"""
        from engine_cli.commands.book import list

        result = cli_runner.invoke(list)

        assert result.exit_code == 0
        assert "No books found" in result.output

    def test_delete_book_success(self, cli_runner, mock_book_service, mock_imports):
        """Test deleting a book successfully"""
        # Create a book first
        from engine_cli.commands.book import create

        cli_runner.invoke(create, ["book_to_delete", "Book to Delete"])

        # Then delete it
        from engine_cli.commands.book import delete

        result = cli_runner.invoke(delete, ["book_to_delete", "--force"])

        assert result.exit_code == 0
        assert "Book 'book_to_delete' deleted successfully" in result.output

    def test_delete_book_not_found(self, cli_runner, mock_book_service, mock_imports):
        """Test deleting a non-existent book"""
        from engine_cli.commands.book import delete

        result = cli_runner.invoke(delete, ["nonexistent_book", "--force"])

        assert result.exit_code == 0
        assert "not found or could not be deleted" in result.output

    def test_delete_book_with_confirmation(
        self, cli_runner, mock_book_service, mock_imports
    ):
        """Test deleting a book with user confirmation"""
        # Create a book first
        from engine_cli.commands.book import create

        cli_runner.invoke(create, ["book_confirm", "Book with Confirmation"])

        # Then try to delete with confirmation
        from engine_cli.commands.book import delete

        with patch("click.confirm", return_value=True):
            result = cli_runner.invoke(delete, ["book_confirm"])

        assert result.exit_code == 0
        assert "deleted successfully" in result.output

    def test_delete_book_cancelled(self, cli_runner, mock_book_service, mock_imports):
        """Test cancelling book deletion"""
        # Create a book first
        from engine_cli.commands.book import create

        cli_runner.invoke(create, ["book_cancel", "Book to Cancel Deletion"])

        # Then cancel deletion
        from engine_cli.commands.book import delete

        with patch("click.confirm", return_value=False):
            result = cli_runner.invoke(delete, ["book_cancel"])

        assert result.exit_code == 0
        # Should not show success message


class TestChapterCLICommands:
    """Test CLI commands for chapter management"""

    def test_add_chapter(self, cli_runner, mock_book_service, mock_imports):
        """Test adding a chapter to a book"""
        # Create a book first
        from engine_cli.commands.book import create

        cli_runner.invoke(create, ["book_with_chapter", "Book with Chapter"])

        # Then add a chapter
        from engine_cli.commands.book import add_chapter

        result = cli_runner.invoke(
            add_chapter,
            [
                "book_with_chapter",
                "chapter_1",
                "Chapter One",
                "--description",
                "First chapter",
            ],
        )

        assert result.exit_code == 0
        assert "Chapter 'chapter_1' added to book 'book_with_chapter'" in result.output

    def test_add_chapter_book_not_found(
        self, cli_runner, mock_book_service, mock_imports
    ):
        """Test adding chapter to non-existent book"""
        from engine_cli.commands.book import add_chapter

        result = cli_runner.invoke(
            add_chapter, ["nonexistent_book", "chapter_1", "Chapter One"]
        )

        assert result.exit_code == 0
        assert "Failed to add chapter" in result.output

    def test_list_chapters(self, cli_runner, mock_book_service, mock_imports):
        """Test listing chapters in a book"""
        # Create a book and add chapters
        from engine_cli.commands.book import add_chapter, create

        cli_runner.invoke(create, ["book_chapters", "Book with Chapters"])
        cli_runner.invoke(add_chapter, ["book_chapters", "chap1", "Chapter 1"])
        cli_runner.invoke(add_chapter, ["book_chapters", "chap2", "Chapter 2"])

        # Then list chapters
        from engine_cli.commands.book import list_chapters

        result = cli_runner.invoke(list_chapters, ["book_chapters"])

        assert result.exit_code == 0
        assert "Chapters in" in result.output

    def test_list_chapters_book_not_found(
        self, cli_runner, mock_book_service, mock_imports
    ):
        """Test listing chapters for non-existent book"""
        from engine_cli.commands.book import list_chapters

        result = cli_runner.invoke(list_chapters, ["nonexistent_book"])

        assert result.exit_code == 0
        assert "Book 'nonexistent_book' not found" in result.output


class TestSearchCLICommands:
    """Test CLI commands for search functionality"""

    def test_search_book(
        self, cli_runner, mock_book_service, mock_book_enums, mock_imports
    ):
        """Test searching content in a book"""
        from engine_cli.commands.book import search

        # Mock BOOK_SERVICE_AVAILABLE and required classes
        with patch("engine_cli.commands.book.BOOK_SERVICE_AVAILABLE", True), patch(
            "engine_cli.commands.book.SearchQuery", MockSearchQuery
        ), patch("engine_cli.commands.book.SearchScope", MockSearchScope):
            result = cli_runner.invoke(
                search, ["test_book", "test query", "--max-results", "5"]
            )

            assert result.exit_code == 0
            assert "Search Results for" in result.output

    def test_search_book_no_results(
        self, cli_runner, mock_book_service, mock_book_enums, mock_imports
    ):
        """Test searching with no results"""
        from engine_cli.commands.book import search

        # Mock BOOK_SERVICE_AVAILABLE and required classes
        with patch("engine_cli.commands.book.BOOK_SERVICE_AVAILABLE", True), patch(
            "engine_cli.commands.book.SearchQuery", MockSearchQuery
        ), patch("engine_cli.commands.book.SearchScope", MockSearchScope):
            # Mock empty search results
            mock_book_service.search_books = AsyncMock(return_value=[])

            result = cli_runner.invoke(search, ["test_book", "nonexistent query"])

            assert result.exit_code == 0
            assert "No results found" in result.output


class TestBookUtilityFunctions:
    """Test utility functions"""

    def test_book_enums_import(self):
        """Test that book enums can be imported from engine_core"""
        try:
            from engine_core import (
                AccessLevel,
                ContentStatus,
                ContentType,
                SearchQuery,
                SearchScope,
            )

            assert ContentType is not None
            assert AccessLevel is not None
            assert ContentStatus is not None
            assert SearchScope is not None
            assert SearchQuery is not None
        except ImportError:
            pytest.skip("engine_core not available")

    def test_format_book_table(self, mock_imports):
        """Test formatting book table"""
        from engine_cli.commands.book import format_book_table

        books = [MockBook("book1", "Book One"), MockBook("book2", "Book Two")]

        # This should not raise an exception
        format_book_table(books)

    def test_cli_group_exists(self, cli_runner):
        """Test that the CLI group exists"""
        from engine_cli.commands.book import cli

        result = cli_runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Book management commands" in result.output
        assert "create" in result.output
        assert "show" in result.output
        assert "list" in result.output
        assert "delete" in result.output
        assert "add-chapter" in result.output
        assert "list-chapters" in result.output
        assert "search" in result.output


if __name__ == "__main__":
    pytest.main([__file__])
