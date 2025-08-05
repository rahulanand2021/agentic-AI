from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import os
import time

# Global console instance
console = Console()

def print_markdown(text, title=None):
    """
    Simple function to print markdown text in the terminal.
    
    Args:
        text (str): Markdown text to display
        title (str, optional): Title for the panel
    """
    md = Markdown(text)
    if title:
        panel = Panel(md, title=title, border_style="blue")
        console.print(panel)
    else:
        console.print(md)

def print_code(code, language="python", title="Code"):
    """
    Display code with syntax highlighting.
    
    Args:
        code (str): Code to display
        language (str): Programming language
        title (str): Panel title
    """
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    panel = Panel(syntax, title=title, border_style="green")
    console.print(panel)

def print_success(message):
    """Print a success message in green."""
    console.print(f"[green]✅ {message}[/green]")

def print_error(message):
    """Print an error message in red."""
    console.print(f"[red]❌ {message}[/red]")

def print_warning(message):
    """Print a warning message in yellow."""
    console.print(f"[yellow]⚠️  {message}[/yellow]")

def print_info(message):
    """Print an info message in blue."""
    console.print(f"[blue]ℹ️  {message}[/blue]")

def print_table(headers, rows, title="Data Table"):
    """
    Display data in a formatted table.
    
    Args:
        headers (list): Column headers
        rows (list): List of rows (each row is a list of values)
        title (str): Table title
    """
    table = Table(title=title)
    
    for header in headers:
        table.add_column(header, style="cyan", no_wrap=True)
    
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    
    console.print(table)

def show_loading_spinner(description="Processing..."):
    """
    Context manager for showing a loading spinner.
    
    Usage:
        with show_loading_spinner("Loading data..."):
            # Your code here
            time.sleep(2)
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    )

# Example usage
if __name__ == "__main__":
    # Test the utilities
    with show_loading_spinner("Loading data..."):
        time.sleep(20)

    print_markdown("# Hello World\nThis is **bold** and *italic* text.", "Test Markdown")
    
    print_code('print("Hello, World!")', "python", "Simple Code")
    
    print_success("Operation completed successfully!")
    print_error("Something went wrong!")
    print_warning("This is a warning message.")
    print_info("Here's some information for you.")
    
    # Example table
    headers = ["Name", "Age", "City"]
    rows = [
        ["Alice", 25, "New York"],
        ["Bob", 30, "Los Angeles"],
        ["Charlie", 35, "Chicago"]
    ]
    print_table(headers, rows, "Sample Data") 