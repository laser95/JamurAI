#include <map>
#include <queue>
#include <utility>
#include <iomanip>
#include <string>
#include <set>
#include "raceState.hpp"

const int SEARCH_DEPTH = 4;

struct PlayerState {
  Point position;
  IntVec velocity;
  bool operator<(const PlayerState &ps) const {
    return position != ps.position ?
      position < ps.position :
      velocity < ps.velocity;
  }
  PlayerState(Point p, IntVec v) : position(p), velocity(v) {}
};

std::ostream& operator<<(std::ostream& out, const Point& p)
{
  return out << "(" << p.x << ", " << p.y << ")";
}

std::ostream& operator<<(std::ostream& out, const LineSegment& ls)
{
  return out << ls.p1 << " => " << ls.p2;
}

std::ostream& operator<<(std::ostream& out, const PlayerState& ps)
{
  return out << "{" << ps.position << ", " << ps.velocity << "}";
}

map<Point, int> bfsed;
using History = vector<pair<Point, Point>>;

static pair<long long, long long> decode(const History& hist, const Course& course)
{
  long long shift_y = 1LL;
  long long sum_y = 0LL;
  for (auto ite = hist.rbegin(); ite != hist.rend(); ++ite) {
    shift_y *= (course.length + 1) * 2;
    sum_y *= (course.length + 1) * 2;
    sum_y -= bfsed[ite->first];
    sum_y += bfsed[ite->second];
    sum_y += course.length;
  }
  return make_pair(sum_y, shift_y);
}

static long long cal(const PlayerState& me, const PlayerState& rv, const History& hist, const int depth, const RaceState& rs, const Course& course)
{
  // calculating heuristic score here
  // HINT: this code use only y-axis, but we can do all kinds of things to win
  const auto de = decode(hist, course);
  long long val = 0;
  val += (SEARCH_DEPTH - depth) * de.second;
  val += de.first;
  return val;
}

const long long INF = 1LL << 60;
int left_border;
using State = pair<int, pair<PlayerState, PlayerState>>;
map<State, pair<long long, IntVec>> memo;

// this function(pseudo alpha-beta algorithm) attempt to prevent enemy's move
static pair<long long, IntVec> alpha_beta(const RaceState& rs, const Course& course, const PlayerState& me, const PlayerState& rv,
  History &hist, int depth = 0, long long alpha = -INF, long long beta = INF)
{
  if (memo.count({ depth, {me, rv} })) {
    return memo[{depth, { me, rv }}];
  }
  IntVec myBestAction = { 0, 0 };
  if (depth == SEARCH_DEPTH || me.position.y >= course.length) {
    if (rs.position == me.position) {
      // stucked
      return { -INF, myBestAction };
    }
    return { cal(me, rv, hist, depth, rs, course), myBestAction };
  }
  int priority = 1;
  if (me.position.x <= left_border)priority = -1;
  for (int my = 1; -1 <= my; --my) {
    // limit velocity
    if (me.velocity.y + my > course.vision / 2) {
      continue;
    }
	int roop_count = 0;
	for (int mx = -1 * priority; roop_count < 3; mx += priority) {
	  roop_count++;
      long long gamma = beta;
	  int rv_priority = 1;
	  if (rv.position.x <= left_border)rv_priority = -1;
      for (int ey = 1; -1 <= ey; --ey) {
		int rv_roop_count = 0;
        for (int ex = -1 * rv_priority; rv_roop_count < 3; ex += rv_priority) {
          PlayerState nextMe = me;
          nextMe.velocity.x += mx;
          nextMe.velocity.y += my;
          nextMe.position.x += nextMe.velocity.x;
          nextMe.position.y += nextMe.velocity.y;
          const LineSegment myMove(me.position, nextMe.position);
          PlayerState nextRv = rv;
          nextRv.velocity.x += ex;
          nextRv.velocity.y += ey;
          nextRv.position.x += nextRv.velocity.x;
          nextRv.position.y += nextRv.velocity.y;
          const LineSegment enMove(rv.position, nextRv.position);
          bool stopped = false;
          if (course.obstacled(me.position, nextMe.position)
            || myMove.goesThru(rv.position)) {
            nextMe.position = me.position;
            stopped |= true;
          }
          if (rv.position.y >= course.length
            || course.obstacled(rv.position, nextRv.position)
            || enMove.goesThru(me.position)) {
            nextRv.position = rv.position;
            stopped |= true;
          }
          if (myMove.intersects(enMove) && !stopped) {
            if (me.position.y != rv.position.y) {
              if (me.position.y < rv.position.y) {
                nextRv.position = rv.position;
              }
              else {
                nextMe.position = me.position;
              }
            }
            else if (me.position.x != rv.position.x) {
              if (me.position.x < rv.position.x) {
                nextRv.position = rv.position;
              }
              else {
                nextMe.position = me.position;
              }
            }
          }
          hist[depth] = make_pair(
            Point(nextMe.position.x,min(course.length, nextMe.position.y)), Point(nextRv.position.x,min(course.length, nextRv.position.y))
          );
          auto res = alpha_beta(rs, course, nextMe, nextRv, hist, depth + 1, alpha, gamma);
          hist[depth] = make_pair(Point(0,0), Point(0,0));
          if (res.first < gamma) {
            gamma = res.first;
          }
          if (alpha >= gamma) {
            gamma = alpha;
            goto END_ENEMY_TURN;
          }
        }
      }
    END_ENEMY_TURN:
      if (alpha < gamma) {
        alpha = gamma;
        myBestAction = { mx, my };
      }
      if (alpha >= beta) {
        memo[{depth, { me, rv }}] = { beta, myBestAction };
        return { beta, myBestAction };
      }
    }
  }
  memo[{depth, { me, rv }}] = { alpha, myBestAction };
  return { alpha, myBestAction };
}

pair<int, IntVec> dls(const Point& p, const IntVec v, const Point rvp, const Course& course, int depth, set<IntVec> done = {})
{
  if (depth == 0) {
    return { 1 << 28, {} };
  }
  int best = 1 << 28;
  IntVec bestAction = {};
  for (int dy = -1; dy <= 1; ++dy) {
    for (int dx = -1; dx <= 1; ++dx) {
      int nvx = v.x + dx;
      int nvy = v.y + dy;
      int npx = p.x + nvx;
      int npy = p.y + nvy;
      const IntVec nv(nvx, nvy);
      const Point np(npx, npy);
      if (done.count(nv)) {
        continue;
      }
      done.insert(nv);
      const LineSegment move(p, np);
      if (course.obstacled(p, np)
        || move.goesThru(rvp)) {
        const auto& ret = dls(p, nv, rvp, course, depth - 1, done);
        if (ret.first < best) {
          best = ret.first;
          bestAction = { dx, dy };
        }
      }
      else {
        if (np.y >= course.length) {
          best = -1;
          bestAction = { dx, dy };
        }
        if (bfsed.count(np) && bfsed[np] < best) {
          best = bfsed[np];
          bestAction = { dx, dy };
        }
      }
    }
  }
  return { best, bestAction };
}

static IntVec find_movable(const RaceState& rs, const Course& course)
{
  // IDDFS
  for (int d = 1; ; ++d) {
    const auto ret = dls(rs.position, rs.velocity, rs.oppPosition, course, d);
    if (ret.first == 1 << 28) {
      continue;
    }
    return ret.second;
  }
}

static void bfs(const RaceState& rs, const Course& course)
{
  bfsed.clear();
  const int ymax = rs.position.y + course.vision;
  for (int x = 0; x < course.width; ++x) {
    if (course.obstacle[ymax][x] == ObstState::OBSTACLE || (x > 0 && course.obstacle[ymax][x - 1] == ObstState::NONE)) {
		continue;
    }
	if (course.obstacle[ymax][x] == ObstState::NONE && course.obstacle[ymax][x - 1] == ObstState::OBSTACLE) {
		int x1 = x + 1;
		while (course.obstacle[ymax][x1] == ObstState::NONE && x1 < course.width + 1) {
			x1 = x1 + 1;
		}
		for (int x2 = x; x2 < x1; ++x2) {
			bfsed[Point(x2, ymax)] = course.width - min(x2 - x, x1 - x2 - 1);
		}
	}
  }
  for (int y = ymax + 1; y < course.length + course.vision; y++) {
    for (int x = 0; x < course.width; x++) {
      bfsed[Point(x, y)] = bfsed[Point(x, y - 1)] - 15;
    }
  }
  for (int y = ymax - 1; y > max(0, rs.position.y - course.vision) - 1; --y) {
	  for (int x = 0; x < course.width; ++x) {
		  if (course.obstacle[y][x] == ObstState::NONE && course.obstacle[y + 1][x] == ObstState::NONE) {
			  bfsed[Point(x, y)] = bfsed[Point(x, y + 1)] + 15;
		  }
		  else if (course.obstacle[y][x] == ObstState::NONE && course.obstacle[y + 1][x] != ObstState::NONE) {
			  bfsed[Point(x, y)] = 1000;
		  }
	  }
	  for (int x = 0; x < course.width; ++x) {
		  if (course.obstacle[y][x] == ObstState::NONE && course.obstacle[y][x - 1] == ObstState::NONE) {
			  if (bfsed[Point(x, y)] > bfsed[Point(x - 1, y)] + 12) {
				  bfsed[Point(x, y)] = bfsed[Point(x - 1, y)] + 12;
			  }
		  }
	  }
	  for (int x = course.width - 1; x > -1; --x) {
		  if (course.obstacle[y][x] == ObstState::NONE && course.obstacle[y][x + 1] == ObstState::NONE) {
			  if (bfsed[Point(x, y)] > bfsed[Point(x + 1, y)] + 12) {
				  bfsed[Point(x, y)] = bfsed[Point(x + 1, y)] + 12;
			  }
		  }
	  }
	  for (int x = 0; x < course.width; ++x) {
		  if (course.obstacle[y][x] == ObstState::NONE) {
			  if (course.obstacle[y + 1][x] == ObstState::NONE) {
				  bfsed[Point(x, y)] = bfsed[Point(x, y)] - 2;
			  }
			  if (course.obstacle[y][x + 1] == ObstState::NONE && course.obstacle[y + 1][x + 1] == ObstState::NONE) {
				  bfsed[Point(x, y)] = bfsed[Point(x, y)] - 2;
			  }
			  if (course.obstacle[y][x - 1] == ObstState::NONE && course.obstacle[y + 1][x - 1] == ObstState::NONE) {
				  bfsed[Point(x, y)] = bfsed[Point(x, y)] - 2;
			  }
		  }
	  }
  }
}

static IntVec play(const RaceState& rs, const Course& course) {
  memo.clear();
  bfs(rs, course);
  History hist(SEARCH_DEPTH);
  auto p = alpha_beta(rs, course, { rs.position, rs.velocity }, { rs.oppPosition, rs.oppVelocity }, hist);  
  cerr << p.first << std::endl; 
  if (p.first == -INF) {
    // If my player will be stuck, use greedy.
    cerr << "not ab!!!!" << std::endl; 
    return find_movable(rs, course);
  }
  return p.second;
}

int main() {
  Course course(cin);
  cout << 0 << endl;
  cout.flush();
  left_border = (int)((course.width - 1) / 3);
  while (true) {
    RaceState rs(cin, course);
    IntVec accel = play(rs, course);
    cout << accel.x << ' ' << accel.y << endl;
  }
}
