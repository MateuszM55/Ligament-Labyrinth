"""Numba-optimized raycasting functions for high-performance rendering."""

import numpy as np
import numba
import math


@numba.njit(fastmath=True)
def cast_ray_numba(
    player_x: float,
    player_y: float,
    angle_rad: float,
    map_grid: np.ndarray,
    map_width: int,
    map_height: int,
    max_depth: float
) -> tuple:
    """Cast a single ray using DDA algorithm (Numba JIT optimized).
    
    Args:
        player_x: Player X position
        player_y: Player Y position
        angle_rad: Ray angle in radians
        map_grid: 2D NumPy array of map tiles
        map_width: Width of the map
        map_height: Height of the map
        max_depth: Maximum ray distance
        
    Returns:
        Tuple of (distance, side, ray_dx, ray_dy, hit_value)
        - distance: Distance to wall
        - side: 0 for vertical wall, 1 for horizontal wall
        - ray_dx: Ray direction X component
        - ray_dy: Ray direction Y component
        - hit_value: Tile value that was hit
    """
    ray_dx = math.cos(angle_rad)
    ray_dy = math.sin(angle_rad)
    
    x = player_x
    y = player_y
    
    map_x = int(x)
    map_y = int(y)
    
    # Calculate delta distances
    if ray_dx != 0:
        delta_dist_x = abs(1.0 / ray_dx)
    else:
        delta_dist_x = 1e30
        
    if ray_dy != 0:
        delta_dist_y = abs(1.0 / ray_dy)
    else:
        delta_dist_y = 1e30
    
    # Calculate step and initial side_dist
    if ray_dx < 0:
        step_x = -1
        side_dist_x = (x - map_x) * delta_dist_x
    else:
        step_x = 1
        side_dist_x = (map_x + 1.0 - x) * delta_dist_x
        
    if ray_dy < 0:
        step_y = -1
        side_dist_y = (y - map_y) * delta_dist_y
    else:
        step_y = 1
        side_dist_y = (map_y + 1.0 - y) * delta_dist_y
    
    # DDA algorithm
    hit = False
    hit_val = 0
    side = 0
    max_iterations = 50
    iterations = 0
    
    while not hit and iterations < max_iterations:
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_x += step_x
            side = 0
        else:
            side_dist_y += delta_dist_y
            map_y += step_y
            side = 1
        
        iterations += 1
        
        # Check if out of bounds
        if map_x < 0 or map_x >= map_width or map_y < 0 or map_y >= map_height:
            hit = True
            hit_val = 1  # Treat out of bounds as wall
        else:
            tile = map_grid[map_y, map_x]
            if tile > 0:
                hit = True
                hit_val = tile
    
    # Calculate perpendicular distance
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
    
    if distance > max_depth or distance < 0:
        distance = max_depth
        
    return distance, side, ray_dx, ray_dy, hit_val


@numba.njit(fastmath=True, parallel=False)
def render_floor_ceiling_numba(
    buffer_pixels: np.ndarray,
    floor_array: np.ndarray,
    ceiling_array: np.ndarray,
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
    floor_fog_intensity: float,
    ceiling_fog_intensity: float,
    fog_distance: float
) -> None:
    """Render floor and ceiling with Numba optimization.
    
    Args:
        buffer_pixels: Output pixel buffer (floor_width x floor_height x 3)
        floor_array: Floor texture array (tex_width x tex_height x 3)
        ceiling_array: Ceiling texture array (tex_width x tex_height x 3)
        floor_width: Width of the render buffer
        floor_height: Height of the render buffer
        floor_scale: Downscaling factor for floor rendering
        screen_width: Actual screen width
        screen_height: Actual screen height
        player_x: Player X position
        player_y: Player Y position
        player_rotation_rad: Player rotation in radians
        fov_rad: Field of view in radians
        bob_offset_y: View bobbing offset
        floor_fog_intensity: Floor fog intensity (0-1)
        ceiling_fog_intensity: Ceiling fog intensity (0-1)
        fog_distance: Base fog distance
    """
    half_fov_rad = fov_rad / 2.0
    tan_half_fov = math.tan(half_fov_rad)
    aspect_ratio = screen_width / screen_height
    screen_half = screen_height / 2.0 + bob_offset_y
    
    floor_tex_width = floor_array.shape[0]
    floor_tex_height = floor_array.shape[1]
    ceiling_tex_width = ceiling_array.shape[0]
    ceiling_tex_height = ceiling_array.shape[1]
    
    player_cos = math.cos(player_rotation_rad)
    player_sin = math.sin(player_rotation_rad)
    
    plane_x = -player_sin * tan_half_fov * aspect_ratio
    plane_y = player_cos * tan_half_fov * aspect_ratio
    
    pos_z = 0.5 * screen_height
    epsilon = 1.0
    
    for y in range(floor_height):
        for x in range(floor_width):
            screen_y = y * floor_scale
            p = screen_y - screen_half
            
            # Calculate row distance
            if abs(p) < epsilon:
                p = epsilon if p >= 0 else -epsilon
            
            row_distance = pos_z / abs(p)
            
            # Calculate ray direction
            screen_x_norm = (2.0 * x / floor_width) - 1.0
            ray_dir_x = player_cos + plane_x * screen_x_norm
            ray_dir_y = player_sin + plane_y * screen_x_norm
            
            # Calculate world position
            world_x = player_x + ray_dir_x * row_distance
            world_y = player_y + ray_dir_y * row_distance
            
            # Calculate fog
            fog_factor = min(row_distance / fog_distance, 1.0)
            
            # Render floor
            if p > epsilon:
                floor_fog = 1.0 - fog_factor * floor_fog_intensity
                
                tex_x = int(world_x * floor_tex_width) % floor_tex_width
                tex_y = int(world_y * floor_tex_height) % floor_tex_height
                
                # Ensure indices are positive
                if tex_x < 0:
                    tex_x += floor_tex_width
                if tex_y < 0:
                    tex_y += floor_tex_height
                
                # Apply fog to color
                buffer_pixels[x, y, 0] = int(floor_array[tex_x, tex_y, 0] * floor_fog)
                buffer_pixels[x, y, 1] = int(floor_array[tex_x, tex_y, 1] * floor_fog)
                buffer_pixels[x, y, 2] = int(floor_array[tex_x, tex_y, 2] * floor_fog)
            
            # Render ceiling
            elif p < -epsilon:
                ceiling_fog = 1.0 - fog_factor * ceiling_fog_intensity
                
                tex_x = int(world_x * ceiling_tex_width) % ceiling_tex_width
                tex_y = int(world_y * ceiling_tex_height) % ceiling_tex_height
                
                # Ensure indices are positive
                if tex_x < 0:
                    tex_x += ceiling_tex_width
                if tex_y < 0:
                    tex_y += ceiling_tex_height
                
                # Apply fog to color
                buffer_pixels[x, y, 0] = int(ceiling_array[tex_x, tex_y, 0] * ceiling_fog)
                buffer_pixels[x, y, 1] = int(ceiling_array[tex_x, tex_y, 1] * ceiling_fog)
                buffer_pixels[x, y, 2] = int(ceiling_array[tex_x, tex_y, 2] * ceiling_fog)


@numba.njit(fastmath=True)
def cast_all_rays_numba(
    player_x: float,
    player_y: float,
    player_rotation_deg: float,
    map_grid: np.ndarray,
    map_width: int,
    map_height: int,
    max_depth: float,
    num_rays: int,
    fov: float,
    screen_width: int,
    screen_height: int
) -> np.ndarray:
    """Cast all rays for the current frame (Numba optimized).
    
    Args:
        player_x: Player X position
        player_y: Player Y position
        player_rotation_deg: Player rotation in degrees
        map_grid: 2D NumPy array of map tiles
        map_width: Width of the map
        map_height: Height of the map
        max_depth: Maximum ray distance
        num_rays: Number of rays to cast
        fov: Field of view in degrees
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
        
    Returns:
        NumPy array of shape (num_rays, 5) containing:
        [distance, side, ray_dx, ray_dy, hit_value] for each ray
    """
    half_fov_rad = math.radians(fov / 2.0)
    tan_half_fov = math.tan(half_fov_rad)
    aspect_ratio = screen_width / screen_height
    
    ray_data = np.zeros((num_rays, 5), dtype=np.float32)
    
    for ray_index in range(num_rays):
        screen_x = (2.0 * ray_index) / num_rays - 1.0
        angle_offset_rad = math.atan(screen_x * tan_half_fov * aspect_ratio)
        angle_offset_deg = math.degrees(angle_offset_rad)
        
        ray_angle_deg = player_rotation_deg + angle_offset_deg
        ray_angle_rad = math.radians(ray_angle_deg)
        
        distance, side, ray_dx, ray_dy, hit_val = cast_ray_numba(
            player_x, player_y, ray_angle_rad,
            map_grid, map_width, map_height, max_depth
        )
        
        ray_data[ray_index, 0] = distance
        ray_data[ray_index, 1] = float(side)
        ray_data[ray_index, 2] = ray_dx
        ray_data[ray_index, 3] = ray_dy
        ray_data[ray_index, 4] = float(hit_val)
    
    return ray_data
