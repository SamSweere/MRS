from pygame.math import Vector2


class Beacon:
    def __init__(self, location, identifier):
        self.location = Vector2(location)
        self.id = identifier
