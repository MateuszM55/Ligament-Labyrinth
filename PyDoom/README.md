# PyDoom

A raycasting game engine inspired by Doom, built with Python and Pygame.

## Description

PyDoom is a 3D raycasting engine that creates a first-person perspective game similar to classic Doom. The engine features:

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
3. Run the game: python main.py

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

## Development

### Running Tests
python -m pytest tests/ -v

### Documentation
See the docs/ folder for architecture and API reference.

## Technical Details

- Raycasting: 3D rendering without true 3D graphics
- Numba JIT: Performance-critical code compiled to machine code
- Pygame: Window management, input, and audio
- NumPy: Efficient array operations

## License

This project is for educational purposes.

## Credits

Inspired by the classic Doom engine and raycasting techniques.
