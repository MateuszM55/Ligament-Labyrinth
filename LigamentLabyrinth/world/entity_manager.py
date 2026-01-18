"""Manages dynamic objects (Monsters, Collectibles)."""
import numpy as np
import random
from typing import List, TYPE_CHECKING
from settings import settings
from world.monster import Monster
from world.collectible import Collectible
from world.entity import Entity

if TYPE_CHECKING:
    from world.player import Player

class EntityManager:
    """Manages all dynamic entities in the game world in a generic, extensible way."""
    
    def __init__(self):
        """Initialize the entity manager with an empty entity list."""
        self.entities: List[Entity] = []
        # Pre-allocate numpy array for rendering
        self.sprite_data: np.ndarray = np.empty((0, 3), dtype=np.float32)

    def add_entity(self, entity: Entity) -> None:
        """Add a single entity to the manager.
        
        Args:
            entity: The entity to add.
        """
        self.entities.append(entity)

    def load_entities(self, monster_data: List[dict], collectible_data: List[dict]):
        """Populate the manager with entities from map data.
        
        Args:
            monster_data: List of dictionaries containing monster position data.
            collectible_data: List of dictionaries containing collectible position data.
        """
        for m in monster_data:
            
            tex_id = random.randint(0, 10) 
            self.add_entity(Monster(m['x'], m['y'], tex_id))
            
        col_idx = 0
        tex_ids = settings.collectible.texture_ids
        for c in collectible_data:
            
            tex_id = tex_ids[col_idx % len(tex_ids)]
            self.add_entity(Collectible(c['x'], c['y'], tex_id))
            col_idx += 1
            
        self.update_sprite_data()

    def update(self, dt: float, player: 'Player') -> int:
        """Update all entities and remove inactive ones.
        
        Args:
            dt: Delta time in seconds.
            player: The player instance.
            
        Returns:
            Number of collectibles that were collected this frame.
        """
        collectibles_collected = 0
        
        # Update all entities
        for entity in self.entities:
            was_collected = isinstance(entity, Collectible) and not entity.collected
            entity.update(dt, player)
            
            # Count newly collected items
            if isinstance(entity, Collectible) and entity.collected and was_collected:
                collectibles_collected += 1
        
        # Remove inactive entities (collected items or collided monsters)
        self.entities = [e for e in self.entities if e.active]
        
        # Rebuild the render array
        self.update_sprite_data()
        
        return collectibles_collected

    def update_sprite_data(self):
        """Flatten active entities into a NumPy array for optimized raycasting."""
        sprites = []
        
        for entity in self.entities:
            sprites.append(list(entity.render_data))
                
        if sprites:
            self.sprite_data = np.array(sprites, dtype=np.float32)
        else:
            self.sprite_data = np.empty((0, 3), dtype=np.float32)

    def check_collisions(self, player: 'Player') -> bool:
        """Check if any monster has successfully attacked the player.
        
        Args:
            player: The player instance.
            
        Returns:
            True if a collision is detected (Game Over), False otherwise.
        """
        for entity in self.entities:
            if isinstance(entity, Monster) and entity.triggered_game_over:
                return True
                
        return False

    def get_closest_monster_distance(self, player: 'Player') -> float:
        """Get the distance to the monster closest to the player.
        
        Args:
            player: The player instance.
            
        Returns:
            The distance to closest monster, or float('inf') if no monsters.
        """
        monsters = [e for e in self.entities if isinstance(e, Monster)]
        if not monsters:
            return float('inf')
        
        return min(m.get_distance_to_player(player) for m in monsters)
    
    @property
    def monsters(self) -> List[Monster]:
        """Get all active monsters. 
        
        Returns:
            List of Monster entities.
        """
        return [e for e in self.entities if isinstance(e, Monster)]
    
    @property
    def collectibles(self) -> List[Collectible]:
        """Get all active collectibles.
        
        Returns:
            List of Collectible entities.
        """
        return [e for e in self.entities if isinstance(e, Collectible)]
