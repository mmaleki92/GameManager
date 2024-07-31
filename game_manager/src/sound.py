import pygame


class Sound:
    def __init__(self, path) -> None:
        self.sound = pygame.mixer.Sound(path)
    
    def play(self, play_once):
        if play_once:
            self.sound.play()
        else:
            self.sound.play(loops=-1)


    def stop(self):
        self.sound.stop()


class SoundManager:
    def __init__(self) -> None:
        self.sound_dict = {}

    def add_sound_from_directory(self):
        raise NotImplementedError

    def add_sound_from_path(self, sound_name: str, path):
        self.sound_dict[sound_name] = Sound(path)

    def play_by_name(self, name, play_once=False):
        sound = self.sound_dict.get(name, None) 
        if sound:
            sound.play(play_once)
