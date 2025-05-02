"""
Helper module with utility functions referenced by test_module.py
"""
from typing import Any, Union, List
import math

def calculate_sum(values: Union[List[float], float]) -> float:
    """
    Calculate sum of values or return the value if it's a single number
    
    Args:
        values: Single value or list of values to sum
    
    Returns:
        Sum of all values
    """
    if isinstance(values, list):
        return sum(values)
    return float(values)

def format_output(value: float) -> str:
    """
    Format a numeric value for output
    
    Args:
        value: Value to format
    
    Returns:
        Formatted string representation
    """
    if value > 1000:
        return f"{value/1000:.2f}K"
    return f"{value:.2f}"

class MathHelper:
    """Helper class with additional math functions"""
    
    @staticmethod
    def square_root(value: float) -> float:
        """Calculate square root of a number"""
        return math.sqrt(value)
    
    @staticmethod
    def power(base: float, exponent: float) -> float:
        """Calculate base raised to the exponent power"""
        return math.pow(base, exponent)
