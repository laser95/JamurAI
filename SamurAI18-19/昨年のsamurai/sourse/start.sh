player1="player/jockey"
name1="jockey1"
player2="player/jockey"
name2="jockey2"
for var in 01 02 03 04 05 06 07 08 09 10 
do
	./official/official samples/course${var}.smrjky $player1 $name1 $player2 $name2 --stdinLogFile0 playerLog/stdin0.txt --stdinLogFile1 playerLog/stdin1.txt --stderrLogFile0 playerLog/stderr0.txt --stderrLogFile1 playerLog/stderr1.txt > gameLog/${var}-1.json
	./official/official samples/course${var}.smrjky $player2 $name2 $player1 $name1 --stdinLogFile0 playerLog/stdin0.txt --stdinLogFile1 playerLog/stdin1.txt --stderrLogFile0 playerLog/stderr0.txt --stderrLogFile1 playerLog/stderr1.txt > gameLog/${var}-2.json
done
./official/official samples/sample-course.smrjky $player1 $name1 $player2 $name2 --stdinLogFile0 playerLog/stdin0.txt --stdinLogFile1 playerLog/stdin1.txt --stderrLogFile0 playerLog/stderr0.txt --stderrLogFile1 playerLog/stderr1.txt > gameLog/sample-1.json
./official/official samples/sample-course.smrjky $player2 $name2 $player1 $name1 --stdinLogFile0 playerLog/stdin0.txt --stdinLogFile1 playerLog/stdin1.txt --stderrLogFile0 playerLog/stderr0.txt --stderrLogFile1 playerLog/stderr1.txt > gameLog/sample-2.json