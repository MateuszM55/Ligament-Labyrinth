import pygame
import sys
import math
from pygame.locals import *

class Player:
    def __init__(self, x, y, rotation=0.0):
        """Initialize player with position and rotation"""
        self.x = float(x)
        self.y = float(y)
        self.rotation = float(rotation)  # Rotation in degrees
        
        # Movement settings
        self.move_speed = 200.0  # pixels per second
        self.rotation_speed = 120.0  # degrees per second
        
    def set_position(self, x, y):
        """Set player position"""
        self.x = float(x)
        self.y = float(y)
        
    def set_rotation(self, rotation):
        """Set player rotation"""
        self.rotation = float(rotation)
        
    def move(self, dx, dy):
        """Move player by delta amounts"""
        self.x += float(dx)
        self.y += float(dy)
        
    def rotate(self, degrees):
        """Rotate player by degrees"""
        self.rotation += float(degrees)
        # Keep rotation in 0-360 range
        self.rotation = self.rotation % 360.0
        
    def move_forward(self, dt):
        """Move player forward in the direction they're facing"""
        rad = math.radians(self.rotation)
        self.x += math.cos(rad) * self.move_speed * dt
        self.y += math.sin(rad) * self.move_speed * dt
        
    def move_backward(self, dt):
        """Move player backward"""
        rad = math.radians(self.rotation)
        self.x -= math.cos(rad) * self.move_speed * dt
        self.y -= math.sin(rad) * self.move_speed * dt
        
    def strafe_left(self, dt):
        """Strafe left (perpendicular to facing direction)"""
        rad = math.radians(self.rotation - 90)
        self.x += math.cos(rad) * self.move_speed * dt
        self.y += math.sin(rad) * self.move_speed * dt
        
    def strafe_right(self, dt):
        """Strafe right (perpendicular to facing direction)"""
        rad = math.radians(self.rotation + 90)
        self.x += math.cos(rad) * self.move_speed * dt
        self.y += math.sin(rad) * self.move_speed * dt
        
    def look_left(self, dt):
        """Rotate player left"""
        self.rotate(-self.rotation_speed * dt)
        
    def look_right(self, dt):
        """Rotate player right"""
        self.rotate(self.rotation_speed * dt)

class Game:
    def __init__(self):
        pygame.init()
        
        # Display settings
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("PyDoom")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game state
        self.running = True
        self.paused = False
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        
        # Initialize player at center of screen
        self.player = Player(self.screen_width / 2, self.screen_height / 2, 0.0)
        
    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                self.handle_keydown(event)
            elif event.type == KEYUP:
                self.handle_keyup(event)
            elif event.type == MOUSEBUTTONDOWN:
                self.handle_mouse_click(event)
                
    def handle_keydown(self, event):
        """Handle key press events"""
        if event.key == K_ESCAPE:
            self.running = False
        elif event.key == K_p:
            self.paused = not self.paused
            
    def handle_keyup(self, event):
        """Handle key release events"""
        pass
        
    def handle_mouse_click(self, event):
        """Handle mouse click events"""
        pass
        
    def handle_player_input(self, dt):
        """Handle continuous keyboard input for player movement"""
        keys = pygame.key.get_pressed()
        
        # Movement: WASD
        if keys[K_w]:
            self.player.move_forward(dt)
        if keys[K_s]:
            self.player.move_backward(dt)
        if keys[K_a]:
            self.player.strafe_left(dt)
        if keys[K_d]:
            self.player.strafe_right(dt)
            
        # Rotation: Arrow keys
        if keys[K_LEFT]:
            self.player.look_left(dt)
        if keys[K_RIGHT]:
            self.player.look_right(dt)
        
    def update(self, dt):
        """Update game logic"""
        if not self.paused:
            self.handle_player_input(dt)
            
    def render(self):
        """Render everything to the screen"""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Draw game objects here
        
        # Update display
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        while self.running:
            # Delta time in seconds
            dt = self.clock.tick(self.fps) / 1000.0
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Render
            self.render()
            
        self.quit()
        
    def quit(self):
        """Clean up and quit"""
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
