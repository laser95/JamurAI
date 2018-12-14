import numpy as np
import gym
import gym.spaces
import subprocess
import json
import sys
import math

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

	def _step(self,action):
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
        next_pos = self._pos + self.next_vel #予定位置


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
        if self._movable(self._pos,self.next_pos): 
        	if self.map[self.next_pos[1]][self.next_pos[0]] == 0:
	        	self._vel = self.next_vel
	        	self._pos = self.next_pos
	        if self.map[self.next_pos[1]][self.next_pos[0]] == 2:
	        	self._pos = self.next_pos
	        	self._vel = np.array([0,0])
        else :
        	self._vel = np.array([0,0])
        	self._pos = self._pos

    	done = self._is_done(_pos,next_pos)

    	#ゴールしたら1,それ以外はゴールにy軸
    	if done:
    		reward = 1.0
    	else:
    		reward = 1.0 * self._pos[1]/goolY



    	#取り得る最大のマップを定義, 全て1(壁)で指定
		big_map = np.empty((100, 20)) 

		#指定されたマップを-1(未知)で指定
		big_map[0:self.length, 0:self.width] = -1

		#指定されたマップのy軸の範囲外を-2(ゴール以降)で指定
		big_map[self.length:99, 0:19] = -2
	
		#指定されたマップ範囲外を-3(コース外)で指定
		big_map[:, self.width+1:19] = -3  
		
		step = 0 
		# ゴールするまで、毎stepでbig_mapを取得
		while self._pos[1] < self.length:
			vision = self._pos[1] + self.vision
			big_map[0:vision-1, 0:self.width] = self.course[0:vision-1, :]
			step += 1


        return {"map" : big_map, "length" : self.length, "position" : self._pos, "velocity" : self._vel},reward,done,{}


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


	def _movable(self,_pos,next_pos): #移動可能判定
        r = []
        if self.next_pos[0] == self._pos[0]:
            addSquares(self._pos[0], self._pos[1], self.next_pos[1], r)
        else:
            a = (self.next_pos[1] - self._pos[1]) / (self.next_pos[0] - self._pos[0])
            sgnx = 1 if self._pos[0] < self.next_pos[0] else -1
            y1 = a * sgnx / 2.0 + self._pos[1] + 0.5
            iy1 = (math.floor(y1) if self.next_pos[1] > self._pos[1]
                   else math.ceil(y1) - 1)
            addSquares(self._pos[0], self._pos[1], iy1, r)
            for x in range(self._pos[0] + sgnx, self.next_pos[0], sgnx):
                y0 = a * (x - self._pos[0] - sgnx / 2) + self._pos[1] + 0.5
                y1 = a * (x - self._pos[0] + sgnx / 2) + self._pos[1] + 0.5
                if self.next_pos[1] > self._pos[1]:
                    iy0, iy1 = math.ceil(y0) - 1, math.floor(y1)
                else:
                    iy0, iy1 = math.floor(y0), math.ceil(y1) - 1
                addSquares(x, iy0, iy1, r)
            y0 = a * (self.next_pos[0] - self._pos[0] - sgnx / 2) + self._pos[1] + 0.5
            iy0 = (math.ceil(y0) - 1 if self.next_pos[1] > self._pos[1]
                   else math.floor(y0))
            addSquares(self.next_pos[0], iy0, self.next_pos[1], r)

		return (0 <= self._pos[0] < self.width 
				and not any(0 <= s[1] and s[0] < self.length and
                                self.map[s[1]][s[0]] == 1 for s in r))

	def addSquares(x, y0, y1, squares):
        if y1 > y0:
            for y in range(y0, y1 + 1, 1):
                squares.append(np.array(x, y))
        else:
            for y in range(y0, y1 - 1, -1):
                squares.append(np.array(x, y))
    
    def _is_done(self,_pos,next_pos):
        if self.next_pos[1] < self.length:
            return False
        
        dx = (self.next_pos[0] - self._pos[0])
        a = (self.next_pos[1] - self._pos[1]) / dx #傾き
        y = math.floor(dx * a) + self._pos[1]
        
        while y <= self.length - 1:
            dx = dx - 1
            y = math.floor(dx * a) + self._pos[1]
        next_pos2 = [self._pos[0] + dx, y]
        
        return self.next_pos[0] < self.width
                and self.movable(self._pos,next_pos2) 
