import numpy as np
import gym
#import gym.spaces
from gym import spaces
import subprocess
import json
import sys
import math

import matplotlib.pyplot as plt

# マップ上のjockyの加速度を操作として、ゴールに移動させることを目標とする環境
class SamuraiEnvBigmap(gym.Env):


	def __init__(self):

		# 加速度9種(-1~1,-1~1)
		self.action_space = spaces.Discrete(9)

		# 観測空間
		self.observation_space = spaces.Box(low=0, high=1, shape=(8, 30, 20), dtype=np.uint8)
		self.startX=[0]*2

		#for plot
		self.reward_plot = []
		self.x_plot = []
		self.reward_stock = 0
		self.all_step = 0

		#_reset呼び出し
		self.reset()

	def step(self,action):

		#actionを加速度と紐づけ
		if action == 0:
			acc = np.array([-1,-1])
		elif action == 1:
			acc = np.array([-1,0])
		elif action == 2:
			acc = np.array([-1,1])
		elif action == 3:
			acc = np.array([0,-1])
		elif action == 4:
			acc = np.array([0,0])
		elif action == 5:
			acc = np.array([0,1])
		elif action == 6:
			acc = np.array([1,-1])
		elif action == 7:
			acc = np.array([1,0])
		elif action == 8:
			acc = np.array([1,1])  

		next_vel = self._vel + acc #予定速度
		next_pos = self._pos + next_vel #予定位置


		self._step+=1
		'''
			0...none
			1...obsta
			2...pool
			next 2 position=nextPosi
				   vel = [0,0]
		    next 1 position = position
		           vel = [0,0]
			→動けない時も上記と同じ
		'''
		
		done = self._is_done(self._pos,next_pos)

		pre_pos = self._pos
		if self._movable(self._pos,next_pos): 
			if next_pos[1]<0 or (not done and self.map[next_pos[1]][next_pos[0]] == 0):
				self._vel = next_vel
				self._pos = next_pos
			elif not done and self.map[next_pos[1]][next_pos[0]] == 2:
				self._pos = next_pos
				self._vel = np.array([0,0])
		else :
			self._vel = np.array([0,0])
			self._pos = self._pos

		#ゴールしたら1,それ以外はゴールにy軸
		if done:
			reward = 100.0
			print('\n\n\n!!!!!!goolgoolgool!!!!\n\n\n')
			
		else:
			#reward = 1.0 * self._pos[1]/goolY
			reward = 100.0 *(next_pos[1]-pre_pos[1])/self.length


		#取り得る最大のマップを定義, 全て1(壁)で指定
		big_map = np.empty((100, 20))

		#指定されたマップを-1(未知)で指定
		big_map[0:self.length, 0:self.width] = -1
		#指定されたマップのy軸の範囲外を-2(ゴール以降)で指定
		big_map[self.length:100, 0:self.width] = -2
		#指定されたマップ範囲外を-3(コース外)で指定
		big_map[:, self.width:20] = -3
		# ゴールするまで、毎stepでbig_mapを取得
		if self._pos[1] < self.length:
			vision = self._pos[1] + self.vision
			if vision < 0:
				pass
			elif vision > self.length:
				big_map[0:self.length,0:self.width] = self.map
			else:
				big_map[0:vision, 0:self.width] = self.map[0:vision,:]

		if self.step_limit <= self._step:
			done = True

		layer_map = np.zeros((8, 100, 20)).astype(np.uint8)
		'''
			0: Outside of course (-3)
			1: Behind of goal (-2)
			2: Unknown (-1)
			3: None (0)
			4: Obstacle (1)
			5: Puddle (2)
			6: Position
			7: Previous position
		'''
		layer_map[0, :, :] = np.where(big_map == -3, 1, 0)
		layer_map[1, :, :] = np.where(big_map == -2, 1, 0)
		layer_map[2, :, :] = np.where(big_map == -1, 1, 0)
		layer_map[3, :, :] = np.where(big_map == 0, 1, 0)
		layer_map[4, :, :] = np.where(big_map == 1, 1, 0)
		layer_map[5, :, :] = np.where(big_map == 2, 1, 0)
		if self._pos[1] >= 0:
			layer_map[6, self._pos[1], self._pos[0]]=1
		if pre_pos[1] >= 0:
			layer_map[7, pre_pos[1], pre_pos[0]] = 1

		#for plot
		self.reward_stock += reward
		self.all_step += 1
		

		#return {"map" : big_map, "length" : self.length, "position" : self._pos, "velocity" : self._vel},reward,done,{}
		return layer_map, reward, done, {}

	def reset(self):
		#コースを生成
		generator_path = "course_generator/course_generator.py"
		subprocess.call("python3 %s > course/course.crs" % generator_path, shell=True)

		course_path = "course/course.crs"
		json_file = open(course_path, 'r')
		json_obj = json.load(json_file)
		if not json_obj['filetype'] == 'race course 2018':
			print("The input file does not contain race course data")
			sys.exit(1)

		self.width = json_obj['width']
		self.length = json_obj['length']
		self.vision = json_obj['vision']
		self.step_limit=json_obj['stepLimit']
		self.startX[0] = json_obj['x0']
		self.startX[1] = json_obj['x1']
		self.map = np.reshape(json_obj['squares'], (self.length, self.width))
		self._step=0
		#視界限界変数に値格納
		#生成されたコースから、スタート地点のx軸計算

		#初期ステータス格納
		self.length=np.array(self.length)
		self._pos = np.array([self.startX[np.random.randint(2)],0])
		self._vel = np.array([0,0])
		
		{
			"map": spaces.Box(-3, 2, shape=(20, 100), dtype="int32"),
			"length": spaces.Box(50, 100, shape=(1,), dtype="int32"),
			"position": spaces.Box(np.array([0, -10]), np.array([19, 99]), dtype="int32"),
			"velocity": spaces.Box(np.array([-10, -10]), np.array([10, 10]), dtype="int32")
		}

		#return {"map" : self.map, "length" : self.length, "position" : self._pos, "velocity" : self._vel}

		big_map = np.empty((100, 20))
		#指定されたマップのy軸の範囲外を-2(ゴール以降)で指定
		big_map[self.length:100, 0:20] = -2

		#指定されたマップ範囲外を-3(コース外)で指定
		big_map[:, self.width:20] = -3

		vision = self._pos[1] + self.vision
		big_map[0:vision, 0:self.width] = self.map[0:vision,:]
		big_map[0:self.length,0:self.width]=self.map

		# コースジェネレーターから取得したコースの情報を出力
		print('\nlength : '+str(self.length)+', width : '+str(self.width)+', vision : '+str(self.vision))

		# create binary map
		layer_map = np.zeros((8, 100, 20))
		'''
			0: Outside of course (-3)
			1: Behind of goal (-2)
			2: Unknown (-1)
			3: None (0)
			4: Obstacle (1)
			5: Puddle (2)
			6: Position
			7: Previous position
		'''
		layer_map[0, :, :] = np.where(big_map == -3, 1, 0)
		layer_map[1, :, :] = np.where(big_map == -2, 1, 0)
		layer_map[2, :, :] = np.where(big_map == -1, 1, 0)
		layer_map[3, :, :] = np.where(big_map == 0, 1, 0)
		layer_map[4, :, :] = np.where(big_map == 1, 1, 0)
		layer_map[5, :, :] = np.where(big_map == 2, 1, 0)
		layer_map[6, self._pos[1], self._pos[0]] = 1
		layer_map[7, self._pos[1], self._pos[0]] = 1

		np.set_printoptions(threshold=np.inf)
		print('big map:\n', big_map)
		print('layer map:\n', layer_map)

		#plot
		self.reward_plot.append(self.reward_stock)
		self.x_plot.append(len(self.reward_plot))
		plt.plot(self.x_plot, self.reward_plot, color='blue')
		plt.title("Learning curve")
		plt.xlabel("Episode")
		plt.ylabel("Reward")
		# plt.pause(0.1)
		self.reward_stock = 0

		return layer_map

	def render(self,mode='human',close=False):
		'''
		outmap = self.map.copy()
		outmap[self._pos[1]][self._pos[0]] = 9

		outfile = sys.stdout
		velostr = 'velocity.x:' + str(self._vel[0]) + '\nvelocity.y:' + str(self._vel[1]) + '\n'
		mapstr = '\n'.join(''.join(
				str(value) for value in row
				) for row in outmap
            ) + '\n'
		outfile.write(velostr + mapstr)
		return outfile	
		'''
		pass

	def seed(self):
		pass

	def close(self):
		pass

	def addSquares(self,x, y0, y1, squares):
		if y1 > y0:
			for y in range(y0, y1 + 1, 1):
				squares.append(np.array([x, y]))
		else:
			for y in range(y0, y1 - 1, -1):
				squares.append(np.array([x, y]))
	def _movable(self,_pos,next_pos): #移動可能判定
		r = []
		if next_pos[0] == _pos[0]:
			self.addSquares(_pos[0], _pos[1], next_pos[1], r)
		else:
			a = (next_pos[1] - _pos[1]) / (next_pos[0] - _pos[0])
			sgnx = 1 if _pos[0] < next_pos[0] else -1
			y1 = a * sgnx / 2.0 + _pos[1] + 0.5
			iy1 = (math.floor(y1) if next_pos[1] > _pos[1] else math.ceil(y1) - 1)
			self.addSquares(_pos[0], _pos[1], iy1, r)
			for x in range(_pos[0] + sgnx, next_pos[0], sgnx):
				y0 = a * (x - _pos[0] - sgnx / 2) + _pos[1] + 0.5
				y1 = a * (x - _pos[0] + sgnx / 2) + _pos[1] + 0.5
				if next_pos[1] > _pos[1]:
					iy0, iy1 = math.ceil(y0) - 1, math.floor(y1)
				else:
					iy0, iy1 = math.floor(y0), math.ceil(y1) - 1
				self.addSquares(x, iy0, iy1, r)
			y0 = a * (next_pos[0] - _pos[0] - sgnx / 2) + _pos[1] + 0.5
			iy0 = (math.ceil(y0) - 1 if next_pos[1] > _pos[1] else math.floor(y0))
			self.addSquares(next_pos[0], iy0, next_pos[1], r)

		return (0 <= next_pos[0] < self.width 
				and not any(0 <= s[1] and s[1] < self.length and 
                                self.map[s[1]][s[0]] == 1 for s in r))

	def _is_done(self,_pos,next_pos):
		if next_pos[1] < self.length:
			return False

		dx = (next_pos[0] - _pos[0])
		if not dx==0:
			a = (next_pos[1] - _pos[1]) / dx #傾き
			y = math.floor(dx * a) + _pos[1]
		y=self.length

		while y <= self.length - 1:
			dx = dx - 1
			y = math.floor(dx * a) + _pos[1]
		next_pos2 = [_pos[0] + dx, y]

		return 0<=next_pos[0] < self.width and self._movable(_pos,next_pos2)


