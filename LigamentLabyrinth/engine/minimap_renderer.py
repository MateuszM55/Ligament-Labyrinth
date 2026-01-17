import math
import pygame

from settings import settings


class MinimapRenderer:
    """Handles 2D minimap rendering and caches static elements."""

    def __init__(self) -> None:
        self.minimap_cache: pygame.Surface = None
        self.minimap_cache_valid: bool = False

    def invalidate_cache(self) -> None:
        self.minimap_cache_valid = False

    def render(self, screen: pygame.Surface, player, game_map) -> None:
        minimap_size = settings.minimap.size
        minimap_scale = minimap_size / max(game_map.width, game_map.height)
        minimap_x = screen.get_width() - minimap_size - settings.minimap.margin
        minimap_y = settings.minimap.margin

        # Generate static minimap cache if not valid
        if not self.minimap_cache_valid:
            self.minimap_cache = pygame.Surface((minimap_size, minimap_size))
            self.minimap_cache.fill(settings.colors.minimap_background)

            # Draw all static walls once
            for y in range(game_map.height):
                for x in range(game_map.width):
                    tile = game_map.grid[y][x]
                    if tile > 0:
                        tile_x = x * minimap_scale
                        tile_y = y * minimap_scale

                        # Look up wall color by tile id from settings; fall back to default
                        color = settings.colors.minimap_wall_colors.get(
                            tile, settings.colors.minimap_wall_default
                        )

                        pygame.draw.rect(
                            self.minimap_cache,
                            color,
                            (tile_x, tile_y, minimap_scale, minimap_scale)
                        )
            self.minimap_cache_valid = True

        # Blit cached static minimap
        screen.blit(self.minimap_cache, (minimap_x, minimap_y))

        # Draw dynamic elements (monsters)
        for i in range(game_map.sprite_data.shape[0]):
            sprite_x_world = game_map.sprite_data[i, 0]
            sprite_y_world = game_map.sprite_data[i, 1]
            monster_x = minimap_x + sprite_x_world * minimap_scale
            monster_y = minimap_y + sprite_y_world * minimap_scale
            pygame.draw.circle(
                screen,
                settings.colors.minimap_entity,
                (int(monster_x), int(monster_y)),
                3
            )

        player_x = minimap_x + player.x * minimap_scale
        player_y = minimap_y + player.y * minimap_scale
        pygame.draw.circle(
            screen,
            settings.colors.minimap_player,
            (int(player_x), int(player_y)),
            settings.minimap.player_dot_radius
        )

        rad = math.radians(player.rotation)
        end_x = player_x + math.cos(rad) * settings.minimap.direction_line_length
        end_y = player_y + math.sin(rad) * settings.minimap.direction_line_length
        pygame.draw.line(
            screen,
            settings.colors.minimap_player,
            (player_x, player_y),
            (end_x, end_y),
            settings.minimap.direction_line_width
        )
