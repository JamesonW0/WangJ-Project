"""
import tkinter
from tkinter import filedialog

tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing

folder_path = filedialog.askopenfilename()

print(folder_path)
"""


import pygame

# Colours
black = (0, 0, 0)
white = (255, 255, 255)
blue = (50, 50, 255)
yellow = (255, 255, 0)
# Initiate
pygame.init()
# Blank screen
size = (640, 480)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Test')  # Set title
done = False  # Exit pygame flag set to false
clock = pygame.time.Clock()  # Manage how fast the screen refreshes



class Button(pygame.sprite.Sprite):
    def __init__(self, centre, width, height, colour, action):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(colour)
        self.rect = self.image.get_rect()
        self.rect.center = centre
        self.action = action

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)


button_group = pygame.sprite.Group()
button_group.add(Button((100, 100), 100, 50, blue, 'button'))

# Main
while not done:
    # User input and control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                button_group.update(event.pos)
        # End if
    # Next event
    # game settings
    screen.fill(black)
    # Drawing here
    button_group.draw(screen)
    pygame.display.flip()  # flip the display to renew
    clock.tick(60)  # tick the clock over
# End while

pygame.quit()