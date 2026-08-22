import pygame

from utils import cell_to_pixel_center


class SuperGum:
    def __init__(self, id, x, y, offset_x):
        self.id = id
        self.eated = False
        self.gum = self._get_img(id)
        self.x = x
        self.y = y
        self.rect = self.gum.get_rect(
            center=cell_to_pixel_center(self.x, self.y, offset_x)
        )

    def _get_img(self, id):
        img_path = f"./assets/images/gum_{id + 1}.jpg"
        gum_img = pygame.image.load(img_path).convert_alpha()
        return pygame.transform.scale(gum_img, (25, 25))

    def draw(self, screen):
        if not self.eated:
            screen.blit(self.gum, self.rect)
