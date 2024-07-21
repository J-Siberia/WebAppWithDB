# WebAppWithDB
Flaskと様々なデータベース(MySQL, MongoDB, Redis)を使って簡単なウェブアプリケーションを作成したもの

# 概要
競馬ラボ(https://www.keibalab.jp/)からスクレイピングによって収集したデータを用いて，JRAのレースを検索したり，レースをブックマークしたりするウェブアプリケーションである．

このアプリケーションの目的は，印象に残ったレースを後から見返せるように記憶することに加えて，投票を通じてお気に入りのレースを他人と共有したり認知してもらったりするというものである．

また，このアプリケーションを利用する際にはユーザ登録およびログインが必要である．

# 機能
このアプリケーションの主な機能を以下に列挙する．

・条件を指定してレースを検索できる，

・レースをブックマークに追加し，後にそれらを確認できる．

・レースに投票できる．投票結果次第では，そのレースを多くの人に認知および共有することができる．

# データベースについて
MySQLはログインとユーザ登録の際に利用される．

MongoDBはレースの検索とレースのブックマークに使われている．
2つの目的で使われているため，コレクションも2つ作成している．

Redisはレースの投票機能に用いられている．

# 使用したデータについて
前述の通り，今回使用したデータは競馬ラボ(https://www.keibalab.jp/)からスクレイピングしたものである．

スクレイピングに利用したコードはjra_2012.pyである．
ファイルの名前の通り，これは2012年のJRAのレース情報を取得するものである．
他の年のデータを取得したい場合，get_holidays()関数内の変数holiday_calendarを変更し，get_holidays()関数の引数を取得したい年の数値に変更すれば良い．

# app.py
このアプリケーションの核となるコードである．

# insert_mongo.py
スクレイピングしたデータをMongoDBに格納するためのコードである．
