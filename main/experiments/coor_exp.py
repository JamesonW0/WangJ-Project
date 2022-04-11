import pygame
from pygame import gfxdraw
import math
# Colours
black = (0, 0, 0)
white = (255, 255, 255)
blue = (50, 50, 255)
yellow = (255, 255, 0)

# Initiate
pygame.init()
# Blank screen
size = (1000, 800)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Test')  # Set title
done = False  # Exit pygame flag set to false
clock = pygame.time.Clock()  # Manage how fast the screen refreshes

###
# Main
while not done:
    # User input and control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        # End if
    # Next event
    # game settings
    screen.fill(white)
    # Drawing here
    pygame.draw.line(screen, black, (100, 65), (99, 689), 1)
    for i in range(854):
        pygame.gfxdraw.pixel(screen, i, round((624*i-13390)/754), black)
    pygame.display.flip()  # flip the display to renew
    clock.tick(60)  # tick the clock over
# End while

pygame.quit()