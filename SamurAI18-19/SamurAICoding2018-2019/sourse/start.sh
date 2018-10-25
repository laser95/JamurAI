python3 course_generator/course_generator.py > course/course.crs
player1="developmentJocker/jockey"
name1="OurJOCKEY"
player2="player/greedy"
name2="greedy"
./official/official course/course.crs $player1 $name1 $player2 $name2 --stdinLogFile0 playerLog/stdin1_race1.txt --stdinLogFile1 playerLog/stdin2_race1.txt --stderrLogFile0 playerLog/stderr1_race1.txt --stderrLogFile1 playerLog/stderr2_race1.txt >gameLog/test1.racelog
./official/official course/course.crs $player2 $name2 $player1 $name1 --stdinLogFile0 playerLog/stdin2_race2.txt --stdinLogFile1 playerLog/stdin1_race2.txt --stderrLogFile0 playerLog/stderr2_race2.txt --stderrLogFile1 playerLog/stderr1_race2.txt >gameLog/test2.racelog