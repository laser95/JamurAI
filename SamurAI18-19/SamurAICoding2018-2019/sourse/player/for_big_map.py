#!/usr/bin/env python3
import numpy as np
import gym
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam
ENV_NAME = 'SamurAI-v0'
nb_actions = 9
obs_shape=(2005,)
model = Sequential()
model.add(Flatten(input_shape=(1,) + obs_shape))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(nb_actions))
model.add(Activation('linear'))

model.load_weights('dqn_{}_weights.h5f'.format(ENV_NAME))


SEARCHDEPTH = 7
SPEEDLIMIT = 1000
searchDepth = SEARCHDEPTH
speedLimitSquared = SPEEDLIMIT * SPEEDLIMIT
nextSeq = 1


# raceInfo.hpp
class IntVec(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, v):
        return IntVec(self.x + v.x, self.y + v.y)

    def __eq__(self, v):
        return self.x == v.x and self.y == v.y

    def __lt__(self, v):
        return self.x > v.x if self.y == v.y else self.y < v.y

    def __str__(self):
        return '(%s,%s)' % (self.x, self.y)

    def __hash__(self):
        return hash((self.x, self.y))


class RaceCourse(object):
    def __init__(self, thinkTime, stepLimit, width, length, vision):
        self.thinkTime = thinkTime
        self.stepLimit = stepLimit
        self.width = width
        self.length = length
        self.vision = vision

    def __str__(self):
        return 'RaceCourse(%s, %s, %s, %s, %s)' % (
            self.thinkTime, self.stepLimit, self.width,
            self.length, self.vision)


def inputRaceCourse():
    thinkTime = int(input())
    stepLimit = int(input())
    width, length = (int(x) for x in input().split())
    vision = int(input())
    return RaceCourse(thinkTime, stepLimit, width, length, vision)


class PlayerState(object):
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity

    def __str__(self):
        return 'PlayerState(%s, %s)' % (self.position, self.velocity)

    def __eq__(self, v):
        return self.position == v.position and self.velocity == v.velocity

    def __lt__(self, v):
        if self.position == v.position:
            return self.velocity < v.velocity
        else:
            return self.position < v.position

    def __hash__(self):
        return hash((self.position, self.velocity))


def inputPlayerState():
    cs = [int(x) for x in input().split()]
    return PlayerState(IntVec(cs[0], cs[1]), IntVec(cs[2], cs[3]))


class RaceInfo(object):
    def __init__(self, stepNumber, timeLeft, me, opponent, squares):
        self.stepNumber = stepNumber
        self.timeLeft = timeLeft
        self.me = me
        self.opponent = opponent
        self.squares = squares

    def __str__(self):
        return 'RaceInfo(%s, %s, %s, %s, %s)' % (
            self.stepNumber, self.timeLeft, self.me,
            self.opponent, self.squares)


def inputRaceInfo():
    stepNumber = int(input())
    timeLeft = int(input())
    me = inputPlayerState()
    opponent = inputPlayerState()
    squares = [[int(x) for x in input().split()] for y in range(course.length)]
    return RaceInfo(stepNumber, timeLeft, me, opponent, squares)


def plan(info, course):
    big_map = np.empty((100, 20)) 
    big_map[0:course.length, 0:course.width] = info.squares
    big_map[course.length + 1:100, 0:course.width] = -2
    big_map[:, course.width + 1:20] = -3 
    big_map[course.vision:course.length, 0:course.width] = -1
    pos = np.array([info.me.position.x,info.me.position.y])
    vel = np.array([info.me.velocity.x,info.me.velocity.y])
    obs = np.concatenate([big_map.reshape(2000,),np.array([course.length]).reshape(1,),pos.reshape(2,),vel.reshape(2,)])
    _input = [[obs]]
    a = max(model.predict_on_batch(np.array(_input)))
    a_list = a.tolist()
    action = a_list.index(max(a_list))
    if action == 0:
        return IntVec(-1, -1)
    elif action == 1:
        return IntVec(-1, 0)
    elif action == 2:
        return IntVec(-1, 1)
    elif action == 3:
        return IntVec(0, -1)
    elif action == 4:
        return IntVec(0, 0)
    elif action == 5:
        return IntVec(0, 1)
    elif action == 6:
        return IntVec(1, -1)
    elif action == 7:
        return IntVec(1, 0)
    elif action == 8:
        return IntVec(1, 1)


def main():
    global course
    course = inputRaceCourse()
    print('0', flush=True)
    try:
        while True:
            info = inputRaceInfo()
            accel = plan(info, course)
            print('%d %d' % (accel.x, accel.y), flush=True)
    except EOFError:
        pass


if __name__ == '__main__':
    main()
