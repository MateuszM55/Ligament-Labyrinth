"""Manages dynamic objects (Monsters, Collectibles)."""
import numpy as np
import random
from typing import List, TYPE_CHECKING
from settings import settings
from world.monster import Monster
from world.collectible import Collectible

if TYPE_CHECKING:
    from world.player import Player

class EntityManager:
    """Manages all dynamic entities in the game world, including monsters and collectibles."""
    
    def __init__(self):
        """Initialize the entity manager with empty entity lists."""
        self.monsters: List[Monster] = []
        self.collectibles: List[Collectible] = []
        # Pre-allocate numpy array for rendering
        self.sprite_data: np.ndarray = np.empty((0, 3), dtype=np.float32)

    def load_entities(self, monster_data: List[dict], collectible_data: List[dict]):
        """Populate the manager with entities from map data.
        
        Args:
            monster_data: List of dictionaries containing monster position data.
            collectible_data: List of dictionaries containing collectible position data.
        """
        for m in monster_data:
            # Random texture for monsters, or pass it in if your map file supports it
            tex_id = random.randint(0, 10) 
            self.monsters.append(Monster(m['x'], m['y'], tex_id))
            
        col_idx = 0
        tex_ids = settings.collectible.texture_ids
        for c in collectible_data:
            # Cycle through collectible textures
            tex_id = tex_ids[col_idx % len(tex_ids)]
            self.collectibles.append(Collectible(c['x'], c['y'], tex_id))
            col_idx += 1
            
        self.update_sprite_data()

    def update(self, dt: float, player: 'Player'):
        """Update all entities' states (AI movement, logic).
        
        Args:
            dt: Delta time in seconds.
            player: The player instance.
        """
        for monster in self.monsters:
            monster.move_towards_player(player, dt)
        
        # Rebuild the render array
        self.update_sprite_data()

    def update_sprite_data(self):
        """Flatten active entities into a NumPy array for optimized raycasting."""
        sprites = []
        
        for m in self.monsters:
            sprites.append([m.x, m.y, m.texture_id])
            
        for c in self.collectibles:
            if not c.collected:
                sprites.append([c.x, c.y, c.texture_id])
                
        if sprites:
            self.sprite_data = np.array(sprites, dtype=np.float32)
        else:
            self.sprite_data = np.empty((0, 3), dtype=np.float32)

    def check_collisions(self, player: 'Player') -> bool:
        """Check if the player has collided with any monster.
        
        Args:
            player: The player instance.
            
        Returns:
            True if a collision is detected (Game Over), False otherwise.
        """
        threshold_sq = settings.monster.collision_distance ** 2
        
        for monster in self.monsters:
            if monster.get_distance_squared_to_player(player) < threshold_sq:
                return True
        return False

    def check_collections(self, player: 'Player') -> int:
        """Check if the player has collected any items.
        
        Args:
            player: The player instance.
            
        Returns:
            The number of items collected in this update cycle.
        """
        count = 0
        dist = settings.collectible.collection_distance
        
        for collectible in self.collectibles:
            if collectible.check_collection(player, dist):
                count += 1
        return count

    def get_closest_monster_distance(self, player: 'Player') -> float:
        """Get the distance to the monster closest to the player.
        
        Args:
            player: The player instance.
            
        Returns:
            The distance to closest monster, or float('inf') if no monsters.
        """
        if not self.monsters:
            return float('inf')
        
        return min(m.get_distance_to_player(player) for m in self.monsters)
