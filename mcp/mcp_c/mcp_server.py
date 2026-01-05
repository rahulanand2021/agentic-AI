from mcp.server.fastmcp import FastMCP
from pydantic import Field
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.tool(name="read_doc_contents", description="Read the content of a document and return it as a string")
def read_document_contents(doc_id: str= Field(description="The ID of the document to read")) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with {doc_id} not in docs")
    return docs[doc_id]


@mcp.tool(name="edit_doc_contents", description="Edit the content of a document with the new string")
def edit_document_contents(
    doc_id : str = Field(description="The ID of the document to read"), 
    old_str:  str = Field(description="The text to replace. Must match exactly, include whitespace" ),
    new_str:  str = Field(description="The new text to insert in the place of old text" )
    ):
    if doc_id not in docs:
        raise ValueError(f"Doc with {doc_id} not in docs")

    docs[doc_id] = docs[doc_id].replace(old_str, new_str)

@mcp.resource("docs://documents", mime_type="application/json")
def list_documents() -> list[str]:
    return list(docs.keys())

@mcp.resource("docs://documents/{doc_id}", mime_type="plain/text")
def read_documents(doc_id : str) -> str:

    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]

@mcp.prompt(name="Format", description="Rewrite the content of the document in the Markdown format")
def format_document(doc_id : str = Field(description="Id of the document to Format")) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document  to be written with Mardown Syntax.

    The id of the document you need is :
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables etc as necessary. Feel free to add in extra text, but dont change the meaning of the report.
    Use the edit_document tool to edit the document.
    """
    return [ base.UserMessage(prompt)]



# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")