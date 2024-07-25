import pygame
import pytmx

class LevelManager:
    def __init__(self, current_level_number: int) -> None:
        self.levels = []
        self.current_level_number = current_level_number

    def add_level_from_tmx_path(self, tmx_path, collision_layer_name):
        self.levels.append(Level(tmx_path, collision_layer_name))
        # self.levels.append(Level(fileName = "maps/resources/level1.tmx"))

    def get_current_level(self):
        if self.levels:
            return self.levels[self.current_level_number]
        else:
            raise Exception("There is no level in your levels.")
    
    def draw(self, screen):
        self.get_current_level().draw(screen)
        # screen.blit(self.overlay, [0, 0])


class Level(object):
    def __init__(self, fileName, collision_layer_name=None):
        #Create map object from PyTMX
        self.mapObject: pytmx.TiledMap = pytmx.load_pygame(fileName)
        self.tile_width = self.mapObject.tilewidth
        self.tile_height = self.mapObject.tileheight
        self.layers = []
        self.levelShift = 0

        for layer in self.mapObject.layers:
            if collision_layer_name:
                if layer.name == collision_layer_name:
                    self.collision_layer = Layer(layer, self.mapObject)
    
            self.layers.append(Layer(layer, self.mapObject))

        if self.collision_layer is None:
            raise Exception(f"There is no collision layer with the name {collision_layer_name} found.")


    #Move layer left/right
    def shiftLevel(self, shiftX):
        self.levelShift += shiftX
        
        for layer in self.layers:
            for tile in layer.tiles:
                tile.rect.x += shiftX
    
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
