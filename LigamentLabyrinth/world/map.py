"""Tile-based map geometry."""
import sys
from typing import List, Tuple, Any
import numpy as np

class Map:
    """Represents the static geometry of the level (Walls, Floors, Ceilings).
    
    The map is stored as a 2D grid where values > 0 represent wall types.
    """
    
    def __init__(self, grid: List[List[int]], player_start: Tuple[float, float], 
                 floor_grid: List[List[int]] = None, ceiling_grid: List[List[int]] = None) -> None:
        """Initialize the map with grid data and player start position.

        Args:
            grid: 2D list for wall layout.
            player_start: (x, y) coordinates for player spawn.
            floor_grid: Optional 2D list for floor textures.
            ceiling_grid: Optional 2D list for ceiling textures.
        """
        self.grid = grid
        self.width = len(grid[0])
        self.height = len(grid)
        self.player_start = player_start
        
        # Geometry Arrays for Numba
        self.grid_array = np.array(grid, dtype=np.int32)
        
        if floor_grid is None:
            floor_grid = [[0] * self.width for _ in range(self.height)]
        if ceiling_grid is None:
            ceiling_grid = [[0] * self.width for _ in range(self.height)]
            
        self.floor_grid_array = np.array(floor_grid, dtype=np.int32)
        self.ceiling_grid_array = np.array(ceiling_grid, dtype=np.int32)

    def is_wall(self, x: float, y: float) -> bool:
        """Check if the given world coordinates are occupied by a wall.
        
        Args:
            x: World X coordinate.
            y: World Y coordinate.

        Returns:
            True if the tile is a wall, False otherwise.
        """
        # Casting to int acts as floor()
        map_x, map_y = int(x), int(y)
        
        if map_x < 0 or map_x >= self.width or map_y < 0 or map_y >= self.height:
            return True
        return self.grid[map_y][map_x] > 0

    @staticmethod
    def load_from_file(filename: str) -> Tuple['Map', List[dict], List[dict]]:
        """Load map data from a text file and associated texture maps.

        Args:
            filename: Path to the map text file.

        Returns:
            A tuple containing (Map object, monsters list, collectibles list).
        """
        grid = []
        player_start = (2.0, 2.0)
        
        # Temporary lists to hold data found in text file
        found_monsters = [] 
        found_collectibles = []
        
        try:
            with open(filename, 'r') as file:
                for y, line in enumerate(file):
                    row = []
                    for x, char in enumerate(line.strip()):
                        if char.isdigit():
                            row.append(int(char))
                        elif char.upper() == 'P':
                            player_start = (float(x) + 0.5, float(y) + 0.5)
                            row.append(0)
                        elif char.upper() == 'M':
                            # Store the data, don't create the object yet
                            found_monsters.append({'x': x + 0.5, 'y': y + 0.5})
                            row.append(0)
                        elif char.upper() == 'C':
                            found_collectibles.append({'x': x + 0.5, 'y': y + 0.5})
                            row.append(0)
                        else:
                            row.append(0)
                    if row:
                        grid.append(row)

            # Pad grid to be rectangular
            if grid:
                max_width = max(len(row) for row in grid)
                for row in grid:
                    while len(row) < max_width:
                        row.append(1)

            # Load extra textures
            f_grid = Map._load_texture_map(filename.replace('.txt', '_floor.txt'), max_width, len(grid))
            c_grid = Map._load_texture_map(filename.replace('.txt', '_ceiling.txt'), max_width, len(grid))
            
            game_map = Map(grid, player_start, floor_grid=f_grid, ceiling_grid=c_grid)
            return game_map, found_monsters, found_collectibles

        except FileNotFoundError:
            print(f"Error: map file '{filename}' not found.")
            sys.exit(1)

    @staticmethod
    def _load_texture_map(filename: str, w: int, h: int) -> List[List[int]]:
        """Helper to load auxiliary texture maps (floor/ceiling).

        Args:
            filename: Path to the texture map file.
            w: Expected width for padding.
            h: Expected height for padding.

        Returns:
            A 2D list of texture IDs.
        """
        try:
            grid = []
            with open(filename, 'r') as f:
                for line in f:
                    row = [int(c) for c in line.strip() if c.isdigit()]
                    if row: grid.append(row)
            return grid
        except FileNotFoundError:
            return [[0] * w for _ in range(h)]