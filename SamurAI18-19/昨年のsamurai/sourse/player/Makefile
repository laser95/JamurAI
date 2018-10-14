CXXFLAGS= -pthread -std=c++11 -W -Wall -O2 -march=native
CXX= c++

OBJECTS_JOCKEY= jockey.o raceState.o

TARGET_JOCKEY= jockey

all: ${TARGET_JOCKEY}

${TARGET_JOCKEY}: ${OBJECTS_JOCKEY}
	${CXX} ${CXXFLAGS} -o $@ $^ ${AM_LDFLAGS}

-include ${OBJECTS:.o=.d}

%.o: %.cpp
	${CXX} -c ${CXXFLAGS} $*.cpp -o $*.o
	${CXX} -MM ${CXXFLAGS} $*.cpp > $*.d


clean:
	rm -f *.o *.d
	rm -rf *~ */*~ \#*\#

distclean: clean
	rm -f ${TARGET_JOCKEY}
