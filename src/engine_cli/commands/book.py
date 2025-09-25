"""
Book Management Commands - Integration with BookService.

This module provides CLI commands for managing books, chapters, pages, and sect
ions
through the BookService, which handles hierarchical memory management in the
Engine Framework.

Commands integrate with:
- BookService for business logic and state management
- MockBookRepository for persistence
- SemanticSearchEngine for content search
- Version control and collaboration features

Hierarchy: Book -> Chapter -> Page -> Section
"""

import asyncio
from typing import Any, List, Optional

import click

# Import Rich formatting
from ..formatting import error, header, key_value, print_table, success, table

# Import BookService and related components
try:
    from engine_core import AccessLevel  # type: ignore
    from engine_core import BookBuilder  # type: ignore
    from engine_core import ContentStatus  # type: ignore
    from engine_core import ContentType  # type: ignore
    from engine_core import SearchQuery  # type: ignore
    from engine_core import SearchScope  # type: ignore
    from engine_core.services.book_service import BookService

    BOOK_SERVICE_AVAILABLE = True

except ImportError:
    BOOK_SERVICE_AVAILABLE = False
    BookService = None
    BookBuilder = None
    ContentType = None
    AccessLevel = None
    ContentStatus = None
    SearchScope = None
    SearchQuery = None


# Global service instance
_book_service = None


def get_book_service():
    """Get or create BookService instance."""
    global _book_service
    if _book_service is None:
        if not BOOK_SERVICE_AVAILABLE or BookService is None:
            raise click.ClickException(
                "BookService not available. Ensure backend services are "
                "properly installed."
            )
        _book_service = BookService()
    return _book_service


def format_book_table(books: List[Any]) -> None:
    """Format and display books in a table."""
    if not books:
        click.echo("No books found.")
        return

    tbl = table(
        "Books",
        ["ID", "Title", "Chapters", "Pages", "Sections", "Status", "Created"],
    )

    for book in books:
        stats = book.get_statistics()
        tbl.add_row(
            book.book_id,
            book.title,
            str(stats["chapter_count"]),
            str(stats["page_count"]),
            str(stats["section_count"]),
            book.metadata.status.value,
            book.metadata.created_at.strftime("%Y-%m-%d"),
        )

    print_table(tbl)


# === BOOK COMMANDS ===


@click.group()
def cli():
    """Book management commands."""


# Alias for backward compatibility
book = cli


@cli.command()
@click.argument("book_id")
@click.argument("title")
@click.option("--description", "-d", help="Book description")
@click.option("--author", "-a", help="Book author")
def create(
    book_id: str,
    title: str,
    description: str = "",
    author: Optional[str] = None,
):
    """Create a new book."""

    async def _create():
        try:
            service = get_book_service()

            book = await service.create_book(
                book_id=book_id,
                title=title,
                description=description,
                author=author,
            )

            if book:
                success(f"Book '{book_id}' created successfully")
                click.echo(f"Title: {book.title}")
                if book.description:
                    click.echo(f"Description: {book.description}")
            else:
                error(f"Failed to create book '{book_id}'")

        except Exception as e:
            error(f"Error creating book: {str(e)}")

    asyncio.run(_create())


@cli.command()
@click.argument("book_id")
def show(book_id: str):
    """Show book information."""

    async def _show():
        try:
            service = get_book_service()
            book = await service.get_book(book_id)

            if book:
                click.echo(f"\n{header(f'Book: {book.title}')}")

                key_value(
                    {
                        "ID": book.book_id,
                        "Title": book.title,
                        "Description": book.description or "No description",
                        "Author": book.author or "Unknown",
                        "Status": book.metadata.status.value,
                        "Created": book.metadata.created_at.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "Version": str(book.metadata.version),
                    }
                )

                stats = book.get_statistics()
                click.echo(f"\n{header('Statistics')}")
                key_value(
                    {
                        "Chapters": str(stats["chapter_count"]),
                        "Pages": str(stats["page_count"]),
                        "Sections": str(stats["section_count"]),
                        "Words": str(stats["word_count"]),
                    }
                )
            else:
                error(f"Book '{book_id}' not found")

        except Exception as e:
            error(f"Error showing book: {str(e)}")

    asyncio.run(_show())


@cli.command()
def list():
    """List all books."""

    async def _list():
        try:
            service = get_book_service()
            books = await service.list_books()

            if books:
                click.echo(f"\n{header('Books')}({len(books)} found)")
                format_book_table(books)
            else:
                click.echo("No books found.")

        except Exception as e:
            error(f"Error listing books: {str(e)}")

    asyncio.run(_list())


@cli.command()
@click.argument("book_id")
@click.option("--force", "-f", is_flag=True, help="Force deletion without confirmation")
def delete(book_id: str, force: bool = False):
    """Delete a book."""

    async def _delete():
        try:
            service = get_book_service()

            if not force:
                if not click.confirm(f"This will delete book '{book_id}'. Continue?"):
                    return

            success_flag = await service.delete_book(book_id)
            if success_flag:
                success(f"Book '{book_id}' deleted successfully")
            else:
                error(f"Book '{book_id}' not found or could not be deleted")

        except Exception as e:
            error(f"Error deleting book: {str(e)}")

    asyncio.run(_delete())


# === CHAPTER COMMANDS ===


@cli.command()
@click.argument("book_id")
@click.argument("chapter_id")
@click.argument("title")
@click.option("--description", "-d", help="Chapter description")
def add_chapter(book_id: str, chapter_id: str, title: str, description: str = ""):
    """Add a chapter to a book."""

    async def _add_chapter():
        try:
            service = get_book_service()

            chapter_id_result = await service.add_chapter(
                book_id=book_id,
                title=title,
                description=description,
            )

            if chapter_id_result:
                success(f"Chapter '{chapter_id_result}' added to book '{book_id}'")
            else:
                error(f"Failed to add chapter to book '{book_id}'")

        except Exception as e:
            error(f"Error adding chapter: {str(e)}")

    asyncio.run(_add_chapter())


@cli.command()
@click.argument("book_id")
def list_chapters(book_id: str):
    """List chapters in a book."""

    async def _list_chapters():
        try:
            service = get_book_service()
            book = await service.get_book(book_id)

            if book:
                title = f'Chapters in "{book.title}"'
                click.echo(f"\n{header(title)}")
                if book.chapters:
                    for chapter in book.chapters:
                        stats = chapter.to_dict()["statistics"]
                        click.echo(f"  • {chapter.title} ({chapter.chapter_id})")
                        click.echo(
                            f"    {stats['page_count']} pages, "
                            f"{stats['section_count']} sections, "
                            f"{stats['word_count']} words"
                        )
                else:
                    click.echo("No chapters in this book.")
            else:
                error(f"Book '{book_id}' not found")

        except Exception as e:
            error(f"Error listing chapters: {str(e)}")

    asyncio.run(_list_chapters())


# === SEARCH COMMANDS ===


@cli.command()
@click.argument("book_id")
@click.argument("query")
@click.option("--max-results", "-m", type=int, default=10, help="Maximum results")
def search(book_id: str, query: str, max_results: int = 10):
    """Search content in a book."""
    if not BOOK_SERVICE_AVAILABLE:
        error("Book service not available. Please install engine-core.")
        return

    if SearchQuery is None or SearchScope is None:
        error("Search functionality not available in current engine-core version.")
        return

    async def _search():
        try:
            service = get_book_service()

            search_query = SearchQuery(  # type: ignore
                query_text=query,
                scope=SearchScope.GLOBAL,  # type: ignore
                max_results=max_results,
                semantic_search=False,
            )

            results = await service.search_books(search_query)

            if results:
                click.echo(f"\n{header(f'Search Results for {query}')}")
                for i, result in enumerate(results, 1):
                    click.echo(f"\nResult {i}:")
                    key_value(
                        {
                            "Type": result.content_type.title(),
                            "Title": result.title,
                            "ID": result.content_id,
                            "Relevance": f"{result.relevance_score:.2f}",
                        }
                    )

                    if result.content_snippet:
                        click.echo(
                            f"  Snippet: {result.content_snippet[:100]}"
                            f"{'...' if len(result.content_snippet) > 100 else ''}"
                        )

                    if result.highlights:
                        click.echo(f"  Highlights: {', '.join(result.highlights[:3])}")
            else:
                click.echo(f"No results found for query: {query}")

        except Exception as e:
            error(f"Error searching: {str(e)}")

    asyncio.run(_search())
