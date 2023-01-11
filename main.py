import pygame
import button


class Game:
    screen = None
    aliens = []
    rockets = []
    alienBullets = []
    lost = False

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        done = False

        hero = Hero(self, width / 2, height - 20)
        generator = Generator(self)
        rocket = None

        lastShoot = pygame.time.get_ticks()
        lastShootCooldown = 560

        while not done:
            if len(self.aliens) == 0:
                self.displayText("VICTORY ACHIEVED", 600, 400)
                self.displayText("Naciśnij ESCAPE aby powrócić do menu", 600, 600)

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_ESCAPE] and len(self.aliens) == 0:  # konczenie gry escapem po wygraniu
                done = True
            if pressed[pygame.K_BACKSPACE]:  # szybkie czyszcenie alienów backspacem
                self.aliens.clear()
            if pressed[pygame.K_LEFT]:
                hero.x -= 2 if hero.x > 20 else 0
            elif pressed[pygame.K_RIGHT]:
                hero.x += 2 if hero.x < width - 20 else 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not self.lost:
                    now = pygame.time.get_ticks()
                    if now - lastShoot >= lastShootCooldown:
                        self.rockets.append(Rocket(self, hero.x-6, hero.y-80))
                        lastShoot = pygame.time.get_ticks()

            pygame.display.flip()
            self.clock.tick(60)
            self.screen.fill((0, 0, 0))

            #self.alienAttackLast = pygame.time.get_ticks()
            #self.alienAttackCooldown = 10

            attack = 0
            for alien in self.aliens:
                alien.draw()
                alien.checkCollision(self)
                if (alien.y > height-(height/6)):
                    self.lost = True
                    self.displayText("YOU DIED")

                if (alien.x) > (self.width - (self.width/20)):
                    for tabalien in self.aliens:
                        if tabalien.row == alien.row:
                            tabalien.direction = 0
                            alien.direction = 0

                elif (alien.x) < (self.width/30):
                    alien.x += (alien.sidewalkStep *2)
                    for tabalien in self.aliens:
                        if tabalien.row == alien.row:
                            tabalien.direction = 1
                            alien.direction = 1

                #self.now = pygame.time.get_ticks()
                #if self.now - self.alienAttackLast >= self.alienAttackCooldown:
                #    self.alienAttackLast = self.now
                #    self.alienBullets.append(AlienBullet(self, alien.x, alien.y))

            for rocket in self.rockets:
                rocket.draw()

            for bullet in self.alienBullets:
                bullet.draw()

            if not self.lost: hero.draw()

    def displayText(self, text, x=None, y=None):
        if x is None and y is None:
            x = self.width
            y = self.height
        pygame.font.init()
        font = pygame.font.SysFont('Arial', 50)
        textsurface = font.render(text, False, (180, 220, 62))
        self.screen.blit(textsurface, (x/2.5, y/2.5))


class Alien:
    def __init__(self, game, x, y, row, position):
        self.x = x
        self.game = game
        self.y = y
        self.size = 30
        self.row = row
        self.position = position

        self.goingDownLast = pygame.time.get_ticks()
        self.goingDownCooldown = 5000

        self.direction = 1
        self.sidewalkLast = pygame.time.get_ticks()
        self.sidewalkCooldown = 19
        self.sidewalkStep = 6

    def goingDown(self):
        now = pygame.time.get_ticks()
        if now - self.goingDownLast >= self.goingDownCooldown:
            self.goingDownLast = now
            self.y += 30


    def sidewalk(self):
        now = pygame.time.get_ticks()
        def left():
            self.x -= self.sidewalkStep
        def right():
            self.x += self.sidewalkStep
        if now - self.sidewalkLast >= self.sidewalkCooldown:
            self.sidewalkLast = now
            if self.direction == 0:
                left()
            else:
                right()


    def draw(self):
        pygame.draw.rect(self.game.screen,
                         (81, 43, 88),
                         pygame.Rect(self.x, self.y, self.size, self.size))
        self.goingDown()
        self.sidewalk(self)

    def checkCollision(self, game):
        for rocket in game.rockets:
            if (rocket.x < self.x + self.size and
                    rocket.x > self.x - self.size and
                    rocket.y < self.y + self.size and
                    rocket.y > self.y - self.size):
                game.rockets.remove(rocket)
                game.aliens.remove(self)

class AlienRed(Alien):
    def draw(self):
        pygame.draw.rect(self.game.screen,
                         (255, 0, 0),
                         pygame.Rect(self.x, self.y, self.size, self.size))
        self.goingDown()
        self.sidewalk()
class AlienGreen(Alien):
    def draw(self):
        pygame.draw.rect(self.game.screen,
                         (0, 255, 0),
                         pygame.Rect(self.x, self.y, self.size, self.size))
        self.goingDown()
        self.sidewalk()
class AlienBlue(Alien):
    def draw(self):
        pygame.draw.rect(self.game.screen,
                         (0, 0, 255),
                         pygame.Rect(self.x, self.y, self.size, self.size))
        self.goingDown()
        self.sidewalk()

class Hero:
    def __init__(self, game, x, y):
        self.x = x
        self.game = game
        self.y = y

    def draw(self):
        playerImage = pygame.image.load('spaceship.png')
        self.game.screen.blit(playerImage, (self.x-40, self.y-80))
        # pygame.draw.rect(self.game.screen,
        #                  (255, 0, 0),
        #                  pygame.Rect(self.x, self.y, 8, 5)) # serokość, wysokość

class Generator:
    def __init__(self, game):
        margin = 30  # margines
        width = 50  # marginesy alienów

        gameMarginStart = margin + int(game.width / 6)
        gameMarginStop = int(game.width - (game.width / 6) - margin)

        start=margin + int(game.height / 12)
        stop=start + int(game.height / 16)
        step=int(game.height / 20)

        row = 0

        for y in range(start, stop, step): # 2 row
            row += 1
            pos = 0
            for x in range(gameMarginStart, gameMarginStop, width): # 15 pos
                pos += 1
                game.aliens.append(AlienRed(game, x, y,row,pos))

        start = stop + int(game.height / 26)
        stop = start + int(game.height / 7)

        for y in range(start, stop, step): # 3 row
            row += 1
            pos = 0
            for x in range(gameMarginStart, gameMarginStop, width): # 15 pos
                pos += 1
                game.aliens.append(AlienGreen(game, x, y,row,pos))

        start = stop + int(game.height / 80)
        stop = start + int(game.height / 20)

        for y in range(start, stop, step): # 1 row
            row += 1
            pos = 0
            for x in range(gameMarginStart, gameMarginStop, width): # 15 pos
                pos += 1
                game.aliens.append(AlienBlue(game, x, y,row,pos))


class Rocket:
    def __init__(self, game, x, y):
        self.x = x
        self.y = y
        self.game = game

    def draw(self):
        rocketImage = pygame.image.load('rocket.png')
        self.game.screen.blit(rocketImage, (self.x, self.y))
        # to był placeholder
        # pygame.draw.rect(self.game.screen, 
        #                  (254, 52, 110),
        #                  pygame.Rect(self.x, self.y, 2, 4))
        self.y -= 8

# planowana, nie wprowadzona
# class AlienBullet:
#     def __init__(self, game, x, y):
#         self.x = x
#         self.y = y
#         self.game = game

#     def draw(self):
#         pygame.draw.rect(self.game.screen,
#                          (255, 255, 255),
#                          pygame.Rect(self.x, self.y, 1, 6))
#         self.y += 3


if __name__ == '__main__':
    pygame.init()  # create game window
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Main Menu")

    game_paused = False
    menu_state = "main"
    font = pygame.font.SysFont("arialblack", 40)
    TEXT_COL = (255, 255, 255)

    bg_img = pygame.image.load("images/background.png").convert_alpha()

    resume_img = pygame.image.load("images/button_resume.png").convert_alpha()
    options_img = pygame.image.load("images/button_options.png").convert_alpha()
    quit_img = pygame.image.load("images/button_quit.png").convert_alpha()
    video_img = pygame.image.load('images/button_video.png').convert_alpha()
    audio_img = pygame.image.load('images/button_audio.png').convert_alpha()
    keys_img = pygame.image.load('images/button_keys.png').convert_alpha()
    back_img = pygame.image.load('images/button_back.png').convert_alpha()

    resume_button = button.Button(200, 400, resume_img, 1)
    options_button = button.Button(450, 550, options_img, 1)
    quit_button = button.Button(450, 650, quit_img, 1)
    video_button = button.Button(450, 550, video_img, 1)
    audio_button = button.Button(450, 550, audio_img, 1)
    keys_button = button.Button(246, 325, keys_img, 1)
    back_button = button.Button(332, 450, back_img, 1)


    def draw_text(text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))


    run = True
    while run:
        screen.blit(bg_img, bg_img.get_rect())
        if menu_state == "main":
            if resume_button.draw(screen):
                game = Game(1200, 800)  # !! tu tworząc obiekt podajemy wymiary okna gry !!
            if options_button.draw(screen):
                menu_state = "options"
            if quit_button.draw(screen):
                run = False
        # check if the options menu is open
        if menu_state == "options":
            # draw the different options buttons
            if video_button.draw(screen):
                print("Video Settings")
            if audio_button.draw(screen):
                print("Audio Settings")
            if keys_button.draw(screen):
                print("Change Key Bindings")
            if back_button.draw(screen):
                menu_state = "main"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    pygame.quit()
