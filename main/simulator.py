import gzip
import random
import pygame
import ast
from configparser import ConfigParser
from PIL import Image
import os
import math
import neat
import sys
import time
import pickle
import neat.six_util
import neat.math_util


class Config:
    """Reading and writing the config file"""

    def __init__(self, track_name):
        # initiate the track
        self.track_config_path = 'tracks/' + track_name[:6] + 'config.txt'
        self.nn_config_path = 'NN/NN' + track_name[:6] + 'config.txt'
        self.track_path = './tracks/' + track_name + '.png'
        self.img = Image.open(self.track_path)
        # initiate the corresponding config object for the track
        self.track_config_obj = ConfigParser()
        if self.check_validity(self.track_config_path):
            self.track_config_obj.read(self.track_config_path)
        else:
            self.new_config()
        # end if
        # two variables for amend_point
        self.coordinates = [(-1, -1), (-1, -1)]
        self.last_cursor = None

    # end procedure

    def new_config(self):
        # size and ratio for showing onto the pygame screen and converting data
        size = self.img.size
        self.track_config_obj['CHECKPOINTS'] = {
            'START': ((-1, -1), -1, (-1, -1), (-1, -1)),  # (midpoint, radius, edge_1, edge_2)
            'FINISH': ((-1, -1), -1, (-1, -1), (-1, -1)),  # (midpoint, radius, edge_1, edge_2)
            'CHECKPOINTS': [],  # [(midpoint, radius, edge_1, edge_2), (midpoint, radius, edge_1, edge_2), ...]
        }
        self.track_config_obj['DISPLAY'] = {
            'ORIGINAL SIZE': size,  # (width, height)
            'SIMULATOR SIZE': (1200, 900),  # (width, height)
        }
        self.track_config_obj['TRACK'] = {
            'START ANGLE': 0,  # automatically filled by the program, do not change
        }
        self.track_config_obj['CAR'] = {
            'SPEED': 10.0,  # Number of pixels the car can travel within 1 second, at the start
            'MAX SPEED': 15.0,  # Maximum speed the car can travel
            'MIN SPEED': 5.0,  # Maximum speed the car can travel
            'SPEED STEP': 1.0,  # The value for the speed to change each time
            'LENGTH': 60.0,  # The length of the car in pixels
            'WIDTH': 60.0,  # The width of the car in pixels
            'TURNING ANGLE': 7,  # angle the car can turn in degrees, max 10 degrees
        }
        self.track_config_obj['NN'] = {
            'LEARNING RATE': 0.01,  # learning rate of the neural network
            'MUTATION RATE': 0.01,  # mutation rate of the neural network
            'POPULATION': 20,  # number of neural networks in one generation, have to be even
            'GENERATIONS': 1000,  # number of generations
            'TIME': 20,  # Time allowed for each generation
            'FITNESS THRESHOLD': 0.0,  # fitness threshold of the neural network, automatically filled by the program
        }

    # end procedure

    def amend_point(self, cursor, mouse_pos):
        # detect if any errors occur, information is returned shows which error is it
        if self.img.getpixel((mouse_pos[0], mouse_pos[1]))[:3] == (255, 255, 255):
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
                    self.coordinates[index] = mouse_pos
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
            if calculate_inside(mouse_pos[0], start[0][0], mouse_pos[1], start[0][1]):
                self.set_item('CHECKPOINTS', 'START', ((-1, -1), -1, (-1, -1), (-1, -1)))
                return
            # end if
            # check if finish line is click
            finish = self.get_item('CHECKPOINTS', 'FINISH')
            if calculate_inside(mouse_pos[0], finish[0][0], mouse_pos[1], finish[0][1]):
                self.set_item('CHECKPOINTS', 'FINISH', ((-1, -1), -1, (-1, -1), (-1, -1)))
                return
            # end if
            # check if any checkpoints is click, in the reverse order of setting
            checkpoints = self.get_item('CHECKPOINTS', 'CHECKPOINTS')
            for i in range(0, len(checkpoints)):
                if calculate_inside(mouse_pos[0], checkpoints[i][0][0], mouse_pos[1], checkpoints[i][0][1]):
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
            colour_a = None
            x = self.coordinates[0][0]
            # increase x to find the first coordinate
            while colour_a != 0:
                x += 1
                y = calculate_y(x)
                try:  # might be going out the map
                    colour_a = self.img.getpixel((int(x), int(y)))[-1]
                except IndexError:
                    colour_a = 0
                # end try
            # end while
            coordinates_by_x.append((x, y))
            # decrease x to find the second coordinate
            colour_a = None
            x = self.coordinates[0][0]
            while colour_a != 0:
                x -= 1
                y = calculate_y(x)
                try:  # might be going out the map
                    colour_a = self.img.getpixel((int(x), int(y)))[-1]
                except IndexError:
                    colour_a = 0
                # end try
            # end while
            coordinates_by_x.append((x, y))
            radius_square.append(pow(coordinates_by_x[0][0] - coordinates_by_x[1][0], 2) +
                                 pow(coordinates_by_x[0][1] - coordinates_by_x[1][1], 2))
        # end if
        # calculate the end points of the track with variable y, given rise is not zero
        if rise != 0:
            colour_a = None
            y = self.coordinates[0][1]
            # increase y to find the first coordinate
            while colour_a != 0:
                y += 1
                x = calculate_x(y)
                try:  # might be going out the map
                    colour_a = self.img.getpixel((int(x), int(y)))[-1]
                except IndexError:
                    colour_a = 0
                # end try
            # end while
            coordinates_by_y.append((x, y))
            # decrease x to find the second coordinate
            colour_a = None
            y = self.coordinates[0][1]
            while colour_a != 0:
                y -= 1
                x = calculate_x(y)
                try:  # might be going out the map
                    colour_a = self.img.getpixel((int(x), int(y)))[-1]
                except IndexError:
                    colour_a = 0
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
    # end function

    def get_item(self, section, key):
        try:
            return ast.literal_eval(self.track_config_obj[section][key])
        except ValueError:
            return self.track_config_obj[section][key]

    # end function

    def set_item(self, section, key, value):
        try:
            if isinstance(ast.literal_eval(value), type(self.get_item(section, key))):
                self.track_config_obj[section][key] = value
        except ValueError:
            if isinstance(value, type(self.get_item(section, key))):
                self.track_config_obj[section][key] = str(value)

    # end procedure

    def save(self):
        checkpoint_0 = self.get_item('CHECKPOINTS', 'CHECKPOINTS')[0][0]
        start = self.get_item('CHECKPOINTS', 'START')[0]
        start_angle = int(math.degrees(math.atan((checkpoint_0[1] - start[1])/(checkpoint_0[0] - start[0]))))
        self.set_item('TRACK', 'START ANGLE', start_angle)

        with open(self.track_config_path, 'w') as file:
            self.track_config_obj.write(file)
        # end with
        nn_config_obj = ConfigParser()
        if os.path.isfile(self.nn_config_path):
            nn_config_obj.read(self.nn_config_path)
        else:
            nn_config_obj.read('NN/config_temp.txt')

        nn_config_obj.set('NEAT', 'pop_size', str(self.get_item('NN', 'POPULATION')))
        nn_config_obj.set('DefaultGenome', 'activation_mutate_rate', str(self.get_item('NN', 'MUTATION RATE')))

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


class Car:

    def __init__(self, config, track):
        # initialise car sprite object and its rotate object
        # load car dimension (x, y) from config
        self.car_dimension = (config.get_item('CAR', 'LENGTH'), config.get_item('CAR', 'WIDTH'))
        self.car_sprite = pygame.image.load('resources/car.png')
        self.car_sprite = pygame.transform.scale(self.car_sprite, self.car_dimension)
        self.rotated_sprite = self.car_sprite

        # load starting data from config
        self.centre = [int(config.get_item('CHECKPOINTS', 'START')[0][0]), int(config.get_item('CHECKPOINTS', 'START')[0][1])]
        self.car_rect = self.rotated_sprite.get_rect()
        self.car_rect.center = self.centre
        self.angle = config.get_item('TRACK', 'START ANGLE')

        # load speed variables
        self.max_speed = config.get_item('CAR', 'MAX SPEED')
        self.min_speed = config.get_item('CAR', 'MIN SPEED')
        self.initial_speed = config.get_item('CAR', 'SPEED')
        self.speed = 0

        self.speed_set = False  # flag for default speed to be set

        self.radars = []  # list of radars
        self.drawing_radars = []  # list of radars to be drawn

        self.alive = True  # alive status for the car

        self.corners = []  # position of the corners of the car to check alive
        # referential data to locate the corner [[angles(rad)], length]
        internal_angle = math.atan(self.car_dimension[1] / self.car_dimension[0])
        self.corner_ref = [[internal_angle, math.pi - internal_angle, math.pi + internal_angle, -internal_angle],
                           (math.sqrt(self.car_dimension[0] ** 2 + self.car_dimension[1] ** 2)) * 0.5 * 0.92]

        # attributes for reward function
        self.distance = 0  # total distance driven
        self.time = 0  # total time passed
        self.checkpoints = config.get_item('CHECKPOINTS', 'CHECKPOINTS')
        self.checkpoints.append(config.get_item('CHECKPOINTS', 'FINISH'))
        # cut other irrelevant items
        for i in range(len(self.checkpoints)):
            self.checkpoints[i] = self.checkpoints[i][:2]
        # next i
        self.old_dist_to_checkpoint = math.sqrt((self.centre[0] - self.checkpoints[0][0][0]) ** 2 +
                                                (self.centre[1] - self.checkpoints[0][0][1]) ** 2)  # Pythagoras
        self.new_dist_to_checkpoint = 0

        self.track = track
        # Get the track colour, for collision and radar
        self.track_colour = self.track.get_at(tuple(self.centre))
    # end procedure

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.car_rect)  # draw the car
        self.draw_radar(screen)  # draw radars
    # end procedure

    def draw_radar(self, screen):
        for radar in self.radars:
            end_pos = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.centre, end_pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), end_pos, 3)
        # next radar

    # end procedure

    def check_collision(self):
        self.alive = True
        for point in self.corners:
            # If any corner not on the track means a crash
            try:
                if self.track.get_at((int(point[0]), int(point[1]))) != self.track_colour:
                    self.alive = False
                    break
                # end if
            except IndexError:
                self.alive = False
                break
            # end try
        # next point
    # end procedure

    def observe(self, radar_angle):
        # set initial radar values
        length = 0
        x = int(self.centre[0])
        y = int(self.centre[1])

        # loop to take observation
        try:
            while self.track.get_at((x, y)) == self.track_colour and length < 200:
                length += 1
                x = int(self.centre[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
                y = int(self.centre[1] - math.sin(math.radians(self.angle + radar_angle)) * length)
        except IndexError:
            pass

        # calculate distance
        dist = int(math.sqrt(math.pow(self.centre[0] - x, 2) + math.pow(self.centre[1] - y, 2)))
        self.radars.append([(x, y), dist])

    # end procedure

    def update(self):

        # Rotate the car sprite
        self.rotated_sprite = self.rotate_centre(self.car_sprite, self.angle)
        # Move it on x-direction
        self.centre[0] += math.cos(math.radians(-self.angle)) * self.speed
        # Move it on y-direction
        self.centre[1] += math.sin(math.radians(-self.angle)) * self.speed
        # If the car sprite gets too close to the edge (preset value a pixel)
        # X: MAX(X_POS, a), MIN(X_POS, SCREEN_WIDTH - 100 - a)
        # Y: MAX(Y_POS, a), MIN(Y_POS, SCREEN_WIDTH - 100 - a)

        # update car_rect
        self.car_rect = self.rotated_sprite.get_rect()
        self.car_rect.center = self.centre

        # Increment distance and time
        self.distance += self.speed
        self.time += 1

        # Get corners of the car
        self.corners.clear()
        for internal_angle in self.corner_ref[0]:
            # calculate the corners given the data
            delta_x = math.cos(-math.radians(self.angle) + internal_angle) * self.corner_ref[1]
            delta_y = math.sin(-math.radians(self.angle) + internal_angle) * self.corner_ref[1]
            self.corners.append([self.centre[0] + delta_x, self.centre[1] + delta_y])
        # next internal_angle

        # Given the corners of the car, check if there is a collision
        self.check_collision()

        # Take radar readings
        self.radars.clear()
        for angle in range(-60, 61, 30):  # from -60 to 60 with step 30
            self.observe(angle)
        # next angle

        # Set The Speed To 20 For The First Time
        if not self.speed_set:
            self.speed = self.initial_speed
            self.speed_set = True
        # end if

    def get_data(self):
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)
        # next radar/i
        return return_values

    # end function

    def get_alive(self):
        return self.alive

    # end function

    def get_reward(self):
        # should be changed
        self.new_dist_to_checkpoint = math.sqrt((self.centre[0] - self.checkpoints[0][0][0]) ** 2 +
                                                (self.centre[1] - self.checkpoints[0][0][1]) ** 2)  # Pythagoras
        reward = self.old_dist_to_checkpoint - self.new_dist_to_checkpoint
        reward += self.speed  # distance reward
        self.old_dist_to_checkpoint = self.new_dist_to_checkpoint

        if (self.centre[0] - self.checkpoints[0][0][0]) ** 2 + (self.centre[1] - self.checkpoints[0][0][1]) ** 2 <= \
                (self.checkpoints[0][1]/2) ** 2:
            del self.checkpoints[0]
            if len(self.checkpoints) == 0:
                self.alive = False
                return 10000
        return reward
    # end function

    def change_speed(self, delta):
        if self.min_speed <= self.speed + delta <= self.max_speed:
            self.speed += delta
        # end if
    # end procedure

    def change_direction(self, delta):
        self.angle += delta
    # end procedure

    @staticmethod
    def rotate_centre(img, angle):
        # Rotate The Rectangle
        rotated_img = pygame.transform.rotozoom(img, angle, 1)
        return rotated_img
    # end function


# end class


class Train:

    def __init__(self, track_name, screen):
        # empty list of cars and NN
        self.cars = []
        self.nets = []
        self.population = None

        # get track
        self.track_path = './tracks/' + track_name + '.png'
        self.track = pygame.image.load('tracks/track1.png')
        self.track = pygame.transform.scale(self.track, (1200, 900))

        # load config file path
        self.nn_config_path = './NN/NN' + track_name[-1] + 'config.txt'

        # load track and adjust the size
        self.track = pygame.image.load(self.track_path)
        self.track = pygame.transform.scale(self.track, (1200, 900))

        # load config files
        self.track_config = Config(track_name)
        self.nn_config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                            neat.DefaultStagnation, self.nn_config_path)

        # load relevant variables from track config
        self.speed_step = self.track_config.get_item('CAR', 'SPEED STEP')
        self.turning_angle = self.track_config.get_item('CAR', "TURNING ANGLE")
        self.max_time = self.track_config.get_item('NN', 'TIME')

        # load screen
        self.screen = screen

        self.generation_no = 0  # store the number of generation
    # end procedure

    def eval_choice(self):
        for i, car in enumerate(self.cars):
            output = self.nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.change_direction(self.turning_angle)  # Left
            elif choice == 1:
                car.change_direction(-self.turning_angle)  # Right
            elif choice == 2:
                car.change_speed(self.speed_step)  # Accelerate
            else:
                car.change_speed(-self.speed_step)  # Decelerate
            # end if
        # next car/i
    # end procedure

    def generation(self, genomes, config):
        # empty the car and net lists for the next generation
        self.cars.clear()
        self.nets.clear()

        # create car instance and net for each genome
        for i, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            genome.fitness = 0
            self.cars.append(Car(self.track_config, self.track))
        # next genome/i

        # update generation counter and set time counter
        self.generation_no += 1
        start_time = time.time()

        # pygame
        clock = pygame.time.Clock()
        while True:
            # Exit On Quit Event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                # end if
            # next event

            self.eval_choice()  # get action from NN and pass it to cars

            # get alive and pass the reward to NN
            still_alive = 0
            for i, car in enumerate(self.cars):
                if car.get_alive():
                    still_alive += 1
                    car.update()
                    genomes[i][1].fitness += car.get_reward()
                # end if
            # next car/i

            # end the generation if no alive or time exceeds
            if still_alive == 0 or time.time() - start_time >= self.max_time:
                #if self.generation_no % 10 == 0:
                    #self.save_checkpoint(self.nn_config, self.population.population, self.population.species, self.generation_no)
                break
            # end if

            self.screen.fill('white')
            self.screen.blit(self.track, (0, 0))
            for car in self.cars:
                if car.get_alive():
                    car.draw(self.screen)
                # end if
            # next car

            # Drawing here
            pygame.draw.line(self.screen, (143, 170, 220), (1203, 0), (1203, 900), 3)

            pygame.display.flip()
            clock.tick(60)  # 60 FPS
        # end while
    # end procedure

    def run(self):
        # Create Population And Add Reporters
        self.population = neat.Population(self.nn_config)
        self.population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        self.population.add_reporter(stats)
        #self.population.add_reporter(neat.Checkpointer(10))

        # Run Simulation For A Maximum of 1000 Generations
        try:
            self.population.run(self.generation, 1000)
        except pygame.error:
            pygame.init()

    def evaluate(self, nn_path):
        pass

    def save_checkpoint(self, config, population, species_set, generation):
        """ Save the current simulation state. """
        filename = '0' + str(self.generation_no)
        print("Saving checkpoint to {0}".format(filename))

        with gzip.open(filename, 'w', compresslevel=5) as f:
            data = (generation, config, population, species_set, random.getstate())
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        # end with
    # end procedure


if __name__ == "__main__":
    # Load track config
    track_config = Config('track1')
    track_config.set_item('CAR', 'LENGTH', 45.0)
    track_config.set_item('CAR', 'WIDTH', 26.0)
    track_config.set_item('CAR', 'SPEED', 7.0)
    track_config.set_item('CAR', 'MAX SPEED', 10.0)
    track_config.set_item('CAR', 'MIN SPEED', 5.0)
    track_config.set_item('CAR', 'SPEED STEP', 1.0)
    track_config.save()

    pygame.init()
    screen = pygame.display.set_mode((1400, 900))

    g = Train('track1', screen)
    g.run()
