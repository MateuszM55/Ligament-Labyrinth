"""Ligament Labyrinth - A raycasting horror game engine."""

import sys
import math
import pygame
from pygame.locals import *

from settings import settings
from world.map import Map
from world.player import Player
from engine.assets import AssetManager
from engine.raycaster import Raycaster
from engine.audio import AudioManager


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
        
        self.collectibles_obtained: int = 0
        self.all_collectibles_obtained: bool = False
        
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
        
        self.audio_manager: AudioManager = AudioManager()
        self.audio_manager.play_music()
        
        self.font: pygame.font.Font = pygame.font.Font(None, 36)
        
        # Dynamic glitch intensity (updated each frame based on monster proximity)
        self.current_glitch_intensity: float = 0.0

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
            self.set_paused(not self.paused)

    def set_paused(self, paused: bool) -> None:
        """Set pause state and manage mouse visibility/grab.
        
        Args:
            paused: True to pause, False to unpause
        """
        self.paused = paused
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
    
    def update(self, dt: float) -> None:
        """Update game logic.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.paused:
            keys = pygame.key.get_pressed()
            self.player.update(dt, keys, self.game_map)
            
            self.audio_manager.update_footsteps(dt, self.player.is_moving, self.player.is_sprinting)
            
            self.game_map.update(dt, self.player)
            
            self.audio_manager.update_all_monster_sounds(self.game_map.monsters, self.player)
            
            collected = self.game_map.check_collectible_collisions(self.player)
            if collected > 0:
                self.collectibles_obtained += collected
                
                if self.collectibles_obtained >= settings.collectible.total_count:
                    self.all_collectibles_obtained = True
                    for monster in self.game_map.monsters:
                        monster.speed_multiplier = settings.monster.speed_boost_multiplier
            
            self.current_glitch_intensity = Raycaster.calculate_glitch_intensity(self.game_map, self.player)
            
            if self.game_map.check_monster_collisions(self.player):
                self.running = False
            
    def render(self) -> None:
        """Render everything to the screen."""
        self.screen.fill(settings.colors.black)
        
        self.raycaster.render(self.screen, self.player, self.game_map, self.current_glitch_intensity)
        
        if settings.minimap.enabled:
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
