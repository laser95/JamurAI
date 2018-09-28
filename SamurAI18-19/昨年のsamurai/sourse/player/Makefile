CXXFLAGS= -pthread -std=c++11 -W -Wall -O2 -march=native
CXX= c++

OBJECTS_JOCKY= jocky.o raceState.o

TARGET_JOCKY= jocky

all: ${TARGET_JOCKY}

${TARGET_JOCKY}: ${OBJECTS_JOCKY}
	${CXX} ${CXXFLAGS} -o $@ $^ ${AM_LDFLAGS}

-include ${OBJECTS:.o=.d}

%.o: %.cpp
	${CXX} -c ${CXXFLAGS} $*.cpp -o $*.o
	${CXX} -MM ${CXXFLAGS} $*.cpp > $*.d


clean:
	rm -f *.o *.d
	rm -rf *~ */*~ \#*\#

distclean: clean
	rm -f ${TARGET_JOCKY}
