import pygame
import os
import math
import sys
import time
import neat


class Car:

    def __init__(self, config, track):
        # load initialising data from config
        self.car_dimension = (45, 25)  # **
        self.centre = [500, 500]  # **
        self.angle = 60   # **

        # load speed variables
        self.max_speed = 10  # **
        self.min_speed = 5  # **
        self.initial_speed = 7  # **
        self.speed = 5
        # flag for speed to be set after the first radar observation
        self.speed_set = False

        self.car_sprite = pygame.image.load('resources/car.png')
        self.car_sprite = pygame.transform.scale(self.car_sprite, self.car_dimension)
        self.rotated_sprite = self.car_sprite
        self.car_rect = self.rotated_sprite.get_rect()
        self.car_rect.center = self.centre

        self.track = track
        # Get the track colour, for collision and radar
        self.track_colour = self.track.get_at(tuple(self.centre))

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
    # end procedure

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.car_rect)  # draw the car
        self.draw_radar(screen)  # draw radars
    # end procedure

    def update(self):
        # Rotate the car sprite
        self.rotated_sprite = self.rotate_centre(self.car_sprite, self.angle)
        # Move it on x-direction
        self.centre[0] += math.cos(math.radians(-self.angle)) * self.speed
        # Move it on y-direction
        self.centre[1] += math.sin(math.radians(-self.angle)) * self.speed

        # update car_rect
        self.car_rect = self.rotated_sprite.get_rect()
        self.car_rect.center = self.centre

        # check collision
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

        # Set speed for the first time
        if not self.speed_set:
            self.speed = self.initial_speed
            self.speed_set = True
        # end if

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
        while self.track.get_at((x, y)) == self.track_colour and length < 200:
            length += 1
            x = int(self.centre[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
            y = int(self.centre[1] - math.sin(math.radians(self.angle + radar_angle)) * length)

        # calculate distance
        dist = int(math.sqrt(math.pow(self.centre[0] - x, 2) + math.pow(self.centre[1] - y, 2)))
        self.radars.append([(x, y), dist])
    # end procedure

    def draw_radar(self, screen):
        for radar in self.radars:
            end_pos = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.centre, end_pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), end_pos, 3)
        # next radar
    # end procedure

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
        reward = self.distance/self.time
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


# game function
def run():
    """Run the GUI"""
    pygame.init()
    screen = pygame.display.set_mode((1400, 900))
    clock = pygame.time.Clock()
    time.sleep(5)
    car = Car(0, 0)

    while True:
        # User input and control
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        # next event
        car.update()
        # Drawing here
        screen.fill('white')
        car.draw(screen)
        pygame.display.flip()  # flip the display to renew
        clock.tick(60)  # limit the frame rate to 60
    # end while
# end procedure


# Main
if __name__ == '__main__':
    run()
# end if

# nn_config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
#                                    neat.DefaultStagnation, 'file_path')

# create car instance and net for each genome
# for i, genome in genomes:
#    net = neat.nn.FeedForwardNetwork.create(genome, config)
#    self.nets.append(net)
#    genome.fitness = 0
#    self.cars.append(Car(self.track_config, self.track))
# next genome/i
