import numpy as np
import gym
import gym.spaces
import subprocess
import json
import sys

# マップ上のjockyの加速度を操作として、ゴールに移動させることを目標とする環境
class SamuraiEnv(gym.Env):

	def _init_(self):

		# 加速度9種(-1~1,-1~1)
		self.action_space = gym.spaces.Discrete(9)

		#観測空間(俺らが見たい世界...jockyのmapとlengthとpositionとvelocity)
		#mapの値域は[-3,2]
		#0->None , 1->Obstacle, 2->Puddle, -1->Unknown, -2->Behind Goal, -3->Outside Course
		#positionの上限はルール通り19,99
		#下限は0,-無限だが、とりあえず、0,-10で
		#速度の上限、下限はとりあえず10,-10で(ステージごとに計算したほうがいい？)
		#map,position,velocityそれぞれで値域が異なるのでDictionaryを使って定義
		self.observation_space = gym.spaces.Dict({
			"map" : spaces.Box(-3,2,shape=(20,100),dtype="int32"),
			"length" : spaces.Box(50,100,dtype="int32")),
			"position" : spaces.Box(np.array([0,-10]),np.array([19,99]),dtype="int32")),
			"velocity" : spaces.Box(np.array([-10,-10]),np.array([10,10]),dtype="int32")
		})

		#_reset呼び出し
		self.reset()


	def _reset(self):
		#コースを生成
		generator_path = “course_generator.py”
		subprocess.call(“python3 %s > course/course.crs” % generator_path)

		course_path = “course/course.crs”
		json_file = open(course_path, 'r')
  		json_obj = json.load(json_file)
  		if not json_obj['filetype'] == 'race course 2018':
	    	print "The input file does not contain race course data"
       		sys.exit(1)
  		 
       	self.width = json_obj['width']
		self.length = json_obj['length']
		self.vision = json_obj['vision']
		self.startX[0] = json_obj['x0']
		self.startX[1] = json_obj['x1']
		self.map = np.reshape(json_obj['squares'], (self.length, self.width))
		#視界限界変数に値格納
		#生成されたコースから、スタート地点のx軸計算

		#初期ステータス格納

		self._pos = [self.startX[np.random.randint(2)],0]
		self._vel = 0.0

		{
			"map" : spaces.Box(-3,2,shape=(20,100),dtype="int32"),
			"length" : spaces.Box(50,100,dtype="int32")),
			"position" : spaces.Box(np.array([0,-10]),np.array([19,99]),dtype="int32")),
			"velocity" : spaces.Box(np.array([-10,-10]),np.array([10,10]),dtype="int32")
		}

		return {"map" : self.map, "length" : self.length, "position" : self._pos, "velocity" : self._vel}

	def _render(self):