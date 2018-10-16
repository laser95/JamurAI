CXXFLAGS= -std=c++11 -W -Wall -g -ggdb
CXX= c++

OBJECTS= raceInfo.o jockey.cpp

TARGET= jockey

all: ${TARGET}

${TARGET}: ${OBJECTS}
	${CXX} ${CXXFLAGS} -o $@ $^

%.o: %.cpp
	${CXX} -c ${CXXFLAGS} $*.cpp -o $*.o
	${CXX} -MM ${CXXFLAGS} $*.cpp > $*.d


clean:
	rm -f *.o *.d
	rm -rf *~ */*~ \#*\#

distclean: clean
	rm -f ${TARGET}
