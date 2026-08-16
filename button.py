import pygame


class Button:
    def __init__(
        self,
        text: str,
        x: int,
        y: int,
        width: int,
        height: int,
        font,
        text_color: str = "black",
        bg_color: str = "yellow",
    ):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):
        """"""
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            text_color, bg_color = self.bg_color, self.text_color
        else:
            text_color, bg_color = self.text_color, self.bg_color

        inner_rect = self.rect.inflate(-4, -4)
        text_surf = self.font.render(self.text, True, bg_color)
        text_rect = text_surf.get_rect(center=self.rect.center)

        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, text_color, inner_rect)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """"""

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
