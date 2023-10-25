import torch
import random
import numpy as np
from collections import deque
from game import *
from model import *
import pygame
from helper import plot


pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()

MAX_MEMORY = 100_000
BATCH_SIZE = 500
LR = 0.1

max_framerate = 120


class Agent():
    def __init__(self):
        self.n_game = 0
        self.epsilon = 100    # initial randomness out of 100
        self.epsilonDecay = .97 # decay rate
        self.minEpsilon = 0
        self.gamma = .8      # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.ProspectorPos = []
        self.model = Linear_QNet(5, 256, 400).eval()
        # self.model.load_state_dict(torch.load("model/model.pth"))
        # self.model.eval()
        self.trainer = Qtrainer(self.model, lr = LR, gamma = self.gamma)

    def getState(self, game:Game):
        self.ProspectorPos.append(20 * game.prospectors[0].y + game.prospectors[0].x)
        while len(self.ProspectorPos) < 5:
            self.ProspectorPos.append(self.ProspectorPos[0])

        if len(self.ProspectorPos) > 5:
            self.ProspectorPos.remove(self.ProspectorPos[0])

        state = [self.ProspectorPos[0],
                self.ProspectorPos[1],
                self.ProspectorPos[2],
                self.ProspectorPos[3],
                self.ProspectorPos[4]]
        
        state = [190, 190, 190, 190, 190]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def trainLongMemory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)

        self.trainer.train_step(np.array(states), np.array(actions), rewards, np.array(next_states), dones)

    def trainShortMemory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def CoordToNum(self, coord:tuple):
        return 20 * coord[1] + coord[0]

    def NumToCoord(self, num):
        y_coord = math.floor(num/20)
        x_coord = num - math.floor(num/20)*20
        return x_coord, y_coord

    def getAction(self, state):
        # random moves
        epsilon = (self.epsilon * (self.epsilonDecay ** self.n_game)) + self.minEpsilon
        final_move = (0, 0)
        if random.randint(0, 100) < epsilon:
            final_move = (random.randint(0, 19), random.randint(0, 19))
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            y_coord = math.floor(move/20)
            x_coord = move - math.floor(move/20)*20
            final_move = (x_coord, y_coord)

        return final_move

def train():
    framerate = max_framerate
    agent = Agent()
    game = Game(20, 20, 1, True, True)
    running = True
    totalReward = 0
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    print("starting starting starting starting starting starting starting starting starting starting")
    while running:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if framerate == max_framerate:
                        framerate = 5
                    elif framerate == 5:
                        framerate = max_framerate
        # get old state
        state_old = agent.getState(game)
        # get move
        final_move = agent.getAction(state_old)
        # perform move and get new state
        reward, done, won = game.interface(True, final_move)
        reward = reward
        state_new = agent.getState(game)

        # transform coords of moves into a number
        final_move = agent.CoordToNum(final_move)

        if framerate == 5:
            print(final_move, state_new, reward)

        # train short memory
        agent.trainShortMemory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        totalReward += reward

        if done:
            # train long memory
            agent.n_game += 1
            agent.trainLongMemory()

            if won:
                agent.model.save()

            agent.ProspectorPos.clear()

            # randomness = (agent.epsilon * (agent.epsilonDecay ** agent.n_game)) + agent.minEpsilon

            plot_scores.append(totalReward)
            total_score += totalReward
            mean_score = total_score / agent.n_game
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

            # print("Game", agent.n_game, "Status:", won, totalReward, "Randomness", randomness)
            totalReward = 0

        pygame.display.flip()
        clock.tick(framerate)


if __name__ == '__main__':
    train()