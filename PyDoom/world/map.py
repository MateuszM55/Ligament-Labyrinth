"""Tile-based map handling."""

import sys
import random
from typing import List, Tuple
import numpy as np

from settings import settings
from world.monster import Monster


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
        self.player_start: Tuple[float, float] = player_start
        self.sprite_data: np.ndarray = np.empty((0, 3), dtype=np.float32)
        self.monsters: List[Monster] = []
        
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
        sprite_list: List[Tuple[float, float, int]] = []
        
        try:
            with open(filename, 'r') as file:
                for y, line in enumerate(file):
                    row: List[int] = []
                    for x, char in enumerate(line.strip()):
                        if char.isdigit():
                            row.append(int(char))
                        elif char.upper() == 'P':
                            player_start = (float(x) + 0.5, float(y) + 0.5)
                            row.append(0)
                        elif char.upper() == 'M':
                            sprite_list.append((float(x) + 0.5, float(y) + 0.5, random.randint(0, 10)))
                            row.append(0)
                    if row:
                        grid.append(row)
            game_map = Map(grid, player_start)
            if sprite_list:
                game_map.sprite_data = np.array(sprite_list, dtype=np.float32)
                for sprite_x, sprite_y, texture_id in sprite_list:
                    game_map.monsters.append(Monster(sprite_x, sprite_y, int(texture_id)))
            return game_map
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
    
    def add_monster(self, x: float, y: float, texture_id: int = None) -> None:
        """Add a monster/sprite to the map.
        
        Args:
            x: X position in world coordinates
            y: Y position in world coordinates
            texture_id: Texture ID for the sprite (random if None)
        """
        if texture_id is None:
            texture_id = random.randint(0, 10)
        new_sprite = np.array([[x, y, texture_id]], dtype=np.float32)
        if self.sprite_data.shape[0] == 0:
            self.sprite_data = new_sprite
        else:
            self.sprite_data = np.vstack([self.sprite_data, new_sprite])
        
        self.monsters.append(Monster(x, y, texture_id))
    
    def update_sprite_data(self) -> None:
        """Update sprite_data array from monster positions."""
        if self.monsters:
            self.sprite_data = np.array(
                [[m.x, m.y, m.texture_id] for m in self.monsters],
                dtype=np.float32
            )
        else:
            self.sprite_data = np.empty((0, 3), dtype=np.float32)