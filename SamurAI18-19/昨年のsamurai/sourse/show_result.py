import sys
import re
import os

#jsonファイルのあるディレクトリ
#各自の環境に応じて要変更
path="./log/"
files=[]
player0=[]
player1=[]
race1_0=[]
race1_1=[]
race2_0=[]
race2_1=[]

for file in os.listdir(path):
    if os.path.isfile(path+file):
        files.append(file)

#log00_0.json,log01_1といった感じで保存されている
#最初の00がコースを指す 00->sample ...
#次の0,1がどちらが左スタートかを判別するための値
for file in files:
    if(file[-7:]=='_0.json'):
        player0.append(file)
    if(file[-7:]=='_1.json'):
        player1.append(file)

for file in player0:
    with open(path+file,"r") as f:
        log=f.readlines()
    #"time0": 200, "time1": 200,
    time=[goal_time.strip() for goal_time in log if 'time0' in goal_time]
    result=time[0].split(' ')
    result[1]=result[1].strip(',')
    result[3]=result[3].strip(',')
    race1_0.append(result[1])
    race1_1.append(result[3])

for file in player1:
    with open(path+file,"r") as f:
        log=f.readlines()
    time=[goal_time.strip() for goal_time in log if 'time0' in goal_time]
    result=time[0].split(' ')
    result[1]=result[1].strip(',')
    result[3]=result[3].strip(',')
    race2_1.append(result[1])
    race2_0.append(result[3])

output=['score : (p0) - (p1)','      ','------','race1 ','race2 ','','winner']
for i in range(11):
    output[1]+='|'+str(i).center(11,' ')
    output[2]+='+-----------'
    #p0 - p1
    output[3]+='|'+('{0:.1f}'.format(float(race1_0[i]))+'-'+'{0:.1f}'.format(float(race1_1[i]))).center(11,' ')
    #p0 - p1
    output[4]+='|'+('{0:.1f}'.format(float(race2_0[i]))+'-'+'{0:.1f}'.format(float(race2_1[i]))).center(11,' ')
    #winner
    p0=float(race1_0[i])+float(race2_0[i])
    p1=float(race1_1[i])+float(race2_1[i])
    output[6]+='|'+('-' if p0==p1 else 'p0' if p0<p1 else 'p1' ).center(11,' ')

output[5]=output[2]

with open("race_result.txt",'w',encoding='utf-8') as f:
    f.write('\n'.join(output))
