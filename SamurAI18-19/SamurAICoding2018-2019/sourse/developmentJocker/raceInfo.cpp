#include <cmath>
#include <algorithm>
#include "raceInfo.hpp"

static int dot(int x1, int y1, int x2, int y2) {
  return x1 * x2 + y1 * y2;
}

static int cross(int x1, int y1, int x2, int y2) {
  return x1 * y2 - x2 * y1;
}

static int ccw(int x1, int y1, int x2, int y2, int x3, int y3) {
  return cross(x2 - x1, y2 - y1, x3 - x2, y3 - y2);
}

IntVec IntVec::operator+(IntVec &another) {
  return IntVec(x + another.x, y + another.y);
}

bool IntVec::operator==(const IntVec &another) const {
  return x == another.x && y == another.y;
}

bool IntVec::operator<(const IntVec &another) const {
  return y == another.y ?	// If y position is the same
    x > another.x :		// better to be more to the left
    y < another.y;
}

RaceCourse course;

PlayerState::PlayerState() {}
PlayerState::PlayerState(Position p, Velocity v):
position(p), velocity(v) {}

void addSquares(int x, int y0, int y1, list <Position> &squares) {
  if (y1 > y0) {
    for (int y = y0; y <= y1; y++) {
      squares.emplace_back(x, y);
    }
  } else {
    for (int y = y0; y >= y1; y--) {
      squares.emplace_back(x, y);
    }
  }
}

bool Movement::goesThru(const Point &p) const {
  return !none_of(touched.begin(),touched.end(),[p](Position s){return s==p;});
}

bool Movement::intersects(const Movement& l) const {
  int minx = min(from.x, to.x);
  int maxx = max(from.x, to.x);
  int minlx = min(l.from.x, l.to.x);
  int maxlx = max(l.from.x, l.to.x);
  if (maxx < minlx || maxlx < minx ) return false;
  int miny = min(from.y, to.y);
  int maxy = max(from.y, to.y);
  int minly = min(l.from.y, l.to.y);
  int maxly = max(l.from.y, l.to.y);
  if (maxy < minly || maxly < miny ) return false;
  int d1 = (from.x-l.from.x)*(l.to.y-l.from.y)-(from.y-l.from.y)*(l.to.x-l.from.x);
  int d2 = (to.x-l.from.x)*(l.to.y-l.from.y)-(to.y-l.from.y)*(l.to.x-l.from.x);
  if (d1*d2 > 0) return false;
  int d3 = (l.from.x-from.x)*(to.y-from.y)-(l.from.y-from.y)*(to.x-from.x);
  int d4 = (l.to.x-from.x)*(to.y-from.y)-(l.to.y-from.y)*(to.x-from.x);
  if (d3*d4 > 0) return false;
  return true;
}

list <Position> Movement::touchedSquares() const {
  list <Position> r;
  int dx = to.x - from.x;
  int dy = to.y - from.y;
  int sgnx = dx > 0 ? 1 : -1;
  int sgny = dy > 0 ? 1 : -1;
  if (dx == 0) {
    for (int k = 0, y = from.y; k <= dy; k++, y += sgny) {
      r.emplace_back(from.x, y);
    }
  } else if (dy == 0) {
    for (int k = 0, x = from.x; k <= dx; k++, x += sgnx) {
      r.emplace_back(x, from.y);
    }
  } else {
    // Let us transform the move line so that it goes up and to the right,
    // that is, with dx > 0 and dy > 0.
    // The results will be adjusted afterwards.
    if (sgnx < 0) dx = -dx;
    if (sgny < 0) dy = -dy;
    // We will use the coordinate system in which the start point
    // of the move is at (0,0) and x-coodinate values are doubled,
    // so that x is integral on square borders.
    // The point (X,Y) in the original coordinate system becomes
    //   x = 2*(X-from.x)
    //   y = Y-from.y
    // Such a movement line satisfies the following.
    //   y = dy/dx/2 * x, or 2*dx*y = dy*x
    //
    // The start square and those directly above it
    for (int y = 0; dx*(2*y-1) <= dy; y++) {
      r.emplace_back(0, y);
    }
    // The remaining squares except for those below (dx, dy)
    for (int x = 1; x < 2*dx-1; x += 2) {
      for (int y = (dy*x+dx)/(2*dx) -
	     (dy*x+dx == (dy*x+dx)/(2*dx)*(2*dx) ? 1 : 0);
	   dx*(2*y-1) <= dy*(x+2);
	   y++) {
	r.emplace_back((x+1)/2, y);
      }
    }
    // For the final squares with x = dx
    for (int y = (dy*(2*dx-1)+dx)/(2*dx) -
	   ((dy*(2*dx-1)+dx) == (dy*(2*dx-1)+dx)/(2*dx)*(2*dx) ? 1 : 0);
	 y <= dy;
	 y++) {
      r.emplace_back(dx, y);
    }
    // Adjustment
    for (auto &p: r) {
      if (sgnx < 0) p.x = -p.x;
      if (sgny < 0) p.y = -p.y;
      p.x += from.x;
      p.y += from.y;
    }
  }
  return r;
}

void RaceInfo::SquaresOutOfView(IntVec accel) {

  if(lastMe.position == me.position){
    Position expectedPosition = me.position;
    expectedPosition = expectedPosition + accel;
    const Movement move(lastMe.position,expectedPosition);
    Position tempPosition;
    for(auto itr = move.touched.begin(); itr != move.touched.end(); ++itr) {
        tempPosition = *itr;
        if(squares[tempPosition.x][tempPosition.y] == UNKNOWN)
        {
          squares[tempPosition.x][tempPosition.y] == MAYBE_OBSTACLE;
        }
    }
  }

  if(lastOpponent.position == opponent.position){
    Position expectedOppPosition = opponent.position + lastOpponent.velocity;
    Position tempOppPosition;
    for(int oppAccelX = -1;oppAccelX <= 1;oppAccelX++){
      for(int oppAccelY = -1;oppAccelY <= 1;oppAccelY++){
        tempOppPosition.x = expectedOppPosition.x + oppAccelX;
        tempOppPosition.y = expectedOppPosition.y + oppAccelY;
        Movement oppMove(lastOpponent.position,tempOppPosition);
        for(auto itr = oppMove.touched.begin(); itr != oppMove.touched.end(); ++itr) {
          tempOppPosition = *itr;
          if(squares[tempOppPosition.x][tempOppPosition.y] == UNKNOWN)
          {
            squares[tempOppPosition.x][tempOppPosition.y] == MAYBE_OBSTACLE;
          }
        }
      }
    }
  }

}

istream &operator>>(istream &in, RaceCourse &course) {
  in >> course.thinkTime
     >> course.stepLimit
     >> course.width >> course.length
     >> course.vision;
  return in;
}

istream &operator>>(istream &in, PlayerState &ps) {
  in >> ps.position.x
     >> ps.position.y
     >> ps.velocity.x
     >> ps.velocity.y;
  return in;
};

istream &operator>>(istream &in, RaceInfo &ri) {
  ri.lastMe = ri.me;
  ri.lastOpponent = ri.opponent;
  in >> ri.stepNumber
     >> ri.timeLeft
     >> ri.me
     >> ri.opponent;

  ri.squares = new ObstState*[course.length];
  for (int y = 0; y != course.length; y++) {
    ri.squares[y] = new ObstState[course.width];
    for (int x = 0; x != course.width; x++) {
      int state;
      in >> state;
      ri.squares[y][x] = ObstState(state);
    }
  }

  return in;
}

