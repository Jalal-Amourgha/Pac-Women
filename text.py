import pygame


class TextInput:
    """A class for handling text input."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        font: pygame.font.Font,
        max_len: int = 12,
    ) -> None:
        """Initialize the text input."""
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = ""
        self.max_len = max_len

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Returns True when Enter is pressed (submit)."""
        if event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_RETURN:
            return True

        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif (
            event.unicode.isalpha()
            or event.unicode.isdigit()
            or event.unicode == " "
        ) and len(self.text) < 10:
            self.text += event.unicode

        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Draws the text input box with a blinking cursor"""
        pygame.draw.rect(surface, "white", self.rect, border_radius=6)
        pygame.draw.rect(surface, "yellow", self.rect, 3, border_radius=6)

        text_surf = self.font.render(self.text, True, "black")
        text_rect = text_surf.get_rect(
            midleft=(self.rect.x + 12, self.rect.centery)
        )
        surface.blit(text_surf, text_rect)

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = text_rect.right + 3 if self.text else self.rect.x + 12
            pygame.draw.line(
                surface,
                "black",
                (cursor_x, self.rect.y + 8),
                (cursor_x, self.rect.bottom - 8),
                2,
            )
