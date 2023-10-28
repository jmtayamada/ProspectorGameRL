import numpy as np
import random
import math
import pygame

pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()

class Treasure:
    def __init__(self, x:int, y:int) -> None:
        self.x = x
        self.y = y

class Prospector:
    def __init__(self, x:int, y:int, treasure:Treasure, sizex:int, sizey:int) -> None:
        self.x = x
        self.y = y
        self.sizex = sizex
        self.sizey = sizey
        self.treasure = treasure
        self.treasureFound = False

    def Turn(self):
        self.Move(self.treasure.x, self.treasure.y)
        if self.x == self.treasure.x and self.y == self.treasure.y:
            self.treasureFound = True

    def Move(self, treasureX, treasureY):
        if not self.treasureFound:
            xDif = treasureX - self.x
            yDif = treasureY - self.y
            if random.randint(0, 1) == 1:
                if abs(xDif) > abs(yDif):
                    try:
                        self.x += xDif/abs(xDif)
                    except:
                        self.x += 0
                else:
                    try:
                        self.y += yDif/abs(yDif)
                    except:
                        self.y += 0
            else:
                if random.randint(0, 1) == 0:
                    while True:
                        self.x += random.choice([-1, 1])
                        if self.x > self.sizex:
                            self.x = self.sizex
                        elif self.x < 0:
                            self.x = 0
                        else:
                            break
                else:
                    self.y += random.choice([-1, 1])
                    while True:
                        if self.y > self.sizey:
                            self.y = self.sizey
                        elif self.y < 0:
                            self.y = 0
                        else:
                            break

class Game:
    def __init__(self, xSize, ySize, prospectorNum, drawn:bool, aiRun:bool) -> None:
        self.aiRun = aiRun
        self.drawn = drawn
        self.xSize = xSize
        self.ySize = ySize
        self.prospectorNum = prospectorNum

        self.turnNum = 0

        self.state = "playing"

        self.playerturn = False
        self.prospectors = []

        self.reset()

    def onLoss(self):
        self.state = "loss"

    def onWin(self):
        self.state = "win"

    def onMiss(self):
        pass

    def onHit(self):
        pass

    def turn(self):
        if len(self.prospectors) > self.prospectorNum:
            self.prospectors.remove(self.prospectors[0])
        if self.drawn:
            self.drawturn()
        else:
            for x in self.prospectors:
                x.Turn()
        self.playerturn = True

    def calculateDistance(self, x, y):
        x = x - self.prospectors[0].x
        y = y - self.prospectors[0].y
        dis = math.sqrt(x*x + y*y)
        return dis

    def reset(self):
        if self.drawn:
            screen.fill("black")
        for x in range(self.prospectorNum):
            # self.prospectors.append(Prospector(random.randint(0, self.xSize-1), random.randint(0, self.ySize-1), Treasure(random.randint(0, self.xSize-1), random.randint(0, self.ySize-1)), self.xSize, self.ySize))
            self.prospectors.append(Prospector(5, 5, Treasure(10, 10), self.xSize, self.ySize))
            if self.aiRun:
                pygame.draw.rect(screen, "red", (20 * self.prospectors[x].treasure.x, 20 * self.prospectors[x].treasure.y, 20, 20))
        self.state = "playing"
        self.turn()
        self.turnNum = 0

    def drawturn(self):
        for x in self.prospectors:
            pygame.draw.rect(screen, "black", (x.x*20, x.y*20, 20, 20))
        for x in self.prospectors:
            x.Turn()
        for x in self.prospectors:
            pygame.draw.rect(screen, "white", (x.x*20, x.y*20, 20, 20))

    def playerTurn(self, mousePressed:bool, mousePosition:tuple):
        for x in self.prospectors:
            if x.treasureFound:
                for x in self.prospectors:
                    self.prospectors.remove(x)
                self.onLoss()
                break
        if mousePressed:
            if self.drawn:
                mx, my = mousePosition
                if self.aiRun:
                    pygame.draw.rect(screen, "blue", (mx*20, my*20, 20, 20))
            else:
                mx, my = mousePosition
            for x in self.prospectors:
                if x.treasure.x == mx and x.treasure.y == my:
                    self.onHit()
                    self.prospectors.remove(x)
                    if len(self.prospectors) == 0:
                        self.onWin()
                        break
                else:
                    self.onMiss()

            self.playerturn = False

    def interface(self, mousePressed:bool, mousePosition:tuple):
        reward = 0

        self.playerTurn(mousePressed, mousePosition)
        if self.playerturn is False:
            self.turn()
            self.turnNum += 1

        if mousePressed and len(self.prospectors) > 0:
            x, y, = mousePosition
            # dx = x - self.prospectors[0].treasure.x
            # dy = y - self.prospectors[0].treasure.y
            # dis = math.sqrt(dx*dx + dy*dy)
            # reward = 100/((dis*dis) + 1)
            # reward = 5 * (5-dis)
            # if reward < 0:
            #     reward = 0
            # dis = float(self.calculateDistance(x, y))
            # reward = 50/((dis*dis)+1)
            
        # if self.state == "loss":
        #     reward = -100.0
        if self.state == "win":
            reward = 200
        # if reward != 0:
        #     print(reward)

        if self.state == "loss" or self.state == "win":
            state = self.state
            self.reset()
            return reward, True, state
        
        return reward, False, self.state

if __name__ == '__main__':
    game1 = Game(20, 20, 1, True, False)

    running = True
    mousePressed = False
    while running:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                mousePressed = True
        mx, my = pygame.mouse.get_pos()
        mx = math.floor(mx/20)
        my = math.floor(my/20)
        game1.interface(mousePressed, (mx, my))
        pygame.display.flip()
        clock.tick(60)
        mousePressed = False