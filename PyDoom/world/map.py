"""Tile-based map handling."""

import sys
from typing import List, Tuple
import numpy as np

from settings import settings


class Map:
    """Tile-based map where each cell can be empty (0) or a wall (1+)."""
    
    def __init__(self, grid: List[List[int]], player_start: Tuple[float, float] = (2.0, 2.0)) -> None:
        """Initialize the map.
        
        Args:
            grid: 2D list representing the map tiles
            player_start: Starting position for the player
        """
        self.grid: List[List[int]] = grid
        self.width: int = len(grid[0])
        self.height: int = len(grid)
        self.tile_size: int = settings.map.tile_size
        self.player_start: Tuple[float, float] = player_start
        
        self.grid_array: np.ndarray = np.array(grid, dtype=np.int32)

    @staticmethod
    def load_from_file(filename: str) -> 'Map':
        """Load map from text file.
        
        Args:
            filename: Path to the map file
            
        Returns:
            Loaded Map instance
            
        Raises:
            SystemExit: If map file is not found
        """
        grid: List[List[int]] = []
        player_start: Tuple[float, float] = (2.0, 2.0)
        
        try:
            with open(filename, 'r') as file:
                for y, line in enumerate(file):
                    row: List[int] = []
                    for x, char in enumerate(line.strip()):
                        if char.isdigit():
                            row.append(int(char))
                        elif char.upper() == 'P':
                            player_start = (float(x), float(y))
                            row.append(0)
                    if row:
                        grid.append(row)
            return Map(grid, player_start)
        except FileNotFoundError:
            print(f"Error: map file '{filename}' not found.")
            sys.exit(1)
        
    def is_wall(self, x: float, y: float) -> bool:
        """Check if given world coordinates contain a wall.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if position contains a wall, False otherwise
        """
        map_x = int(x)
        map_y = int(y)
        
        if map_x < 0 or map_x >= self.width or map_y < 0 or map_y >= self.height:
            return True
            
        return self.grid[map_y][map_x] > 0
        
    def get_tile(self, x: float, y: float) -> int:
        """Get tile type at given world coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tile type ID
        """
        map_x = int(x)
        map_y = int(y)
        
        if map_x < 0 or map_x >= self.width or map_y < 0 or map_y >= self.height:
            return 1
            
        return self.grid[map_y][map_x]
