#include <algorithm>
#include <iostream>
#include <map>
#include <math.h>
#include <set>
#include <vector>

using namespace std;

struct DistNode {
  int x, y, d;
};

bool operator<(const DistNode &lhs, const DistNode &rhs) {
  return lhs.d < rhs.d;
}

struct OpponentState {
  int x, y, vx, vy;
};

struct Node {
  int x, y, vx, vy, from, id, coli, d;
};

bool operator<(const Node &lhs, const Node &rhs) {
  if (lhs.d == rhs.d) {
    if (lhs.coli == rhs.coli) {
      if (lhs.vy > 0)
        return lhs.vy < rhs.vy;
      else
        return lhs.vy > rhs.vy;
    }
    return lhs.coli < rhs.coli;
  }
  return lhs.d < rhs.d;
}

//course map
vector<vector<bool>> mp;
//map of my vision
vector<vector<int>> dist;
long long t, s;
int w, l, d;
//beam witdth , search depth
int beam = 600, pre = 7, maxSpeed = 8;

int gcd(int a, int b) {
  if (a % b == 0)
    return b;
  return gcd(b, a % b);
}

int getDist(vector<vector<int>> &vec, int y, int x) {
  if (y < 0)
    return 1000000;
  if (y > d * 2)
    return d * 2 - y;
  return vec[y][x];
}

// 互いに素なvx, vyに対して衝突判定を行う
bool innerCollision(int x, int y, int vx, int vy) {
  if (mp[y + vy][x + vx])
    return true;
  if (vy == 0 || vx == 0) {
    return false;
  }
  double f = (double)vy / vx;
  int diff = vx / abs(vx);
  double g = f * diff / 1000;
  for (int i = 0; i != diff * abs(vx); i += diff) {
    if (mp[y + (int)(ceil(g))][x + i] && mp[y + (int)(floor(g))][x + i]) {
      return true;
    }
    if (mp[y + (int)(ceil(g))][x + i + diff] &&
        mp[y + (int)(floor(g))][x + i]) {
      return true;
    }
    if (mp[y + (int)(ceil(g))][x + i] &&
        mp[y + (int)(floor(g))][x + i + diff]) {
      return true;
    }
    g += f * diff;
  }
  g = 0;
  f = (double)vx / vy;
  diff = vy / abs(vy);
  g += f * diff / 1000;
  for (int i = 0; i != diff * abs(vy); i += diff) {
    if (mp[y + i][x + (int)(ceil(g))] && mp[y + i][x + (int)(floor(g))]) {
      return true;
    }
    if (mp[y + i + diff][x + (int)(ceil(g))] &&
        mp[y + i][x + (int)(floor(g))]) {
      return true;
    }
    if (mp[y + i][x + (int)(ceil(g))] &&
        mp[y + i + diff][x + (int)(floor(g))]) {
      return true;
    }
    g += f * diff;
  }
  return false;
}

//collide with obstacle
bool collision(int x, int y, int vx, int vy) {
  if (y > l) {
    return false;
  }
  int ax, ay;
  if (vx == 0 && vy == 0) {
    return false;
  }
  int v;
  if (vx == 0) {
    ax = 0;
    ay = vy / abs(vy);
    v = abs(vy);
  }
  if (vy == 0) {
    ax = vx / abs(vx);
    ay = 0;
    v = abs(vx);
  }
  if (vx != 0 && vy != 0) {
    v = gcd(abs(vx), abs(vy));
    ax = vx / v;
    ay = vy / v;
  }
  for (int i = 0; i < v; i++) {
    if (innerCollision(x, y, ax, ay))
      return true;
    x += ax;
    y += ay;
  }
  return false;
}

//collide with stopping opponent player
bool collideOpponent(int x, int y, int vx, int vy, int ex, int ey) {
  int evx, evy;
  if (vx != 0 && vy != 0) {
    int gxy = gcd(abs(vx), abs(vy));
    evx = vx / gxy;
    evy = vy / gxy;
  } else if (vy != 0) {
    evy = vy / abs(vy);
    evx = 0;
  } else if (vx != 0) {
    evx = vx / abs(vx);
    evy = 0;
  } else {
    evx = 0;
    evy = 0;
  }
  int ivx = evx, ivy = evy;
  while (true) {
    if (x + ivx == ex && y + ivy == ey) {
      return true;
    }
    if (ivx == vx && ivy == vy)
      break;
    ivx += evx;
    ivy += evy;
  }
  return false;
}

//crossing
// 0: don't crossing
// 1: crossing with priority
// -1: crossing with no priority
int collideMovingOpponent(int x, int y, int vx, int vy, int ex, int ey, int evx,
                          int evy) {
  bool hasPriority;
  if (y == ey)
    hasPriority = x < ex;
  else
    hasPriority = y < ey;
  int x1 = x, x2 = x + vx, y1 = y, y2 = y + vy;
  int x3 = ex, x4 = ex + evx, y3 = ey, y4 = ey + evy;
  int a = (x3 - x4) * (y1 - y3) + (y3 - y4) * (x3 - x1);
  int b = (x3 - x4) * (y2 - y3) + (y3 - y4) * (x3 - x2);
  int c = (x1 - x2) * (y3 - y1) + (y1 - y2) * (x1 - x3);
  int d = (x1 - x2) * (y4 - y1) + (y1 - y2) * (x1 - x4);
  if (c * d < 0 && a * b < 0) {
    if (hasPriority)
      return 1;
    else
      return -1;
  } else {
    return 0;
  }
}

int hx[9] = {1, 1, 1, 0, 0, 0, -1, -1, -1};
int hy[9] = {1, 0, -1, 1, 0, -1, 1, 0, -1};

//hash of state
long long h(long long a, long long b, long long c, long long d) {
  return ((a + 200) << 48) | ((b + 200) << 32) | ((c + 200) << 16) | (d + 200);
}

int main() {
  //initialization
  cin >> t >> s >> w >> l >> d;
  cout << 0 << endl;
  mp.resize(l + 100);
  for (int i = 0; i < l + 100; i++)
    mp[i].resize(w);
  dist.resize(d * 2 + 1);
  for (int i = 0; i < d * 2 + 1; i++)
    dist[i].resize(w);
  maxSpeed = min(maxSpeed, d - 1);

  //proccessing of turn
  while (true) {
    int ss, tt;
    cin >> ss >> tt;
    int x, y, vx, vy;
    cin >> x >> y >> vx >> vy;
    int ex, ey, evx, evy;
    cin >> ex >> ey >> evx >> evy;
    for (int i = 0; i < d * 2 + 1; i++) {
      vector<int> v(w);
      for (int j = 0; j < w; j++)
        cin >> v[j];
      if (y - d + i >= 0) {
        for (int j = 0; j < w; j++)
          mp[y - d + i][j] = (v[j] == 1);
      }
    }
    //distance of between goal and each position
    for (int i = 0; i < d * 2 + 1; i++) {
      for (int j = 0; j < w; j++)
        dist[i][j] = 10000000;
    }
    //using bfs
    multiset<DistNode> dq;
    for (int i = 0; i < w; i++) {
      if (!mp[min(l, y + d)][i]) {
        DistNode ds{i, min(l, y + d), 0};
        dq.insert(ds);
      }
    }
    int searchMinY = max(0, y - d), searchMaxY = y + d;
    int distOffset = -y + d;

    //bfs
    //most short distance to go out of view
    while (dq.size() > 0) {
      DistNode now = *dq.begin();
      dq.erase(dq.begin());
      if (dist[now.y + distOffset][now.x] <= now.d)
        continue;
      dist[now.y + distOffset][now.x] = now.d;
      for (int i = 0; i < 9; i++) {
        if (i == 4)
          continue;
        int nx = now.x + hx[i], ny = now.y + hy[i];
        if (nx < 0 || nx >= w || ny < searchMinY || ny > searchMaxY)
          continue;
        if (mp[ny][nx])
          continue;
        if (i == 0 || i == 2 || i == 6 || i == 8) {
          if (mp[ny][now.x] && mp[now.y][nx])
            continue;
        }
        if (ny + distOffset < 0 || ny + distOffset > 2 * d)
          continue;
        DistNode next{nx, ny, now.d + 1};
        if (dist[ny + distOffset][nx] <= next.d)
          continue;
        dq.insert(next);
      }
    }

    //array of state [SEARCH_DEPTH][]
    vector<vector<Node>> qs(pre + 1);
    //estimate state of opponent player
    vector<OpponentState> oss(pre + 1);
    for (int i = 0; i < pre + 1; i++)
      oss[i] = OpponentState{0, -1, 0, 0};
    //if opponent player come into my view
    if (ey >= 0) {
      Node es{ex, ey, evx, evy, -1, -1, 0, dist[ey + distOffset][x]};
      oss[0].x = ex;
      oss[0].y = ey;
      oss[0].vx = evx;
      oss[0].vy = evy;
      qs[0].push_back(es);
      map<long long, bool> check;
      int nowPre = pre;
      //beam search
      for (int i = 0; i < nowPre; i++) {
        if (qs[i].size() == 0) {
          nowPre = i - 1;
          break;
        }
        sort(qs[i].begin(), qs[i].end());
        for (int j = 0; j < (int)min(beam, (int)qs[i].size()); j++) {
          if (qs[i][j].d <= 0) {
            nowPre = i;
            break;
          }
          for (int k = 0; k < 9; k++) {
            int ny = qs[i][j].y + qs[i][j].vy + hy[k];
            int nx = qs[i][j].x + qs[i][j].vx + hx[k];
            Node next{nx,
                      ny,
                      qs[i][j].vx + hx[k],
                      qs[i][j].vy + hy[k],
                      k,
                      j,
                      qs[i][j].coli,
                      getDist(dist, ny + distOffset, nx)};
            //move to current my position
            if (i == 0) {
              if (collideOpponent(ex, ey, next.vx, next.vy, x, y)) {
                next.x = qs[i][j].x;
                next.y = qs[i][j].y;
                next.coli++;
                next.d = getDist(dist, next.y + distOffset, next.x);
                if (next.vy > maxSpeed)
                  continue;
                if (check[h(next.x, next.y, next.vx, next.vy)])
                  continue;
                check[h(next.x, next.y, next.vx, next.vy)] = true;
                qs[i + 1].push_back(next);
                continue;
              }
            }
            //course out
            if (next.x < 0 || next.x >= w || next.y < 0) {
              next.x = qs[i][j].x;
              next.y = qs[i][j].y;
              next.coli++;
              next.d = getDist(dist, next.y + distOffset, next.x);
              if (next.vy > maxSpeed)
                continue;
              if (check[h(next.x, next.y, next.vx, next.vy)])
                continue;
              check[h(next.x, next.y, next.vx, next.vy)] = true;
              qs[i + 1].push_back(next);
              continue;
            }
            //contact with obstacle
            if (collision(qs[i][j].x, qs[i][j].y, next.vx, next.vy)) {
              next.x = qs[i][j].x;
              next.y = qs[i][j].y;
              next.d = getDist(dist, next.y + distOffset, next.x);
              next.coli++;
            }
            if (next.vy > maxSpeed)
              continue;
            if (check[h(next.x, next.y, next.vx, next.vy)])
              continue;
            check[h(next.x, next.y, next.vx, next.vy)] = true;
            qs[i + 1].push_back(next);
          }
        }
      }
      sort(qs[nowPre].begin(), qs[nowPre].end());
      oss[nowPre] = OpponentState{qs[nowPre][0].x, qs[nowPre][0].y,
                                  qs[nowPre][0].vx, qs[nowPre][0].vy};
      int id = qs[nowPre][0].id;
      for (int i = nowPre - 1; i > 0 && id >= 0; i--) {
        oss[i] =
            OpponentState{qs[i][id].x, qs[i][id].y, qs[i][id].vx, qs[i][id].vy};
        id = qs[i][id].id;
      }
      oss[0] = OpponentState{ex, ey, evx, evy};
      for (int i = 0; i < pre + 1; i++)
        qs[i].clear();
    }

    Node start{x, y, vx, vy, -1, -1, 0, dist[y + distOffset][x]};
    qs[0].push_back(start);
    // for check whether states are duplicated
    map<long long, bool> check;
    int nowPre = pre;
    //beam search
    for (int i = 0; i < nowPre; i++) {
      sort(qs[i].begin(), qs[i].end());
      for (int j = 0; j < (int)min(beam, (int)qs[i].size()); j++) {
        if (qs[i][j].d <= 0) {
          nowPre = i;
          break;
        }
        for (int k = 0; k < 9; k++) {
          int ny = qs[i][j].y + qs[i][j].vy + hy[k];
          int nx = qs[i][j].x + qs[i][j].vx + hx[k];
          Node next{
              nx, ny, qs[i][j].vx + hx[k], qs[i][j].vy + hy[k],
              k,  j,  qs[i][j].coli,       getDist(dist, ny + distOffset, nx)};
          //move to opponent position
          if (collideOpponent(qs[i][j].x, qs[i][j].y, next.vx, next.vy,
                              oss[i].x, oss[i].y)) {
            next.x = qs[i][j].x;
            next.y = qs[i][j].y;
            next.coli++;
            next.d = getDist(dist, next.y + distOffset, next.x);
            qs[i + 1].push_back(next);
            continue;
          }
          //crossing with opponent player
          if (oss[i].y >= 0 && oss[i + 1].y >= 0) {
            int cmo = collideMovingOpponent(
                qs[i][j].x, qs[i][j].y, next.vx, next.vy, oss[i].x, oss[i].y,
                oss[i + 1].x - oss[i].x, oss[i + 1].y - oss[i].y);
            if (cmo < 0) {
              next.x = qs[i][j].x;
              next.y = qs[i][j].y;
              next.coli++;
              next.d = getDist(dist, next.y + distOffset, next.x);
              qs[i + 1].push_back(next);
              continue;
            } else if (cmo > 0) {
              next.coli--;
            }
          }
          //course out
          if (next.x < 0 || next.x >= w || next.y < 0) {
            next.x = qs[i][j].x;
            next.y = qs[i][j].y;
            next.coli++;
            next.d = getDist(dist, next.y + distOffset, next.x);
            if (next.vy > maxSpeed)
              continue;
            if (check[h(next.x, next.y, next.vx, next.vy)])
              continue;
            check[h(next.x, next.y, next.vx, next.vy)] = true;
            qs[i + 1].push_back(next);
            continue;
          }
          //contact with obstacle
          if (collision(qs[i][j].x, qs[i][j].y, next.vx, next.vy)) {
            next.x = qs[i][j].x;
            next.y = qs[i][j].y;
            next.d = getDist(dist, next.y + distOffset, next.x);
            next.coli++;
          }
          if (next.vy > maxSpeed)
            continue;
          if (check[h(next.x, next.y, next.vx, next.vy)])
            continue;
          check[h(next.x, next.y, next.vx, next.vy)] = true;
          qs[i + 1].push_back(next);
        }
      }
    }
    sort(qs[nowPre].begin(), qs[nowPre].end());
    int id = qs[nowPre][0].id;
    for (int i = nowPre - 1; i > 1; i--) {
      id = qs[i][id].id;
    }
    int from = qs[1][id].from;
    cout << hx[from] << " " << hy[from] << endl;
  }
  return 0;
}
