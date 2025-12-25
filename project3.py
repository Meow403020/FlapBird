import pygame
import neat
import os
import random
pygame.font.init()
windowWidth = 500
windowHeight = 800

birdImg = [pygame.transform.scale2x(pygame.image.load("bird1.png")), pygame.transform.scale2x(pygame.image.load("bird2.png")), pygame.transform.scale2x(pygame.image.load("bird3.png"))]
pipeImg = pygame.transform.scale2x(pygame.image.load("pipe.png"))
baseImg = pygame.transform.scale2x(pygame.image.load("base.png"))
backgImg = pygame.transform.scale2x(pygame.image.load("bg.png"))
statFont = pygame.font.SysFont("comicsans", 50)


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
        return pygame.mask.from_surface(self.img)
    
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
        self.pipeBottom = pipeImg

        self.passed = False
        self.setHeight()

    def setHeight(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.pipeTop.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.pipeTop, (self.x, self.top))
        win.blit(self.pipeBottom, (self.x, self.bottom))

    def collide(self, bird):
        birdMask = bird.getMask()
        topMask = pygame.mask.from_surface(self.pipeTop)
        bottomMask = pygame.mask.from_surface(self.pipeBottom)

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
            
    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))
        

def drawWindow(win, birds, pipes, base, score):
    win.blit(backgImg, (0,0))
    for pipe in pipes:
        pipe.draw(win)

    text = statFont.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (windowWidth - 10 - text.get_width(), 10))
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()

def main(genomes, config):
    nets = []
    ge = []
    birds = []

    for __, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((windowWidth, windowHeight))
    clock = pygame.time.Clock()
    score = 0
    run = True
    while run:
        clock.tick(40)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        if len(birds) == 0:
            break


        pipeInd = 0
        if len(birds) > 0:
            pipeInd = 0
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipeTop.get_width():
                pipeInd = 1

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipeInd].height), abs(bird.y - pipes[pipeInd].bottom)))

            if output[0] > 0.5:
                bird.jump()

        addPipe = False
        #bird.move()
        remove = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    addPipe = True

            if pipe.x + pipe.pipeTop.get_width() < 0:
                remove.append(pipe)
            
            pipe.move()

        if addPipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in remove:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        
        base.move()
        drawWindow(win, birds, pipes, base, score)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main, 50)
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)


