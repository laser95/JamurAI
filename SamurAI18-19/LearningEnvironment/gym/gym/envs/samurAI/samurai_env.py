import numpy as np
import gym
import gym.spaces

# マップ上のjockyの加速度を操作として、ゴールに移動させることを目標とする環境
class SamuraiEnv(gym.Env):

	def _init_(self):

		# 加速度9種(-1~1,-1~1)
		self.action_space = gym.spaces.Discrete(9)

		#観測空間(俺らが見たい世界...jockyのmapとpositionとvelocity)
		#mapの値域は[-3,2]
		#0->None , 1->Obstacle, 2->Puddle, -1->Unknown, -2->Behind Goal, -3->Outside Course
		#positionの上限はルール通り19,99
		#下限は0,-無限だが、とりあえず、0,-10で
		#速度の上限、下限はとりあえず10,-10で(ステージごとに計算したほうがいい？)
		#map,position,velocityそれぞれで値域が異なるのでDictionaryを使って定義
		#
		self.observation_space = gym.spaces.Dict({
			"map" : spaces.Box(-3,2,shape=(20,100),dtype="int32"),
			"position" : spaces.Box(np.array([0,-10]),np.array([19,99]),dtype="int32")),
			"velocity" : spaces.Box(np.array([-10,-10]),np.array([10,10]),dtype="int32")
		})

		#_reset呼び出し
		self.reset()


	def _reset(self):
