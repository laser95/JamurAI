from __future__ import division
import numpy as np

from rl.util import *

#greedy
import heapq
import itertools
import math

class Policy(object):
    """Abstract base class for all implemented policies.

    Each policy helps with selection of action to take on an environment.

    Do not use this abstract base class directly but instead use one of the concrete policies implemented.
    To implement your own policy, you have to implement the following methods:

    - `select_action`

    # Arguments
        agent (rl.core.Agent): Agent used
    """
    def _set_agent(self, agent):
        self.agent = agent

    @property
    def metrics_names(self):
        return []

    @property
    def metrics(self):
        return []

    def select_action(self, **kwargs):
        raise NotImplementedError()

    def get_config(self):
        """Return configuration of the policy

        # Returns
            Configuration as dict
        """
        return {}


class LinearAnnealedPolicy(Policy):
    """Implement the linear annealing policy

    Linear Annealing Policy computes a current threshold value and
    transfers it to an inner policy which chooses the action. The threshold
    value is following a linear function decreasing over time."""
    def __init__(self, inner_policy, attr, value_max, value_min, value_test, nb_steps):
        if not hasattr(inner_policy, attr):
            raise ValueError('Policy does not have attribute "{}".'.format(attr))

        super(LinearAnnealedPolicy, self).__init__()

        self.inner_policy = inner_policy
        self.attr = attr
        self.value_max = value_max
        self.value_min = value_min
        self.value_test = value_test
        self.nb_steps = nb_steps

    def get_current_value(self):
        """Return current annealing value

        # Returns
            Value to use in annealing
        """
        if self.agent.training:
            # Linear annealed: f(x) = ax + b.
            a = -float(self.value_max - self.value_min) / float(self.nb_steps)
            b = float(self.value_max)
            value = max(self.value_min, a * float(self.agent.step) + b)
        else:
            value = self.value_test
        return value

    def select_action(self, **kwargs):
        """Choose an action to perform

        # Returns
            Action to take (int)
        """
        setattr(self.inner_policy, self.attr, self.get_current_value())
        return self.inner_policy.select_action(**kwargs)

    @property
    def metrics_names(self):
        """Return names of metrics

        # Returns
            List of metric names
        """
        return ['mean_{}'.format(self.attr)]

    @property
    def metrics(self):
        """Return metrics values

        # Returns
            List of metric values
        """

        return [getattr(self.inner_policy, self.attr)]

    def get_config(self):
        """Return configurations of LinearAnnealedPolicy

        # Returns
            Dict of config
        """
        config = super(LinearAnnealedPolicy, self).get_config()
        config['attr'] = self.attr
        config['value_max'] = self.value_max
        config['value_min'] = self.value_min
        config['value_test'] = self.value_test
        config['nb_steps'] = self.nb_steps
        config['inner_policy'] = get_object_config(self.inner_policy)
        return config

class SoftmaxPolicy(Policy):
    """ Implement softmax policy for multinimial distribution

    Simple Policy

    - takes action according to the pobability distribution

    """
    def select_action(self, nb_actions, probs):
        """Return the selected action

        # Arguments
            probs (np.ndarray) : Probabilty for each action

        # Returns
            action

        """
        action = np.random.choice(range(nb_actions), p=probs)
        return action

#greedy
SEARCHDEPTH = 7
SPEEDLIMIT = 1000
searchDepth = SEARCHDEPTH
speedLimitSquared = SPEEDLIMIT * SPEEDLIMIT
nextSeq = 1

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
		

def addSquares(x, y0, y1, squares):
    if y1 > y0:
        for y in range(y0, y1 + 1, 1):
            squares.append(IntVec(x, y))
    else:
        for y in range(y0, y1 - 1, -1):
            squares.append(IntVec(x, y))

class Movement(object):
    def __init__(self, from_, to):
        self.from_ = from_
        self.to = to

    def __str__(self):
        return 'Movement(%s,%s)' % (self.from_, self.to)

    def touchedSquares(self):
        r = []
        if self.to.x == self.from_.x:
            addSquares(self.from_.x, self.from_.y, self.to.y, r)
        else:
            a = (self.to.y - self.from_.y) / (self.to.x - self.from_.x)
            sgnx = 1 if self.from_.x < self.to.x else -1
            y1 = a * sgnx / 2.0 + self.from_.y + 0.5
            iy1 = (math.floor(y1) if self.to.y > self.from_.y
                   else math.ceil(y1) - 1)
            addSquares(self.from_.x, self.from_.y, iy1, r)
            for x in range(self.from_.x + sgnx, self.to.x, sgnx):
                y0 = a * (x - self.from_.x - sgnx / 2) + self.from_.y + 0.5
                y1 = a * (x - self.from_.x + sgnx / 2) + self.from_.y + 0.5
                if self.to.y > self.from_.y:
                    iy0, iy1 = math.ceil(y0) - 1, math.floor(y1)
                else:
                    iy0, iy1 = math.floor(y0), math.ceil(y1) - 1
                addSquares(x, iy0, iy1, r)
            y0 = a * (self.to.x - self.from_.x - sgnx / 2) + self.from_.y + 0.5
            iy0 = (math.ceil(y0) - 1 if self.to.y > self.from_.y
                   else math.floor(y0))
            addSquares(self.to.x, iy0, self.to.y, r)
        return r

class Candidate(object):
    def __init__(self, t, s, f, a, length):
        global nextSeq
        self.seq = nextSeq
        nextSeq += 1
        self.step = t
        self.state = s
        self.from_ = f
        self.how = a
        self.goaled = s.position.y >= length
        if self.goaled:
            self.goalTime = (self.step + (length - s.position.y - 0.5) / s.velocity.y)

    def __lt__(self, c):
        if self.goaled:
            return not c.goaled or c.goalTime > self.goalTime
        elif self.state == c.state:
            return c.step > self.step
        else:
            return c.state < self.state

    def __str__(self):
        return ('#%s:%s@(%s,%s)+(%s,%s) <- #%s' %
                (self.seq, self.step, self.state.position.x,
                 self.state.position.y, self.state.velocity.x,
                 self.state.velocity.y,
                 (0 if self.from_ is None else self.from_.seq)))

class SamurAIPolicy(Policy):
    """Implement the epsilon greedy policy

    Eps Greedy policy either:

    - takes a random action with probability epsilon
    - takes current best action with prob (1 - epsilon)
    """
    def __init__(self, eps=.1):
        super(SamurAIPolicy, self).__init__()
        self.eps = eps

    def select_action(self, q_values, observation=None):
        """Return the selected action

        # Arguments
            q_values (np.ndarray): List of the estimations of Q for each action

        # Returns
            Selection action
        """
        assert q_values.ndim == 1
        nb_actions = q_values.shape[0]

        if (np.random.uniform() < self.eps) and not (observation is None):
	    #action = np.random.random_integers(0, nb_actions-1)
	    #greedy for SamurAI Jockey
            print("greedy\n")
            map=observation[0:2000].reshape(100,20)
            length=int(observation[2000])
            _position=observation[2001:2003]
            _velocity=observation[2003:2005]
            
            position=IntVec(int(_position[0]),int(_position[1]))
            velocity=IntVec(int(_velocity[0]),int(_velocity[1]))

            width=0
            while map[0,width] != -2:
                if(width==19):
                        break
                width+=1

            candidates = []
            reached = {}
            initial = PlayerState(position, velocity)
            initialCand = Candidate(0, initial, None, IntVec(0, 0),length)
            reached[initial] = initialCand
            best = initialCand
            heapq.heappush(candidates, initialCand)
            while len(candidates) > 0:
                c = heapq.heappop(candidates)
                for cay, cax in itertools.product(range(1, -2, -1), range(-1, 2)):
                    accel = IntVec(cax, cay)
                    velo = c.state.velocity + accel
                    if velo.x * velo.x + velo.y * velo.y <= speedLimitSquared:
                        pos = c.state.position + velo
                        if 0 <= pos.x and pos.x < width:
                            move = Movement(c.state.position, pos)
                            touched = move.touchedSquares()
                            if (not any(0 <= s.y and s.y < length and
                                        map[s.y][s.x] == 1 for s in touched)):
                                if (0 <= pos.y and pos.y < length and
                                        map[pos.y][pos.x] == 2):
                                    velo = IntVec(0, 0)
                                nextState = PlayerState(pos, velo)
                                nextCand = Candidate(c.step + 1, nextState, c, accel,length)
                                if (not nextCand.goaled and
                                    c.step < searchDepth and
                                    (nextState not in reached or
                                     reached[nextState].step > c.step + 1)):
                                    heapq.heappush(candidates, nextCand)
                                    reached[nextState] = nextCand
                                if nextCand < best:
                                    best = nextCand
            if best == initialCand:
                ax = 0
                ay = 0
                if velocity.x < 0:
                    ax += 1
                elif velocity.x > 0:
                    ax -= 1
                if velocity.y < 0:
                    ay += 1
                elif velocity.y > 0:
                    ay -= 1
                
                if ax == -1:
                    if ay == -1:
                        action = 0
                    elif ay == 0:
                        action = 1
                    else:
                        action = 2
                elif ax == 0:
                    if ay == -1:
                        action = 3
                    elif ay == 0:
                        action = 4
                    else:
                        action = 5
                else:
                    if ay == -1:
                        action = 6
                    elif ay == 0:
                        action = 7
                    else:
                        action = 8
                return action

            c = best
            while c.from_ != initialCand:
                c = c.from_

            #processor
            if c.how.x == -1:
                if c.how.y == -1:
                    action = 0
                elif c.how.y == 0:
                    action = 1
                else:
                    action = 2
            elif c.how.x == 0:
                if c.how.y == -1:
                    action = 3
                elif c.how.y == 0:
                    action = 4
                else:
                    action = 5
            else:
                if c.how.y == -1:
                    action = 6
                elif c.how.y == 0:
                    action = 7
                else:
                    action = 8
		
        else:
            print("Q-function")
            action = np.argmax(q_values)
        return action

    def get_config(self):
        """Return configurations of EpsGreedyQPolicy

        # Returns
            Dict of config
        """
        config = super(EpsGreedyQPolicy, self).get_config()
        config['eps'] = self.eps
        return config

class EpsGreedyQPolicy(Policy):
    """Implement the epsilon greedy policy

    Eps Greedy policy either:

    - takes a random action with probability epsilon
    - takes current best action with prob (1 - epsilon)
    """
    def __init__(self, eps=.1):
        super(EpsGreedyQPolicy, self).__init__()
        self.eps = eps

    def select_action(self, q_values, observation=None):
        """Return the selected action

        # Arguments
            q_values (np.ndarray): List of the estimations of Q for each action

        # Returns
            Selection action
        """
        assert q_values.ndim == 1
        nb_actions = q_values.shape[0]

        if np.random.uniform() < self.eps:
	    action = np.random.random_integers(0, nb_actions-1)
	    
        else:
            action = np.argmax(q_values)
        return action

    def get_config(self):
        """Return configurations of EpsGreedyQPolicy

        # Returns
            Dict of config
        """
        config = super(EpsGreedyQPolicy, self).get_config()
        config['eps'] = self.eps
        return config

class GreedyQPolicy(Policy):
    """Implement the greedy policy

    Greedy policy returns the current best action according to q_values
    """
    def select_action(self, q_values):
        """Return the selected action

        # Arguments
            q_values (np.ndarray): List of the estimations of Q for each action

        # Returns
            Selection action
        """
        assert q_values.ndim == 1
        action = np.argmax(q_values)
        return action


class BoltzmannQPolicy(Policy):
    """Implement the Boltzmann Q Policy

    Boltzmann Q Policy builds a probability law on q values and returns
    an action selected randomly according to this law.
    """
    def __init__(self, tau=1., clip=(-500., 500.)):
        super(BoltzmannQPolicy, self).__init__()
        self.tau = tau
        self.clip = clip

    def select_action(self, q_values):
        """Return the selected action

        # Arguments
            q_values (np.ndarray): List of the estimations of Q for each action

        # Returns
            Selection action
        """
        assert q_values.ndim == 1
        q_values = q_values.astype('float64')
        nb_actions = q_values.shape[0]

        exp_values = np.exp(np.clip(q_values / self.tau, self.clip[0], self.clip[1]))
        probs = exp_values / np.sum(exp_values)
        action = np.random.choice(range(nb_actions), p=probs)
        return action

    def get_config(self):
        """Return configurations of BoltzmannQPolicy

        # Returns
            Dict of config
        """
        config = super(BoltzmannQPolicy, self).get_config()
        config['tau'] = self.tau
        config['clip'] = self.clip
        return config


class MaxBoltzmannQPolicy(Policy):
    """
    A combination of the eps-greedy and Boltzman q-policy.

    Wiering, M.: Explorations in Efficient Reinforcement Learning.
    PhD thesis, University of Amsterdam, Amsterdam (1999)

    https://pure.uva.nl/ws/files/3153478/8461_UBA003000033.pdf
    """
    def __init__(self, eps=.1, tau=1., clip=(-500., 500.)):
        super(MaxBoltzmannQPolicy, self).__init__()
        self.eps = eps
        self.tau = tau
        self.clip = clip

    def select_action(self, q_values):
        """Return the selected action
        The selected action follows the BoltzmannQPolicy with probability epsilon
        or return the Greedy Policy with probability (1 - epsilon)

        # Arguments
            q_values (np.ndarray): List of the estimations of Q for each action

        # Returns
            Selection action
        """
        assert q_values.ndim == 1
        q_values = q_values.astype('float64')
        nb_actions = q_values.shape[0]

        if np.random.uniform() < self.eps:
            exp_values = np.exp(np.clip(q_values / self.tau, self.clip[0], self.clip[1]))
            probs = exp_values / np.sum(exp_values)
            action = np.random.choice(range(nb_actions), p=probs)
        else:
            action = np.argmax(q_values)
        return action

    def get_config(self):
        """Return configurations of MaxBoltzmannQPolicy

        # Returns
            Dict of config
        """
        config = super(MaxBoltzmannQPolicy, self).get_config()
        config['eps'] = self.eps
        config['tau'] = self.tau
        config['clip'] = self.clip
        return config


class BoltzmannGumbelQPolicy(Policy):
    """Implements Boltzmann-Gumbel exploration (BGE) adapted for Q learning
    based on the paper Boltzmann Exploration Done Right
    (https://arxiv.org/pdf/1705.10257.pdf).

    BGE is invariant with respect to the mean of the rewards but not their
    variance. The parameter C, which defaults to 1, can be used to correct for
    this, and should be set to the least upper bound on the standard deviation
    of the rewards.

    BGE is only available for training, not testing. For testing purposes, you
    can achieve approximately the same result as BGE after training for N steps
    on K actions with parameter C by using the BoltzmannQPolicy and setting
    tau = C/sqrt(N/K)."""

    def __init__(self, C=1.0):
        assert C > 0, "BoltzmannGumbelQPolicy C parameter must be > 0, not " + repr(C)
        super(BoltzmannGumbelQPolicy, self).__init__()
        self.C = C
        self.action_counts = None

    def select_action(self, q_values):
        """Return the selected action

        # Arguments
            q_values (np.ndarray): List of the estimations of Q for each action

        # Returns
            Selection action
        """
        # We can't use BGE during testing, since we don't have access to the
        # action_counts at the end of training.
        assert self.agent.training, "BoltzmannGumbelQPolicy should only be used for training, not testing"

        assert q_values.ndim == 1, q_values.ndim
        q_values = q_values.astype('float64')

        # If we are starting training, we should reset the action_counts.
        # Otherwise, action_counts should already be initialized, since we
        # always do so when we begin training.
        if self.agent.step == 0:
            self.action_counts = np.ones(q_values.shape)
        assert self.action_counts is not None, self.agent.step
        assert self.action_counts.shape == q_values.shape, (self.action_counts.shape, q_values.shape)

        beta = self.C/np.sqrt(self.action_counts)
        Z = np.random.gumbel(size=q_values.shape)

        perturbation = beta * Z
        perturbed_q_values = q_values + perturbation
        action = np.argmax(perturbed_q_values)

        self.action_counts[action] += 1
        return action

    def get_config(self):
        """Return configurations of BoltzmannGumbelQPolicy

        # Returns
            Dict of config
        """
        config = super(BoltzmannGumbelQPolicy, self).get_config()
        config['C'] = self.C
        return config
