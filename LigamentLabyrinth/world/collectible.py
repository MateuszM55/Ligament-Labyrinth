"""Collectible entity that player can pick up."""
from world.entity import Entity
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.player import Player


class Collectible(Entity):
    """Represents a collectible item in the game world that the player can pick up."""

    def __init__(self, x: float, y: float, texture_id: int = 11) -> None:
        """Initialize a collectible item.

        Args:
            x: World X position.
            y: World Y position.
            texture_id: ID of the texture to display.
        """
        super().__init__(x, y, texture_id)

        self.collected: bool = False

    def check_collection(self, player: 'Player', collection_distance: float) -> bool:
        """Check if the player is within range to collect this item.

        Args:
            player: The player instance.
            collection_distance: The maximum distance for collection.

        Returns:
            True if the item was newly collected, False otherwise.
        """
        if self.collected:
            return False

        dist_squared = self.get_distance_squared_to_player(player)

        if dist_squared < collection_distance * collection_distance:
            self.collected = True
            return True
        return False
