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
  //通過する升目のリストを保持
  list<Position> touched;
  bool goesOff(RaceCourse &course);
  /*
    pointを受け取って、from-toに進む直線が点の属する升目を通過するかチェック
    通過すればtrue,しなければfalseを返す
  */
  bool goesThru(const Point &p) const;
  /*
    相手のMovementを受け取って、優先度チェック
    自分に優先度があればtrue,相手にあればfalseを返す
  */
  bool intersects(const Movement& l) const;
  list <Position> touchedSquares() const;
  Movement(Position from, Position to): from(from), to(to) {
    touched = touchedSquares();
  };
};

enum ObstState { UNKNOWN=-1, OBSTACLE=1, PUDDLE=2, MAYBE_OBSTACLE=3, NONE=0};

struct PlayerState {
  Position position;
  Velocity velocity;
  PlayerState();
  PlayerState(Position p, Velocity v);
  bool operator<(const PlayerState &ps) const {
    return position != ps.position ?
      position < ps.position :
      velocity < ps.velocity;
  }
};

struct RaceInfo {
  int stepNumber;
  uint64_t timeLeft;
  PlayerState me, lastMe, opponent, lastOpponent;
  ObstState **squares;
  void SquaresOutOfView(IntVec accel);
};

istream &operator>>(istream &in, RaceCourse &course);
istream &operator>>(istream &in, PlayerState &ps);
istream &operator>>(istream &in, RaceInfo &ri);
