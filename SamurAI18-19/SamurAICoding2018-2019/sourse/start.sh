python3 course_generator/course_generator.py > course/course.crs
player1="player/greedy"
name1="KENT_GO"
player2="player/greedy"
name2="YAMAUCHI_LASER"
./official/official course/course.crs $player1 $name1 $player2 $name2 >gameLog/test1.racelog
./official/official course/course.crs $player2 $name2 $player1 $name1 >gameLog/test2.racelog