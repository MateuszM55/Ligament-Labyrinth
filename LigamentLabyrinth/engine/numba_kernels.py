"""Numba-optimized raycasting functions for high-performance rendering."""
"""AI generated code"""

import numpy as np
import numba
from numba import types
import math

# -----------------------------------------------------------------------------
# What is Raycasting?
# Imagine you are standing in a room with your eyes closed. To figure out the shape
# of the room, you send out laser pointers (rays) in a fan shape in front of you.
# When a laser hits a wall, you measure the distance.
# 
# 1. Short distance = Wall is close = Draw a tall wall strip.
# 2. Long distance = Wall is far = Draw a short wall strip.
# 
# This file handles the heavy math to do this thousands of times per second.
# -----------------------------------------------------------------------------



# We use @numba.njit to compile this Python code into C-speed machine code.
# Without this, the game would run at 1 frame per second.
@numba.njit(
    types.Tuple((types.float64, types.int64, types.float64, types.float64, types.int64))(
        types.float64, types.float64, types.float64,
        types.int32[:, :], types.int64, types.int64, types.float64
    ),
    fastmath=True,
    cache=True
)
def cast_ray_numba(
    player_x: float,
    player_y: float,
    angle_rad: float,
    map_grid: np.ndarray,
    map_width: int,
    map_height: int,
    max_depth: float
) -> tuple:
    """
    Casts a SINGLE ray from the player to find the nearest wall.
    
    It uses an algorithm called DDA (Digital Differential Analysis).
    Instead of checking every 0.1 steps (which is slow), DDA checks 
    intersection points on the grid lines. It jumps from grid line to grid line.
    """
    
    # 1. Calculate Ray Direction
    # We turn the angle (radians) into X and Y vector components.
    ray_dx = math.cos(angle_rad)
    ray_dy = math.sin(angle_rad)
    
    # Current position on the map
    x = player_x
    y = player_y
    
    # Which grid square are we in? (e.g., Row 5, Column 3)
    map_x = int(x)
    map_y = int(y)
    
    # 2. Calculate Delta Distances
    # "If I move 1 unit along the ray, how many X units or Y units did I cross?"
    # This helps us scale the steps to hit the next grid line perfectly.
    if ray_dx != 0:
        delta_dist_x = abs(1.0 / ray_dx)
    else:
        delta_dist_x = 1e30 # Avoid division by zero (infinity)
        
    if ray_dy != 0:
        delta_dist_y = abs(1.0 / ray_dy)
    else:
        delta_dist_y = 1e30

    # 3. Calculate Step and Initial Side Distances
    # We need to decide if we are stepping Left (-1) or Right (+1), Up or Down.
    if ray_dx < 0:
        step_x = -1
        # Distance to the first grid line to our left
        side_dist_x = (x - map_x) * delta_dist_x
    else:
        step_x = 1
        # Distance to the first grid line to our right
        side_dist_x = (map_x + 1.0 - x) * delta_dist_x
        
    if ray_dy < 0:
        step_y = -1
        # Distance to the first grid line above us
        side_dist_y = (y - map_y) * delta_dist_y
    else:
        step_y = 1
        # Distance to the first grid line below us
        side_dist_y = (map_y + 1.0 - y) * delta_dist_y
    
    # 

    # 4. Perform DDA (The Search Loop)
    hit = False
    hit_val = 0
    side = 0 # 0 = hit a vertical wall, 1 = hit a horizontal wall (used for shading)
    max_iterations = 50 # Safety limit: don't look further than 50 blocks
    iterations = 0
    
    while not hit and iterations < max_iterations:
        # Jump to whichever grid line is closer (X or Y)
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_x += step_x
            side = 0 # We moved horizontally, so we hit a vertical line
        else:
            side_dist_y += delta_dist_y
            map_y += step_y
            side = 1 # We moved vertically, so we hit a horizontal line
        
        iterations += 1
        
        # Check if ray went out of bounds (outside the map)
        if map_x < 0 or map_x >= map_width or map_y < 0 or map_y >= map_height:
            hit = True
            hit_val = 1 # Treat out-of-bounds as a solid wall
        else:
            # Check the map grid: Is there a wall here?
            tile = map_grid[map_y, map_x]
            if tile > 0:
                hit = True
                hit_val = tile
    
    # 5. Calculate Final Distance
    # This math corrects the "Fish-eye" effect. We want the perpendicular distance
    # to the camera plane, not the Euclidean distance to the player point.
    if side == 0:
        if ray_dx != 0:
            distance = (map_x - x + (1 - step_x) / 2) / ray_dx
        else:
            distance = max_depth
    else:
        if ray_dy != 0:
            distance = (map_y - y + (1 - step_y) / 2) / ray_dy
        else:
            distance = max_depth
    
    distance = abs(distance)
    
    # Cap the distance to avoid rendering errors at infinite depth
    if distance > max_depth or distance < 0:
        distance = max_depth
        
    return distance, side, ray_dx, ray_dy, hit_val


@numba.njit(
    types.void(
        types.uint8[:, :, :],      # buffer_pixels
        types.uint8[:, :, :, :],   # floor_arrays
        types.uint8[:, :, :, :],   # ceiling_arrays
        types.int32[:, :],         # floor_grid
        types.int32[:, :],         # ceiling_grid
        types.int64,               # map_width
        types.int64,               # map_height
        types.int64,               # floor_width
        types.int64,               # floor_height
        types.int64,               # floor_scale
        types.int64,               # screen_width
        types.int64,               # screen_height
        types.float64,             # player_x
        types.float64,             # player_y
        types.float64,             # player_rotation_rad
        types.float64,             # fov_rad
        types.float64,             # bob_offset_y
        types.float64,             # wall_height_factor
        types.boolean,             # enable_inverse_square
        types.float64,             # light_intensity
        types.float64,             # ambient_light
        types.boolean,             # enable_vignette
        types.float64,             # vignette_intensity
        types.float64,             # vignette_radius
        types.float64              # glitch_intensity
    ),
    fastmath=True,
    parallel=True, # Uses multiple CPU cores
    cache=True
)
def render_floor_ceiling_numba(
    buffer_pixels: np.ndarray,
    floor_arrays: np.ndarray,
    ceiling_arrays: np.ndarray,
    floor_grid: np.ndarray,
    ceiling_grid: np.ndarray,
    map_width: int,
    map_height: int,
    floor_width: int,
    floor_height: int,
    floor_scale: int,
    screen_width: int,
    screen_height: int,
    player_x: float,
    player_y: float,
    player_rotation_rad: float,
    fov_rad: float,
    bob_offset_y: float,
    wall_height_factor: float,
    enable_inverse_square: bool,
    light_intensity: float,
    ambient_light: float,
    enable_vignette: bool,
    vignette_intensity: float,
    vignette_radius: float,
    glitch_intensity: float
) -> None:
    """
    Renders the floor and ceiling.
    
    This is trickier than walls. We iterate over every horizontal ROW of the screen.
    For a specific row on screen, the distance to the floor in the 3D world is constant.
    
    Concept:
    Screen Top ----------------- (Ceiling, infinite distance)
                 ...
    Horizon    ----------------- (Horizon line, infinite distance)
                 ...
    Screen Bot ----------------- (Floor at your feet, distance 0)
    """
    
    # 1. Setup Frustum (The "Camera Triangle")
    half_fov_rad = fov_rad / 2.0
    tan_half_fov = math.tan(half_fov_rad)
    aspect_ratio = screen_width / screen_height
    screen_half = screen_height / 2.0 + bob_offset_y
    
    # Get texture dimensions so we know how to map pixels
    num_floor_textures = floor_arrays.shape[0]
    num_ceiling_textures = ceiling_arrays.shape[0]
    floor_tex_width = floor_arrays.shape[1]
    floor_tex_height = floor_arrays.shape[2]
    ceiling_tex_width = ceiling_arrays.shape[1]
    ceiling_tex_height = ceiling_arrays.shape[2]
    
    # Bitwise mask is a fast way to wrap textures (e.g. coord 65 becomes 1 in a 64-size texture)
    floor_tex_mask = floor_tex_width - 1
    ceiling_tex_mask = ceiling_tex_width - 1
    
    # Pre-calculate player direction vectors
    player_cos = math.cos(player_rotation_rad)
    player_sin = math.sin(player_rotation_rad)
    
    # Calculate the left and right edges of the camera plane
    plane_x = -player_sin * tan_half_fov * aspect_ratio
    plane_y = player_cos * tan_half_fov * aspect_ratio
    
    # Camera height (Z)
    pos_z = 0.5 * screen_height * wall_height_factor
    epsilon = 1.0
    
    # Constants for the "Vignette" (dark corners effect)
    vignette_radius_squared = vignette_radius * vignette_radius
    vignette_denominator = 1.414 - vignette_radius + 0.001
    
    # 2. Iterate over Rows (Parallelized for speed)
    # y represents the vertical coordinate on the screen
    for y in numba.prange(floor_height):
        screen_y = y * floor_scale
        
        # p is the position relative to the center of the screen (horizon)
        p = screen_y - screen_half
        
        # Avoid division by zero at the exact horizon line
        if abs(p) < epsilon:
            p = epsilon if p >= 0 else -epsilon
        
        # MAGIC MATH: Calculate how far away this screen row is in the 3D world.
        # Pixels closer to the center of the screen are far away (high row_distance).
        # Pixels at the bottom of the screen are close (low row_distance).
        row_distance = pos_z / abs(p)
        
        # Calculate lighting factor for this whole row based on distance
        if enable_inverse_square:
            distance_factor = light_intensity / (row_distance * row_distance + 0.1)
            distance_factor = max(ambient_light, min(1.0, distance_factor))
        else:
            distance_factor = 1.0
        
        # 3. Iterate over Columns (pixels in the row)
        for x in range(floor_width):
            screen_x = x * floor_scale
            
            # Map screen X (-1 to 1) to world coordinates
            screen_x_norm = (2.0 * x / floor_width) - 1.0
            ray_dir_x = player_cos + plane_x * screen_x_norm
            ray_dir_y = player_sin + plane_y * screen_x_norm
            
            # This is the exact spot on the floor map this pixel represents
            world_x = player_x + ray_dir_x * row_distance
            world_y = player_y + ray_dir_y * row_distance
            
            # --- VIGNETTE & GLITCH EFFECTS ---
            vignette_multiplier = 1.0
            if enable_vignette:
                # Calculate distance from center of screen for darkness
                x_norm = (screen_x - screen_width / 2.0) / (screen_width / 2.0)
                y_norm = (screen_y - screen_height / 2.0) / (screen_height / 2.0)
                screen_dist_squared = x_norm * x_norm + y_norm * y_norm
                
                if screen_dist_squared > vignette_radius_squared:
                    screen_dist = math.sqrt(screen_dist_squared)
                    vignette_falloff = (screen_dist - vignette_radius) / vignette_denominator
                    vignette_falloff = min(1.0, vignette_falloff)
                    vignette_multiplier = 1.0 - (vignette_falloff * vignette_intensity)
            
            base_lighting = distance_factor * vignette_multiplier
            
            # The "Glitch" makes colors weird by multiplying them negatively
            corruption_multiplier = 1.0 - glitch_intensity
            final_lighting = base_lighting * corruption_multiplier
            
            # --- TEXTURE MAPPING ---
            map_x = int(world_x)
            map_y = int(world_y)
            
            # Clamp to map boundaries so we don't crash reading outside the array
            if map_x < 0: map_x = 0
            if map_x >= map_width: map_x = map_width - 1
            if map_y < 0: map_y = 0
            if map_y >= map_height: map_y = map_height - 1
            
            # Decide if we are drawing Floor (bottom half) or Ceiling (top half)
            if p > epsilon:
                # --- FLOOR ---
                floor_tex_id = floor_grid[map_y, map_x]
                if floor_tex_id >= num_floor_textures: floor_tex_id = 0
                
                # Get the pixel from the texture image
                tex_x = int(world_x * floor_tex_width) & floor_tex_mask
                tex_y = int(world_y * floor_tex_height) & floor_tex_mask
                
                # Apply color and lighting
                # The % 256 is vital for the glitch effect to "wrap around" colors
                r = int(floor_arrays[floor_tex_id, tex_x, tex_y, 0] * final_lighting) % 256
                g = int(floor_arrays[floor_tex_id, tex_x, tex_y, 1] * final_lighting) % 256
                b = int(floor_arrays[floor_tex_id, tex_x, tex_y, 2] * final_lighting) % 256
                
                # Fix negative numbers if glitch caused them
                r = (r + 256) % 256
                g = (g + 256) % 256
                b = (b + 256) % 256
                
                buffer_pixels[x, y, 0] = r
                buffer_pixels[x, y, 1] = g
                buffer_pixels[x, y, 2] = b
            
            elif p < -epsilon:
                # --- CEILING ---
                # (Logic is identical to floor, just using ceiling arrays)
                ceiling_tex_id = ceiling_grid[map_y, map_x]
                if ceiling_tex_id >= num_ceiling_textures: ceiling_tex_id = 0
                
                tex_x = int(world_x * ceiling_tex_width) & ceiling_tex_mask
                tex_y = int(world_y * ceiling_tex_height) & ceiling_tex_mask
                
                r = int(ceiling_arrays[ceiling_tex_id, tex_x, tex_y, 0] * final_lighting) % 256
                g = int(ceiling_arrays[ceiling_tex_id, tex_x, tex_y, 1] * final_lighting) % 256
                b = int(ceiling_arrays[ceiling_tex_id, tex_x, tex_y, 2] * final_lighting) % 256
                
                r = (r + 256) % 256
                g = (g + 256) % 256
                b = (b + 256) % 256
                
                buffer_pixels[x, y, 0] = r
                buffer_pixels[x, y, 1] = g
                buffer_pixels[x, y, 2] = b


@numba.njit(
types.void(
        types.uint8[:, :, :],      # screen_pixels
        types.uint8[:, :, :, :],   # texture_arrays
        types.int32[:],            # texture_map
        types.float64,             # player_x
        types.float64,             # player_y
        types.float64,             # player_rotation_deg
        types.int32[:, :],         # map_grid
        types.int64,               # map_width
        types.int64,               # map_height
        types.int64,               # screen_width
        types.int64,               # screen_height
        types.float64,             # fov
        types.float64,             # max_depth
        types.int64,               # num_rays
        types.float64,             # ray_width
        types.float64,             # bob_offset_y
        types.float64,             # wall_height_factor
        types.boolean,             # enable_inverse_square
        types.float64,             # light_intensity
        types.float64,             # ambient_light
        types.boolean,             # enable_vignette
        types.float64,             # vignette_intensity
        types.float64,             # vignette_radius
        types.float64,             # glitch_intensity
        types.float32[:]           # depth_buffer (passed in, modified in-place)
    ),
    fastmath=True,
    parallel=True,
    cache=True
)
def render_walls_numba(
    screen_pixels: np.ndarray,
    texture_arrays: np.ndarray,
    texture_map: np.ndarray,
    player_x: float,
    player_y: float,
    player_rotation_deg: float,
    map_grid: np.ndarray,
    map_width: int,
    map_height: int,
    screen_width: int,
    screen_height: int,
    fov: float,
    max_depth: float,
    num_rays: int,
    ray_width: float,
    bob_offset_y: float,
    wall_height_factor: float,
    enable_inverse_square: bool,
    light_intensity: float,
    ambient_light: float,
    enable_vignette: bool,
    vignette_intensity: float,
    vignette_radius: float,
    glitch_intensity: float,
    depth_buffer: np.ndarray
) -> None:
    """
    Renders the vertical wall strips.
    
    This is the core of the 3D effect. We sweep across the screen from left to right.
    For every vertical column of pixels:
    1. Cast a ray at that angle.
    2. See how far away the wall is.
    3. Draw a vertical line of pixels.
       - Close wall = Long line (looks big).
       - Far wall = Short line (looks small).
    """
    
    half_fov_rad = math.radians(fov / 2.0)
    tan_half_fov = math.tan(half_fov_rad)
    aspect_ratio = screen_width / screen_height
    screen_half = screen_height / 2.0 + bob_offset_y
    
    tex_width = texture_arrays.shape[1]
    tex_height = texture_arrays.shape[2]
    tex_mask = tex_width - 1
    
    # Precompute vignette constants
    vignette_radius_squared = vignette_radius * vignette_radius
    vignette_denominator = 1.414 - vignette_radius + 0.001 
    
    # Clear the depth buffer (reset distance to infinity for new frame)
    # The depth buffer remembers how far away the wall is at every pixel column.
    # We need this later so sprites don't draw ON TOP of walls they should be behind.
    depth_buffer[:] = max_depth
    
    # 

    # LOOP: Process every vertical strip (ray) of the screen
    for ray_index in numba.prange(num_rays):
        
        # 1. Calculate the Ray Angle
        # Map ray_index (0 to screen_width) to -1 to 1
        screen_x = (2.0 * ray_index) / num_rays - 1.0
        
        # Calculate angle offset from the player's center view
        angle_offset_rad = math.atan(screen_x * tan_half_fov * aspect_ratio)
        angle_offset_deg = math.degrees(angle_offset_rad)
        
        ray_angle_deg = player_rotation_deg + angle_offset_deg
        ray_angle_rad = math.radians(ray_angle_deg)
        
        # 2. Cast the Ray (Find the wall)
        distance, side, ray_dx, ray_dy, hit_val = cast_ray_numba(
            player_x, player_y, ray_angle_rad,
            map_grid, map_width, map_height, max_depth
        )
        
        # 3. Fix Fish-Eye Effect
        # If we use raw distance, straight walls look curved. We must multiply
        # by cos(angle_offset) to flatten the view.
        raw_distance = distance
        distance *= math.cos(angle_offset_rad)
        
        if distance < 0.01: distance = 0.01 # Prevent divide by zero
        
        # 4. Calculate Wall Dimensions
        # Height is inversely proportional to distance (1/distance)
        wall_height = int((screen_height * wall_height_factor) / distance)
        
        # Find where the wall starts on screen (centered vertically)
        wall_top = int(screen_half - (wall_height / 2.0))
        
        # 5. Calculate Texture X Coordinate
        # We need to know exactly WHERE on the wall block we hit (0.0 to 1.0)
        # to know which column of the texture image to draw.
        if side == 0:
            wall_x = player_y + raw_distance * ray_dy
        else:
            wall_x = player_x + raw_distance * ray_dx
        
        wall_x -= math.floor(wall_x) # Keep only the decimal part
        tex_x = int(wall_x * tex_width)
        
        # Flip texture if hitting the "back" side of a block so it doesn't look mirrored
        if side == 0 and ray_dx > 0:
            tex_x = tex_width - tex_x - 1
        if side == 1 and ray_dy < 0:
            tex_x = tex_width - tex_x - 1
        
        tex_x = max(0, min(tex_x, tex_width - 1))
        
        # Look up which texture image to use
        texture_idx = 0
        if hit_val < len(texture_map):
            texture_idx = int(texture_map[hit_val])
        
        # 6. Lighting Calculation
        lighting_multiplier = 1.0
        if enable_inverse_square:
            distance_factor = light_intensity / (distance * distance + 0.1)
            distance_factor = max(ambient_light, min(1.0, distance_factor))
        else:
            distance_factor = 1.0
        
        lighting_multiplier *= distance_factor
        
        # Determine which screen columns this ray covers (usually just 1, unless low res)
        x_start = int(ray_index * ray_width)
        x_end = int((ray_index + 1) * ray_width)
        x_end = min(x_end, screen_width)
        
        # 7. Draw the Wall Strip
        if wall_height > 0 and wall_height < 8000:
            for screen_x_pos in range(x_start, x_end):
                
                # Write to Depth Buffer (Vital for Sprites later!)
                depth_buffer[screen_x_pos] = distance
                
                # Iterate down the vertical line
                for screen_y_pos in range(max(0, wall_top), min(screen_height, wall_top + wall_height)):
                    
                    # --- Vignette Calculation ---
                    vignette_multiplier = 1.0
                    if enable_vignette:
                        x_norm = (screen_x_pos - screen_width / 2.0) / (screen_width / 2.0)
                        y_norm = (screen_y_pos - screen_height / 2.0) / (screen_height / 2.0)
                        screen_dist_squared = x_norm * x_norm + y_norm * y_norm
                        
                        if screen_dist_squared > vignette_radius_squared:
                            screen_dist = math.sqrt(screen_dist_squared)
                            vignette_falloff = (screen_dist - vignette_radius) / vignette_denominator
                            vignette_falloff = min(1.0, vignette_falloff)
                            vignette_multiplier = 1.0 - (vignette_falloff * vignette_intensity)
                    
                    # Combine Lighting + Glitch
                    base_lighting = lighting_multiplier * vignette_multiplier
                    corruption_multiplier = 1.0 - glitch_intensity
                    final_lighting = base_lighting * corruption_multiplier
                    
                    # --- Texture Sampling ---
                    # Map screen Y to Texture Y
                    y_ratio = (screen_y_pos - wall_top) / wall_height
                    tex_y = int(y_ratio * tex_height)
                    tex_y = max(0, min(tex_y, tex_height - 1))
                    
                    # Get RGB colors
                    r = texture_arrays[texture_idx, tex_x, tex_y, 0]
                    g = texture_arrays[texture_idx, tex_x, tex_y, 1]
                    b = texture_arrays[texture_idx, tex_x, tex_y, 2]
                    
                    # Apply final lighting and write to screen buffer
                    r_lit = int(r * final_lighting) % 256
                    g_lit = int(g * final_lighting) % 256
                    b_lit = int(b * final_lighting) % 256
                    
                    r_lit = (r_lit + 256) % 256
                    g_lit = (g_lit + 256) % 256
                    b_lit = (b_lit + 256) % 256
                    
                    screen_pixels[screen_x_pos, screen_y_pos, 0] = r_lit
                    screen_pixels[screen_x_pos, screen_y_pos, 1] = g_lit
                    screen_pixels[screen_x_pos, screen_y_pos, 2] = b_lit


@numba.njit(
    types.float32[:, :](
        types.float32[:, :],       # sprite_data
        types.float64,             # player_x
        types.float64,             # player_y
        types.float64,             # player_rotation_deg
        types.float64,             # fov
        types.int64,               # screen_width
        types.int64,               # screen_height
        types.float64,             # max_depth
        types.float64,             # wall_height_factor
        types.float64,             # bob_offset_y
        types.boolean,             # enable_inverse_square
        types.float64,             # light_intensity
        types.float64,             # ambient_light
        types.float32[:],          # depth_buffer
        types.UniTuple(types.int64, 3)  # collectible_texture_ids
    ),
    fastmath=True,
    cache=True
)
def process_sprites_numba(
    sprite_data: np.ndarray,
    player_x: float,
    player_y: float,
    player_rotation_deg: float,
    fov: float,
    screen_width: int,
    screen_height: int,
    max_depth: float,
    wall_height_factor: float,
    bob_offset_y: float,
    enable_inverse_square: bool,
    light_intensity: float,
    ambient_light: float,
    depth_buffer: np.ndarray,
    collectible_texture_ids: tuple
) -> np.ndarray:
    """
    Calculates where to draw 2D sprites (items, monsters) on the screen.
    
    This technique is called 'Billboarding'. The sprite is a 2D flat image,
    but we calculate its size and position so it *looks* like it's standing
    in the 3D world.
    
    
    """
    
    num_sprites = sprite_data.shape[0]
    if num_sprites == 0:
        return np.empty((0, 6), dtype=np.float32)
    
    # Pre-calc trig
    player_rad = math.radians(player_rotation_deg)
    player_cos = math.cos(player_rad)
    player_sin = math.sin(player_rad)
    
    half_fov = math.radians(fov / 2.0)
    tan_half_fov = math.tan(half_fov)
    aspect_ratio = screen_width / screen_height
    
    # We create a temporary array to hold valid sprites.
    # We cannot use Python lists because Numba doesn't support them efficiently.
    visible_sprites_array = np.empty((num_sprites, 6), dtype=np.float32)
    count = 0
    
    for i in range(num_sprites):
        sprite_x_world = sprite_data[i, 0]
        sprite_y_world = sprite_data[i, 1]
        texture_id = sprite_data[i, 2]
        
        # 1. Translate sprite position relative to player
        dx = sprite_x_world - player_x
        dy = sprite_y_world - player_y
        
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 0.1 or distance > max_depth:
            continue
        
        # 2. Transform Sprite to "Camera Space" (Matrix rotation)
        # sprite_y here is essentially "depth" (distance in front of camera)
        # sprite_x here is horizontal position relative to camera center
        sprite_y = dx * player_cos + dy * player_sin
        sprite_x = dy * player_cos - dx * player_sin
        
        # If sprite is behind the player (negative depth), don't draw
        if sprite_y <= 0.1:
            continue
        
        # 3. Project to Screen Space
        # Calculate where on the 2D screen this 3D point lands
        projection_plane_x = (sprite_x / sprite_y) / (tan_half_fov * aspect_ratio)
        screen_x = (screen_width / 2.0) * (1.0 + projection_plane_x)
        
        # Calculate scale (size) based on distance
        sprite_height = (screen_height / sprite_y) * wall_height_factor
        sprite_width = sprite_height
        
        # Check if off-screen
        if screen_x + sprite_width / 2 < 0 or screen_x - sprite_width / 2 > screen_width:
            continue
        
        # 4. Occlusion Culling (Hiding behind walls)
        # We compare the sprite's distance to the 'depth_buffer' we filled in render_walls.
        is_collectible = False
        for coll_tex_id in collectible_texture_ids:
            if texture_id == coll_tex_id:
                is_collectible = True
                break
        
        # Logic: If the wall at this pixel is CLOSER than the sprite, 
        # the sprite is hidden.
        if is_collectible:
            sprite_left = int(max(0, screen_x - sprite_width / 2))
            sprite_right = int(min(screen_width - 1, screen_x + sprite_width / 2))
            
            occluded_count = 0
            checked_count = 0
            for check_x in range(sprite_left, sprite_right + 1):
                if check_x >= 0 and check_x < screen_width:
                    checked_count += 1
                    # depth_buffer stores wall distance. sprite_y is sprite distance.
                    if depth_buffer[check_x] < sprite_y: 
                        occluded_count += 1
            
            # If >70% of the sprite is hidden by a wall, don't draw it at all.
            if checked_count > 0 and occluded_count / checked_count > 0.7:
                continue
        
        # 5. Store valid sprite for rendering
        if sprite_height > 0 and sprite_height < 10000:
            light_factor = 1.0
            if enable_inverse_square:
                light_factor = min(1.0, light_intensity / (distance * distance + 0.1))
                light_factor = max(ambient_light, light_factor)
            
            visible_sprites_array[count, 0] = distance
            visible_sprites_array[count, 1] = screen_x
            visible_sprites_array[count, 2] = sprite_height
            visible_sprites_array[count, 3] = sprite_width
            visible_sprites_array[count, 4] = texture_id
            visible_sprites_array[count, 5] = light_factor
            count += 1
    
    if count == 0:
        return np.empty((0, 6), dtype=np.float32)
    
    # 6. Sort Sprites
    # We must draw sprites from Farthest to Closest (Painter's Algorithm)
    # so that close sprites overlap far ones correctly.
    visible_sprites_array = visible_sprites_array[:count]
    
    # Sort by distance (column 0), descending order (-visible...)
    indices = np.argsort(-visible_sprites_array[:, 0])
    sorted_sprites = visible_sprites_array[indices]
    
    # Repackage results for the main game loop
    result = np.empty((len(sorted_sprites), 6), dtype=np.float32)
    for i in range(len(sorted_sprites)):
        result[i, 0] = sorted_sprites[i, 1] # Screen X
        result[i, 1] = sorted_sprites[i, 2] # Height
        result[i, 2] = sorted_sprites[i, 3] # Width
        result[i, 3] = sorted_sprites[i, 0] # Distance
        result[i, 4] = sorted_sprites[i, 4] # Texture ID
        result[i, 5] = sorted_sprites[i, 5] # Light
    
    return result