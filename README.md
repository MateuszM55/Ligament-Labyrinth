# Ligament Labyrinth

A raycasting game engine with horror elements, built with Python and Pygame.

## Description

Ligament Labyrinth is a 3D raycasting engine that creates a first-person perspective horror game. The engine features:

- Real-time raycasting rendering with textured walls, floors, and ceilings
- Numba-optimized rendering for high performance
- Dynamic lighting and visual effects
- Monster AI with proximity-based behaviors
- Collectible system
- 3D positional audio
- Minimap overlay
- Fully configurable settings

## Installation

### Requirements
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository
2. Install dependencies: pip install -r requirements.txt

## Controls

- W/A/S/D: Move forward/left/backward/right
- Mouse: Look around
- Shift: Sprint
- P: Pause game
- ESC: Quit game

## Project Structure

The project follows Python best practices with clear module separation:
- engine/ - Core rendering and audio engine
- world/ - Game world and entities
- textures/ - Texture assets
- docs/ - Project documentation
- tests/ - Unit and integration tests

## Running Build
python build.py

## Configure setttings
try playing around with settings.py or config.json

### Running Tests
python -m pytest tests/ -v 
or
python run_tests.py

## Technical Details

- Raycasting: 3D rendering without true 3D graphics
- Numba JIT: Performance-critical code compiled to machine code
- Pygame: Window management, input, and audio
- NumPy: Efficient array operations

## License

This project is for educational purposes.

## Credits

Textures and audio assets sourced from free online resources:
Monster Sprites:
	Artist: BTL Games
	Source: https://btl-games.itch.io/
	License: CC0 1.0 Universal

Textures:
	Artist: Screaming Brain Studios
	Source: https://screamingbrainstudios.itch.io/
	License: CC0 1.0 Universal

Music:
	Composer: Trey Travis
	Source: https://trey-travis.itch.io/
	License: CC0 1.0 Universal