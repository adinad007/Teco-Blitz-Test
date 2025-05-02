"""
Unit tests for the enhanced CodeParser functionality
Tests the ZIP archive and file relationship extraction capabilities
"""
import os
import sys
import pytest
import tempfile
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import patch, MagicMock

# Add the backend directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

# Import the CodeParser class
from app.parsers.code_parser import CodeParser, parse_code

# Test file paths
TEST_FILES_DIR = Path(__file__).parent
ZIP_TEST_FILE = TEST_FILES_DIR / "test_code_project.zip"
SINGLE_PY_FILE = TEST_FILES_DIR / "test_module.py"

@pytest.fixture
def code_parser():
    """Fixture to create a CodeParser instance"""
    return CodeParser()

@pytest.mark.asyncio
async def test_parse_single_file(code_parser):
    """Test parsing a single Python file"""
    # Make sure the test file exists
    assert SINGLE_PY_FILE.exists(), f"Test file not found: {SINGLE_PY_FILE}"
    
    # Parse the single file
    result = await code_parser.parse(str(SINGLE_PY_FILE))
    
    # Validate basic structure
    assert result is not None
    assert "code_id" in result
    assert "code_content" in result
    assert "code_structure" in result
    
    # Check if structure extraction worked
    structure = result["code_structure"]
    assert "functions" in structure
    assert "classes" in structure
    
    # Verify specific content was extracted
    function_names = [f["name"] for f in structure["functions"]]
    class_names = [c["name"] for c in structure["classes"]]
    
    assert "process_data" in function_names
    assert "DataProcessor" in class_names
    
    # Check for imports detection
    assert "imports" in structure
    assert any(imp["name"] == "helper_module" for imp in structure["imports"])

@pytest.mark.asyncio
async def test_parse_zip_archive(code_parser):
    """Test parsing a ZIP archive with Python files"""
    # Make sure the ZIP file exists
    assert ZIP_TEST_FILE.exists(), f"Test ZIP file not found: {ZIP_TEST_FILE}"
    
    # Parse the ZIP file
    result = await code_parser.parse(str(ZIP_TEST_FILE), source_type="zip")
    
    # Validate the result structure
    assert result is not None
    assert "codebase_id" in result
    assert "files" in result
    assert "structure" in result
    assert "file_count" in result
    
    # We expect 3 files in our test zip
    assert result["file_count"] == 3
    
    # Check for cross-file relationship detection
    structure = result["structure"]
    assert "dependencies" in structure
    
    # We expect test_module.py to depend on helper_module.py
    dependencies = structure["dependencies"]
    test_module_path = next((path for path in dependencies.keys() 
                            if "test_module.py" in path), None)
    
    assert test_module_path is not None, "Expected to find test_module.py in dependencies"
    
    # Verify the relationship with helper_module.py was detected
    test_module_deps = dependencies[test_module_path]
    assert any("helper_module.py" in dep["imported_file"] for dep in test_module_deps), \
           "Expected to detect dependency on helper_module.py"
    
    # Verify code metrics were calculated
    files = result["files"]
    assert any("code_metrics" in file for file in files)

# Test the main parse_code function
@pytest.mark.asyncio
async def test_parse_code_function():
    """Test the main parse_code function with different source types"""
    # Test with a single file
    single_file_result = await parse_code(str(SINGLE_PY_FILE))
    assert single_file_result is not None
    assert "code_id" in single_file_result
    
    # Test with zip file
    zip_file_result = await parse_code(str(ZIP_TEST_FILE), source_type="zip")
    assert zip_file_result is not None
    assert "codebase_id" in zip_file_result

if __name__ == "__main__":
    """Run the tests manually"""
    asyncio.run(test_parse_single_file(CodeParser()))
    asyncio.run(test_parse_zip_archive(CodeParser()))
    asyncio.run(test_parse_code_function())
    print("✅ All tests passed successfully!")
