"""Utility functions for entity operations."""

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.player import Player


def calculate_distance_squared(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate squared distance between two points (faster, no sqrt).
    
    Args:
        x1: First point X coordinate
        y1: First point Y coordinate
        x2: Second point X coordinate
        y2: Second point Y coordinate
        
    Returns:
        Squared distance between the two points
    """
    dx = x2 - x1
    dy = y2 - y1
    return dx * dx + dy * dy
