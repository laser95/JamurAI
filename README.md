# samurai18-19_practice
***
##運用方法について  
Issue毎にローカルリポジトリにブランチを作成  
ローカルリポジトリ内でマージしたのち，リモートリポジトリの個人のブランチにプッシュ  
ただしプッシュする前にリモートリポジトリのブランチをローカルリポジトリにプル  
***
##コマンドについて  

#最初にやること  
1. ローカルPCにgithub用のディレクトリを作成  
2. git clone https://github.com/laser95/samurai18-19_practice.git を該当ディレクトリ内で入力  
3. 新しいディレクトリができているはずなので移動  
4. git init を入力  
5. git fetch を入力  

##編集から追加の流れ  
1． git checkout -b [ブランチ名] ブランチはローカルリポジトリのブランチ(タスクと対応させたほうがいいと思う)  
2． ファイルを編集  
3． git add [(ディレクトリ名/)ファイル名]  
4． git commit -m “[コメント]”  
5． git checkout master  
6． git pull origin [個人のブランチ名] ブランチはリモートリポジトリのブランチ  
7． git merge [ブランチ名]  
8． 競合したら手動でがんばる(競合しなかった自動)  
9． git remote add [個人のブランチ名] https://github.com/laser95/samurai18-19_practice.git ブランチはリモートリポジトリのブランチ  
10． git push origin [個人のブランチ名] ブランチはリモートリポジトリのブランチ 
11． タスクが終了したら git branch -d [ブランチ名] ブランチはローカルリポジトリのブランチ  
