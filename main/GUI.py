import numpy as np
import pygame
import sys
import os
import tkinter
from tkinter import filedialog
from tkinter import messagebox
import PIL.Image

pygame.init()  # Initialize pygame, must done at the beginning, before any other pygame function
# colour dictionary, RGB values, no alpha channel, use set_alpha instead
Colours = {'black': (0, 0, 0), 'white': (255, 255, 255), 'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
           'light_blue': (143, 170, 220)}
button_font_large = pygame.font.Font('fonts/comicbd.ttf', 50)  # comic sans MS, size 50, bold
button_font_medium = pygame.font.Font('fonts/comicbd.ttf', 35)  # comic sans MS, size 35, bold
text_font_large = pygame.font.Font('fonts/times.ttf', 35)  # times new roman, size 35
# !!! initialise button command and action, important for buttons to work !!!
next_command = None
next_action = None


class GUI:
    """All the GUI elements of the program"""

    def __init__(self, width, height, page='Home'):
        self.screen = pygame.display.set_mode((width, height))
        # actions of tp command, value will be used in eval()
        self.all_pages = {'Home': 'self.HomePage(self.screen)', 'Start': 'self.StartPage(self.screen)',
                          'Tracks': 'self.TracksPage(self.screen)'}
        self.clock = pygame.time.Clock()
        self.page_obj = eval(self.all_pages[page])  # set current page
        # buttons should be drawn at the end, to make sure no buttons are covered by other images
    # end procedure

    class HomePage:
        """All components of the home page. Including the GIF demonstration, and two buttons"""

        def __init__(self, screen):
            self.screen = screen
            pygame.display.set_caption('Home')  # set title
            # GIF yet to be added
            # self.image = pygame.image.load(give a image path)
            # self.image = pygame.transform.scale(self.image, fixed_value)
            # self.image_rect = self.image.get_rect()
            # create button objects, where their destinations are given at the end of the function statement
            self.buttons = pygame.sprite.Group()
            self.buttons.add(Button((1230, 220), Colours['black'], 'Start', 'tp', 'Start'))
            self.buttons.add(Button((1230, 650), Colours['black'], 'Tracks', 'tp', 'Tracks'))
        # end procedure

        def draw(self):
            self.screen.fill(Colours['white'])
            # self.screen.blit(self.image, self.image_rect)
            pygame.draw.line(self.screen, Colours['light_blue'], (1050, 0), (1050, 900), 3)  # split buttons
            self.buttons.draw(self.screen)
        # end procedure

    class StartPage:
        """All components of the start page. Including five tracks and 4 buttons"""
        def __init__(self, screen):
            self.screen = screen
            pygame.display.set_caption('Start')
            # create button objects, where their destinations are given at the end of the function statement
            self.buttons = pygame.sprite.Group()
            # home button (image button at bottom left)
            self.buttons.add(Button((22, 877), None, 'Home', 'tp', 'Home',img_path='resources/home.png', img_size=(40, 40)))
            self.buttons.add(Button((1230, 160), Colours['black'], 'New Training', 'tp', 'New Training'))
            self.buttons.add(Button((1230, 450), Colours['black'], 'Evaluate', 'tp', 'Evaluate'))
            self.buttons.add(Button((1230, 740), Colours['black'], 'Just Play', 'tp', 'Just Play'))
            self.tracks = GUI.get_tracks()
        # end procedure

        def draw(self):
            self.screen.fill(Colours['white'])
            GUI.draw_text('Start', text_font_large, Colours['black'], self.screen, (100, 100))  # To be deleted
            pygame.draw.line(self.screen, Colours['light_blue'], (1050, 0), (1050, 900), 3)  # split buttons
            pygame.draw.line(self.screen, Colours['light_blue'], (0, 200), (1050, 200), 3)  # split select and show
            self.buttons.draw(self.screen)
        # end procedure

    class TracksPage:
        """All components of the tracks page. Including import tracks and select a track to edit"""
        def __init__(self, screen):
            self.screen = screen
            pygame.display.set_caption('Tracks')
            self.buttons = pygame.sprite.Group()
            # home button (image button at bottom left)
            self.buttons.add(Button((22, 877), None, 'Home', 'tp', 'Home', img_path='resources/home.png', img_size=(40, 40)))
            # button to import tracks (*.png or *.jpg)
            self.buttons.add(Button((700, 570), Colours['black'], 'Import', 'im', 'img', font=button_font_medium))
        # end procedure

        def draw(self):
            self.screen.fill(Colours['white'])
            GUI.draw_text('Select a track to edit', text_font_large, Colours['black'], self.screen, (700, 100))
            GUI.draw_text('Or import a new track', text_font_large, Colours['black'], self.screen, (700, 500))
            self.buttons.draw(self.screen)
        # end procedure

    def update(self):
        """Update the page"""
        global next_command, next_action
        # if any command is given, then update the page according to the command and the action
        if next_command is not None:
            if next_command == 'tp':  # to_page command
                self.page_obj = eval(self.all_pages[next_action])
            else:  # other commands (im, sem, swm)
                GUI.pop_ups(next_command, next_action)
            # end if
            # reset the command and action for next update
            next_command = None
            next_action = None
        # end if
    # end procedure

    def draw(self):  # draw the page
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

    @staticmethod
    def pop_ups(command, action):
        """All pop up windows, using tkinter"""

        if command == 'im':  # import
            tkinter.Tk().withdraw()  # hide the tk main window
            # validation process is done by tkinter using filetypes parameter
            validation = {'img': [('Image File', '*.png'), ('Image File', '*.jpg')], 'txt': [('Text File', '*.txt')]}
            file_path = filedialog.askopenfilename(title='Select a file', filetypes=validation[action])
            if len(file_path) == 0:
                GUI.pop_ups('sem', 'no_file')
            # end if
        elif command == 'sem':  # show error message
            tkinter.Tk().withdraw()  # hide the tk main window
            # actions contain what error message to show given the action
            actions = {'no_file': 'Please select a file',
                       'track_overflow': 'More than 5 tracks, only the first 5 will be shown',
                       'track_underflow': 'No tracks found, please import a track'}
            tkinter.messagebox.showerror('Error', actions[action])
        # end if
    # end procedure

    @staticmethod
    def get_tracks():
        """Get all tracks from the tracks folder, display a error message if more than 5 tracks are found"""
        tracks = []
        # find file in tracks folder, that start with 'track', end with image extension, length 10
        for file in os.listdir('tracks'):
            if file.endswith('.png') or file.endswith('.jpg') and file.startswith('track') and len(file) == 10:
                # validation
                try:
                    int(file[5])
                except ValueError:
                    continue
                tracks.append(file)
            # end if
        # next file
        # sort tracks according to the 6th (python index 5) digit of the file name
        tracks.sort(key=lambda x: int(x[5]))
        if len(tracks) > 5:  # only show 5 tracks, and show an error message if there are more than 5 tracks
            tracks = tracks[:5]
            GUI.pop_ups('sem', 'track_overflow')
        return tracks
    # end function
# end class


class Button(pygame.sprite.Sprite):
    """Create a button"""
    def __init__(self, centre, colour, text, command, action, font=button_font_large, img_path=None, img_size=None):
        super().__init__()
        if img_path is not None:  # if image button
            self.command = command
            self.action = action
            self.image = pygame.image.load(img_path)
            self.image = pygame.transform.scale(self.image, img_size)
            self.rect = self.image.get_rect()  # image rect, name it rect for sprite group draw
            self.rect.center = centre
        else:  # if text button
            self.command = command
            self.action = action
            self.font = font
            self.image = self.font.render(text, True, colour)  # text object, name it image for sprite group draw
            self.rect = self.image.get_rect()  # text rect, name it rect for sprite group draw
            self.rect.center = centre
        # end if
    # end procedure

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            # improve performance by checking collision first, then get global variables
            global next_command, next_action
            next_command = self.command
            next_action = self.action
    # end procedure
# end class


# game function
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
        # next event
        # Drawing here
        Interface.update()
        Interface.draw()
        pygame.display.flip()  # flip the display to renew
    # end while
# end procedure


# Main
if __name__ == '__main__':
    run()
# end if
