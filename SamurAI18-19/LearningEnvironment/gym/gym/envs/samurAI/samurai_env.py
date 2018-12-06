import numpy as np
import gym
import gym.spaces

# マップ上のjockyの加速度を操作として、ゴールに移動させることを目標とする環境
class SamuraiEnv(gym.Env):

	def _init_(self):

		# 加速度9種(-1~1,-1~1)
		self.action_space = gym.spaces.Discrete(9)

		#観測空間(俺らが見たい世界...jockyのpositionとvelocity)
		#positionの上限はルール通り19,99
		#下限は0,-無限だが、とりあえず、0,-10で
		#速度の上限、下限はとりあえず10,-10で(ステージごとに計算したほうがいい？)
		high = np.array[[19,99],[10,10]]
		low = np.array[[0,-10],[-10,-10]]
		self.observation_space = gym.spaces.Box(low,high)

		#_reset呼び出し
		self.reset()


	def _reset(self):