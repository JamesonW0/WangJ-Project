import pygame

# Colours
black = (0, 0, 0)
white = (255, 255, 255)
blue = (50, 50, 255)
yellow = (255, 255, 0)

# Initiate
pygame.init()
# Blank screen
size = (1200, 800)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Test')  # Set title
done = False  # Exit pygame flag set to false
clock = pygame.time.Clock()  # Manage how fast the screen refreshes


# Track class
class Track(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('example.png').convert_alpha(), (1024, 576))
        self.rect = self.image.get_rect(center=(600, 400))
        self.mask = pygame.mask.from_surface(self.image)


# User class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill('red')
        self.rect = self.image.get_rect(center=(300, 300))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.mask = pygame.mask.from_surface(self.image)
        if pygame.mouse.get_pos():
            self.rect.center = pygame.mouse.get_pos()



track = pygame.sprite.GroupSingle(Track())
player = pygame.sprite.GroupSingle(Player())
###
# Main loop
while not done:
    # User input and control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        # End if
    # Next event
    # game settings
    screen.fill(white)  # Fill screen with white
    # Drawing here
    track.draw(screen)
    player.update()
    player.draw(screen)

    # collision

    if pygame.sprite.spritecollide(player.sprite, track, False, pygame.sprite.collide_mask):
        player.sprite.image.fill('green')
    else:
        player.sprite.image.fill('red')

    pygame.display.flip()  # flip the display to renew
    clock.tick(60)  # tick the clock over
# End while

pygame.quit()
