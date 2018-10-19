#include <map>
#include <queue>
#include <utility>
#include <iomanip>
#include <string>
#include <set>
#include <algorithm>
#include <map>
#include <list>
#include <cctype>
#include "raceInfo.hpp"

const int SEARCH_DEPTH = 4;

ostream &operator<<(ostream &out, const IntVec &v) {
  out << "(" << v.x << "," << v.y << ")";
  return out;
}

map<Point, int> bfsed;
using History = vector<pair<Point, Point>>;

static pair<long long, long long> decode(const History& hist, const RaceCourse& course)
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

static long long cal(const History& hist, const int depth, const RaceCourse& course)
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
static pair<long long, IntVec> alpha_beta(const RaceInfo& rs, const RaceCourse& course, const PlayerState& me, const PlayerState& rv,
  History &hist, int depth = 0, long long alpha = -INF, long long beta = INF)
{
  if (memo.count({ depth, {me, rv} })) {
    return memo[{depth, { me, rv }}];
  }
  IntVec myBestAction = { 0, 0 };
  if (depth == SEARCH_DEPTH || me.position.y >= course.length) {
    if (rs.me.position == me.position) {
      // stucked
      return { -INF, myBestAction };
    }
    return { cal(hist, depth, course), myBestAction };
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
          rv_roop_count++;
          PlayerState nextMe = me;
          nextMe.velocity.x += mx;
          nextMe.velocity.y += my;
          nextMe.position.x += nextMe.velocity.x;
          nextMe.position.y += nextMe.velocity.y;
          const Movement myMove(me.position, nextMe.position);
          PlayerState nextRv = rv;
          nextRv.velocity.x += ex;
          nextRv.velocity.y += ey;
          nextRv.position.x += nextRv.velocity.x;
          nextRv.position.y += nextRv.velocity.y;
          const Movement enMove(rv.position, nextRv.position);
          bool stopped = false;
          if (!none_of(myMove.touched.begin(), myMove.touched.end(),
                  [rs, course](Position s) {
                    return
                      0 <= s.y &&
                      s.y < course.length &&
                      rs.squares[s.y][s.x] == OBSTACLE;
                  }))
          {
            nextMe.position = me.position;
            stopped |= true;
          }
          if (rv.position.y >= course.length
            || !none_of(enMove.touched.begin(), enMove.touched.end(),
                    [rs, course](Position s) {
                      return
                        0 <= s.y &&
                        s.y < course.length &&
                        rs.squares[s.y][s.x] == OBSTACLE;
                    }))
          {
            nextRv.position = rv.position;
            stopped |= true;
          }
          if (myMove.intersects(enMove) && !stopped) {
            bool myStopped = myMove.goesThru(rv.position),enStopped = enMove.goesThru(me.position);
            if(myStopped){
              if(enStopped){
                nextMe.position = me.position;
                nextRv.position = rv.position;
              }
              else{
                nextMe.position = me.position;
              }
            }
            else if(enStopped){
              nextRv.position = rv.position;
            }
            else if (me.position.y != rv.position.y) {
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

pair<int, IntVec> dls(const RaceInfo& rs,const Point& p, const IntVec v, const Point rvp, const RaceCourse& course, int depth, set<IntVec> done = {})
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
      const Movement move(p, np);
      list <Position> touched = move.touchedSquares();
      if (none_of(touched.begin(), touched.end(),
                [rs, course](Position s) {
                  return
                    0 <= s.y &&
                    s.y < course.length &&
                    rs.squares[s.y][s.x] == OBSTACLE;
                })
        /*|| move.goesThru(rvp)*/) {
        const auto& ret = dls(rs, p, nv, rvp, course, depth - 1, done);
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

static IntVec find_movable(const RaceInfo& rs, const RaceCourse& course)
{
  // IDDFS
  for (int d = 1; ; ++d) {
    const auto ret = dls(rs,rs.me.position, rs.me.velocity, rs.opponent.position, course, d);
    if (ret.first == 1 << 28) {
      continue;
    }
    return ret.second;
  }
}

static void bfs(const RaceInfo& rs, const RaceCourse& course)
{
  bfsed.clear();
  int ymax;
  if(rs.me.position.y>rs.opponent.position.y){
   ymax = rs.me.position.y + course.vision;
  }
  else{
    ymax = rs.opponent.position.y + course.vision;
  }

  for (int x = 0; x < course.width; ++x) {
    if (rs.squares[ymax][x] == OBSTACLE || (x > 0 && rs.squares[ymax][x - 1] == NONE)) {
		continue;
    }
	if (rs.squares[ymax][x] == NONE && rs.squares[ymax][x - 1] == OBSTACLE) {
		int x1 = x + 1;
		while (rs.squares[ymax][x1] == NONE && x1 < course.width + 1) {
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
  for (int y = ymax - 1; y > - 1; --y) {
	  for (int x = 0; x < course.width; ++x) {
		  if (rs.squares[y][x] == NONE && rs.squares[y + 1][x] == NONE) {
			  bfsed[Point(x, y)] = bfsed[Point(x, y + 1)] + 15;
		  }
		  else if (rs.squares[y][x] == NONE && rs.squares[y + 1][x] != NONE) {
			  bfsed[Point(x, y)] = 1000;
		  }
	  }
	  for (int x = 0; x < course.width; ++x) {
		  if (rs.squares[y][x] == NONE && rs.squares[y][x - 1] == NONE) {
			  if (bfsed[Point(x, y)] > bfsed[Point(x - 1, y)] + 12) {
				  bfsed[Point(x, y)] = bfsed[Point(x - 1, y)] + 12;
			  }
		  }
	  }
	  for (int x = course.width - 1; x > -1; --x) {
		  if (rs.squares[y][x] == NONE && rs.squares[y][x + 1] == NONE) {
			  if (bfsed[Point(x, y)] > bfsed[Point(x + 1, y)] + 12) {
				  bfsed[Point(x, y)] = bfsed[Point(x + 1, y)] + 12;
			  }
		  }
	  }
	  for (int x = 0; x < course.width; ++x) {
		  if (rs.squares[y][x] == NONE) {
			  if (rs.squares[y + 1][x] == NONE) {
				  bfsed[Point(x, y)] = bfsed[Point(x, y)] - 2;
			  }
			  if (rs.squares[y][x + 1] == NONE && rs.squares[y + 1][x + 1] == NONE) {
				  bfsed[Point(x, y)] = bfsed[Point(x, y)] - 2;
			  }
			  if (rs.squares[y][x - 1] == NONE && rs.squares[y + 1][x - 1] == NONE) {
				  bfsed[Point(x, y)] = bfsed[Point(x, y)] - 2;
			  }
		  }
	  }
  }
}

static IntVec play(const RaceInfo& rs, const RaceCourse& course) {
  memo.clear();
  bfs(rs, course);
  History hist(SEARCH_DEPTH);
  auto p = alpha_beta(rs, course, { rs.me.position, rs.me.velocity }, { rs.opponent.position, rs.opponent.velocity }, hist);
  if (p.first == -INF) {
    // If my player will be stuck, use greedy.
    return find_movable(rs, course);
  }
  return p.second;
}

int main(int, char *[]) {
  cin >> course;
  cout << "0" << endl;
  cout.flush();
  left_border = (int)((course.width - 1) / 3);
  while (true) {
    RaceInfo rs;
    cin >> rs;
    IntVec accel = play(rs, course);
    cout << accel.x << ' ' << accel.y << endl;
    cout.flush();
    while (isspace(cin.peek())) cin.ignore(1);
  }
}
