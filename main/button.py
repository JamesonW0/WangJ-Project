import pygame

pygame.init()
button_font_large = pygame.font.Font('fonts/comicbd.ttf', 50)  # comic sans MS, size 50, bold


class Button:
    """Create a button"""

    def __init__(self, screen, centre, colour, text, action, font=button_font_large, img_path=None, img_size=None):
        self.screen = screen
        if img_path is not None:  # if image button
            self.action = action
            self.image = pygame.image.load(img_path)
            self.image = pygame.transform.scale(self.image, img_size)
            self.image = self.image.convert_alpha()
            # self.image.set_alpha(100)  # for testing only
            self.rect = self.image.get_rect()  # image rect, name it rect for sprite group draw
            self.rect.center = centre
        else:  # if text button
            self.action = action
            self.font = font
            self.image = self.font.render(text, True, colour)  # text object, name it image for sprite group draw
            self.rect = self.image.get_rect()  # text rect, name it rect for sprite group draw
            self.rect.center = centre
        # end if
    # end procedure

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return True
        # end if
        return False
    # end function

    def draw(self):
        self.screen.blit(self.image, self.rect)
    # end procedure

    def clicked(self):
        return self.action
    # end function
# end class
