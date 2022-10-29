import pygame
import sys
import math

pygame.init()
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()

car_dimension = (40, 30)
car = pygame.image.load('resources/car.png')
car = pygame.transform.scale(car, (40, 30))

internal_angle = math.atan(car_dimension[0] / car_dimension[1])
corner_ref = [[internal_angle, math.pi - internal_angle, math.pi + internal_angle, -internal_angle],
                   (math.sqrt(car_dimension[0] ** 2 + car_dimension[1] ** 2)) * 0.5 * 0.85]

angle = 0
centre = [400, 400]
corners = []

for internal_angle in corner_ref[0]:
    # calculate the corners given the data
    delta_x = math.cos(math.radians(angle) + internal_angle) * corner_ref[1]
    delta_y = math.sin(math.radians(angle) + internal_angle) * corner_ref[1]
    corners.append([centre[0] + delta_x, centre[1] + delta_y])

while True:
    # Exit On Quit Event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        # end if
        # next event

    screen.fill('white')
    screen.blit(car, centre)
    for coords in corners:
        pygame.draw.circle(screen, (0, 255, 0), coords, 3)

    pygame.display.flip()
    clock.tick(60)
