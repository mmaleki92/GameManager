import pygame
import pytmx

class LevelManager:
    def __init__(self, current_level_number: int) -> None:
        self.levels = []
        self.current_level_number = current_level_number

    def add_level_from_tmx_path(self, tmx_path, collision_layer_name_list: list):
        self.levels.append(Level(tmx_path, collision_layer_name_list))

    def get_current_level(self):
        if self.levels:
            return self.levels[self.current_level_number]
        else:
            raise Exception("There is no level in your levels.")
    
    def draw(self, screen):
        self.get_current_level().draw(screen)



class Level(object):
    def __init__(self, fileName, collision_layer_name_list=[]):
        #Create map object from PyTMX
        self.mapObject: pytmx.TiledMap = pytmx.load_pygame(fileName)
        self.tile_width = self.mapObject.tilewidth
        self.tile_height = self.mapObject.tileheight
        self.layers = []
        self.level_shift_x = 0
        self.level_shift_y = 0
        self.collision_layers = []
        self.layers_name = []

        for layer in self.mapObject.layers:
            self.layers_name.append(layer.name)
            if collision_layer_name_list:
                if layer.name in collision_layer_name_list:
                    self.collision_layers.append(Layer(layer, self.mapObject))
    
            self.layers.append(Layer(layer, self.mapObject))

        if len(self.collision_layers) == 0:
            raise Exception("There is no collision layer found.")

        self.names_layers_dict = dict(zip(self.layers_name, self.layers))
   
    #Move layer left/right
    def shift_level(self, offset, internal_offset, internal_surf):
        # for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
        #     internal_surf.blit(sprite.image, offset_pos)

        for layer in self.layers:
            for tile in layer.tiles:
                offset_pos = tile.rect.topleft - offset + internal_offset
                internal_surf.blit(tile.image, offset_pos)

                # ground_offset = -offset + internal_offset
                # tile.rect.x += ground_offset[0]
                # tile.rect.y += ground_offset[1]

    #Update layer
    def draw(self, screen):
        for layer in self.layers:
            layer.draw(screen)
        
class Layer(object):
    def __init__(self, layer, mapObject: pytmx.TiledMap):
        #Layer index from tiled map
        self.id = layer.id
        self.name = layer.name
        
        #Create gruop of tiles for this layer
        self.tiles = pygame.sprite.Group()
        
        #Reference map object
        self.mapObject = mapObject

        for (x, y, surface) in layer.tiles():
            self.tiles.add(Tile(image = surface, x = (x * self.mapObject.tilewidth), y = (y * self.mapObject.tileheight)))

    #Draw layer
    def draw(self, screen):
        self.tiles.draw(screen)


class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
