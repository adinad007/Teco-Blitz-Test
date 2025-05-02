import os
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

# Import directly since we're already in the app package
from parsers.document_parser import parse_document, _parse_with_llamaparse, _chunk_document

# Test data
TEST_TEXT_CONTENT = "This is test content for document parsing."


class MockLlamaParseResult:
    """Mock class for LlamaParse result object"""
    def __init__(self, text=None, pages=None, metadata=None):
        self.text = text
        self.pages = pages or []
        self.metadata = metadata or {}
    
    def get_text_documents(self):
        """Mock method to get text documents"""
        class MockTextDoc:
            def __init__(self, text):
                self.text = text
        
        return [MockTextDoc(self.text)] if self.text else []
    
    def get_markdown_documents(self):
        """Mock method to get markdown documents"""
        class MockMarkdownDoc:
            def __init__(self, text):
                self.text = text
        
        return [MockMarkdownDoc(self.text)] if self.text else []


@pytest.fixture
def mock_temp_file():
    """Create a temporary test file for document parsing tests."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp.write(TEST_TEXT_CONTENT.encode('utf-8'))
        tmp_path = tmp.name
    
    yield tmp_path
    
    # Cleanup after test
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.mark.asyncio
@patch('parsers.document_parser.LlamaParse')
async def test_parse_with_llamaparse_text_attribute(mock_llama_parse, mock_temp_file):
    """Test _parse_with_llamaparse when result has text attribute."""
    # Setup mock
    mock_instance = MagicMock()
    mock_llama_parse.return_value = mock_instance
    
    # Create mock result with text attribute
    mock_result = MockLlamaParseResult(text=TEST_TEXT_CONTENT)
    # Create an awaitable mock
    async def mock_coro(*args, **kwargs):
        return mock_result
    
    mock_instance.aparse.side_effect = mock_coro
    
    # Call function
    text_content, metadata = await _parse_with_llamaparse(mock_temp_file)
    
    # Assertions
    assert len(text_content) == 1
    assert text_content[0] == TEST_TEXT_CONTENT
    assert isinstance(metadata, dict)
    
    # Verify LlamaParse was called correctly
    mock_llama_parse.assert_called_once()
    mock_instance.aparse.assert_called_once()
    args, kwargs = mock_instance.aparse.call_args
    assert "extra_info" in kwargs
    assert kwargs["extra_info"]["file_name"] == Path(mock_temp_file).name


@pytest.mark.asyncio
@patch('parsers.document_parser.LlamaParse')
async def test_parse_with_llamaparse_pages_attribute(mock_llama_parse, mock_temp_file):
    """Test _parse_with_llamaparse when result has pages attribute."""
    # Setup mock
    mock_instance = MagicMock()
    mock_llama_parse.return_value = mock_instance
    
    # Create mock pages
    class MockPage:
        def __init__(self, text):
            self.text = text
    
    mock_pages = [MockPage(f"Page {i} content") for i in range(3)]
    # Create mock result with pages and metadata
    mock_result = MockLlamaParseResult(
        pages=mock_pages,
        metadata={"page_count": 3}
    )
    
    # Create an awaitable mock
    async def mock_coro(*args, **kwargs):
        return mock_result
    
    mock_instance.aparse.side_effect = mock_coro
    
    # Call function
    text_content, metadata = await _parse_with_llamaparse(mock_temp_file)
    
    # Assertions
    assert len(text_content) == 3
    assert all("Page" in content for content in text_content)
    assert metadata.get("page_count") == 3


def test_chunk_document():
    """Test document chunking functionality."""
    # Test with a single document
    documents = ["This is a test document. It has multiple sentences. We want to make sure it gets chunked properly."]
    
    # Set small chunk size for testing
    chunks = _chunk_document(documents, chunk_size=20, chunk_overlap=5)
    
    # Assertions
    assert len(chunks) > 1
    assert all(isinstance(chunk, dict) for chunk in chunks)
    assert all("chunk_id" in chunk for chunk in chunks)
    assert all("text" in chunk for chunk in chunks)
    assert all("metadata" in chunk for chunk in chunks)
    
    # Test with multiple documents
    documents = ["Document 1 content.", "Document 2 content."]
    chunks = _chunk_document(documents, chunk_size=20, chunk_overlap=5)
    
    # Assertions
    assert len(chunks) >= 2
    assert chunks[0]["metadata"]["document_index"] == 0
    assert chunks[-1]["metadata"]["document_index"] == 1


@pytest.mark.asyncio
@patch('parsers.document_parser._parse_with_llamaparse')
async def test_parse_document_integration(mock_parse_with_llamaparse, mock_temp_file):
    """Test the complete parse_document function."""
    # Setup mock
    mock_text_content = ["Document content for testing"]
    mock_metadata = {"page_count": 1}
    
    # Create an awaitable mock
    async def mock_coro(*args, **kwargs):
        return (mock_text_content, mock_metadata)
    
    mock_parse_with_llamaparse.side_effect = mock_coro
    
    # Call function
    result = await parse_document(mock_temp_file)
    
    # Assertions
    assert isinstance(result, dict)
    assert "document_id" in result
    assert "parsed_chunks" in result
    assert "chunk_count" in result
    assert "metadata" in result
    
    # Verify chunks were created
    assert len(result["parsed_chunks"]) > 0
    assert result["chunk_count"] > 0
    
    # Verify metadata was included
    assert "file_name" in result["metadata"]
    assert "file_path" in result["metadata"]
    assert "file_size" in result["metadata"]
    assert "file_extension" in result["metadata"]
    assert "content_type" in result["metadata"]
    assert "creation_time" in result["metadata"]
    assert "modification_time" in result["metadata"]
    assert "parse_timestamp" in result["metadata"]
    assert "raw_metadata" in result["metadata"]
    assert "page_count" in result["metadata"]["raw_metadata"]
