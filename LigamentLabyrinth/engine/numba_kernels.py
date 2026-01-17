"""Numba-optimized raycasting functions for high-performance rendering."""
"""AI generated code"""

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
    
    if ray_dx != 0:
        delta_dist_x = abs(1.0 / ray_dx)
    else:
        delta_dist_x = 1e30
        
    if ray_dy != 0:
        delta_dist_y = abs(1.0 / ray_dy)
    else:
        delta_dist_y = 1e30
    
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
        
        if map_x < 0 or map_x >= map_width or map_y < 0 or map_y >= map_height:
            hit = True
            hit_val = 1
        else:
            tile = map_grid[map_y, map_x]
            if tile > 0:
                hit = True
                hit_val = tile
    
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


@numba.njit(fastmath=True, parallel=True)
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
    """Render floor and ceiling with Numba optimization and advanced lighting.
    
    Args:
        buffer_pixels: Output pixel buffer (floor_width x floor_height x 3)
        floor_arrays: All floor textures (num_textures x tex_width x tex_height x 3)
        ceiling_arrays: All ceiling textures (num_textures x tex_width x tex_height x 3)
        floor_grid: Floor texture ID map (map_height x map_width)
        ceiling_grid: Ceiling texture ID map (map_height x map_width)
        map_width: Width of the map
        map_height: Height of the map
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
        wall_height_factor: Multiplier for wall height calculation
        enable_inverse_square: Use inverse square law for distance
        light_intensity: Base light power for inverse square
        ambient_light: Minimum light level (0-1)
        enable_vignette: Enable screen edge vignette
        vignette_intensity: Vignette darkness (0-1)
        vignette_radius: Vignette start radius (0-1)
        glitch_intensity: LSD Glitch effect intensity (0=off, higher=more intense)
    """
    half_fov_rad = fov_rad / 2.0
    tan_half_fov = math.tan(half_fov_rad)
    aspect_ratio = screen_width / screen_height
    screen_half = screen_height / 2.0 + bob_offset_y
    
    num_floor_textures = floor_arrays.shape[0]
    num_ceiling_textures = ceiling_arrays.shape[0]
    floor_tex_width = floor_arrays.shape[1]
    floor_tex_height = floor_arrays.shape[2]
    ceiling_tex_width = ceiling_arrays.shape[1]
    ceiling_tex_height = ceiling_arrays.shape[2]
    
    # Precompute texture mask for bitwise AND (assumes power-of-2 textures)
    floor_tex_mask = floor_tex_width - 1
    ceiling_tex_mask = ceiling_tex_width - 1
    
    player_cos = math.cos(player_rotation_rad)
    player_sin = math.sin(player_rotation_rad)
    
    plane_x = -player_sin * tan_half_fov * aspect_ratio
    plane_y = player_cos * tan_half_fov * aspect_ratio
    
    pos_z = 0.5 * screen_height * wall_height_factor
    epsilon = 1.0
    
    # Parallelize the outer loop across CPU cores
    for y in numba.prange(floor_height):
        for x in range(floor_width):
            screen_y = y * floor_scale
            screen_x = x * floor_scale
            p = screen_y - screen_half
            
            if abs(p) < epsilon:
                p = epsilon if p >= 0 else -epsilon
            
            row_distance = pos_z / abs(p)
            
            screen_x_norm = (2.0 * x / floor_width) - 1.0
            ray_dir_x = player_cos + plane_x * screen_x_norm
            ray_dir_y = player_sin + plane_y * screen_x_norm
            
            world_x = player_x + ray_dir_x * row_distance
            world_y = player_y + ray_dir_y * row_distance
            
            # Calculate distance-based lighting
            if enable_inverse_square:
                distance_factor = light_intensity / (row_distance * row_distance + 0.1)
                distance_factor = max(ambient_light, min(1.0, distance_factor))
            else:
                distance_factor = 1.0
            
            # Calculate vignette effect
            vignette_multiplier = 1.0
            if enable_vignette:
                x_norm = (screen_x - screen_width / 2.0) / (screen_width / 2.0)
                y_norm = (screen_y - screen_height / 2.0) / (screen_height / 2.0)
                screen_dist = math.sqrt(x_norm * x_norm + y_norm * y_norm)
                
                if screen_dist > vignette_radius:
                    vignette_falloff = (screen_dist - vignette_radius) / (1.414 - vignette_radius + 0.001)
                    vignette_falloff = min(1.0, vignette_falloff)
                    vignette_multiplier = 1.0 - (vignette_falloff * vignette_intensity)
            
            # Combine lighting effects with glitch (branchless)
            # "Corrupted Flashlight" effect: Light itself fuels the glitch
            # The brighter the light, the more intense the negative overflow
            base_lighting = distance_factor * vignette_multiplier
            corruption_multiplier = 1.0 - glitch_intensity
            final_lighting = base_lighting * corruption_multiplier
            # When glitch_intensity == 0, this behaves normally (corruption_multiplier = 1.0)
            # When glitch_intensity > 0, lighting gets darker enabling color wrapping effects
            
            # Get map tile coordinates
            map_x = int(world_x)
            map_y = int(world_y)
            
            # Clamp to map bounds
            if map_x < 0:
                map_x = 0
            if map_x >= map_width:
                map_x = map_width - 1
            if map_y < 0:
                map_y = 0
            if map_y >= map_height:
                map_y = map_height - 1
            
            if p > epsilon:
                # Floor rendering
                floor_tex_id = floor_grid[map_y, map_x]
                if floor_tex_id >= num_floor_textures:
                    floor_tex_id = 0
                
                # Use bitwise AND for texture wrapping (faster than modulo)
                tex_x = int(world_x * floor_tex_width) & floor_tex_mask
                tex_y = int(world_y * floor_tex_height) & floor_tex_mask
                
                # Apply lighting with potential wrapping for glitch effect (branchless)
                # Always use modulo wrapping - when glitch_intensity is 0, values stay in valid range naturally
                r = int(floor_arrays[floor_tex_id, tex_x, tex_y, 0] * final_lighting) % 256
                g = int(floor_arrays[floor_tex_id, tex_x, tex_y, 1] * final_lighting) % 256
                b = int(floor_arrays[floor_tex_id, tex_x, tex_y, 2] * final_lighting) % 256
                # Handle negative values (wrap from 255)
                r = (r + 256) % 256
                g = (g + 256) % 256
                b = (b + 256) % 256
                buffer_pixels[x, y, 0] = r
                buffer_pixels[x, y, 1] = g
                buffer_pixels[x, y, 2] = b
            
            
            elif p < -epsilon:
                # Ceiling rendering
                ceiling_tex_id = ceiling_grid[map_y, map_x]
                if ceiling_tex_id >= num_ceiling_textures:
                    ceiling_tex_id = 0
                
                # Use bitwise AND for texture wrapping (faster than modulo)
                tex_x = int(world_x * ceiling_tex_width) & ceiling_tex_mask
                tex_y = int(world_y * ceiling_tex_height) & ceiling_tex_mask
                
                # Apply lighting with potential wrapping for glitch effect (branchless)
                # Always use modulo wrapping - when glitch_intensity is 0, values stay in valid range naturally
                r = int(ceiling_arrays[ceiling_tex_id, tex_x, tex_y, 0] * final_lighting) % 256
                g = int(ceiling_arrays[ceiling_tex_id, tex_x, tex_y, 1] * final_lighting) % 256
                b = int(ceiling_arrays[ceiling_tex_id, tex_x, tex_y, 2] * final_lighting) % 256
                # Handle negative values (wrap from 255)
                r = (r + 256) % 256
                g = (g + 256) % 256
                b = (b + 256) % 256
                buffer_pixels[x, y, 0] = r
                buffer_pixels[x, y, 1] = g
                buffer_pixels[x, y, 2] = b


@numba.njit(fastmath=True, parallel=True)
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
    glitch_intensity: float
) -> np.ndarray:
    """Render walls using Numba optimization with advanced horror lighting.
    
    Args:
        screen_pixels: Output pixel buffer (screen_width x screen_height x 3)
        texture_arrays: All wall textures (max_textures x tex_width x tex_height x 3)
        texture_map: Map from hit_value to texture index (max_tile_types,)
        player_x: Player X position
        player_y: Player Y position
        player_rotation_deg: Player rotation in degrees
        map_grid: 2D NumPy array of map tiles
        map_width: Width of the map
        map_height: Height of the map
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
        fov: Field of view in degrees
        max_depth: Maximum ray distance
        num_rays: Number of rays to cast
        ray_width: Width of each ray column in pixels
        bob_offset_y: View bobbing offset
        wall_height_factor: Multiplier for wall height calculation
        enable_inverse_square: Use inverse square law for distance
        light_intensity: Base light power for inverse square
        ambient_light: Minimum light level (0-1)
        enable_vignette: Enable screen edge vignette
        vignette_intensity: Vignette darkness (0-1)
        vignette_radius: Vignette start radius (0-1)
        glitch_intensity: LSD Glitch effect intensity (0=off, higher=more intense)
        
    Returns:
        Depth buffer array of shape (screen_width,) with distance for each column
    """
    half_fov_rad = math.radians(fov / 2.0)
    tan_half_fov = math.tan(half_fov_rad)
    aspect_ratio = screen_width / screen_height
    screen_half = screen_height / 2.0 + bob_offset_y
    
    tex_width = texture_arrays.shape[1]
    tex_height = texture_arrays.shape[2]
    
    # Precompute texture mask for bitwise AND (assumes power-of-2 textures)
    tex_mask = tex_width - 1
    
    depth_buffer = np.full(screen_width, max_depth, dtype=np.float32)
    
    # Parallelize ray casting across CPU cores
    for ray_index in numba.prange(num_rays):
        screen_x = (2.0 * ray_index) / num_rays - 1.0
        angle_offset_rad = math.atan(screen_x * tan_half_fov * aspect_ratio)
        angle_offset_deg = math.degrees(angle_offset_rad)
        
        ray_angle_deg = player_rotation_deg + angle_offset_deg
        ray_angle_rad = math.radians(ray_angle_deg)
        
        distance, side, ray_dx, ray_dy, hit_val = cast_ray_numba(
            player_x, player_y, ray_angle_rad,
            map_grid, map_width, map_height, max_depth
        )
        
        raw_distance = distance
        distance *= math.cos(angle_offset_rad)
        
        if distance < 0.01:
            distance = 0.01
        
        wall_height = int((screen_height * wall_height_factor) / distance)
        wall_top = int(screen_half - (wall_height / 2.0))
        
        if side == 0:
            wall_x = player_y + raw_distance * ray_dy
        else:
            wall_x = player_x + raw_distance * ray_dx
        
        wall_x -= math.floor(wall_x)
        tex_x = int(wall_x * tex_width)
        
        if side == 0 and ray_dx > 0:
            tex_x = tex_width - tex_x - 1
        if side == 1 and ray_dy < 0:
            tex_x = tex_width - tex_x - 1
        
        tex_x = max(0, min(tex_x, tex_width - 1))
        
        texture_idx = 0
        if hit_val < len(texture_map):
            texture_idx = int(texture_map[hit_val])
        
        # Calculate lighting intensity
        lighting_multiplier = 1.0
        
        # Distance-based lighting (inverse square law or constant)
        if enable_inverse_square:
            # Inverse square law: intensity = power / (distance^2)
            distance_factor = light_intensity / (distance * distance + 0.1)
            distance_factor = max(ambient_light, min(1.0, distance_factor))
        else:
            # No distance falloff
            distance_factor = 1.0
        
        lighting_multiplier *= distance_factor
        
        x_start = int(ray_index * ray_width)
        x_end = int((ray_index + 1) * ray_width)
        x_end = min(x_end, screen_width)
        
        
        
        if wall_height > 0 and wall_height < 8000:
            for screen_x_pos in range(x_start, x_end):
                # Store distance in depth buffer for occlusion testing
                depth_buffer[screen_x_pos] = distance
                
                # Calculate vignette effect (per-pixel screen position)
                for screen_y_pos in range(max(0, wall_top), min(screen_height, wall_top + wall_height)):
                    vignette_multiplier = 1.0
                    if enable_vignette:
                        x_norm = (screen_x_pos - screen_width / 2.0) / (screen_width / 2.0)
                        y_norm = (screen_y_pos - screen_height / 2.0) / (screen_height / 2.0)
                        screen_dist = math.sqrt(x_norm * x_norm + y_norm * y_norm)
                        
                        if screen_dist > vignette_radius:
                            vignette_falloff = (screen_dist - vignette_radius) / (1.414 - vignette_radius + 0.001)
                            vignette_falloff = min(1.0, vignette_falloff)
                            vignette_multiplier = 1.0 - (vignette_falloff * vignette_intensity)
                    
                    # Combine all lighting effects with glitch (branchless)
                    # "Corrupted Flashlight" effect: Light itself fuels the glitch
                    # The brighter the light, the more intense the negative overflow
                    base_lighting = lighting_multiplier * vignette_multiplier
                    corruption_multiplier = 1.0 - glitch_intensity
                    final_lighting = base_lighting * corruption_multiplier
                    # When glitch_intensity == 0, this behaves normally (corruption_multiplier = 1.0)
                    # When glitch_intensity > 0, lighting gets darker enabling color wrapping effects
                    
                    y_ratio = (screen_y_pos - wall_top) / wall_height
                    tex_y = int(y_ratio * tex_height)
                    tex_y = max(0, min(tex_y, tex_height - 1))
                    
                    r = texture_arrays[texture_idx, tex_x, tex_y, 0]
                    g = texture_arrays[texture_idx, tex_x, tex_y, 1]
                    b = texture_arrays[texture_idx, tex_x, tex_y, 2]
                    
                    # Apply lighting with potential wrapping for glitch effect (branchless)
                    # Always use modulo wrapping - when glitch_intensity is 0, values stay in valid range naturally
                    r_lit = int(r * final_lighting) % 256
                    g_lit = int(g * final_lighting) % 256
                    b_lit = int(b * final_lighting) % 256
                    # Handle negative values (wrap from 255)
                    r_lit = (r_lit + 256) % 256
                    g_lit = (g_lit + 256) % 256
                    b_lit = (b_lit + 256) % 256
                    screen_pixels[screen_x_pos, screen_y_pos, 0] = r_lit
                    screen_pixels[screen_x_pos, screen_y_pos, 1] = g_lit
                    screen_pixels[screen_x_pos, screen_y_pos, 2] = b_lit
    
    return depth_buffer


@numba.njit(fastmath=True)
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
    """Process sprite rendering with Numba optimization and depth buffer occlusion for collectibles only.
    
    Args:
        sprite_data: Array of shape (N, 3) with [x, y, texture_id] for each sprite
        player_x: Player X position
        player_y: Player Y position
        player_rotation_deg: Player rotation in degrees
        fov: Field of view in degrees
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
        max_depth: Maximum render distance
        wall_height_factor: Multiplier for sprite height calculation
        bob_offset_y: View bobbing offset
        enable_inverse_square: Use inverse square law for lighting
        light_intensity: Base light power
        ambient_light: Minimum light level (0-1)
        depth_buffer: Array of shape (screen_width,) with wall distances for occlusion
        collectible_texture_ids: Tuple of texture IDs that should be occluded by walls
        
    Returns:
        Array of shape (M, 6) with [screen_x, sprite_height, sprite_width, distance, texture_id, light_factor]
        sorted by distance (farthest first), where M <= N (after culling)
    """
    num_sprites = sprite_data.shape[0]
    if num_sprites == 0:
        return np.empty((0, 6), dtype=np.float32)
    
    player_rad = math.radians(player_rotation_deg)
    player_cos = math.cos(player_rad)
    player_sin = math.sin(player_rad)
    
    half_fov = math.radians(fov / 2.0)
    tan_half_fov = math.tan(half_fov)
    aspect_ratio = screen_width / screen_height
    
    visible_sprites = []
    
    for i in range(num_sprites):
        sprite_x_world = sprite_data[i, 0]
        sprite_y_world = sprite_data[i, 1]
        texture_id = sprite_data[i, 2]
        
        dx = sprite_x_world - player_x
        dy = sprite_y_world - player_y
        
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 0.1 or distance > max_depth:
            continue
        
        sprite_y = dx * player_cos + dy * player_sin
        sprite_x = dy * player_cos - dx * player_sin
        
        if sprite_y <= 0.1:
            continue
        
        projection_plane_x = (sprite_x / sprite_y) / (tan_half_fov * aspect_ratio)
        screen_x = (screen_width / 2.0) * (1.0 + projection_plane_x)
        
        sprite_height = (screen_height / sprite_y) * wall_height_factor
        sprite_width = sprite_height
        
        if screen_x + sprite_width / 2 < 0 or screen_x - sprite_width / 2 > screen_width:
            continue
        
        # Check depth buffer for occlusion - ONLY for collectibles, not monsters
        is_collectible = False
        for coll_tex_id in collectible_texture_ids:
            if texture_id == coll_tex_id:
                is_collectible = True
                break
        
        if is_collectible:
            # Check if collectible is behind walls
            sprite_left = int(max(0, screen_x - sprite_width / 2))
            sprite_right = int(min(screen_width - 1, screen_x + sprite_width / 2))
            
            # Check if sprite is behind walls for most of its width
            occluded_count = 0
            checked_count = 0
            for check_x in range(sprite_left, sprite_right + 1):
                if check_x >= 0 and check_x < screen_width:
                    checked_count += 1
                    if depth_buffer[check_x] < sprite_y:  # sprite_y is the perpendicular distance
                        occluded_count += 1
            
            # If more than 70% of sprite width is occluded, skip it
            if checked_count > 0 and occluded_count / checked_count > 0.7:
                continue
        
        if sprite_height > 0 and sprite_height < 10000:
            light_factor = 1.0
            if enable_inverse_square:
                light_factor = min(1.0, light_intensity / (distance * distance + 0.1))
                light_factor = max(ambient_light, light_factor)
            
            visible_sprites.append((distance, screen_x, sprite_height, sprite_width, texture_id, light_factor))
    
    if len(visible_sprites) == 0:
        return np.empty((0, 6), dtype=np.float32)
    
    visible_sprites_array = np.array(visible_sprites, dtype=np.float32)
    
    indices = np.argsort(-visible_sprites_array[:, 0])
    sorted_sprites = visible_sprites_array[indices]
    
    result = np.empty((len(sorted_sprites), 6), dtype=np.float32)
    for i in range(len(sorted_sprites)):
        result[i, 0] = sorted_sprites[i, 1]
        result[i, 1] = sorted_sprites[i, 2]
        result[i, 2] = sorted_sprites[i, 3]
        result[i, 3] = sorted_sprites[i, 0]
        result[i, 4] = sorted_sprites[i, 4]
        result[i, 5] = sorted_sprites[i, 5]
    
    return result
