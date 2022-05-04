import ast
from configparser import ConfigParser
from PIL import Image
import os
import pygame


class Config:
    """Reading and writing the config file"""

    def __init__(self, track_name):
        self.config_obj = ConfigParser()
        self.config_path = 'tracks/' + track_name[:6] + '.txt'
        self.track_name = track_name
        self.coordinates = [(-1, -1), (-1, -1)]
        self.last_cursor = None
        self.img = Image.open(os.path.join('tracks', self.track_name))
        if self.check_validity(self.config_path):
            self.config_obj.read(self.config_path)
        else:
            self.new_config()
    # end procedure

    def new_config(self):
        size = self.img.size
        settings_ratio = float(min(1200 / size[0], 820 / size[1]))
        simulator_ratio = float(min(1200 / size[0], 820 / size[1]))  # change 1200 and 820 to the appropriate size later
        print((600 - size[0] * settings_ratio / 2, 485 - size[1] * settings_ratio / 2))  # needs to be deleted
        self.config_obj['CHECKPOINTS'] = {
            'START': ((-1, -1), (-1, -1)),  # (midpoint, radius)
            'FINISH': ((-1, -1), -1),  # (midpoint, radius)
            'CHECKPOINTS': [],  # [(midpoint, radius), (midpoint, radius), ...]
        }
        self.config_obj['TRACK'] = {
            'START ANGLE': 0,  # automatically filled by the program, do not change
            'MAX STEP': 0,  # automatically filled by the program, only change when the training cannot be done
            'SETTINGS RATIO': settings_ratio,  # ratio of the track on the checkpoints page(settings)
            'SIMULATOR RATIO': simulator_ratio,  # ratio change of the track on any simulator page
            'ORIGINAL SIZE': size,  # (width, height)
            'ADJUSTED VALUE': (600 - size[0] * settings_ratio / 2, 485 - size[1] * settings_ratio / 2),
        }
        self.config_obj['CAR'] = {
            'SPEED RATIO': 0.0,  # assume the length of the starting line is 1, enter distance the car can cover in 1s
            'CAR RATIO': 0.0,  # length of the car relative to the starting line, max 0.8
            'TURNING ANGLE': 0,  # angle the car can turn in degree, max 60
        }
        self.config_obj['NN'] = {
            'LEARNING RATE': 0.05,  # learning rate of the neural network
            'MUTATION RATE': 0.05,  # mutation rate of the neural network
            'MOMENTUM': 0.9,  # momentum of the neural network
            'ACTIVATION': 'tanh',  # activation function of the neural network
            'POPULATION': 20,  # number of neural networks in one generation, have to be even
            'GENERATIONS': 1000,  # number of generations
            'FITNESS THRESHOLD': 0.0,  # fitness threshold of the neural network, automatically filled by the program
        }
    # end procedure

    def add_point(self, cursor, mouse_pos):
        adjusted_pos = ((mouse_pos[0] - self.get_item('TRACK', 'ADJUSTED VALUE')[0])
                            / self.get_item('TRACK', 'SETTINGS RATIO'),
                        (mouse_pos[1] - self.get_item('TRACK', 'ADJUSTED VALUE')[1])
                            / self.get_item('TRACK', 'SETTINGS RATIO'))
        # detect if any errors occur, information returned shows which error is it
        if self.last_cursor is not None and self.last_cursor != cursor:
            return 'cursor_mismatch'
        elif cursor == 'Starting Line' and self.get_item('CHECKPOINTS', 'START') != ((-1, -1), (-1,-1)):
            return 'starting_line_already_set'
        elif cursor == 'Finish Line' and self.get_item('CHECKPOINTS', 'FINISH') != ((-1, -1), (-1, -1)):
            return 'finish_line_already_set'
        # end if
        # set points given the cursor is not Delete
        if cursor != 'Delete':
            for index in range(2):
                if self.coordinates[index] == (-1, -1):
                    self.coordinates[index] = adjusted_pos
                    data = self.get_point_data()
                    if data is None:
                        break
                    else:
                        self.last_cursor = None
                        self.coordinates = [(-1, -1), (-1, -1)]
                        if cursor == 'Starting Line':
                            self.set_item('CHECKPOINTS', 'START', data)
                        elif cursor == 'Finish Line':
                            self.set_item('CHECKPOINTS', 'FINISH', data)
                        else:
                            checkpoints = self.get_item('CHECKPOINTS', 'CHECKPOINTS')
                            checkpoints.append(data)
                            self.set_item('CHECKPOINTS', 'CHECKPOINTS', checkpoints)
                        # end if
                # end if
            # next index
        else:
            pass
        # end if
    # end function

    def get_point_data(self):
        for coordinate in self.coordinates:
            if coordinate == (-1, -1):
                return
            # end if
        # next coordinate
        rise = self.coordinates[0][1] - self.coordinates[1][1]
        run = self.coordinates[0][0] - self.coordinates[1][0]
        calculate_y = lambda x: (rise * x + run * self.coordinates[0][1] - rise * self.coordinates[0][0]) / run
        calculate_x = lambda y: (run * y + rise * self.coordinates[0][0] - run * self.coordinates[0][1]) / rise
        coordinates_by_x = []
        coordinates_by_y = []
        radius_square = []  # by x square, then by y square
        # calculate the end points of the track with variable x
        colour = (0, 0, 0)
        x = self.coordinates[0][0]
        # increase x to find the first coordinate
        while colour != (255, 255, 255):
            x += 1
            y = calculate_y(x)
            try:
                colour = self.img.getpixel((int(x), int(y)))[:3]
            except IndexError:
                colour = (255, 255, 255)
            # end try
        # end while
        coordinates_by_x.append((x, y))
        # decrease x to find the second coordinate
        colour = (0, 0, 0)
        x = self.coordinates[0][0]
        while colour != (255, 255, 255):
            x -= 1
            y = calculate_y(x)
            try:
                colour = self.img.getpixel((int(x), int(y)))[:3]
            except IndexError:
                colour = (255, 255, 255)
            # end try
        # end while
        coordinates_by_x.append((x, y))
        # calculate the end points of the track with variable y
        colour = (0, 0, 0)
        y = self.coordinates[0][1]
        # increase y to find the first coordinate
        while colour != (255, 255, 255):
            y += 1
            x = calculate_x(y)
            try:
                colour = self.img.getpixel((int(x), int(y)))[:3]
            except IndexError:
                colour = (255, 255, 255)
            # end try
        # end while
        coordinates_by_y.append((x, y))
        # decrease x to find the second coordinate
        colour = (0, 0, 0)
        y = self.coordinates[0][1]
        while colour != (255, 255, 255):
            y -= 1
            x = calculate_x(y)
            try:
                colour = self.img.getpixel((int(x), int(y)))[:3]
            except IndexError:
                colour = (255, 255, 255)
            # end try
        # end while
        coordinates_by_y.append((x, y))
        radius_square.append(pow(coordinates_by_x[0][0] - coordinates_by_x[1][0], 2) +
                             pow(coordinates_by_x[0][1] - coordinates_by_x[1][1], 2))
        radius_square.append(pow(coordinates_by_y[0][0] - coordinates_by_y[1][0], 2) +
                             pow(coordinates_by_y[0][1] - coordinates_by_y[1][1], 2))
        print(radius_square)
        if radius_square[0] < radius_square[1]:
            print(((coordinates_by_x[0][0] - 1, calculate_y(coordinates_by_x[0][0] - 1),
                    (coordinates_by_x[1][0] + 1, calculate_y(coordinates_by_x[1][0] + 1)))))
            return (((coordinates_by_x[0][0] - 1, calculate_y(coordinates_by_x[0][0] - 1)),
                     (coordinates_by_x[1][0] + 1, calculate_y(coordinates_by_x[1][0] + 1))))
            return (((coordinates_by_x[0][0] + coordinates_by_x[1][0]) / 2,
                     (calculate_y(coordinates_by_x[0][0] - 1) + calculate_y(coordinates_by_x[1][0] + 1)) / 2),
                    pow(radius_square[0], 0.5))
        else:
            print(((calculate_x(coordinates_by_y[0][1] - 1), coordinates_by_y[0][1]),
                   (calculate_x(coordinates_by_y[1][1] + 1), coordinates_by_y[1][1])))
            return (((calculate_x(coordinates_by_y[0][1] - 1), coordinates_by_y[0][1]),
                    (calculate_x(coordinates_by_y[1][1] + 1), coordinates_by_y[1][1])))
            return (((calculate_x(coordinates_by_y[0][1] - 1) + calculate_x(coordinates_by_y[1][1] + 1)) / 2,
                     (coordinates_by_y[0][1] + coordinates_by_y[1][1]) / 2), pow(radius_square[1], 0.5))

    def get_item(self, section, key):
        return ast.literal_eval(self.config_obj[section][key])
    # end function

    def set_item(self, section, key, value):
        self.config_obj[section][key] = str(value)
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


if __name__ == '__main__':
    a = Config('track1.png')
    a.set_item('CHECKPOINTS', 'START', ((0, 0), 20))
    print(a.get_item('CHECKPOINTS', 'START'))
    img = Image.open('tracks/track1.png').convert('RGB')
    print(img.getpixel((-1, -1)))
