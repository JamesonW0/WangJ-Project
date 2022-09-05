import pygame
import sys
import os
import tkinter
from tkinter import filedialog
from tkinter import messagebox
import shutil
import simulator

"""
20/5/22 notes: text box not finished yet. should be reviewed (or redo) after the simulator done. 
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
text_font_small = pygame.font.Font('fonts/times.ttf', 15)  # times new roman, size 15


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
        # cursor status can only be changed at set checkpoints page, so will not affect other pages
        self.cursor = 'Cursor'
        self.track_config = None  # dictionary of track data
        # tp command, value will be used in eval()
        self.to_page = {'Home': 'self.set_home_page()', 'Start': 'self.set_start_page()',
                        'Tracks': 'self.set_tracks_page()', 'Settings_new': 'self.set_settings_page(True)'}
        self.import_options = {'Img': 'self.import_file("img")', 'Txt': 'self.import_file("txt")'}
        # set current page to home page
        self.current_page = ''
        self.text_box = None
        self.set_home_page()
        # a class wide temporary variable to that allows the pass data, should be deleted, not in use now
        self.temp = None

    # end procedure

    def update(self, event):
        # update procedure
        if event.type == pygame.QUIT:  # check for quit
            sys.exit()  # remember to register any functions that need to run at exit
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # check for buttons
            mouse_pos = event.pos
            # if cursor is not 'Cursor', means a tool is in use and we should not check other buttons in this case
            if self.cursor != 'Cursor' and self.buttons[0].update(mouse_pos):  # check is the track is clicked
                # try to add/delete a point given the cursor state and the mouse position, return None if no error
                any_error = self.track_config.amend_point(self.cursor, mouse_pos)
                if any_error is not None:  # any return other than None will be deemed as an error
                    self.show_error(any_error)
                # end if
            else:
                for button in self.buttons:
                    if button.update(mouse_pos):
                        action = button.clicked()  # if clicked, get action
                        # evaluate action
                        if action[:2] == 'tp':  # to page
                            eval(self.to_page[action[2:]])
                        elif action[:2] == 'im':  # import file
                            eval(self.import_options[action[2:]])
                        elif action[:2] == 'ex':  # execute the command
                            exec(action[2:])
                        elif action[:2] == 'ev':  # show text
                            eval(action[2:])
                        elif action[:2] == 'tl':  # set cursor to the tool selected
                            self.cursor = action[2:]
                        # end if
                    # end if
            # next button
        if self.text_box is not None:
            self.text_box.update(event)
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
            image_obj = pygame.transform.scale(pygame.image.load(image[0]), image[1])  # resize
            image_rect = image_obj.get_rect()
            image_rect.center = image[2]
            self.screen.blit(image_obj, image_rect)
        # next image
        # draw all texts
        for text in self.texts:
            self.draw_text(text[0], text[1], text[2], self.screen, text[3])
        # next text
        # if a track is loaded, then the program will draw all checkpoints in the Config file
        if self.current_page == 'Edit Checkpoints':
            # get all checkpoints data
            start = self.track_config.get_item('CHECKPOINTS', 'START')
            checkpoints = self.track_config.get_item('CHECKPOINTS', 'CHECKPOINTS')
            finish = self.track_config.get_item('CHECKPOINTS', 'FINISH')
            ratio = self.track_config.get_item('DISPLAY', 'SETTINGS RATIO')
            adjust_value = self.track_config.get_item('DISPLAY', 'ADJUSTED VALUE')
            # this anonymous function converts the actual points on the track to point that can be drawn on the screen
            convert_pos = lambda pos: (int(pos[0] * ratio + adjust_value[0]), int(pos[1] * ratio + adjust_value[1]))
            if start[1] != -1:  # if starting line is set
                # convert the coordinates
                centre = convert_pos(start[0])
                # usability feature
                pygame.draw.line(self.screen, Colours['light_green'], convert_pos(start[2]), convert_pos(start[3]), 2)
                pygame.draw.circle(self.screen, Colours['light_green'], centre, 20)
                self.draw_text('S', text_font_small, Colours['black'], self.screen, centre)
            # end if
            if finish[1] != -1:  # if finish line is set
                # convert the coordinates
                centre = convert_pos(finish[0])
                # usability feature
                pygame.draw.line(self.screen, Colours['light_red'], convert_pos(finish[2]), convert_pos(finish[3]), 2)
                pygame.draw.circle(self.screen, Colours['light_red'], centre, 20)
                self.draw_text('F', text_font_small, Colours['black'], self.screen, centre)
            # end if
            if checkpoints:  # if any checkpoints have been set
                # loop through all checkpoints
                for i in range(len(checkpoints)):
                    centre = convert_pos(checkpoints[i][0])
                    # usability feature
                    pygame.draw.line(self.screen, Colours['light_blue'], convert_pos(checkpoints[i][2]),
                                     convert_pos(checkpoints[i][3]), 2)
                    pygame.draw.circle(self.screen, Colours['light_blue'], centre, 20)
                    self.draw_text('C' + str(i), text_font_small, Colours['black'], self.screen, centre)
                # next i
            # end if
        # end if
        # if a tool is in use, then draw the corresponding cursor
        if self.cursor != 'Cursor':
            mouse_pos = pygame.mouse.get_pos()
            if self.cursor == 'Starting Line':  # green dot for starting line
                pygame.draw.circle(self.screen, Colours['light_green'], mouse_pos, 5)
            elif self.cursor == 'Checkpoints':  # blue dot for checkpoints
                pygame.draw.circle(self.screen, Colours['light_blue'], mouse_pos, 5)
            elif self.cursor == 'Finish Line':  # red dot for finish line
                pygame.draw.circle(self.screen, Colours['light_red'], mouse_pos, 5)
            else:  # blitz delete image for delete
                image_obj = pygame.transform.scale(pygame.image.load(os.path.join('resources', 'delete.png')), (20, 20))
                image_rect = image_obj.get_rect()
                image_rect.center = mouse_pos
                self.screen.blit(image_obj, image_rect)
            # end if
        # end if
        if self.text_box is not None:
            self.text_box.draw()
    # end procedure

    def set_home_page(self):
        pygame.display.set_caption('Home')
        self.current_page = 'Home'
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
        self.current_page = 'Start'
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
        self.current_page = 'Tracks'
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
        self.current_page = 'Edit Checkpoints'
        self.buttons.clear()
        self.drawings.clear()
        self.images.clear()
        self.texts.clear()
        # initialise the track config, if not initialised already
        if self.track_config is None:
            self.track_config = simulator.Config(track_name)
        # get ratio data
        size = self.track_config.get_item('DISPLAY', 'ORIGINAL SIZE')
        ratio = self.track_config.get_item('DISPLAY', 'SETTINGS RATIO')
        size = (int(size[0] * ratio), int(size[1] * ratio))
        # treat track as a button, this button must be the first button in the list buttons
        # with centre (600, 485) and size optimized
        self.buttons.append(Button(self.screen, (600, 485), None, '', 'track',
                                   img_path=os.path.join('tracks', track_name), img_size=size))
        action = 'evself.set_settings_page("' + track_name + '")'
        self.buttons.append(
            Button(self.screen, (930, 35), Colours['black'], 'Settings', action, font=button_font_small))
        self.set_toolbar()
        self.drawings.append("pygame.draw.line(self.screen, Colours['light_blue'], (0, 70), (1400, 70), 3)")
        self.drawings.append("pygame.draw.line(self.screen, Colours['light_blue'], (1200, 70), (1200, 900), 3)")
        self.texts.append(('Checkpoints', button_font_small, Colours['light_green'], (460, 35)))
    # end procedure

    def set_settings_page(self, track_name):
        pygame.display.set_caption('Edit Settings')
        self.current_page = 'Edit Settings'
        self.cursor = 'Cursor'
        self.buttons.clear()
        self.drawings.clear()
        self.images.clear()
        self.texts.clear()
        # initialise the track config, if not initialised already
        if self.track_config is None:
            self.track_config = simulator.Config(track_name)
        action = 'evself.set_checkpoints_page("' + track_name + '")'
        self.buttons.append(
            Button(self.screen, (460, 35), Colours['black'], 'Checkpoints', action, font=button_font_small))
        self.drawings.append("pygame.draw.line(self.screen, Colours['light_blue'], (0, 70), (1400, 70), 3)")
        self.text_box = SettingsBox(self.screen, self.track_config)
        self.texts.append(('Settings', button_font_small, Colours['light_green'], (930, 35)))
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
                action = 'exself.images[-1] = (' + '"tracks/' + tracks[i] + '", ' + size + ', (525, 550))'
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
                    # end try
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
        # add all tools' button and text
        # add dots for checkpoints, starting/finish line
        self.drawings.append("pygame.draw.circle(self.screen, Colours['light_green'], (1300, 170), 8)")
        self.drawings.append("pygame.draw.circle(self.screen, Colours['light_blue'], (1300, 328), 8)")
        self.drawings.append("pygame.draw.circle(self.screen, Colours['light_red'], (1300, 486), 8)")
        # add image for cursor and delete
        self.images.append((os.path.join('resources', 'delete.png'), (40, 40), (1300, 635)))
        self.images.append((os.path.join('resources', 'cursor.png'), (40, 40), (1300, 793)))
        for i in range(len(tools)):
            # texts y value at 125, 283, 441, 599, 757
            self.texts.append((tools[i], button_font_small, Colours['black'], (1300, 125 + i * 158)))
            self.buttons.append(Button(self.screen, (1300, 150 + i * 158), None, '', 'tl' + tools[i],
                                       img_path='resources/mask.png', img_size=(170, 80)))
        # next i
    # end procedure

    @staticmethod
    def show_error(error_type):
        tkinter.Tk().withdraw()  # hide the tk main window
        # messages contain what error message to show given the action
        messages = {'no_file_selected': 'Please select a file.',
                    'track_overflow': 'More than 5 tracks, only the first five will be shown.',
                    'track_underflow': 'No tracks found, please import a track.',
                    'import_overflow': 'More than 5 tracks exist, please delete them before importing.',
                    'point_not_on_track': 'The point you selected is not on the track. Try again.',
                    'starting_line_already_set': 'Please remove the current starting line before setting a new one.',
                    'finish_line_already_set': 'Please remove the current finish line before setting a new one.',
                    'cursor_mismatch': 'Please finish setting the current point before use another cursor.',
                    'same_points_input': 'Cannot process two same points. Please try again.',
                    'no_delete_point_selected': 'Please click a point shown on the map to delete it.'}
        tkinter.messagebox.showerror('Error', messages[error_type])
    # end procedure

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


class SettingsBox:
    def __init__(self, screen, config_obj):
        self.value_font = button_font_small
        self.name_font = text_font_medium
        self.screen = screen
        self.config = config_obj
        # get data that can be changed on the settings page
        self.data = {'TRACK: Maximum Step': self.config.get_item('TRACK', 'MAX STEP'),
                     'CAR: Speed': self.config.get_item('CAR', 'SPEED'),
                     'CAR: Car Length': self.config.get_item('CAR', 'CAR LENGTH'),
                     'CAR: Car Width': self.config.get_item('CAR', 'CAR WIDTH'),
                     'CAR: Turning Angle': self.config.get_item('CAR', 'TURNING ANGLE'),
                     'NN: Learning Rate': self.config.get_item('NN', 'LEARNING RATE'),
                     'NN: Mutation Rate': self.config.get_item('NN', 'MUTATION RATE'),
                     'NN: Momentum': self.config.get_item('NN', 'MOMENTUM'),
                     'NN: Activation Function': self.config.get_item('NN', 'ACTIVATION FUNCTION'),
                     'NN: Population': self.config.get_item('NN', 'POPULATION'),
                     'NN: Generations': self.config.get_item('NN', 'GENERATIONS'),
                     'NN: Fitness Threshold': self.config.get_item('NN', 'FITNESS THRESHOLD'),
                     }
        self.active = None  # contains the index of the setting box in active
        self.settings_names = []  # (text_obj, text_rect)
        self.entry_values = []  # (text_obj, text_rect)
        self.entry_boxes = []  # rect
        self.names = list(self.data.keys())  # global because used for update these settings in config
        values = list(self.data.values())
        for i in range(len(self.data)):
            # initialise names for display
            name_text = self.name_font.render(str(self.names[i]), True, Colours['black'])
            name_rect = name_text.get_rect()
            name_rect.topleft = (200 + (i // 6) * 600, 90 + (i % 6) * 135)
            self.settings_names.append((name_text, name_rect))
            # initialise input data for display
            self.entry_values.append([str(values[i]), (450 + (i // 6) * 600, 85 + (i % 6) * 135)])
            # initialise input boxes for display
            self.entry_boxes.append(pygame.Rect(450 + (i // 6) * 600, 85 + (i % 6) * 135, 100, 35))
        # next i

    def update(self, event):  # given clicked, check if any input boxes are clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.entry_boxes)):
                if self.entry_boxes[i].collidepoint(event.pos):
                    if self.active is not None:
                        pass
                    self.active = i
                    return
                # end if
            # next i
            self.active = None
        if event.type == pygame.KEYDOWN:
            if self.active is not None:
                if event.key == pygame.K_RETURN:
                    self.active = None
                elif event.key == pygame.K_BACKSPACE:
                    self.entry_values[self.active][0] = self.entry_values[self.active][0][:-1]
                else:
                    self.entry_values[self.active][0] += event.unicode
                # end if
            # end if
    # end procedure

    def draw(self):
        '''
        def draw_text(text, font, colour, surface, centre):
        text_obj = font.render(text, True, colour)
        text_box = text_obj.get_rect()
        text_box.center = centre
        surface.blit(text_obj, text_box)
        '''
        for i in range(len(self.data)):
            self.screen.blit(self.settings_names[i][0], self.settings_names[i][1])
            entry_text = self.value_font.render(self.entry_values[i][0], True, Colours['black'])
            entry_box = entry_text.get_rect()
            entry_box.topleft = self.entry_values[i][1]
            self.screen.blit(entry_text, entry_box)

# end class


# game function
def run():
    """Run the GUI"""
    Interface = GUI(1400, 900)
    clock = pygame.time.Clock()
    while True:
        # User input and control
        for event in pygame.event.get():
            Interface.update(event)
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
