"""Tile-based map handling."""

import sys
import random
from typing import List, Tuple
import numpy as np

from settings import settings
from world.monster import Monster
from world.collectible import Collectible


class Map:
    """Tile-based map where each cell can be empty (0) or a wall (1+)."""
    
    def __init__(self, grid: List[List[int]], player_start: Tuple[float, float] = (2.0, 2.0), 
                 floor_grid: List[List[int]] = None, ceiling_grid: List[List[int]] = None) -> None:
        """Initialize the map.
        
        Args:
            grid: 2D list representing the map tiles
            player_start: Starting position for the player
            floor_grid: 2D list representing floor texture IDs
            ceiling_grid: 2D list representing ceiling texture IDs
        """
        self.grid: List[List[int]] = grid
        self.width: int = len(grid[0])
        self.height: int = len(grid)
        self.player_start: Tuple[float, float] = player_start
        self.sprite_data: np.ndarray = np.empty((0, 3), dtype=np.float32)
        self.monsters: List[Monster] = []
        self.collectibles: List[Collectible] = []
        
        self.grid_array: np.ndarray = np.array(grid, dtype=np.int32)
        
        # Floor and ceiling texture maps
        if floor_grid is None:
            floor_grid = [[0] * self.width for _ in range(self.height)]
        if ceiling_grid is None:
            ceiling_grid = [[0] * self.width for _ in range(self.height)]
            
        self.floor_grid: List[List[int]] = floor_grid
        self.ceiling_grid: List[List[int]] = ceiling_grid
        self.floor_grid_array: np.ndarray = np.array(floor_grid, dtype=np.int32)
        self.ceiling_grid_array: np.ndarray = np.array(ceiling_grid, dtype=np.int32)

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
        collectible_list: List[Tuple[float, float, int]] = []
        
        try:
            with open(filename, 'r') as file:
                collectible_index = 0
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
                        elif char.upper() == 'C':
                            # Use different texture IDs for each collectible
                            texture_id = settings.collectible.texture_ids[collectible_index % len(settings.collectible.texture_ids)]
                            collectible_list.append((float(x) + 0.5, float(y) + 0.5, texture_id))
                            collectible_index += 1
                            row.append(0)
                    if row:
                        grid.append(row)
            
            # Normalize grid to ensure all rows have the same length
            if grid:
                max_width = max(len(row) for row in grid)
                for row in grid:
                    while len(row) < max_width:
                        row.append(1)  # Pad with walls
            
            # Load floor and ceiling maps
            floor_grid = Map._load_texture_map(filename.replace('.txt', '_floor.txt'), max_width if grid else 0, len(grid)) if grid else None
            ceiling_grid = Map._load_texture_map(filename.replace('.txt', '_ceiling.txt'), max_width if grid else 0, len(grid)) if grid else None
            
            game_map = Map(grid, player_start, floor_grid, ceiling_grid)
            if sprite_list:
                game_map.sprite_data = np.array(sprite_list, dtype=np.float32)
                for sprite_x, sprite_y, texture_id in sprite_list:
                    game_map.monsters.append(Monster(sprite_x, sprite_y, int(texture_id)))
            if collectible_list:
                for coll_x, coll_y, texture_id in collectible_list:
                    game_map.collectibles.append(Collectible(coll_x, coll_y, int(texture_id)))
            return game_map
        except FileNotFoundError:
            print(f"Error: map file '{filename}' not found.")
            sys.exit(1)
    
    @staticmethod
    def _load_texture_map(filename: str, expected_width: int, expected_height: int) -> List[List[int]]:
        """Load a texture map from file (for floors or ceilings).
        
        Args:
            filename: Path to the texture map file
            expected_width: Expected width of the map
            expected_height: Expected height of the map
            
        Returns:
            2D list of texture IDs, or default grid if file not found
        """
        try:
            texture_grid: List[List[int]] = []
            with open(filename, 'r') as file:
                for line in file:
                    row: List[int] = []
                    for char in line.strip():
                        if char.isdigit():
                            row.append(int(char))
                    if row:
                        texture_grid.append(row)
            print(f"Loaded texture map from {filename}")
            return texture_grid
        except FileNotFoundError:
            print(f"Warning: texture map file '{filename}' not found. Using default texture (ID 0).")
            return [[0] * expected_width for _ in range(expected_height)]
        
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
        
        self.monsters.append(Monster(x, y, texture_id))
        # Rebuild sprite_data from monsters list (avoids expensive np.vstack)
        self.update_sprite_data()
    
    def update_sprite_data(self) -> None:
        """Update sprite_data array from monster and collectible positions."""
        sprite_list = []
        
        # Add all monsters
        for m in self.monsters:
            sprite_list.append([m.x, m.y, m.texture_id])
        
        # Add uncollected collectibles
        for c in self.collectibles:
            if not c.collected:
                sprite_list.append([c.x, c.y, c.texture_id])
        
        if sprite_list:
            self.sprite_data = np.array(sprite_list, dtype=np.float32)
        else:
            self.sprite_data = np.empty((0, 3), dtype=np.float32)
    
    def update(self, dt: float, player) -> None:
        """Update all entities in the map.
        
        Args:
            dt: Delta time in seconds
            player: The player object for AI targeting
        """
        for monster in self.monsters:
            monster.move_towards_player(player, dt)
        
        self.update_sprite_data()
    
    def check_monster_collisions(self, player) -> bool:
        """Check if player collides with any monsters.
        
        Args:
            player: The player object
            
        Returns:
            True if collision detected, False otherwise
        """
        collision_distance_squared = settings.monster.collision_distance ** 2
        
        for monster in self.monsters:
            distance_squared = monster.get_distance_squared_to_player(player)
            
            if distance_squared < collision_distance_squared:
                return True
        
        return False
    
    def check_collectible_collisions(self, player) -> int:
        """Check if player collects any collectibles.
        
        Args:
            player: The player object
            
        Returns:
            Number of collectibles collected this frame
        """
        collection_distance = settings.collectible.collection_distance
        collected_count = 0
        
        for collectible in self.collectibles:
            if collectible.check_collection(player, collection_distance):
                collected_count += 1
        
        return collected_count
    
    def get_closest_monster_distance(self, player) -> float:
        """Get distance to closest monster.
        
        Args:
            player: The player object
            
        Returns:
            Distance to closest monster, or infinity if no monsters
        """
        if not self.monsters:
            return float('inf')
        
        closest_distance = float('inf')
        for monster in self.monsters:
            distance = monster.get_distance_to_player(player)
            closest_distance = min(closest_distance, distance)
        
        return closest_distance