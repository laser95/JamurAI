import numpy as np
import gym

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten,Permute,Convolution2D, Reshape
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy,LinearAnnealedPolicy
#from rl.policy import SamurAIPolicy
from rl.memory import SequentialMemory, EpisodeParameterMemory

import matplotlib.pyplot as plt
from argparse import ArgumentParser

argparser=ArgumentParser()
argparser.add_argument('-w','--weight',type=str,default=None)
argparser.add_argument('-m','--mode',choices=['train','test'],default='train')
args=argparser.parse_args()

ENV_NAME = 'SamurAI-v2'
WINDOW_LENGTH=1

env = gym.make(ENV_NAME)
nb_actions = env.action_space.n

input_shape=(8,30,20)

# モデルの定義

model = Sequential()
model.add(Reshape((8,30,20),input_shape=(1,)+input_shape))
model.add(Convolution2D(32,(4,4),strides=(1,1),padding='same',data_format='channels_first'))
model.add(Activation('relu'))
model.add(Convolution2D(64,(4,4),strides=(2,2),data_format='channels_first'))
model.add(Activation('relu'))
model.add(Convolution2D(64,(3,3),strides=(1,1),data_format='channels_first'))
model.add(Activation('relu'))
model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dense(nb_actions))
model.add(Activation('linear'))
print(model.summary())

# コンパイル
memory = SequentialMemory(limit=1000000, window_length=WINDOW_LENGTH)

if args.weight != None:
	policy = EpsGreedyQPolicy(eps=0.1)
else:
	policy = LinearAnnealedPolicy(EpsGreedyQPolicy(),attr='eps',value_max=.7,value_min=.1,value_test=.05,nb_steps=1000000)

#tuning learning parameter
policy = LinearAnnealedPolicy(EpsGreedyQPolicy(),attr='eps',value_max=.4,value_min=.1,value_test=.05,nb_steps=500000)

dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=5000, gamma=.95, target_model_update=10000,train_interval=4, policy=policy,delta_clip=1.)

dqn.compile(Adam(lr=0.00025), metrics=['mae'])

if args.weight != None:
	print('load : {}'.format(args.weight))
	dqn.load_weights(args.weight)

if args.mode == 'train':
	# 学習
	dqn.fit(env, nb_steps=7000000, visualize=True, verbose=1,log_interval=1)
	
	# 学習したパラメータの保存
	if env.all_step >= 50000:
		dqn.save_weights('dqn_{0}_weights_{1}.h5f'.format(ENV_NAME,env.all_step), overwrite=True)
		plt.savefig('LerningCurve_{}.jpg'.format(env.all_step))
	plt.close(env.graph_fig)
	
	fig=plt.figure()
	ax1=fig.add_subplot(111)
	ax1.plot(env.x_plot,env.reward_plot,'C0',linewidth=0.5,label='reward')
	ax2=ax1.twinx()
	ax2.plot(env.x2_plot,env.gr_plot,'C1',linewidth=1.0,label='goal ratio')
	ax1.set_xlabel('episode')
	ax1.set_ylabel('reward')
	ax1.grid(True)
	ax2.set_ylabel('goal ratio')
	ax2.set_ylim(-.1,1.1)
	fig.legend()
	plt.title('Learning Curve')
	plt.show()
	
	#　テスト
	#dqn.test(env, nb_episodes=5, visualize=True)
	dqn.test(env, nb_episodes=5, visualize=False)
else:
	dqn.test(env,nb_episodes=5, visualize=True)


