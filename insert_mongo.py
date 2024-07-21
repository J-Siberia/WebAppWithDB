from time import sleep
import csv
import sys
from datetime import date, timedelta, datetime
import pymongo
import json
import os

ua = ''
headers = {'User-Agent': ua}

csv_header = ['馬名', '父', '母', '母父', '系統(父)', '系統(母)', '系統(父母)', '系統(母母)', #7
              '当該レース(開催日)', '当該レース(競馬場)', '当該レース(開催回数)', '当該レース(コース)', '当該レース(距離)', '当該レース(天気)', '当該レース(馬場状態)', '当該レース(レース名)', '当該レース(人気)', '当該レース(着順)', '当該レース(騎手)', '当該レース(斤量)', '当該レース(頭数)', '当該レース(枠番)', '当該レース(馬番)', '当該レース(タイム)', '当該レース(着差)', '当該レース(上がり)', '当該レース(ブリンカー)', '当該レース(馬体重)', '当該レース(変動)', '当該レース(4角位置)', #29
              '1走前(開催日)', '1走前(競馬場)', '1走前(開催回数)', '1走前(コース)', '1走前(距離)', '1走前(天気)', '1走前(馬場状態)', '1走前(レース名)', '1走前(人気)', '1走前(着順)', '1走前(騎手)', '1走前(斤量)', '1走前(頭数)', '1走前(枠番)', '1走前(馬番)', '1走前(タイム)', '1走前(着差)', '1走前(上がり)', '1走前(ブリンカー)', '1走前(馬体重)', '1走前(変動)', '1走前(4角位置)', #51
              '2走前(開催日)', '2走前(競馬場)', '2走前(開催回数)', '2走前(コース)', '2走前(距離)', '2走前(天気)', '2走前(馬場状態)', '2走前(レース名)', '2走前(人気)', '2走前(着順)', '2走前(騎手)', '2走前(斤量)', '2走前(頭数)', '2走前(枠番)', '2走前(馬番)', '2走前(タイム)', '2走前(着差)', '2走前(上がり)', '2走前(ブリンカー)', '2走前(馬体重)', '2走前(変動)', '2走前(4角位置)', #73
              '3走前(開催日)', '3走前(競馬場)', '3走前(開催回数)', '3走前(コース)', '3走前(距離)', '3走前(天気)', '3走前(馬場状態)', '3走前(レース名)', '3走前(人気)', '3走前(着順)', '3走前(騎手)', '3走前(斤量)', '3走前(頭数)', '3走前(枠番)', '3走前(馬番)', '3走前(タイム)', '3走前(着差)', '3走前(上がり)', '3走前(ブリンカー)', '3走前(馬体重)', '3走前(変動)', '3走前(4角位置)', #95
              '4走前(開催日)', '4走前(競馬場)', '4走前(開催回数)', '4走前(コース)', '4走前(距離)', '4走前(天気)', '4走前(馬場状態)', '4走前(レース名)', '4走前(人気)', '4走前(着順)', '4走前(騎手)', '4走前(斤量)', '4走前(頭数)', '4走前(枠番)', '4走前(馬番)', '4走前(タイム)', '4走前(着差)', '4走前(上がり)', '4走前(ブリンカー)', '4走前(馬体重)', '4走前(変動)', '4走前(4角位置)', #117
              '5走前(開催日)', '5走前(競馬場)', '5走前(開催回数)', '5走前(コース)', '5走前(距離)', '5走前(天気)', '5走前(馬場状態)', '5走前(レース名)', '5走前(人気)', '5走前(着順)', '5走前(騎手)', '5走前(斤量)', '5走前(頭数)', '5走前(枠番)', '5走前(馬番)', '5走前(タイム)', '5走前(着差)', '5走前(上がり)', '5走前(ブリンカー)', '5走前(馬体重)', '5走前(変動)', '5走前(4角位置)'] #139

def create_mongodb_connection():
    # MongoDBへの接続
    user = 'user_name'
    pwd = 'user_password'
    client = pymongo.MongoClient('')
    db = client['db_number']  # データベースの選択
    return db

db = create_mongodb_connection()

def time_to_int(time_str):
    # "m:s.ms"または"s.ms"の形式の時間データを受け取り、秒単位の数値に変換する関数
    if ':' in time_str:
        minutes, seconds_ms = time_str.split(':')
        return float(minutes) * 60 + float(seconds_ms)
    else:
        return float(time_str)

# 重複をチェックするセットを作成
duplicate_check_set = set()

# コマンドライン引数の確認
args_count = len(sys.argv)
if args_count == 1:
    print("引数が指定されていません。")
    sys.exit()

# 読み込むファイルがあるディレクトリ内の全てのCSVファイルに対して処理を行う
for filename in os.listdir(sys.argv[1]):
    if filename.endswith('.csv'):
        # 読み込むファイルのパス
        source_file = os.path.join(sys.argv[1], filename)
        # CSVファイルの読み込みとデータの挿入
        with open(source_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # 勝ち時計を計算
                record = time_to_int(row['当該レース(タイム)'])
                cyakusa = time_to_int(row['当該レース(着差)'])
                if (row['当該レース(着順)'] == '1'):
                    cyakusa = 0.0
                win_record = round(record - cyakusa, 1)
                print(row['当該レース(開催日)'])
                print('record: {0}'.format(record))
                print('cyakusa: {0}'.format(cyakusa))
                print('win_record: {0}'.format(win_record))
                # 特定の列の値をキーとして重複をチェック
                key = (row['当該レース(開催日)'], row['当該レース(競馬場)'], row['当該レース(開催回数)'], row['当該レース(コース)'], row['当該レース(距離)'], row['当該レース(天気)'], row['当該レース(馬場状態)'], row['当該レース(レース名)'], row['当該レース(頭数)'], win_record)  # 重複をチェックする列のキーを指定
                if key not in duplicate_check_set: #重複していない場合，レース情報と1着馬の情報を挿入
                    duplicate_check_set = set()
                    duplicate_check_set.add(key)
                    document = {
                        'race_date': row['当該レース(開催日)'], 
                        'race_place': row['当該レース(競馬場)'], 
                        'place_num': row['当該レース(開催回数)'], 
                        'race_course': row['当該レース(コース)'], 
                        'race_distance': row['当該レース(距離)'], 
                        'race_weather': row['当該レース(天気)'], 
                        'race_condition': row['当該レース(馬場状態)'], 
                        'race_name': row['当該レース(レース名)'],
                        'horse':[
                            {
                                'horse_placing': row['当該レース(着順)'],
                                'horse_name': row['馬名'], 
                                'horse_jockey': row['当該レース(騎手)'],
                                'horse_ninki': row['当該レース(人気)'],
                                'horse_handicap': row['当該レース(斤量)'],
                                'horse_waku': row['当該レース(枠番)'],
                                'horse_num': row['当該レース(馬番)'],
                                'horse_time': row['当該レース(タイム)'],
                                'horse_cyakusa': row['当該レース(着差)'],
                                'horse_blinker': row['当該レース(ブリンカー)'],
                                'horse_weight': row['当該レース(馬体重)'],
                                'horse_wvariation': row['当該レース(変動)'],
                                'horse_4ctime': row['当該レース(上がり)'],
                                'horse_4cposition': row['当該レース(4角位置)'],
                                'horse_sire': row['父'], 
                                'horse_mare': row['母'], 
                                'horse_broodmare': row['母父'], 
                                'horse_p_s': row['系統(父)'], 
                                'horse_p_m': row['系統(母)'], 
                                'horse_p_sm': row['系統(父母)'], 
                                'horse_p_mm': row['系統(母母)']
                            }
                        ]
                    }
                    result = db.races.insert_one(document)
                else: #重複している場合，出走馬の情報のみを挿入
                    new_document = {
                        'horse_placing': row['当該レース(着順)'],
                        'horse_name': row['馬名'], 
                        'horse_jockey': row['当該レース(騎手)'],
                        'horse_ninki': row['当該レース(人気)'],
                        'horse_handicap': row['当該レース(斤量)'],
                        'horse_waku': row['当該レース(枠番)'],
                        'horse_num': row['当該レース(馬番)'],
                        'horse_time': row['当該レース(タイム)'],
                        'horse_cyakusa': row['当該レース(着差)'],
                        'horse_blinker': row['当該レース(ブリンカー)'],
                        'horse_weight': row['当該レース(馬体重)'],
                        'horse_wvariation': row['当該レース(変動)'],
                        'horse_4ctime': row['当該レース(上がり)'],
                        'horse_4cposition': row['当該レース(4角位置)'],
                        'horse_sire': row['父'], 
                        'horse_mare': row['母'], 
                        'horse_broodmare': row['母父'], 
                        'horse_p_s': row['系統(父)'], 
                        'horse_p_m': row['系統(母)'], 
                        'horse_p_sm': row['系統(父母)'], 
                        'horse_p_mm': row['系統(母母)']
                    }
                    db.races.update_one(
                        {'_id': result.inserted_id},  # 更新対象のドキュメントを識別するクエリ
                        {'$push': {'horse': new_document}}  # `$push`演算子で配列に要素を追加
                    )
                    
        print("Finished! ({0})".format(source_file))