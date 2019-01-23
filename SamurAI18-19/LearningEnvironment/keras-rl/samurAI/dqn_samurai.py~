import numpy as np
import gym

from rl.agents.dqn import DQNAgent

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

ENV_NAME = 'SamurAI-v0'

env = gym.make(ENV_NAME)
nb_actions = env.action_space.n
#nb_actions = 9

#obs_shape=env.observation_space.spaces['map'].shape+env.observation_space.spaces['length'].shape+env.observation_space.spaces['position'].shape+env.observation_space.spaces['velocity'].shape
obs_shape=(2005,)

# モデルの定義
model = Sequential() # 線形のレイヤー
model.add(Flatten(input_shape=(1,) + obs_shape)) # 最初のレイヤーは入力のshapeを指定する
#model.add(Dense(16,input_shape=obs_shape))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(nb_actions))
model.add(Activation('linear'))
print(model.summary())

# コンパイル
memory = SequentialMemory(limit=50000, window_length=1)
policy = EpsGreedyQPolicy()

dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=10,target_model_update=1e-2, policy=policy)

dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# 学習
dqn.fit(env, nb_steps=1000, visualize=True, verbose=1,log_interval=1)

# 学習したパラメータの保存
dqn.save_weights('dqn_{}_weights.h5f'.format(ENV_NAME), overwrite=True)

#　テスト
dqn.test(env, nb_episodes=5, visualize=True)
