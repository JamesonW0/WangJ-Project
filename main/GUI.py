import numpy as np
import pygame
import sys
import tkinter
from tkinter import filedialog
import PIL.Image

pygame.init()
Colours = {'black': (0, 0, 0), 'white': (255, 255, 255), 'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
           'light_blue': (143, 170, 220)}
button_font_large = pygame.font.Font('fonts/comic.ttf', 50)
button_font_medium = pygame.font.Font('fonts/comic.ttf', 35)
text_font_large = pygame.font.Font('fonts/times.ttf', 35)
next_ = None


class GUI:
    """All the GUI elements of the program"""

    def __init__(self, width, height, page='Home'):
        self.screen = pygame.display.set_mode((width, height))
        self.all_pages = {'Home': 'self.HomePage(self.screen)', 'Start': 'self.StartPage(self.screen)',
                          'Tracks': 'self.TracksPage(self.screen)'}
        self.clock = pygame.time.Clock()
        self.page_obj = eval(self.all_pages[page])
    # end procedure

    class HomePage:
        """All components of the home page. Including the GIF demonstration, and two buttons"""

        def __init__(self, screen):
            self.screen = screen
            pygame.display.set_caption('Home')
            # self.image = pygame.image.load(give a image path)
            # self.image = pygame.transform.scale(self.image, fixed_value)
            # self.image_rect = self.image.get_rect()
            self.buttons = pygame.sprite.Group()
            self.buttons.add(Button((1230, 220), Colours['black'], 'Start'))
            self.buttons.add(Button((1230, 650), Colours['black'], 'Tracks'))
        # end procedure

        def draw(self):
            self.screen.fill(Colours['white'])
            # self.screen.blit(self.image, self.image_rect)
            pygame.draw.line(self.screen, Colours['light_blue'], (1050, 0), (1050, 900), 3)
            self.buttons.draw(self.screen)
        # end procedure

    class StartPage:
        """All components of the start page. Including five tracks and 4 buttons"""
        def __init__(self, screen):
            self.screen = screen
            pygame.display.set_caption('Start')
            self.buttons = pygame.sprite.Group()
            self.buttons.add(Button((22, 877), None, 'Home', img_path='resources/home.png', img_size=(40, 40)))
            self.buttons.add(Button((1230, 160), Colours['black'], 'New Training'))
            self.buttons.add(Button((1230, 450), Colours['black'], 'Evaluate'))
            self.buttons.add(Button((1230, 740), Colours['black'], 'Just Play'))
        # end procedure

        def draw(self):
            self.screen.fill(Colours['white'])
            GUI.draw_text('Start', text_font_large, Colours['black'], self.screen, (100, 100))  # delete
            pygame.draw.line(self.screen, Colours['light_blue'], (1050, 0), (1050, 900), 3)
            pygame.draw.line(self.screen, Colours['light_blue'], (0, 200), (1050, 200), 3)
            self.buttons.draw(self.screen)
        # end procedure

    class TracksPage:
        """All components of the tracks page. Including import tracks and select a track to edit"""
        def __init__(self, screen):
            self.screen = screen
            pygame.display.set_caption('Tracks')
            self.buttons = pygame.sprite.Group()
            self.buttons.add(Button((22, 877), None, 'Home', img_path='resources/home.png', img_size=(40, 40)))
            self.buttons.add(Button((700, 570), Colours['black'], 'Import', font=button_font_medium))
        # end procedure

        def draw(self):
            self.screen.fill(Colours['white'])
            GUI.draw_text('Select a track to edit', text_font_large, Colours['black'], self.screen, (700, 100))
            GUI.draw_text('Or Import a new track', text_font_large, Colours['black'], self.screen, (700, 500))
            self.buttons.draw(self.screen)
        # end procedure

    def update(self):
        """Update the page"""
        global next_
        if next_ is not None:
            self.page_obj = eval(self.all_pages[next_])
            next_ = None
        # end if
    # end procedure

    def draw(self):
        self.page_obj.draw()
    # end procedure

    @staticmethod
    def draw_text(text, font, colour, surface, centre):
        """Draws text on the screen"""
        text_obj = font.render(text, True, colour)
        text_box = text_obj.get_rect()
        text_box.center = centre
        surface.blit(text_obj, text_box)
    # end procedure

"""
Popup windows can use pygame utility libraries or tkinter.or pyzenity or screenshots.
"""


class Button(pygame.sprite.Sprite):
    def __init__(self, centre, colour, action, font=button_font_large, img_path=None, img_size=None):
        super().__init__()
        if img_path is not None:
            self.action = action
            self.image = pygame.image.load(img_path)
            self.image = pygame.transform.scale(self.image, img_size)
            self.rect = self.image.get_rect()
            self.rect.center = centre
        else:
            self.action = action
            self.font = font
            self.image = self.font.render(self.action, True, colour)
            self.rect = self.image.get_rect()
            self.rect.center = centre
        # end if
    # end procedure

    def update(self, mouse_pos):
        global next_
        if self.rect.collidepoint(mouse_pos):
            next_ = self.action
    # end procedure


def run():
    """Runs the GUI"""
    Interface = GUI(1400, 900, page='Home')
    x = None
    while True:
        # User input and control
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            # end if
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                Interface.page_obj.buttons.update(event.pos)
            # end if
        # Next event
        # game settings
        # Drawing here
        Interface.update()
        Interface.draw()
        pygame.display.flip()  # flip the display to renew
    # End while
# End procedure


if __name__ == '__main__':
    run()