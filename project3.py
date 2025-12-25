import pygame
import neat
import os
import random
windowWidth = 500
windowHeight = 800

birdImg = [pygame.transform.scale2x(pygame.image.load("bird1.png")), pygame.transform.scale2x(pygame.image.load("bird2.png")), pygame.transform.scale2x(pygame.image.load("bird3.png"))]
pipeImg = pygame.transform.scale2x(pygame.image.load("pipe.png"))
baseImg = pygame.transform.scale2x(pygame.image.load("base.png"))
backgImg = pygame.transform.scale2x(pygame.image.load("bg.png"))

class Bird:
    imgs = birdImg
    maxRotation = 25
    veloc = 20
    anim = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tickCount = 0
        self.vel = 0
        self.height = self.y
        self.imgCount = 0
        self.img =self.imgs[0]

    def jump(self):
        self.vel = -10.5
        self.tickCount = 0
        self.height = self.y

    def move(self):
        self.tickCount += 1

        d = self.vel*self.tickCount + 1.5*self.tickCount**2
        if d >= 16:
            d = 16
        if d < 0:
            d -= 2
        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.maxRotation:
                self.tilt = self.maxRotation
        else:
            if self.tilt > -90:
                self.tilt -= self.veloc

    def draw(self, win):
        self.imgCount += 1
        if self.imgCount < self.anim:
            self.img = self.imgs[0]
        elif self.imgCount < self.anim*2:
            self.img = self.imgs[1]
        elif self.imgCount < self.anim*3:
            self.img = self.imgs[2]
        elif self.imgCount < self.anim*4:
            self.img = self.imgs[1]
        elif self.imgCount < self.anim*4 + 1:
            self.img = self.imgs[0]
            self.imgCount = 0 

        if self.tilt <= -80:
            self.img = self.imgs[1]
            self.imgCount = self.anim*2
        rotatedImg = pygame.transform.rotate(self.img, self.tilt)
        newRec = rotatedImg.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotatedImg, newRec.topleft)

    def getMask(self):
        return pygame.mask.fromSurface(self.img)
    
class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.pipeTop = pygame.transform.flip(pipeImg, False, True)
        self.pipBottom = pipeImg

        self.passed = False
        self.setHeight()

        def setHeight(self):
            self.height = random.randrange(50, 450)
            self.top = self.height - self.pipeTop.get_height()
            self.bottom = self.height + self.GAP

        def move(self):
            self.x -= self.VEL

        def draw(self, win):
            win.blitt(self.pipeTop, (self.x, self.top))
            win.blitt(self.pipeBottom, (self.x, self.bottom))

        def collide(self, bird):
            birdMask = bird.getMask()
            topMask = pygame.mask.fromSurface(self.pipeTop)
            bottomMask = pygame.mask.fromSurface(self.pipeBottom)

            topOffset = (self.x - bird.x, self.top - round(bird.y))
            bottomOffset = (self.x-bird.x, self.bottom - round(bird.y))

            bPoint = birdMask.overlap(bottomMask, bottomOffset)
            tPoint = birdMask.overlap(topMask, topOffset)

            if tPoint or bPoint:
                return True
            return False
        
class Base:
    vel = 5
    width = baseImg.get_width()
    img = baseImg

    def __init__(self,y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width

    def move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel
        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width
            

def drawWindow(win, bird):
    win.blit(backgImg, (0,0))
    bird.draw(win)
    pygame.display.update()

def main():
    bird = Bird(200,200)
    win = pygame.display.set_mode((windowWidth, windowHeight))
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        #bird.move()
        drawWindow(win, bird)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()


