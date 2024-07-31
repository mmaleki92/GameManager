
import pygame
import numpy as np
import copy


class Collision:
    def __init__(self, collision_layers:list, with_mask=False) -> None:
        self.collision_layers = collision_layers
        self.with_mask = with_mask
    def collide_sprite_mask(self, sprite, layer):
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

    def collide_sprite_rect(self, sprite, layer):
        """
        Check for collisions between a sprite and all tiles in the layer.
        
        Parameters:
        sprite (pygame.sprite.Sprite): The sprite to check for collisions.
        layer (pygame.sprite.Layer): The layer containing tiles (or obstacles).

        Returns:
        list: A list of tuples, each containing a tile and the collision position.
        """
        collides = pygame.sprite.spritecollide(sprite, layer.tiles, False)


        return collides

    def get_close_standing(self, elongated_sprite, layer):
        """
        Check for collisions between an elongated rect and all tiles in the layer.
        
        Parameters:
        elongated_rect (pygame.Rect): The elongated rectangle to check for collisions.
        layer (pygame.sprite.Layer): The layer containing tiles (or obstacles).

        Returns:
        list: A list of tiles that the elongated rect collides with.
        """
        # close_list = []
        

        close_list = pygame.sprite.spritecollide(elongated_sprite, layer.tiles, False)

        # for tile in layer.tiles:
        #     if elongated_rect.colliderect(tile.rect):
                # close_list.append(tile)
                
        return close_list

    def move_sprite(self, sprite, dx, dy):
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
        for collision_layer in self.collision_layers:
            # Store the original position
            original_rect = sprite.rect.copy()

            # Move the sprite
            sprite.rect.x += dx
            sprite.rect.y += dy

            # Check for collisions
            if self.with_mask:
                collisions = self.collide_sprite_mask(sprite, collision_layer)
            else:
                collisions = self.collide_sprite_rect(sprite, collision_layer)
            
            # If collisions are detected, adjust the position
            if collisions:
                # Restore the sprite's original position
                sprite.rect = original_rect
                hit_list.append(True)
            # else:
            #     No collision detected, keep the new position
                # hit_list.append(True)
            
        return not any(hit_list)

    def is_sprite_standing(self, player: pygame.sprite.Sprite, obstacles: pygame.sprite.Group = None, tolerance: int = 2):

# new_d = copy.copy(d)
# new_d.rect = d.rect.copy()

        # Create an elongated rect for collision checking
        elongated_sprite = copy.copy(player) 
        elongated_sprite.rect = player.rect.copy()
        elongated_sprite.rect.height += tolerance
        elongated_sprite.rect.y += tolerance

        if obstacles: 
            collided_obstacles = self.get_close_standing(elongated_sprite, obstacles)
            if collided_obstacles:
                print("Player has collided with the ground")
                return True
            return False
        else:
            print("Using the default collision layers.")

            for collision_layer in self.collision_layers:
                collided_obstacles = self.get_close_standing(elongated_sprite, collision_layer)
                print(collided_obstacles)
                if collided_obstacles:
                    print("Player has collided with the ground")
                    return True
            return False
