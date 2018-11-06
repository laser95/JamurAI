#include <algorithm>
#include <iostream>
#include <map>
#include <math.h>
#include <set>
#include <vector>
#include "raceInfo.hpp"
#include <iomanip>

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
vector<vector<int>> mp;
//map of my vision
vector<vector<int>> dist;

//beam witdth , search depth
int beam = 600, pre = 7, maxSpeed = 8;

int gcd(int a, int b) {
  if (a % b == 0)
    return b;
  return gcd(b, a % b);
}

int getDist(const RaceCourse& course,vector<vector<int>> &vec, int y, int x, int fromY) {
  if (y < 0 || x < 0 || x >= course.width || y < fromY - course.vision )
    return 1000000;
  if (y > course.vision + fromY)
    return course.vision - y;
  return vec[y][x];
}

bool collision(const RaceInfo& rs,const RaceCourse& course,Movement move, Position p={-1,-1}, Position next={-1,-1}) {
  if(next.x==-1){
    return !none_of(move.touched.begin(),move.touched.end(),
                    [rs,course](Position s){
                      return
                        s.x < 0 || course.width <= s.x ||
                        (0<=s.y && s.y <course.length &&
                        rs.squares[s.y][s.x]==OBSTACLE);
                    });
  }
  else{
    bool stop = collision(rs,course,move);
    if(stop)return true;
    Movement enMove(p,next);
    bool enStop = collision(rs,course,enMove);
    if(!enStop){
      if(move.intersects(enMove)){
        stop=move.goesThru(p);
        enStop=enMove.goesThru(move.from);
        if(stop)return true;
        else if(!enStop){
          if(move.from.y != p.y){
            if(move.from.y > p.y)return true;
            else return false;
          }
          else if(move.from.x != p.x){
            if(move.from.x > p.x)return true;
            else return false;
          }
          return false;
        }
      }
    }
  }
  return false;
}

int hx[9] = {1, 1, 1, 0, 0, 0, -1, -1, -1};
int hy[9] = {1, 0, -1, 1, 0, -1, 1, 0, -1};

//hash of state
long long h(long long a, long long b, long long c, long long d) {
  return ((a + 200) << 48) | ((b + 200) << 32) | ((c + 200) << 16) | (d + 200);
}

int main() {
  //initialization
  cin >> course;
  cout << 0 << endl;
  cout.flush();
  dist.resize(course.vision * 2 + 1 + course.length);
  for (int i = 0; i < course.vision * 2 + 1 + course.length; i++)
    dist[i].resize(course.width);
  maxSpeed = min(maxSpeed,course.vision - 1);

  for(int i = 0; i < course.vision * 2 + 1 + course.length; i++){
    for(int j = 0; j < course.width ; j++){
      dist[i][j] = 10000000;
    }
  }


  RaceInfo rs;
  //proccessing of turn
  while (true) {
    cin >> rs;

    int x=rs.me.position.x;
    int y=rs.me.position.y;
    int vx=rs.me.velocity.x;
    int vy=rs.me.velocity.y;

    int ex=rs.opponent.position.x;
    int ey=rs.opponent.position.y;
    int evx=rs.opponent.velocity.x;
    int evy=rs.opponent.velocity.y;

    int ymax = y, ymin = y;
    if(y < ey)ymax = min(ey, course.length - 1);
    else ymin = max(ey, - course.vision);

    int searchMinY = max(- course.vision, ymin - course.vision), searchMaxY = min(ymax + course.vision,course.length - 1);
    int distOffset = -y + course.vision;


    //distance of between goal and each position
    for (int i = - course.vision ; i < course.length + course.vision; i++) {
      for (int j = 0; j < course.width; j++)
        if(i - course.vision >= course.length)
          dist[i + course.vision][j] = course.length - i;
        else
          dist[i + course.vision][j] = 10000000;
    }


    //using bfs
    multiset<DistNode> dq;
    for (int i = 0; i < course.width; i++) {
      if(ymax + course.vision >= 0){
        if (rs.squares[min(course.length-1, ymax + course.vision - 1)][i]==NONE || rs.squares[min(course.length-1, ymax + course.vision - 1)][i]==PUDDLE ) {
          DistNode ds{i, min(course.length-1, ymax + course.vision - 1), 0};
          dq.insert(ds);
        }
      }
      else{
        DistNode ds{i, min(course.length-1, ymax + course.vision - 1), 0};
        dq.insert(ds);
      }
    }

    //bfs
    //most short distance to go out of view
    while (dq.size() > 0) {
      DistNode now = *dq.begin();
      dq.erase(dq.begin());
      if (dist[now.y + course.vision][now.x] <= now.d)
        continue;
      dist[now.y + course.vision][now.x] = now.d;
      for (int i = 0; i < 9; i++) {
        if (i == 4)
          continue;
        int nx = now.x + hx[i], ny = now.y + hy[i];
        if (nx < 0 || nx >= course.width || ny < searchMinY || ny > searchMaxY)
          continue;
        else if(ny < 0){
          if (ny + course.vision < 0 || ny >= course.length)
            continue;
          DistNode next{nx, ny, now.d + 1};
          if (dist[ny + course.vision][nx] <= next.d)
            continue;
          dq.insert(next);
          continue;
        }
        if (0 <= ny && ny < course.length && rs.squares[ny][nx]==OBSTACLE)
          continue;
        if (i == 0 || i == 2 || i == 6 || i == 8) {
          if (0<=ny && ny<course.length && 0 <= now.y && now.y < course.length && (rs.squares[ny][now.x]==OBSTACLE || rs.squares[now.y][nx]==OBSTACLE))
            continue;
        }
        if (ny + course.vision  < 0 || ny  >= course.length)
          continue;
        DistNode next{nx, ny, now.d + 1};
        if (dist[ny + course.vision][nx] <= next.d)
          continue;
        dq.insert(next);
      }
    }

    /*
    if(rs.stepNumber == 23){
      for(int i = ymax + course.vision * 2 ; i >= ymin ;i--){
        cerr<<setw(2)<<i<<" : ";
        for(int j=0;j<course.width;j++){
          if(dist[i][j] >= 10000000)cerr<<"  # ";
          else cerr<<setw(3)<<dist[i][j]<<" ";
        }
        cerr<<endl;
      }
      cerr<<endl;
      for(int i = course.length + course.vision * 2  ; i >= 0 ; i--){
        cerr<<setw(2)<<i<<" : ";
        for(int j=0;j<course.width;j++){
          if(dist[i][j] >= 10000000)cerr<<"  # ";
          else cerr<<setw(3)<<dist[i][j]<<" ";
        }
        cerr<<endl;
      }
    }
    */


    //array of state [SEARCH_DEPTH][]
    vector<vector<Node>> qs(pre + 1);
    //estimate state of opponent player
    vector<OpponentState> oss(pre + 1);
    for (int i = 0; i < pre + 1; i++)
      oss[i] = OpponentState{0, -1, 0, 0};

    if(ey + distOffset >= 0 && ey + distOffset < course.vision * 2 + 1 && ey < course.length -1){
      Node es{ex, ey, evx, evy, -1, -1, 0, dist[ey + course.vision][x]};
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
            if(qs[i][j].d == 0 && searchMaxY == course.length - 1)
              continue;
            else{
              nowPre = i;
              break;
            }
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
                      getDist(course,dist, ny + course.vision , nx , qs[i][j].y)};
            const Movement move({qs[i][j].x,qs[i][j].y},{nx,ny});
            //move to current my position
            if (i == 0) {
              if (collision(rs,course,move,{x,y},{x,y})) {
                next.x = qs[i][j].x;
                next.y = qs[i][j].y;
                next.vx = 0;
                next.vy = 0;
                next.coli++;
                next.d = getDist(course,dist, next.y + course.vision , next.x , qs[i][j].y);
                if (check[h(next.x, next.y, next.vx, next.vy)])
                  continue;
                check[h(next.x, next.y, next.vx, next.vy)] = true;
                qs[i + 1].push_back(next);
                continue;
              }
              if(next.y >= 0 && next.y < course.length && rs.squares[next.y][next.x]==PUDDLE){
                next.vx = 0;
                next.vy = 0;
              }
              if (next.vy > maxSpeed)
                continue;
              if (check[h(next.x, next.y, next.vx, next.vy)])
                continue;
              check[h(next.x, next.y, next.vx, next.vy)] = true;
              qs[i + 1].push_back(next);
              continue;
            }
            //contact with obstacle or course out
            if (collision(rs,course,move)) {
              next.x = qs[i][j].x;
              next.y = qs[i][j].y;
              next.vx = 0;
              next.vy = 0;
              next.d = getDist(course,dist, next.y + course.vision , next.x , qs[i][j].y);
              next.coli++;
            }
            if(next.y >= 0 && next.y < course.length && rs.squares[next.y][next.x]==PUDDLE){
              next.vx = 0;
              next.vy = 0;
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

    Node start{x, y, vx, vy, -1, -1, 0, dist[y + course.vision][x]};
    qs[0].push_back(start);
    // for check whether states are duplicated
    map<long long, bool> check;
    int nowPre = pre;
    //beam search
    for (int i = 0; i < nowPre; i++) {
      sort(qs[i].begin(), qs[i].end());
      for (int j = 0; j < (int)min(beam, (int)qs[i].size()); j++) {
        if (qs[i][j].d <= 0 ) {
          if(qs[i][j].d == 0 && searchMaxY == course.length - 1)
            continue;
          else{
            nowPre = i;
            break;
          }
        }
        for (int k = 0; k < 9; k++) {
          int ny = qs[i][j].y + qs[i][j].vy + hy[k];
          int nx = qs[i][j].x + qs[i][j].vx + hx[k];
          Node next{
              nx, ny, qs[i][j].vx + hx[k], qs[i][j].vy + hy[k],
              k,  j,  qs[i][j].coli,       getDist(course,dist, ny + course.vision , nx , qs[i][j].y)};
          Movement myMove({qs[i][j].x,qs[i][j].y},{nx,ny});
          if(collision(rs,course,myMove,{oss[i].x,oss[i].y},{oss[i].x+oss[i].vx,oss[i].y+oss[i].vy})){
              next.x = qs[i][j].x;
              next.y = qs[i][j].y;
              next.vx = 0;
              next.vy = 0;
              next.d = getDist(course,dist, next.y + course.vision , next.x , qs[i][j].y);
              next.coli++;
          }
          if(next.y >= 0 && next.y < course.length && rs.squares[next.y][next.x] == PUDDLE){
            next.vx = 0;
            next.vy = 0;
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
