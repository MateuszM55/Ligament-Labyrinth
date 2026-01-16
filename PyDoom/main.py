"""PyDoom - A raycasting game engine inspired by Doom."""

import sys
import math
import pygame
from pygame.locals import *

from settings import settings
from world.map import Map
from world.player import Player
from engine.assets import AssetManager
from engine.raycaster import Raycaster


class Game:
    """Main game class handling initialization, game loop, and events."""
    
    def __init__(self) -> None:
        """Initialize the game."""
        pygame.init()
        
        self.screen_width: int = settings.display.width
        self.screen_height: int = settings.display.height
        self.screen: pygame.Surface = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        pygame.display.set_caption(settings.display.title)
        
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.fps: int = settings.display.fps
        
        self.running: bool = True
        self.paused: bool = False
        
        self.show_fps: bool = settings.show_fps
        
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        
        self.game_map: Map = Map.load_from_file(settings.map.default_map_file)
        
        start_x, start_y = self.game_map.player_start
        self.player: Player = Player(start_x, start_y, 0.0)
        
        
        self.asset_manager: AssetManager = AssetManager()
        self.raycaster: Raycaster = Raycaster(
            self.screen_width, 
            self.screen_height,
            self.asset_manager
        )
        
        self.font: pygame.font.Font = pygame.font.Font(None, 36)

    def handle_events(self) -> None:
        """Handle all pygame events."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                self.handle_keydown(event)
            elif event.type == MOUSEMOTION:
                self.handle_mouse_motion(event)
                
    def handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle key press events.
        
        Args:
            event: The pygame key event
        """
        if event.key == K_ESCAPE:
            self.running = False
        elif event.key == K_p:
            self.paused = not self.paused
            if self.paused:
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
            else:
                pygame.event.set_grab(True)
                pygame.mouse.set_visible(False)
                pygame.mouse.get_rel()

    def handle_keyup(self, event: pygame.event.Event) -> None:
        """Handle key release events.
        
        Args:
            event: The pygame key event
        """
        pass
        
        
    def handle_mouse_motion(self, event: pygame.event.Event) -> None:
        """Handle mouse motion events.
        
        Args:
            event: The pygame mouse event
        """
        if not self.paused:
            dx, dy = pygame.mouse.get_rel()
            
            if dx != 0:
                self.player.rotate_from_mouse(dx)

    def handle_player_input(self, dt: float) -> None:
        """Process continuous keyboard input for smooth movement.
        
        Args:
            dt: Delta time in seconds
        """
        keys = pygame.key.get_pressed()
        
        total_dx = 0.0
        total_dy = 0.0
        
        is_sprinting = keys[K_LSHIFT] or keys[K_RSHIFT]
        self.player.is_sprinting = is_sprinting
        
        move_speed = settings.player.move_speed * dt
        if is_sprinting:
            move_speed *= settings.player.sprint_multiplier
        
        if keys[K_w]:
            total_dx += self.player._cos_cache * move_speed
            total_dy += self.player._sin_cache * move_speed
            
        if keys[K_s]:
            total_dx += -self.player._cos_cache * move_speed
            total_dy += -self.player._sin_cache * move_speed
            
        if keys[K_a]:
            total_dx += self.player._sin_cache * move_speed
            total_dy += -self.player._cos_cache * move_speed
            
        if keys[K_d]:
            total_dx += -self.player._sin_cache * move_speed
            total_dy += self.player._cos_cache * move_speed

        self.player.is_moving = (keys[K_w] or keys[K_s] or keys[K_a] or keys[K_d])

        if self.player.is_moving:
            current_speed = math.sqrt(total_dx**2 + total_dy**2)
            if current_speed > move_speed:
                scale = move_speed / current_speed
                total_dx *= scale
                total_dy *= scale

        if total_dx != 0 or total_dy != 0:
            self.player._move_with_collision(total_dx, total_dy, self.game_map)
           
    def update(self, dt: float) -> None:
        """Update game logic.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.paused:
            self.handle_player_input(dt)
            self.player.update_bobbing(dt)
            
    def render(self) -> None:
        """Render everything to the screen."""
        self.screen.fill(settings.colors.black)
        
        self.raycaster.render_3d_view_numba(self.screen, self.player, self.game_map)
        
        self.raycaster.render_minimap(self.screen, self.player, self.game_map)
        
        if self.show_fps:
            fps_text = self.font.render(
                f"FPS: {int(self.clock.get_fps())}", 
                True, 
                settings.colors.green
            )
            self.screen.blit(fps_text, (10, 10))
        
        pygame.display.flip()
        
    def run(self) -> None:
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.render()
            
        self.quit()
        
    def quit(self) -> None:
        """Clean up and quit."""
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
