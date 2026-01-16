import random

# CONFIGURATION
WIDTH = 128
HEIGHT = 128

# TILE DEFINITIONS
AIR = 0
BORDER = 1
WALL_STONE = 2
WALL_CRACKED = 3
WALL_FLESH = 4
WALL_BONE = 5
BARS = 6
DOOR = 9
PLAYER = 'P'
MONSTER = 'M'

def generate_horror_map():
    # Initialize grid with all Stone Walls (2) to carve out later, 
    # or Air (0) to build into. Let's fill with 0 (Air) first.
    grid = [[AIR for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # --- 1. THE OUTER SHELL ---
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if x == 0 or x == WIDTH - 1 or y == 0 or y == HEIGHT - 1:
                grid[y][x] = BORDER

    # --- 2. THE SOUTHERN CASTLE (Structured, Logic) ---
    # Create rooms and corridors for the bottom half (y > 64)
    for y in range(64, HEIGHT - 1):
        for x in range(1, WIDTH - 1):
            # Create a main corridor down the middle
            if 60 < x < 68: 
                grid[y][x] = AIR
            
            # Create side rooms (Standard Castle Layout)
            elif (y % 16 in [0, 1, 15]) and x % 16 != 0:
                grid[y][x] = WALL_STONE # Room walls
            
            # Add random columns
            elif x % 8 == 0 and y % 8 == 0:
                grid[y][x] = WALL_STONE

    # --- 3. THE TRANSITION (Middle) ---
    # Randomly replace Stone with Cracked Stone or Flesh
    for y in range(40, 80):
        for x in range(1, WIDTH - 1):
            if grid[y][x] == WALL_STONE:
                roll = random.random()
                if roll < 0.3: grid[y][x] = WALL_CRACKED
                elif roll < 0.4: grid[y][x] = WALL_FLESH

    # --- 4. THE GUT (North - Organic/Chaotic) ---
    # We use a cellular automata style or noise approach for organic caves
    for y in range(1, 60):
        for x in range(1, WIDTH - 1):
            # Noise function for organic shapes
            noise = (x * 0.1) + (y * 0.2) + random.uniform(-2, 2)
            dist_from_center = abs(x - 64)
            
            if dist_from_center < (y * 0.5) + 10: # Funnel shape
                if random.random() > 0.8:
                    grid[y][x] = WALL_BONE # Scattered bones
                else:
                    grid[y][x] = AIR
            else:
                grid[y][x] = WALL_FLESH # The thick flesh walls

    # --- 5. PLACEMENT OF KEY ELEMENTS ---
    
    # Player Start (Bottom Center)
    grid[HEIGHT-5][64] = PLAYER
    
    # The Monster/Objective (Top Center - The Heart)
    # Clear a circle
    cy, cx = 15, 64
    for y in range(cy-10, cy+10):
        for x in range(cx-10, cx+10):
            if (x-cx)**2 + (y-cy)**2 < 100:
                grid[y][x] = AIR
            if (x-cx)**2 + (y-cy)**2 < 110 and (x-cx)**2 + (y-cy)**2 >= 100:
                grid[y][x] = WALL_BONE # Ring of bone around the boss
                
    grid[cy][cx] = MONSTER

    # --- 6. CLEANUP & DOORS ---
    # Add doors to rooms in the south
    for y in range(64, HEIGHT - 2):
        for x in range(1, WIDTH - 1):
            # If we are strictly between a wall and air, maybe place a door
            if grid[y][x] == AIR:
                if grid[y][x-1] == WALL_STONE and grid[y][x+1] == WALL_STONE:
                     if random.random() < 0.1: grid[y][x] = DOOR

    return grid

def save_map(grid, filename="castle_map.txt"):
    with open(filename, "w") as f:
        for row in grid:
            line = "".join(str(cell) for cell in row)
            f.write(line + "\n")
    print(f"Map saved to {filename}")

# Generate and Save
map_data = generate_horror_map()
save_map(map_data)