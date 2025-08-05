from terminal_utils import print_markdown, print_success, print_error, print_info, print_code
from openai import OpenAI
import os
from dotenv import load_dotenv

def demonstrate_markdown_in_llm_output():
    """
    Example of how to display LLM responses with proper markdown formatting
    """
    load_dotenv()
    
    # Example 1: Display a formatted response
    llm_response = """
# AI Response Analysis

## Summary
This is a **comprehensive analysis** of the given question.

### Key Points
1. **First point**: Important observation
2. **Second point**: Another critical insight
3. **Third point**: Final conclusion

### Code Example
```python
def analyze_data(data):
    return data.analyze()
```

> **Note**: This is a sample response showing markdown formatting.
"""
    
    print_markdown(llm_response, "AI Response")
    
    # Example 2: Display error messages nicely
    print_error("API key not found in environment variables")
    print_success("Successfully connected to OpenAI API")
    print_info("Processing your request...")
    
    # Example 3: Display code snippets
    sample_code = '''
def process_llm_response(response):
    """Process and format LLM response for display."""
    if response.startswith("#"):
        return format_as_markdown(response)
    else:
        return format_as_text(response)
'''
    
    print_code(sample_code, "python", "Response Processing Function")

if __name__ == "__main__":
    demonstrate_markdown_in_llm_output() 