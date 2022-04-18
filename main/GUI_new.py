import pygame
import sys
import os
import tkinter
from tkinter import filedialog
from tkinter import messagebox
import shutil
from configparser import ConfigParser

pygame.init()  # Initialize pygame, must done at the beginning, before any other pygame function
# colour dictionary, RGB values, no alpha channel, use set_alpha instead
Colours = {'black': (0, 0, 0), 'white': (255, 255, 255), 'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
           'light_blue': (143, 170, 220)}
button_font_large = pygame.font.Font('fonts/comicbd.ttf', 50)  # comic sans MS, size 50, bold
button_font_medium = pygame.font.Font('fonts/comicbd.ttf', 35)  # comic sans MS, size 35, bold
text_font_large = pygame.font.Font('fonts/times.ttf', 35)  # times new roman, size 35
text_font_medium = pygame.font.Font('fonts/times.ttf', 25)  # times new roman, size 25


class GUI:
    """All the GUI elements of the program"""

    def __init__(self, width, height):
        self.screen = pygame.display.set_mode((width, height))
        # actions of tp command, value will be used in eval()
        self.clock = pygame.time.Clock()
        # buttons should be drawn at the end, to make sure no buttons are covered by other images
        self.buttons = []
        self.drawings = []
        self.images = []  # (image_path, size, centre)
        self.texts = []  # (text, font, colour,centre)
        self.to_page = {'Home': 'self.set_home_page()', 'Start': 'self.set_start_page()',
                        'Tracks': 'self.set_tracks_page()', 'Settings_new': 'self.set_settings_page(True)'}
        self.import_options = {'Img': 'self.import_file("img")', 'Txt': 'self.import_file("txt")'}
        self.set_home_page()

    # end procedure

    def update(self, mouse_pos):
        for button in self.buttons:
            if button.update(mouse_pos):
                action = button.clicked()
                if action[:2] == 'tp':  # to page
                    eval(self.to_page[action[2:]])
                elif action[:2] == 'im':  # import file
                    eval(self.import_options[action[2:]])
                elif action[:2] == 'si':  # show image
                    exec(action[2:])
                elif action[:2] == 'ev':  # show text
                    eval(action[2:])

    def draw(self):
        self.screen.fill(Colours['white'])
        for button in self.buttons:
            button.draw()
        for drawing in self.drawings:
            eval(drawing)
        for image in self.images:
            image_obj = pygame.transform.scale(pygame.image.load(image[0]), image[1])
            image_rect = image_obj.get_rect()
            image_rect.center = image[2]
            self.screen.blit(image_obj, image_rect)
        for text in self.texts:
            self.draw_text(text[0], text[1], text[2], self.screen, text[3])

    # end procedure

    def set_home_page(self):
        pygame.display.set_caption('Home')
        self.buttons.clear()
        self.drawings.clear()
        self.images.clear()
        self.texts.clear()
        # GIF demo needs to be added
        self.buttons.append(Button(self.screen, (1230, 220), Colours['black'], 'Start', 'tpStart'))
        self.buttons.append(Button(self.screen, (1230, 650), Colours['black'], 'Tracks', 'tpTracks'))
        self.drawings.append("pygame.draw.line(self.screen, Colours['light_blue'], (1050, 0), (1050, 900), 3)")

    def set_start_page(self):
        pygame.display.set_caption('Start')
        self.buttons.clear()
        self.drawings.clear()
        self.images.clear()
        self.texts.clear()
        self.get_tracks((525, 100), 100)
        self.buttons.append(Button(self.screen, (22, 877), None, '', 'tpHome', img_path='resources/home.png',
                                   img_size=(40, 40)))
        self.buttons.append(Button(self.screen, (1230, 160), Colours['black'], 'New Training', 'tp'))
        self.buttons.append(Button(self.screen, (1230, 450), Colours['black'], 'Evaluate', 'tp'))
        self.buttons.append(Button(self.screen, (1230, 740), Colours['black'], 'Just Play', 'tp'))
        self.drawings.append("pygame.draw.line(self.screen, Colours['light_blue'], (1050, 0), (1050, 900), 3)")
        self.drawings.append("pygame.draw.line(self.screen, Colours['light_blue'], (0, 200), (1050, 200), 3)")

    def set_tracks_page(self):
        pygame.display.set_caption('Tracks')
        self.buttons.clear()
        self.drawings.clear()
        self.images.clear()
        self.texts.clear()
        self.get_tracks((700, 280), 120, to_settings=True)
        self.buttons.append(Button(self.screen, (22, 877), None, '', 'tpHome', img_path='resources/home.png',
                                   img_size=(40, 40)))
        self.buttons.append(
            Button(self.screen, (700, 570), Colours['black'], 'Import', 'imImg', font=button_font_medium))
        self.texts.append(('Select a track to edit', text_font_large, Colours['black'], (700, 100)))
        self.texts.append(('Or import a new track', text_font_large, Colours['black'], (700, 500)))

    def set_checkpoints_page(self, track_name):
        pygame.display.set_caption('Edit checkpoints')
        self.buttons.clear()
        self.drawings.clear()
        self.images.clear()
        self.texts.clear()

    def get_tracks(self, centre, width, to_settings=False):
        """Get all tracks from the tracks folder, display a error message if more than 5 tracks are found"""
        global text_font_medium
        tracks = []
        coords = []
        x = centre[0]
        y = centre[1]
        # find file in tracks folder, that start with 'track', end with image extension, length 10
        for file in os.listdir('tracks'):
            if (file.endswith('.png') or file.endswith('.jpg')) and file.startswith('track') and len(file) == 10:
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
            GUI.show_error('track_overflow')
        if len(tracks) == 0:  # show error message if there are no tracks
            GUI.show_error('track_underflow')
        track_num = len(tracks)
        track_num_div = track_num // 2
        if track_num % 2 == 1:
            # centre coordinates for odd number of tracks
            for i in range(-track_num_div, track_num_div + 1):
                coords.append((x + i * width * 2, y))
            # next i
        else:
            # centre coordinates for even number of tracks
            for i in range(-2 * track_num_div + 1, 2 * track_num_div, 2):  # [-1, 1] or [-3, -1, 1, 3]
                coords.append((x + i * width, y))
            # next i
        # end if
        # put images to list ready for drawing
        for i in range(len(tracks)):
            self.images.append((os.path.join('tracks', tracks[i]), (width, width), coords[i]))
            self.texts.append((tracks[i][:6], text_font_medium, Colours['black'],
                               (coords[i][0], coords[i][1] + width / 2 + 20)))
        if not to_settings:
            self.images.append((os.path.join('resources', 'mask.png'), (1050, 700), (525, 550)))
            for i in range(len(coords)):
                track = pygame.image.load(os.path.join('tracks', tracks[i]))
                size = track.get_size()
                ratio = min(1050 / size[0], 700 / size[1])
                size = str((int(size[0] * ratio), int(size[1] * ratio)))
                action = 'siself.images[-1] = (' + '"tracks/' + tracks[i] + '", ' + size + ', (525, 550))'
                self.buttons.append(Button(self.screen, (coords[i][0], coords[i][1] + 17), None, '', action,
                                           img_path='resources/mask.png', img_size=(width, width + 34)))
        else:
            for i in range(len(coords)):
                action = 'evself.set_settings_page("' + tracks[i] + '")'
                self.buttons.append(Button(self.screen, (coords[i][0], coords[i][1] + 17), None, '', action,
                                           img_path='resources/mask.png', img_size=(width, width + 34)))

    # end function

    def import_file(self, filetype):
        tkinter.Tk().withdraw()  # hide the tk main window
        # validation process is done by tkinter using filetypes parameter
        validation = {'img': [('Image File', '*.png'), ('Image File', '*.jpg')], 'txt': [('Text File', '*.txt')]}
        file_path = filedialog.askopenfilename(title='Select a file', filetypes=validation[filetype])
        if len(file_path) == 0:
            GUI.show_error('no_file_selected')
        elif filetype == 'img':
            track_no = []
            for file in os.listdir('tracks'):
                if (file.endswith('.png') or file.endswith('.jpg')) and file.startswith('track') and len(file) == 10:
                    # validation
                    try:
                        int(file[5])
                    except ValueError:
                        continue
                    track_no.append(int(file[5]))
            if len(track_no) >= 5:
                GUI.show_error('import_overflow')
            else:
                track_no.sort()
                for i in range(1, 6):
                    if i not in track_no:
                        shutil.copyfile(file_path, os.path.join('tracks', 'track' + str(i) + file_path[-4:]))
                        file_name = 'track' + str(i) + file_path[-4:]
                        self.set_checkpoints_page(file_name)
                        break

    @staticmethod
    def show_error(error_type):
        tkinter.Tk().withdraw()  # hide the tk main window
        # messages contain what error message to show given the action
        messages = {'no_file_selected': 'Please select a file',
                    'track_overflow': 'More than 5 tracks, only the first 5 will be shown',
                    'track_underflow': 'No tracks found, please import a track',
                    'import_overflow': 'More than 5 tracks exist, please delete them before importing'}
        tkinter.messagebox.showerror('Error', messages[error_type])

    @staticmethod
    def pop_ups(command, action):
        """All pop up windows, using tkinter, depreciated, waiting to be deleted"""

        if command == 'im':  # import
            tkinter.Tk().withdraw()  # hide the tk main window
            # validation process is done by tkinter using filetypes parameter
            validation = {'img': [('Image File', '*.png'), ('Image File', '*.jpg')], 'txt': [('Text File', '*.txt')]}
            file_path = filedialog.askopenfilename(title='Select a file', filetypes=validation[action])
            if len(file_path) == 0:
                GUI.pop_ups('sem', 'no_file_selected')
            # end if
        elif command == 'sem':  # show error message
            tkinter.Tk().withdraw()  # hide the tk main window
            # messages contain what error message to show given the action
            messages = {'no_file_selected': 'Please select a file',
                        'track_overflow': 'More than 5 tracks, only the first 5 will be shown',
                        'track_underflow': 'No tracks found, please import a track'}
            tkinter.messagebox.showerror('Error', messages[action])
        elif command == 'swm':  # show warning message (ask yes or no)
            tkinter.Tk().withdraw()  # hide the tk main window
            # messages contain what warning message to show given the action
            messages = {'no_settings_found': 'No settings found. Do you want delete the track?'}
            return tkinter.messagebox.askyesno('Warning', messages[action])
        # end if

    # end function

    @staticmethod
    def draw_text(text, font, colour, surface, centre):
        """Draws text on the screen"""
        text_obj = font.render(text, True, colour)
        text_box = text_obj.get_rect()
        text_box.center = centre
        surface.blit(text_obj, text_box)

    @staticmethod
    def get_settings(track_name):
        """Retrieve settings file correspond to a particular track from the settings folder"""
        file_path = 'tracks/' + track_name[:6] + '.txt'
        print(file_path)
        if not os.path.isfile(file_path):
            pass


class Button:
    """Create a button"""

    def __init__(self, screen, centre, colour, text, action, font=button_font_large, img_path=None, img_size=None):
        self.screen = screen
        if img_path is not None:  # if image button
            self.action = action
            self.image = pygame.image.load(img_path)
            self.image = pygame.transform.scale(self.image, img_size)
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


class Config:
    """Read and write config file"""

    def __init__(self, track_name):
        self.config_obj = ConfigParser()
        self.config_path = 'tracks/' + track_name[:6] + '.txt'
        if not os.path.isfile(self.config_path):
            self.new_config()
        else:
            self.read_config()

    # end procedure

    def new_config(self):
        self.config_obj['CHECKPOINTS'] = {
            'START': None,  # (coordinate_1, coordinate_2)
            'FINISH': None,  # (coordinate, radius)
            'CHECKPOINTS': [],  # [(coordinate, radius), (coordinate, radius), ...]
        }
        self.config_obj['TRACK'] = {
            'START ANGLE': None,  # automatically filled by the program, do not change
            'MAX STEP': None,  # automatically filled by the program, only change when the training cannot be done
        }
        self.config_obj['CAR'] = {
            'SPEED RATIO': None,  # assume the length of the starting line is 1, enter distance the car can cover in 1s
            'CAR RATIO': None,  # length of the car relative to the starting line, max 0.8
            'TURNING ANGLE': None,  # angle the car can turn in degree, max 60
        }
        self.config_obj['NN'] = {
            'LEARNING RATE': None,  # learning rate of the neural network
            'MUTATION RATE': None,  # mutation rate of the neural network
            'MOMENTUM': None,  # momentum of the neural network
            'POPULATION': None,  # number of neural networks in one generation, have to be even
            'GENERATIONS': None,  # number of generations
            'FITNESS THRESHOLD': None,  # fitness threshold of the neural network, automatically filled by the program
        }


# game function
def run():
    """Runs the GUI"""
    Interface = GUI(1400, 900)
    while True:
        # User input and control
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            # end if
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                Interface.update(event.pos)
            # end if
        # next event
        # Drawing here
        Interface.draw()
        pygame.display.flip()  # flip the display to renew
    # end while


# end procedure


# Main
if __name__ == '__main__':
    run()
# end if
