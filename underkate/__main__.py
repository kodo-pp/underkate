from .player import get_player
from .vector import Vector

import pygame


def main():
    pygame.init()
    pygame.display.set_mode((800, 600))
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    player = get_player()
    while True:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        pressed_keys = pygame.key.get_pressed()
        mx, my = 0, 0
        if pressed_keys[pygame.K_LEFT]:
            mx -= 1
        if pressed_keys[pygame.K_RIGHT]:
            mx += 1
        if pressed_keys[pygame.K_UP]:
            my -= 1
        if pressed_keys[pygame.K_DOWN]:
            my += 1

        player.set_moving(mx, my)

        player.update(time_delta)

        screen.fill((0, 0, 0))
        player.draw(screen)
        pygame.display.flip()



if __name__ == '__main__':
    main()
