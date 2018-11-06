#include <iostream>
#include <utility>
#include <list>

using namespace std;
using namespace rel_ops;

struct IntVec {
  int x, y;
  IntVec operator+(IntVec &another);
  bool operator==(const IntVec &another) const;
  bool operator<(const IntVec &another) const;
  IntVec(int x = 0, int y = 0): x(x), y(y) {};
};

typedef IntVec Position;
typedef IntVec Velocity;
typedef IntVec Acceleration;
typedef IntVec Point;
struct RaceCourse {
  uint64_t thinkTime;
  int stepLimit;
  int width, length;
  int vision;
};

extern RaceCourse course;

struct Movement {
  Position from, to;
  list<Position> touched;
  bool goesOff(RaceCourse &course);
  bool goesThru(const Point &p) const;
  bool intersects(const Movement& l) const;
  list <Position> touchedSquares() const;
  Movement(Position from, Position to): from(from), to(to) {
    touched=touchedSquares();
  };
};

enum ObstState { UNKNOWN=-1, OBSTACLE=1, PUDDLE=2, MAYBE_OBSTACLE=3, NONE=0};

struct PlayerState {
  Position position;
  Velocity velocity;
  PlayerState();
  PlayerState(Position p, Velocity v);
};

struct RaceInfo {
  int stepNumber;
  uint64_t timeLeft;
  PlayerState me, opponent;
  char **squares;
};

istream &operator>>(istream &in, RaceCourse &course);
istream &operator>>(istream &in, PlayerState &ps);
istream &operator>>(istream &in, RaceInfo &ri);
