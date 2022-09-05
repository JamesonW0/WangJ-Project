import pygame
import ast
from configparser import ConfigParser
from PIL import Image
import os
import math
import numpy as np


class Config:
    """Reading and writing the config file"""

    def __init__(self, track_name):
        # initiate the track
        self.config_path = 'tracks/' + track_name[:6] + '.txt'
        self.track_name = track_name
        self.img = Image.open(os.path.join('tracks', self.track_name))
        # initiate the corresponding config object for the track
        self.config_obj = ConfigParser()
        if self.check_validity(self.config_path):
            self.config_obj.read(self.config_path)
        else:
            self.new_config()
        # end if
        # two classwide variable for amend_point
        self.coordinates = [(-1, -1), (-1, -1)]
        self.last_cursor = None

    # end procedure

    def new_config(self):
        # size and ratio for showing onto the pygame screen and converting data
        size = self.img.size
        settings_ratio = float(min(1200 / size[0], 820 / size[1]))
        simulator_ratio = float(min(1200 / size[0], 820 / size[1]))  # change 1200 and 820 to the appropriate size later
        self.config_obj['CHECKPOINTS'] = {
            'START': ((-1, -1), -1, (-1, -1), (-1, -1)),  # (midpoint, radius, edge_1, edge_2)
            'FINISH': ((-1, -1), -1, (-1, -1), (-1, -1)),  # (midpoint, radius, edge_1, edge_2)
            'CHECKPOINTS': [],  # [(midpoint, radius, edge_1, edge_2), (midpoint, radius, edge_1, edge_2), ...]
        }
        self.config_obj['DISPLAY'] = {
            'SETTINGS RATIO': settings_ratio,  # ratio of the track on the checkpoints page(settings)
            'SIMULATOR RATIO': simulator_ratio,  # ratio change of the track on any simulator page
            'ORIGINAL SIZE': size,  # (width, height)
            'ADJUSTED VALUE': (600 - size[0] * settings_ratio / 2, 485 - size[1] * settings_ratio / 2),
        }
        self.config_obj['TRACK'] = {
            'START ANGLE': 0,  # automatically filled by the program, do not change
            'MAX STEP': 0,  # automatically filled by the program, only change when the training cannot be done
        }
        self.config_obj['CAR'] = {
            'SPEED': 0.0,  # Number of pixels the car can travel within 1 second
            'CAR LENGTH': 800.0,  # The length of the car in pixels
            'CAR WIDTH': 400.0,  # The width of the car in pixels
            'TURNING ANGLE': 5,  # angle the car can turn in degrees, max 10 degrees
        }
        self.config_obj['NN'] = {
            'LEARNING RATE': 0.05,  # learning rate of the neural network
            'MUTATION RATE': 0.05,  # mutation rate of the neural network
            'MOMENTUM': 0.9,  # momentum of the neural network
            'ACTIVATION FUNCTION': 'tanh',  # activation function of the neural network
            'POPULATION': 20,  # number of neural networks in one generation, have to be even
            'GENERATIONS': 1000,  # number of generations
            'FITNESS THRESHOLD': 0.0,  # fitness threshold of the neural network, automatically filled by the program
        }

    # end procedure

    def amend_point(self, cursor, mouse_pos):
        # convert click position to actual position on the track
        adjusted_pos = ((mouse_pos[0] - self.get_item('DISPLAY', 'ADJUSTED VALUE')[0])
                        / self.get_item('DISPLAY', 'SETTINGS RATIO'),
                        (mouse_pos[1] - self.get_item('DISPLAY', 'ADJUSTED VALUE')[1])
                        / self.get_item('DISPLAY', 'SETTINGS RATIO'))
        # detect if any errors occur, information is returned shows which error is it
        if self.img.getpixel((int(adjusted_pos[0]), int(adjusted_pos[1])))[:3] == (255, 255, 255):
            return 'point_not_on_track'
        elif self.last_cursor is not None and self.last_cursor != cursor:
            return 'cursor_mismatch'
        elif cursor == 'Starting Line' and self.get_item('CHECKPOINTS', 'START')[1] != -1:
            return 'starting_line_already_set'
        elif cursor == 'Finish Line' and self.get_item('CHECKPOINTS', 'FINISH')[1] != -1:
            return 'finish_line_already_set'
        # end if
        # set points given the cursor is not Delete
        if cursor != 'Delete':
            self.last_cursor = cursor
            # loop through the self.coordinates to set points
            for index in range(2):
                if self.coordinates[index] == (-1, -1):
                    self.coordinates[index] = adjusted_pos
                    try:
                        data = self.get_point_data()
                    except ZeroDivisionError:  # if same point is clicked, information is returned and shown
                        return 'same_points_input'
                    # end try
                    if data is None:
                        break
                    else:
                        self.last_cursor = None
                        self.coordinates = [(-1, -1), (-1, -1)]
                        if cursor == 'Starting Line':  # set starting line
                            self.set_item('CHECKPOINTS', 'START', data)
                        elif cursor == 'Finish Line':  # set finish line
                            self.set_item('CHECKPOINTS', 'FINISH', data)
                        else:  # set checkpoints
                            checkpoints = self.get_item('CHECKPOINTS', 'CHECKPOINTS')
                            checkpoints.append(data)
                            self.set_item('CHECKPOINTS', 'CHECKPOINTS', checkpoints)
                        # end if
                    # end if
                # end if
            # next index
        else:
            # for checking if a point is inside radius of 20, return True or False
            calculate_inside = lambda x_0, x_1, y_0, y_1: pow(x_0 - x_1, 2) + pow(y_0 - y_1, 2) <= 400
            # only 1 point can be deleted at a time
            # check if starting line is click
            start = self.get_item('CHECKPOINTS', 'START')
            if calculate_inside(adjusted_pos[0], start[0][0], adjusted_pos[1], start[0][1]):
                self.set_item('CHECKPOINTS', 'START', ((-1, -1), -1, (-1, -1), (-1, -1)))
                return
            # end if
            # check if finish line is click
            finish = self.get_item('CHECKPOINTS', 'FINISH')
            if calculate_inside(adjusted_pos[0], finish[0][0], adjusted_pos[1], finish[0][1]):
                self.set_item('CHECKPOINTS', 'FINISH', ((-1, -1), -1, (-1, -1), (-1, -1)))
                return
            # end if
            # check if any checkpoints is click, in the reverse order of setting
            checkpoints = self.get_item('CHECKPOINTS', 'CHECKPOINTS')
            for i in range(0, len(checkpoints)):
                if calculate_inside(adjusted_pos[0], checkpoints[i][0][0], adjusted_pos[1], checkpoints[i][0][1]):
                    del checkpoints[i]
                    self.set_item('CHECKPOINTS', 'CHECKPOINTS', checkpoints)
                    return
                # end if
            # next i
            # return an error if empty click
            return 'no_delete_point_selected'
        # end if

    # end function

    def get_point_data(self):
        # check if both coordinates are recorded
        for coordinate in self.coordinates:
            if coordinate == (-1, -1):
                return
            # end if
        # next coordinate
        rise = self.coordinates[0][1] - self.coordinates[1][1]
        run = self.coordinates[0][0] - self.coordinates[1][0]
        # if coordinates are the same
        if rise == 0 and run == 0:
            raise ZeroDivisionError
        # end if
        # function to calculate with respect to x and y
        calculate_y = lambda x: (rise * x + run * self.coordinates[0][1] - rise * self.coordinates[0][0]) / run
        calculate_x = lambda y: (run * y + rise * self.coordinates[0][0] - run * self.coordinates[0][1]) / rise
        # lists to record result for the calculation
        coordinates_by_x = []
        coordinates_by_y = []
        radius_square = []  # by x square, then by y square
        # calculate the end points of the track with variable x, given run is not 0
        if run != 0:
            colour = (0, 0, 0)
            x = self.coordinates[0][0]
            # increase x to find the first coordinate
            while colour != (255, 255, 255):
                x += 1
                y = calculate_y(x)
                try:  # might be going out the map
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
                try:  # might be going out the map
                    colour = self.img.getpixel((int(x), int(y)))[:3]
                except IndexError:
                    colour = (255, 255, 255)
                # end try
            # end while
            coordinates_by_x.append((x, y))
            radius_square.append(pow(coordinates_by_x[0][0] - coordinates_by_x[1][0], 2) +
                                 pow(coordinates_by_x[0][1] - coordinates_by_x[1][1], 2))
        # end if
        # calculate the end points of the track with variable y, given rise is not zero
        if rise != 0:
            colour = (0, 0, 0)
            y = self.coordinates[0][1]
            # increase y to find the first coordinate
            while colour != (255, 255, 255):
                y += 1
                x = calculate_x(y)
                try:  # might be going out the map
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
                try:  # might be going out the map
                    colour = self.img.getpixel((int(x), int(y)))[:3]
                except IndexError:
                    colour = (255, 255, 255)
                # end try
            # end while
            coordinates_by_y.append((x, y))
            radius_square.append(pow(coordinates_by_y[0][0] - coordinates_by_y[1][0], 2) +
                                 pow(coordinates_by_y[0][1] - coordinates_by_y[1][1], 2))
        # end if
        # if one of rise or run is zero
        if len(radius_square) == 1:
            # means one list will not be filled, then we can return the other one
            if not coordinates_by_x:
                return (((calculate_x(coordinates_by_y[0][1] - 1) + calculate_x(coordinates_by_y[1][1] + 1)) / 2,
                         (coordinates_by_y[0][1] + coordinates_by_y[1][1]) / 2), pow(radius_square[0], 0.5),
                        (calculate_x(coordinates_by_y[0][1] - 1), coordinates_by_y[0][1] - 1),
                        (calculate_x(coordinates_by_y[1][1] + 1), coordinates_by_y[1][1] + 1))
            else:
                return (((coordinates_by_x[0][0] + coordinates_by_x[1][0]) / 2,
                         (calculate_y(coordinates_by_x[0][0] - 1) + calculate_y(coordinates_by_x[1][0] + 1)) / 2),
                        pow(radius_square[0], 0.5),
                        (coordinates_by_x[0][0] - 1, calculate_y(coordinates_by_x[0][0] - 1)),
                        (coordinates_by_x[1][0] + 1, calculate_y(coordinates_by_x[1][0] + 1)))
            # end if
        if radius_square[0] < radius_square[1]:
            return (((coordinates_by_x[0][0] + coordinates_by_x[1][0]) / 2,
                     (calculate_y(coordinates_by_x[0][0] - 5) + calculate_y(coordinates_by_x[1][0] + 5)) / 2),
                    pow(radius_square[0], 0.5), (coordinates_by_x[0][0] - 5, calculate_y(coordinates_by_x[0][0] - 5)),
                    (coordinates_by_x[1][0] + 5, calculate_y(coordinates_by_x[1][0] + 5)))
        else:
            return (((calculate_x(coordinates_by_y[0][1] - 5) + calculate_x(coordinates_by_y[1][1] + 5)) / 2,
                     (coordinates_by_y[0][1] + coordinates_by_y[1][1]) / 2), pow(radius_square[1], 0.5),
                    (calculate_x(coordinates_by_y[0][1] - 5), coordinates_by_y[0][1] - 5),
                    (calculate_x(coordinates_by_y[1][1] + 5), coordinates_by_y[1][1] + 5))
        # end if

    # end procedure

    def get_item(self, section, key):
        try:
            return ast.literal_eval(self.config_obj[section][key])
        except ValueError:
            return self.config_obj[section][key]

    # end function

    def set_item(self, section, key, value):
        try:
            if isinstance(ast.literal_eval(value), type(self.get_item(section, key))):
                self.config_obj[section][key] = str(value)
        except ValueError:
            if isinstance(value, type(self.get_item(section, key))):
                self.config_obj[section][key] = str(value)

    # end procedure

    def save(self):
        pass

    def exit(self):
        pass

    @staticmethod
    def check_validity(file_path):
        if not os.path.isfile(file_path):  # file doesn't exist
            return False
        else:
            config_obj = ConfigParser()
            config_obj.read(file_path)
            sections = config_obj.sections()
            # sections not right
            if 'CHECKPOINTS' not in sections or 'TRACK' not in sections or 'CAR' not in sections or 'NN' not in sections:
                return False
            else:  # exists with correct sections
                return True
            # end if`
        # end if
    # end function


# end class


class Car(pygame.sprite.Sprite):

    def __init__(self, config, screen):
        super().__init__()
        self.config = config
        self.screen = screen
        self.original_car = pygame.image.load(os.path.join("resources", 'car.png'))
        self.original_car = pygame.transform.scale(self.original_car, (config.get_item('CAR', 'CAR LENGTH'),
                                                                       config.get_item('CAR', "CAR WIDTH")))
        self.image = self.original_car
        self.rect = self.image.get_rect(center=config.get_item('CHECKPOINTS', 'START')[0])
        self.vel_vector = pygame.math.Vector2(1, 0)
        self.angle = self.config.get_item('TRACK', 'START ANGLE')
        self.turn_angle = self.config.get_item('CAR', "TURNING ANGLE")
        self.direction = 0
        self.alive = True
        self.radars = []
        self.radar_angles = [-60, -30, 0, 30, 60]
        self.speed = self.config.get_item('CAR', 'SPEED') / 60
        self.reward = 0

    def drive(self):
        self.rect.center += self.vel_vector * self.speed

    def turn(self):
        if self.direction == 1:
            self.angle -= self.turn_angle
            self.vel_vector.rotate_ip(self.turn_angle)
        if self.direction == -1:
            self.angle += self.turn_angle
            self.vel_vector.rotate_ip(-self.turn_angle)

        self.image = pygame.transform.rotozoom(self.original_car, self.angle, 0.1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def collide(self):
        mask = pygame.mask.from_surface(self.image).outline()
        for coordinate in mask:
            if self.screen.get_at(coordinate) == pygame.Color('white'):
                self.alive = False
                break

    def observe(self):
        self.radars.clear()
        for radar_angle in self.radar_angles:
            length = 0
            x = int(self.rect.center[0])
            y = int(self.rect.center[1])

            while not self.screen.get_at((x, y)) == pygame.Color('white') and length < 200:
                length += 1
                x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
                y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)

            # Draw Radar, can be deleted
            pygame.draw.line(self.screen, (255, 254, 255, 255), self.rect.center, (x, y), 1)
            pygame.draw.circle(self.screen, (0, 255, 0, 0), (x, y), 3)
            # calculate distance
            distance = int(math.sqrt(math.pow(self.rect.center[0] - x, 2) + math.pow(self.rect.center[1] - y, 2)))
            self.radars.append(distance)

    def update(self, direction):
        self.direction = direction
        self.drive()
        self.turn()
        self.collide()
        self.observe()
        return self.radars, self.reward, self.alive


# mirror sampling
def sign(kid_id):
    if kid_id % 2 == 0:
        return -1
    else:
        return 0


# NN optimiser using momentum
class SGD:
    def __init__(self, params, learning_rate, momentum=0.9):
        self.vector = np.zeros_like(params).astype(np.float32)
        self.learning_rate = learning_rate
        self.momentum = momentum

    def new_gradient(self, gradients):
        self.vector = self.momentum * self.vector + (1 - self.momentum) * gradients
        return self.learning_rate * self.vector


def build_net():
    def linear(n_in, n_out):  # 网络线性层
        w = np.random.randn(n_in * n_out).astype(np.float32) * .1  # 矩阵大小为输入乘以输出
        b = np.random.randn(n_out).astype(np.float32) * .1  # 矩阵大小为输出
        return (n_in, n_out), np.concatenate((w, b))

    s0, p0 = linear(5, 30)
    s1, p1 = linear(30, 20)
    s2, p2 = linear(20, 1)
    return [s0, s1, s2], np.concatenate((p0, p1, p2))


def reshape_params(shapes, params):
    temp_params = []
    start = 0
    for i, shape in enumerate(shapes):
        n_w = shape[0] * shape[1]
        n_b = shape[1]
        temp_params += [params[start: start + n_w].reshape(shape),
                        params[start + n_w: start + n_w + n_b].reshape((1, shape[1]))]
        start += (n_w + n_b)
        return temp_params


def get_action(params, data):
    data = data[np.newaxis, :]
    data = np.tanh(data.dot(params[0]) + params[1])
    data = np.tanh(data.dot(params[2]) + params[3])
    data = data.dot(params[4]) + params[5]
    return np.argmax(data, axis=1)[0]


class Generation:
    def __init__(self, num, config, screen):
        self.cars = pygame.sprite.Group()
        self.alive_status = []
        self.ep_r = []
        self.radars = []
        for i in range(num):
            self.cars.add(Car(config, screen))
            self.alive_status.append(True)
            self.ep_r.append(0)
        # next i

    def update(self, actions):
        for i, car in enumerate(self.cars):
            if actions[i] > 0.7:
                s, r, alive = car.update(1)
            elif actions[i] < -0.7:
                s, r, alive = car.update(-1)
            else:
                s, r, alive = car.update(0)


def run(screen, config):
    """Run the GUI"""
    clock = pygame.time.Clock()
    car = pygame.sprite.Group()
    car.add(Car(config, screen))
    while True:
        # User input and control
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # check for quit
                pygame.quit()
        # next event
        screen.fill('black')
        car.update()
        # Drawing here
        car.draw(screen)
        pygame.display.flip()  # flip the display to renew
        clock.tick(60)  # limit the frame rate to 60


if __name__ == '__main__':
    screen = pygame.display.set_mode((1400, 900))
    track_config = Config('track1.png')
    track_config.set_item('CHECKPOINTS', 'START', ((500, 500), 10, (510, 510), (490, 490)))
    track_config.set_item('CAR', 'SPEED', 300.0)
    run(screen, track_config)
# end if
