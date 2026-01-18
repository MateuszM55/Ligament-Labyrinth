
import os
import sys

# Support for PyInstaller and Numba
if getattr(sys, 'frozen', False):
    # Set Numba cache to a user folder so it can write its compiled code
    os.environ['NUMBA_CACHE_DIR'] = os.path.join(os.path.expanduser('~'), '.numba_cache')
    # Change directory to the EXE location so it finds mapData and assets
    os.chdir(sys._MEIPASS)

"""Ligament Labyrinth - A raycasting horror game engine."""

import sys
import math
import pygame
from pygame.locals import *

from settings import settings
from world.map import Map
from world.player import Player
from world.entity_manager import EntityManager
from engine.assets import AssetManager
from engine.raycaster import Raycaster
from engine.audio import AudioManager
from engine.minimap_renderer import MinimapRenderer


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
        
        # Load the raw data
        self.game_map, m_data, c_data = Map.load_from_file(settings.map.default_map_file)
        
        # Initialize the entity manager
        self.entity_manager: EntityManager = EntityManager()
        self.entity_manager.load_entities(m_data, c_data)
        
        start_x, start_y = self.game_map.player_start
        self.player: Player = Player(start_x, start_y, 0.0)
        
        
        self.asset_manager: AssetManager = AssetManager()
        self.raycaster: Raycaster = Raycaster(
            self.screen_width, 
            self.screen_height,
            self.asset_manager
        )

        # Minimap renderer (separate from Raycaster)
        self.minimap_renderer: MinimapRenderer = MinimapRenderer()
        
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
        """Handle individual key press events.
        
        Args:
            event: The pygame key event.
        """
        if event.key == K_ESCAPE:
            self.running = False
        elif event.key == K_p:
            self.set_paused(not self.paused)

    def set_paused(self, paused: bool) -> None:
        """Update the game's pause state and toggle hardware input focus.
        
        Args:
            paused: True to pause logic; False to resume.
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
        """Update game logic including physics, AI, and collision.
        
        Args:
            dt: Delta time in seconds since the last frame.
        """
        if not self.paused:
            keys = pygame.key.get_pressed()
            self.player.update(dt, keys, self.game_map)
            
            self.audio_manager.update_footsteps(dt, self.player.is_moving, self.player.is_sprinting)
            
            self.entity_manager.update(dt, self.player)
            
            self.audio_manager.update_all_monster_sounds(self.entity_manager.monsters, self.player)
            
            collected = self.entity_manager.check_collections(self.player)
            if collected > 0:
                self.collectibles_obtained += collected
                
                if self.collectibles_obtained >= settings.collectible.total_count:
                    self.all_collectibles_obtained = True
                    for monster in self.entity_manager.monsters:
                        monster.speed_multiplier = settings.monster.speed_boost_multiplier
            
            # Calculate glitch effect based on how close the monster is
            self.current_glitch_intensity = Raycaster.calculate_glitch_intensity(self.entity_manager, self.player)
            
            # End game if any monster touches the player
            if self.entity_manager.check_collisions(self.player):
                self.running = False
            
    def render(self) -> None:
        """Clear the screen and render the 3D world, HUD, and UI elements."""
        self.screen.fill(settings.colors.black)
        
        # Synchronization hack: ensure map has newest sprite locations
        self.game_map.sprite_data = self.entity_manager.sprite_data
        
        self.raycaster.render(self.screen, self.player, self.game_map, self.current_glitch_intensity)
        
        if settings.minimap.enabled:
            self.minimap_renderer.render(self.screen, self.player, self.game_map)
        
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
