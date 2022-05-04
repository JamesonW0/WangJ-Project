import multiprocessing as mp
import numpy as np
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
clock = pygame.time.Clock()  # Manage how fast the screen refreshes

###
# Main
def run():
    done = False
    while not done:
        # User input and control
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            # End if
        # Next event
        # game settings
        screen.fill(black)
        # Drawing here
        pygame.draw.rect(screen, blue, (1, 1, 200, 150))
        pygame.draw.circle(screen, yellow, (200, 165), 40, 0)
        pygame.display.flip()  # flip the display to renew
        clock.tick(60)  # tick the clock over
# End while


cores = mp.cpu_count() - 1


def get_reward(size):
    array_1 = np.random.randn(size).astype(np.float32)
    array_1.reshape((1, size))
    array_2 = np.random.randn(size).astype(np.float32)
    array_2.reshape((size, 1))
    return np.dot(array_1, array_2)


if __name__ == '__main__':
    pool = mp.Pool(processes=cores)
    jobs = pool.apply(run)