CXXFLAGS= -std=c++11 -W -Wall -g -ggdb
CXX= c++
TARGET= greedy
BEAM= beamSearch

all: ${TARGET} ${BEAM}

greedy: raceInfo.o dp.cpp
	${CXX} ${CXXFLAGS} -o $@ $^

beamSearch: raceInfo.o beamSearch.cpp
	${CXX} ${CXXFLAGS} -o $@ $^

%.o: %.cpp
	${CXX} -c ${CXXFLAGS} $*.cpp -o $*.o
	${CXX} -MM ${CXXFLAGS} $*.cpp > $*.d
clean:
	rm -f *.o *.d
	rm -rf *~ */*~ \#*\#

distclean: clean
	rm -f ${TARGET}
