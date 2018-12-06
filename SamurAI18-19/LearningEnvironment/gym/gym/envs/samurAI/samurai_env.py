import numpy as np
import gym
import gym.spaces

# マップ上のjockyの加速度を操作として、ゴールに移動させることを目標とする環境
class SamuraiEnv(gym.Env):

	def _init_(self):

		# 加速度9種(-1~1,-1~1)
		self.action_space = gym.spaces.Discrete(9)

		#観測空間(俺らが見たい世界...jockyのpositionとvelocity)
		#速度の上限、下限はとりあえず10,-10で(ステージごとに計算したほうがいい？)
		#positionの上限はルール通り19,99
		#下限は0,-無限だが、とりあえず、0,-10で
		high = np.array[[10,10],[19,99]]
		low = np.array[[-10,-10],[0,-10]]
		self.observation_space = gym.spaces.Box(low=-high, high=high)

		#_reset呼び出し
		self.reset()