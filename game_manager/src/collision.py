
import pygame

def collide_sprite_mask(sprite, layer):
    """
    Check for collisions between a sprite and all tiles in the layer.
    
    Parameters:
    sprite (pygame.sprite.Sprite): The sprite to check for collisions.
    layer (pygame.sprite.Layer): The layer containing tiles (or obstacles).

    Returns:
    list: A list of tuples, each containing a tile and the collision position.
    """
    collides = []

    for tile in layer.tiles:
        offset = pygame.sprite.collide_mask(sprite, tile)
        if offset:
            collides.append((tile, offset))  # Append tile and collision offset
            # print(f"Collision with tile at offset {offset}")
    
    return collides

def move_sprite(sprite, dx, dy, collision_layers):
    """
    Attempt to move the sprite by (dx, dy). If a collision is detected, adjust position.

    Parameters:
    sprite (pygame.sprite.Sprite): The sprite to move.
    dx (int): The amount to move the sprite along the x-axis.
    dy (int): The amount to move the sprite along the y-axis.
    layer (pygame.sprite.Layer): The layer containing tiles (or obstacles).

    Returns:
    None: The sprite's position is adjusted in place if necessary.
    """
    hit_list = []
    for collision_layer in collision_layers:
        # Store the original position
        original_rect = sprite.rect.copy()

        # Move the sprite
        sprite.rect.x += dx
        sprite.rect.y += dy

        # Check for collisions
        collisions = collide_sprite_mask(sprite, collision_layer)

        
        # If collisions are detected, adjust the position
        if collisions:
            # Restore the sprite's original position
            sprite.rect = original_rect
            hit_list.append(True)
        else:
            # No collision detected, keep the new position
            hit_list.append(True)
        
        return any(hit_list)
