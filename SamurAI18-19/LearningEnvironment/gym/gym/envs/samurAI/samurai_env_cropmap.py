import numpy as np
import gym
#import gym.spaces
from gym import spaces
import subprocess
import json
import sys
import math
import itertools

import matplotlib.pyplot as plt
from PIL import Image

# マップ上のjockyの加速度を操作として、ゴールに移動させることを目標とする環境
class SamuraiEnvCropmap(gym.Env):


	def __init__(self):

		# 加速度9種(-1~1,-1~1)
		self.action_space = spaces.Discrete(9)

		#観測空間
		self.observation_space = spaces.Box(low=0,high=1,shape=(8,30,20),dtype=np.uint8)
		
		self.crop_map = np.empty((30, 20)).astype(np.int8)
		self.startX=[0]*2
		
		self.reward_plot=[]
		self.gr_plot=[0]
		self.x_plot=[]
		self.x2_plot=[0]

		self.reward_stock=0
		self.all_step=0
		self.goal_count=0.0

		self.graph_fig=plt.figure()
		self.ax1=self.graph_fig.add_subplot(111)
		self.hl1,=self.ax1.plot(self.x_plot,self.reward_plot,'C0',linewidth=0.5,label='reward')
		self.ax2=self.ax1.twinx()
		self.hl2,=self.ax2.plot([0],[0],'C1',linewidth=1.0,label='goal ratio')
		self.ax1.set_xlabel('episode')
		self.ax1.set_ylabel('reward')
		self.ax1.grid(True)
		self.graph_fig.legend()
		self.ax2.set_ylabel('goal ratio')
		self.ax2.set_ylim(-.1,1.1)
		
		plt.title('Learning Curve')
		
		self.imgf = True
		self.img_fig=None

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
		
		done = self._is_done(self._pos,next_pos)

		pre_pos=self._pos
		if self._movable(self._pos,next_pos): 
			if next_pos[1]<0 or (not done and next_pos[1]<self.length and self.map[next_pos[1]][next_pos[0]] == 0):
				self._vel = next_vel
				self._pos = next_pos
			elif not done and next_pos[1]<self.length and self.map[next_pos[1]][next_pos[0]] == 2:
				self._pos = next_pos
				self._vel = np.array([0,0])
			else:
				self._vel = next_vel
				self._pos = next_pos
		else :
			self._vel = np.array([0,0])
			self._pos = self._pos

		#(length:30, width:20) , 0-9 : behind , 10 : current position , forward : 11-29
		self.crop_map[:, self.width:20] = -3

		vision_limit=self.vision
		if self.length <= self._pos[1]+self.vision:
			vision_limit=self.length - self._pos[1]
		forward_limit=min(20,self.length-self._pos[1])
		backward_limit=self._pos[1]-10
		
		if done:
			self.crop_map[10:30,0:self.width]=-2
			self.crop_map[0:10-(self._pos[1]-self.length),0:self.width]=self.map[backward_limit:self.length,:]
			self.crop_map[10-(self._pos[1]-self.length):10,0:self.width]=-2
			forward_limit=0
		elif backward_limit > 0:
			if forward_limit < 0:
				self.crop_map[0:10+forward_limit,0:self.width]=self.map[backward_limit:10+backward_limit,:]
			else:
				self.crop_map[0:10,0:self.width]=self.map[backward_limit:10+backward_limit,:]
		else:
			for i in range(min(-backward_limit,10)):
				self.crop_map[i,0:self.width]=0
			if backward_limit >= -10:
				self.crop_map[-backward_limit:10,0:self.width]=self.map[0:self._pos[1],:]
		
		if self._pos[1] >= 0:
			self.crop_map[10:10+vision_limit,0:self.width]=self.map[self._pos[1]:self._pos[1]+vision_limit,:]
		else:
			backyard=min(-self._pos[1],20)
			self.crop_map[10:10+backyard,0:self.width]=0
			self.crop_map[10+backyard:30,0:self.width]=self.map[0:20-backyard,:]
		self.crop_map[10+vision_limit:30,0:self.width]=-1
		if forward_limit < 20:
			self.crop_map[10+forward_limit:30,0:self.width]=-2

		layer_map=np.zeros((8,30,20)).astype(np.uint8)
		'''
			0 : Outside of course (-3)
			1 : Behind of goal (-2)
			2 : Unknown (-1)
			3 : None (0)
			4 : Obstacle (1)
			5 : Puddle (2)
			6 : Position
			7 : Previous position
		'''
		layer_map[0,:,:]=np.where(self.crop_map == -3, 1, 0)
		layer_map[1,:,:]=np.where(self.crop_map == -2, 1, 0)
		layer_map[2,:,:]=np.where(self.crop_map == -1, 1, 0)
		layer_map[3,:,:]=np.where(self.crop_map == 0, 1, 0)
		layer_map[4,:,:]=np.where(self.crop_map == 1, 1, 0)
		layer_map[5,:,:]=np.where(self.crop_map == 2, 1, 0)
		
		layer_map[6,10,self._pos[0]]=1
		if self._vel[1] <=  10 and self._vel[1] >= -19:
			layer_map[7,10-self._vel[1],self._pos[0]-self._vel[0]]=1
		"""
		if self._pos[1]-pre_pos[1] <=  10 and self._pos[1]-pre_pos[1] >= -19:
			layer_map[7,10-(self._pos[1]-pre_pos[1]),self._pos[0]-pre_pos[0]]=1
		"""
		
		if done:
			#reward = (self._pos[1]-pre_pos[1])/self.length + 10*pow(0.99,self._step)
			#reward = 5*(self._pos[1]-pre_pos[1])/self.length + 10
			reward = 5*(self._pos[1]-pre_pos[1])/50 + 10
			print('\n#\n#\n#\n#\n#\n#\n!!!!!!goolgoolgool!!!!\n#\n#\n#\n#\n#\n#\n#\n#')
			#self.score=self._step+(self.length-self._pos[1])/(self._pos[1]-pre_pos[1])
			self.goal_count += 1.0
			
		else:
			#reward = max((self._pos[1]-pre_pos[1])/self.length,-0.05)*5
			reward = max((self._pos[1]-pre_pos[1])/50,-0.05)*5
		
		#if np.allclose(self._pos,pre_pos):
		#	reward -= .005
		
		print('                 setp : {0}, goal : {1},  pos : ( {2} , {3} ) '.format(self._step,self.length,self._pos[0],self._pos[1]))
		if self.step_limit <= self._step and not done:
			done=True
			#self.score=2*self._step
			#self.score_plot.append(0)

		self.reward_stock += reward
		self.all_step += 1

		return layer_map, reward, done, {}


	def reset(self):
		#コースを生成
		generator_path = "course_generator/course_generator.py"
		subprocess.call("python3 %s > course/course.crs" % generator_path,shell=True)

		course_path = "course/course.crs"
		#course_path = "course/666.crs"
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
		
		#初期ステータス格納
		self.length=np.array(self.length)
		self._pos = np.array([self.startX[np.random.randint(2)],0])
		self._vel = np.array([0,0])
		
		self.crop_map[0:10,0:self.width] = 0
		self.crop_map[10:10+self.vision,0:self.width] = self.map[0:self.vision,:]
		self.crop_map[10+self.vision:30,0:self.width] = -1
		self.crop_map[:,self.width:20] = -3
		
		layer_map=np.zeros((8,30,20))
		layer_map[0,:,:]=np.where(self.crop_map == -3, 1, 0)
		layer_map[2,:,:]=np.where(self.crop_map == -1, 1, 0)
		layer_map[3,:,:]=np.where(self.crop_map == 0, 1, 0)
		layer_map[4,:,:]=np.where(self.crop_map == 1, 1, 0)
		layer_map[5,:,:]=np.where(self.crop_map == 2, 1, 0)
		layer_map[6,10,self._pos[0]]=1
		layer_map[7,10,self._pos[0]]=1
		
		print('\nlength : '+str(self.length)+', width : '+str(self.width)+', vision : '+str(self.vision))
		self.plot()
		self.imgf = True
		
		return layer_map

	def plot(self):
		
		self.reward_plot.append(self.reward_stock)
		self.x_plot.append(len(self.reward_plot))
				
		#for plot episode reward
		self.hl1.set_xdata(self.x_plot)
		self.hl1.set_ydata(self.reward_plot)
		#for plot winning percentage for last 10 race
		if len(self.x_plot) % 10 == 0:
			plt.xlim(0,len(self.x_plot))
			if min(self.reward_plot) != max(self.reward_plot):
				#plt.ylim(min(self.reward_plot)*1.1,max(self.reward_plot)*1.1)
				self.ax1.set_ylim(max(min(self.reward_plot)*1.1,-5),max(self.reward_plot)*1.1)
				plt.pause(0.01)
				#plt.draw()
			if len(self.x_plot) % 100 == 0:
				self.gr_plot.append(self.goal_count / 100.0)
				self.x2_plot.append(len(self.reward_plot))
				self.goal_count = 0.0
				self.hl2.set_xdata(self.x2_plot)
				self.hl2.set_ydata(self.gr_plot)
				self.ax2.set_ylim(-.1,1.1)
				plt.pause(0.01)
				#plt.draw()

		self.reward_stock=0

	def showMap(self, map):
		img=np.zeros((30,20,3)).astype(np.int32)
		
		img[np.where(map==-3)]=[0,0,0]
		img[np.where(map==-2)]=[0,0,0]
		img[np.where(map==-1)]=[200,250,205]
		img[np.where(map==0)]=[130,200,110]
		img[np.where(map==1)]=[100,70,40]
		img[np.where(map==2)]=[150,200,220]
		img[10,self._pos[0]]=[200,180,90]

		img=img[::-1,:,:]
		
		if self.imgf:
			if self.img_fig != None:
				plt.close(self.img_fig)
			self.img_fig=plt.figure()
			self.mapimg=plt.imshow(img,vmin=0,vmax=255)
			self.imgf = False
		else:
			self.mapimg.set_data(img)
		plt.pause(1e-2)

	def render(self,mode='human'):
		if mode=='human':
			plt.close(self.graph_fig)
			self.showMap(self.crop_map)

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
		ax = 0
		if not dx==0:
			a = (next_pos[1] - _pos[1]) / dx #傾き
			y = math.floor(dx * a) + _pos[1]
			while y < self.length and ax < dx:
				ax += 1
				y = math.floor(ax * a) + _pos[1]
			y = math.floor(ax * a) + _pos[1]
		else:
			y=self.length
        

		next_pos2 = [_pos[0] + ax, y]
        
		return 0<=next_pos[0] < self.width and self._movable(_pos,next_pos2) 
