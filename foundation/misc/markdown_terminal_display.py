from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
import os

def display_markdown_in_terminal(markdown_text, title="Markdown Content"):
    """
    Display markdown content properly formatted in the terminal using Rich.
    
    Args:
        markdown_text (str): The markdown text to display
        title (str): Optional title for the panel
    """
    console = Console()
    
    # Create a markdown object
    md = Markdown(markdown_text)
    
    # Display in a panel for better visual separation
    panel = Panel(md, title=title, border_style="blue")
    console.print(panel)

def display_markdown_file(file_path, title=None):
    """
    Display a markdown file in the terminal.
    
    Args:
        file_path (str): Path to the markdown file
        title (str): Optional title, defaults to filename
    """
    if not os.path.exists(file_path):
        console = Console()
        console.print(f"[red]Error: File '{file_path}' not found[/red]")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if title is None:
        title = os.path.basename(file_path)
    
    display_markdown_in_terminal(content, title)

def display_code_with_syntax(code, language="python", title="Code"):
    """
    Display code with syntax highlighting in the terminal.
    
    Args:
        code (str): The code to display
        language (str): Programming language for syntax highlighting
        title (str): Optional title for the panel
    """
    console = Console()
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    panel = Panel(syntax, title=title, border_style="green")
    console.print(panel)

# Example usage and demonstration
if __name__ == "__main__":
    console = Console()
    
    # Example 1: Display markdown text
    sample_markdown = """
# Welcome to Markdown Terminal Display

This is a **bold** example of how to display markdown in the terminal.

## Features

- ✅ **Rich formatting** with colors and styles
- ✅ **Code syntax highlighting**
- ✅ **Lists and tables** support
- ✅ **Links and images** (displayed as text)

### Code Example

```python
def hello_world():
    print("Hello, World!")
    return "Success"
```

### Table Example

| Feature | Status | Notes |
|---------|--------|-------|
| Bold | ✅ | Works great |
| Italic | ✅ | Also works |
| Code | ✅ | With syntax highlighting |

> **Note**: This is a blockquote example.

For more information, visit [Rich documentation](https://rich.readthedocs.io/).
"""
    
    console.print("\n[bold blue]Example 1: Displaying Markdown Text[/bold blue]")
    display_markdown_in_terminal(sample_markdown, "Sample Markdown")
    
    # Example 2: Display code with syntax highlighting
    sample_code = '''
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Example usage
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
'''
    
    console.print("\n[bold green]Example 2: Code with Syntax Highlighting[/bold green]")
    display_code_with_syntax(sample_code, "python", "Fibonacci Function")
    
    # Example 3: Display README.md if it exists
    readme_path = "README.md"
    if os.path.exists(readme_path):
        console.print("\n[bold yellow]Example 3: Displaying README.md[/bold yellow]")
        display_markdown_file(readme_path, "Project README")
    else:
        console.print(f"\n[yellow]Note: {readme_path} not found in current directory[/yellow]")
    
    # Example 4: Simple text with rich formatting
    console.print("\n[bold magenta]Example 4: Rich Text Formatting[/bold magenta]")
    text = Text()
    text.append("This is ", style="bold blue")
    text.append("rich", style="bold red")
    text.append(" text formatting!", style="bold green")
    console.print(text) 