"""
Test module demonstrating a Python module with imports and functions
"""
import os
import sys
from typing import List, Dict, Any

from helper_module import calculate_sum, format_output

def process_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process a list of data dictionaries
    
    Args:
        data: List of data dictionaries to process
        
    Returns:
        Dict containing processed results
    """
    result = {}
    total = 0
    
    for item in data:
        if "value" in item:
            total += calculate_sum(item["value"])
    
    result["total"] = total
    result["formatted"] = format_output(total)
    return result

class DataProcessor:
    """Data processing class for more complex operations"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize with optional configuration"""
        self.config = config or {}
        self.processed_count = 0
    
    def batch_process(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple items and return results"""
        results = []
        for item in items:
            results.append(process_data([item]))
            self.processed_count += 1
        return results
    
if __name__ == "__main__":
    # Example usage
    test_data = [{"value": 5}, {"value": 10}, {"value": 15}]
    result = process_data(test_data)
    print(f"Processed result: {result}")
