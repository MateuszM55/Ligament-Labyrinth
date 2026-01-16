"""Utility functions for entity operations."""

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.player import Player


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points.
    
    Args:
        x1: First point X coordinate
        y1: First point Y coordinate
        x2: Second point X coordinate
        y2: Second point Y coordinate
        
    Returns:
        Distance between the two points
    """
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)


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


def distance_to_player(entity_x: float, entity_y: float, player: 'Player') -> float:
    """Calculate distance from an entity to the player.
    
    Args:
        entity_x: Entity X position
        entity_y: Entity Y position
        player: Player object
        
    Returns:
        Distance in world units
    """
    return calculate_distance(entity_x, entity_y, player.x, player.y)


def distance_squared_to_player(entity_x: float, entity_y: float, player: 'Player') -> float:
    """Calculate squared distance from an entity to the player (faster).
    
    Args:
        entity_x: Entity X position
        entity_y: Entity Y position
        player: Player object
        
    Returns:
        Squared distance in world units
    """
    return calculate_distance_squared(entity_x, entity_y, player.x, player.y)
