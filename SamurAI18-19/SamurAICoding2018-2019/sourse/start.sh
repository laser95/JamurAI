#!/bin/bash
player1="developmentJocker/jockey"
name1="OurJOCKEY"
player2="player/greedy"
name2="greedy"
win=0
lose=0
aiko=0
for ((i=0 ; i<1000 ; i++))
do
echo $i"-1回目"
python3 course_generator/course_generator.py > course/course${i}.crs
./official/official course/course${i}.crs $player1 $name1 $player2 $name2 --stdinLogFile0 playerLog/stdin1_race${i}-1.txt --stdinLogFile1 playerLog/stdin2_race${i}-1.txt --stderrLogFile0 playerLog/stderr1_race${i}-1.txt --stderrLogFile1 playerLog/stderr2_race${i}-1.txt >gameLog/test${i}-1.racelog
echo $i"-2回目"
./official/official course/course${i}.crs $player2 $name2 $player1 $name1 --stdinLogFile0 playerLog/stdin1_race${i}-2.txt --stdinLogFile1 playerLog/stdin2_race${i}-2.txt --stderrLogFile0 playerLog/stderr1_race${i}-2.txt --stderrLogFile1 playerLog/stderr2_race${i}-2.txt >gameLog/test${i}-2.racelog
json_file=`cat ./gameLog/test${i}-1.racelog`
finished00=`echo ${json_file} | jq .finished[0]`
finished01=`echo ${json_file} | jq .finished[1]`

json_file=`cat ./gameLog/test${i}-2.racelog`
finished10=`echo ${json_file} | jq .finished[1]`
finished11=`echo ${json_file} | jq .finished[0]`

total0=`echo "scale=2; $finished00 + $finished10 " | bc`


total1=`echo "scale=2; $finished01 + $finished11 " | bc`


if [ `echo "$total0 < $total1 "| bc` == 1 ]; then
	echo "勝ち"
	(( win++ ))
elif [ `echo "$total0 > $total1 "| bc` == 1 ]; then
	(( lose++ )) 
	echo "負け"
else
	echo "あいこ"
	(( aiko++ )) 
fi
done

echo $win"勝"$lose"負"$aiko"あいこ"