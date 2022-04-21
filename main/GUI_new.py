import pygame
import sys
import os
import tkinter
from tkinter import filedialog
from tkinter import messagebox
import shutil
from configparser import ConfigParser

"""
Development notes: now colours can be got by using tools from the toolbar, further amendments required to track_data
dictionary (perhaps replace it with config file), consider a temporary array (class scale) to hold click data.
Screenshot have not been taken for today's progress
"""

# Initialize pygame, must done at the beginning, before any other pygame function
pygame.init()
# colour dictionary, RGB values, no alpha channel, use set_alpha instead
Colours = {'black': (0, 0, 0), 'white': (255, 255, 255), 'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
           'light_blue': (143, 170, 220), 'light_green': (112, 173, 71), 'light_red': (255, 60, 60)}
button_font_large = pygame.font.Font('fonts/comicbd.ttf', 50)  # comic sans MS, size 50, bold
button_font_medium = pygame.font.Font('fonts/comicbd.ttf', 35)  # comic sans MS, size 35, bold
button_font_small = pygame.font.Font('fonts/comicbd.ttf', 25)  # comic sans MS, size 25, bold
text_font_large = pygame.font.Font('fonts/times.ttf', 35)  # times new roman, size 35
text_font_medium = pygame.font.Font('fonts/times.ttf', 25)  # times new roman, size 25


class GUI:
    """All the GUI elements of the program"""

    def __init__(self, width, height):
        # set screen size
        self.screen = pygame.display.set_mode((width, height))
        # actions of tp command, value will be used in eval()
        # buttons should be drawn at the end, to make sure no buttons are covered by other images
        self.buttons = []  # list of buttons, append button objects
        self.drawings = []  # list of drawings, append drawing strings (will be eval()'ed)
        self.images = []  # (image_path, size, centre)
        self.texts = []  # (text, font, colour,centre)
        self.cursor = 'Cursor'
        self.track_data = {'track': pygame.image.load('resources/mask.png'), 'start': [], 'ratio': 1.0,
                           'checkpoints': [], 'end': []}  # dictionary of track data
        # tp command, value will be used in eval()
        self.to_page = {'Home': 'self.set_home_page()', 'Start': 'self.set_start_page()',
                        'Tracks': 'self.set_tracks_page()', 'Settings_new': 'self.set_settings_page(True)'}
        self.import_options = {'Img': 'self.import_file("img")', 'Txt': 'self.import_file("txt")'}
        # set current page to home page
        self.set_home_page()
    # end procedure

    def update(self, mouse_pos):
        # check if any buttons are clicked
        if self.cursor != 'Cursor':
            if self.buttons[0].update(mouse_pos):
                pixel_colour = self.screen.get_at(mouse_pos)
                print(pixel_colour)
        else:
            for button in self.buttons:
                if button.update(mouse_pos):
                    action = button.clicked()  # if clicked, get action
                    # evaluate action
                    if action[:2] == 'tp':  # to page
                        eval(self.to_page[action[2:]])
                    elif action[:2] == 'im':  # import file
                        eval(self.import_options[action[2:]])
                    elif action[:2] == 'si':  # show image
                        exec(action[2:])
                    elif action[:2] == 'ev':  # show text
                        eval(action[2:])
                    elif action[:2] == 'tl':  # set cursor to a selected tool
                        self.cursor = action[2:]
                    # end if
                # end if
        # next button
    # end procedure

    def draw(self):
        # always fill the background first
        self.screen.fill(Colours['white'])
        # draw all buttons
        for button in self.buttons:
            button.draw()
        # next button
        # draw all drawings
        for drawing in self.drawings:
            eval(drawing)
        # next drawing
        # blit all images
        for image in self.images:
            image_obj = pygame.transform.scale(pygame.image.load(image[0]), image[1])
            image_rect = image_obj.get_rect()
            image_rect.center = image[2]
            self.screen.blit(image_obj, image_rect)
        # next image
        # draw all texts
        for text in self.texts:
            self.draw_text(text[0], text[1], text[2], self.screen, text[3])
        # next text
    # end procedure

    def set_home_page(self):
        pygame.display.set_caption('Home')
        # clear all buttons/drawings/images/texts from the previous page
        self.buttons.clear()
        self.drawings.clear()
        self.images.clear()
        self.texts.clear()
        # GIF demo needs to be added
        self.buttons.append(Button(self.screen, (1230, 220), Colours['black'], 'Start', 'tpStart'))
        self.buttons.append(Button(self.screen, (1230, 650), Colours['black'], 'Tracks', 'tpTracks'))
        self.drawings.append("pygame.draw.line(self.screen, Colours['light_blue'], (1050, 0), (1050, 900), 3)")
    # end procedure

    def set_start_page(self):
        pygame.display.set_caption('Start')
        self.buttons.clear()
        self.drawings.clear()
        self.images.clear()
        self.texts.clear()
        # get and add tracks to images list to be drawn
        self.get_tracks((525, 100), 100)
        self.buttons.append(Button(self.screen, (22, 877), None, '', 'tpHome', img_path='resources/home.png',
                                   img_size=(40, 40)))
        # button command to be fill after the simulator is created
        self.buttons.append(Button(self.screen, (1230, 160), Colours['black'], 'New Training', 'tp'))
        self.buttons.append(Button(self.screen, (1230, 450), Colours['black'], 'Evaluate', 'tp'))
        self.buttons.append(Button(self.screen, (1230, 740), Colours['black'], 'Just Play', 'tp'))
        self.drawings.append("pygame.draw.line(self.screen, Colours['light_blue'], (1050, 0), (1050, 900), 3)")
        self.drawings.append("pygame.draw.line(self.screen, Colours['light_blue'], (0, 200), (1050, 200), 3)")
    # end procedure

    def set_tracks_page(self):
        pygame.display.set_caption('Tracks')
        self.buttons.clear()
        self.drawings.clear()
        self.images.clear()
        self.texts.clear()
        # get and add tracks to images list to be drawn
        self.get_tracks((700, 280), 120, to_settings=True)
        self.buttons.append(Button(self.screen, (22, 877), None, '', 'tpHome', img_path='resources/home.png',
                                   img_size=(40, 40)))
        self.buttons.append(
            Button(self.screen, (700, 570), Colours['black'], 'Import', 'imImg', font=button_font_medium))
        self.texts.append(('Select a track to edit', text_font_large, Colours['black'], (700, 100)))
        self.texts.append(('Or import a new track', text_font_large, Colours['black'], (700, 500)))
    # end procedure

    def set_checkpoints_page(self, track_name):
        pygame.display.set_caption('Edit checkpoints')
        self.buttons.clear()
        self.drawings.clear()
        self.images.clear()
        self.texts.clear()
        # treat track as a button, this button must be the first button in the list buttons
        track = pygame.image.load(os.path.join('tracks', track_name))
        size = track.get_size()
        self.track_data['ratio'] = min(1200 / size[0], 820 / size[1])
        size = (int(size[0] * self.track_data['ratio']), int(size[1] * self.track_data['ratio']))
        self.track_data['track'] = pygame.transform.scale(track, size)
        self.buttons.append(Button(self.screen, (600, 490), None, '', 'track',
                                   img_path=os.path.join('tracks', track_name), img_size=size))
        action = 'evself.set_settings_page("' + track_name + '")'
        self.buttons.append(Button(self.screen, (930, 35), Colours['black'], 'Settings', action, font=button_font_small))
        self.set_toolbar()
        self.drawings.append("pygame.draw.line(self.screen, Colours['light_blue'], (0, 70), (1400, 70), 3)")
        self.drawings.append("pygame.draw.line(self.screen, Colours['light_blue'], (1200, 70), (1200, 900), 3)")
        self.texts.append(('Checkpoints', button_font_small, Colours['light_green'], (460, 35)))
    # end procedure

    def get_tracks(self, centre, width, to_settings=False):
        """Get all tracks from the tracks folder, display a error message if more than 5 tracks are found"""
        global text_font_medium  # get font from global scope
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
        elif len(tracks) == 0:  # show error message if there are no tracks
            GUI.show_error('track_underflow')
        # end if
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
        # next i
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
            # next i
        else:
            for i in range(len(coords)):
                action = 'evself.set_checkpoints_page("' + tracks[i] + '")'
                self.buttons.append(Button(self.screen, (coords[i][0], coords[i][1] + 17), None, '', action,
                                           img_path='resources/mask.png', img_size=(width, width + 34)))
            # next i
        # end if
    # end procedure

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
                # end if
            # next file
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
                    # end if
                # next i
            # end if
        # end if
    # end procedure

    def set_toolbar(self):
        tools = ['Starting Line', 'Checkpoints', 'Finish Line', 'Delete', 'Cursor']
        for i in range(len(tools)):
            # texts y value at 125, 283, 441, 599, 757
            self.texts.append((tools[i], button_font_small, Colours['black'], (1300, 125 + i * 158)))
            self.buttons.append(Button(self.screen, (1300, 150 + i * 158), None, '', 'tl'+tools[i],
                                       img_path='resources/mask.png', img_size=(170, 80)))
        self.drawings.append("pygame.draw.circle(self.screen, Colours['light_green'], (1300, 170), 8)")
        self.drawings.append("pygame.draw.circle(self.screen, Colours['light_blue'], (1300, 328), 8)")
        self.drawings.append("pygame.draw.circle(self.screen, Colours['light_red'], (1300, 486), 8)")
        self.images.append((os.path.join('resources', 'delete.png'), (40, 40), (1300, 635)))
        self.images.append((os.path.join('resources', 'cursor.png'), (40, 40), (1300, 793)))

    @staticmethod
    def show_error(error_type):
        tkinter.Tk().withdraw()  # hide the tk main window
        # messages contain what error message to show given the action
        messages = {'no_file_selected': 'Please select a file',
                    'track_overflow': 'More than 5 tracks, only the first 5 will be shown',
                    'track_underflow': 'No tracks found, please import a track',
                    'import_overflow': 'More than 5 tracks exist, please delete them before importing'}
        tkinter.messagebox.showerror('Error', messages[error_type])
    # end procedure

    @staticmethod
    def pop_ups(command, action):
        """All pop up windows, using tkinter, depreciated, waiting to be deleted"""
        if command == 'swm':  # show warning message (ask yes or no)
            tkinter.Tk().withdraw()  # hide the tk main window
            # messages contain what warning message to show given the action
            messages = {'no_settings_found': 'No settings found. Do you want delete the track?'}
            return tkinter.messagebox.askyesno('Warning', messages[action])
        # end if

    @staticmethod
    def draw_text(text, font, colour, surface, centre):
        """Draws text on the screen"""
        text_obj = font.render(text, True, colour)
        text_box = text_obj.get_rect()
        text_box.center = centre
        surface.blit(text_obj, text_box)
    # end procedure
# end class


class Button:
    """Create a button"""

    def __init__(self, screen, centre, colour, text, action, font=button_font_large, img_path=None, img_size=None):
        self.screen = screen
        if img_path is not None:  # if image button
            self.action = action
            self.image = pygame.image.load(img_path)
            self.image = pygame.transform.scale(self.image, img_size)
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


class Config:
    """Read and write config file"""

    def __init__(self, track_name):
        self.config_obj = ConfigParser()
        self.config_path = 'tracks/' + track_name[:6] + '.txt'
        if self.check_validity(self.config_path):
            self.config_obj.read(self.config_path)
        else:
            self.new_config()
    # end procedure

    def new_config(self):
        self.config_obj['CHECKPOINTS'] = {
            'START': None,  # (coordinate_1, coordinate_2)
            'FINISH': None,  # (coordinate, radius)
            'CHECKPOINTS': None,  # [(coordinate, radius), (coordinate, radius), ...]
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
            'ACTIVATION': None,  # activation function of the neural network
            'POPULATION': None,  # number of neural networks in one generation, have to be even
            'GENERATIONS': None,  # number of generations
            'FITNESS THRESHOLD': None,  # fitness threshold of the neural network, automatically filled by the program
        }
    # end procedure

    @staticmethod
    def check_validity(file_path):
        if not os.path.isfile(file_path):
            return False
        else:
            config_obj = ConfigParser()
            config_obj.read(file_path)
            sections = config_obj.sections()
            if 'CHECKPOINTS' not in sections or 'TRACK' not in sections or 'CAR' not in sections or 'NN' not in sections:
                return False
            else:
                return True
            # end if`
    # end function
# end class


# game function
def run():
    """Runs the GUI"""
    Interface = GUI(1400, 900)
    clock = pygame.time.Clock()
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
        clock.tick(60)  # limit the frame rate to 60
    # end while
# end procedure


# Main
if __name__ == '__main__':
    run()
# end if
