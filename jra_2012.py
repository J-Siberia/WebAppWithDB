from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
from lxml import etree
from lxml import html
from time import sleep
import csv
import re
from datetime import date, timedelta, datetime

horse_element_list=[]
ua = 'uwaaaaaaaaaaaaaaaaaaaaaaa'
headers = {'User-Agent': ua}

csv_header = ['馬名', '父', '母', '母父', '系統(父)', '系統(母)', '系統(父母)', '系統(母母)', 
              '当該レース(開催日)', '当該レース(競馬場)', '当該レース(開催回数)', '当該レース(コース)', '当該レース(距離)', '当該レース(天気)', '当該レース(馬場状態)', '当該レース(レース名)', '当該レース(人気)', '当該レース(着順)', '当該レース(騎手)', '当該レース(斤量)', '当該レース(頭数)', '当該レース(枠番)', '当該レース(馬番)', '当該レース(タイム)', '当該レース(着差)', '当該レース(上がり)', '当該レース(ブリンカー)', '当該レース(馬体重)', '当該レース(変動)', '当該レース(4角位置)',
              '1走前(開催日)', '1走前(競馬場)', '1走前(開催回数)', '1走前(コース)', '1走前(距離)', '1走前(天気)', '1走前(馬場状態)', '1走前(レース名)', '1走前(人気)', '1走前(着順)', '1走前(騎手)', '1走前(斤量)', '1走前(頭数)', '1走前(枠番)', '1走前(馬番)', '1走前(タイム)', '1走前(着差)', '1走前(上がり)', '1走前(ブリンカー)', '1走前(馬体重)', '1走前(変動)', '1走前(4角位置)',
              '2走前(開催日)', '2走前(競馬場)', '2走前(開催回数)', '2走前(コース)', '2走前(距離)', '2走前(天気)', '2走前(馬場状態)', '2走前(レース名)', '2走前(人気)', '2走前(着順)', '2走前(騎手)', '2走前(斤量)', '2走前(頭数)', '2走前(枠番)', '2走前(馬番)', '2走前(タイム)', '2走前(着差)', '2走前(上がり)', '2走前(ブリンカー)', '2走前(馬体重)', '2走前(変動)', '2走前(4角位置)',
              '3走前(開催日)', '3走前(競馬場)', '3走前(開催回数)', '3走前(コース)', '3走前(距離)', '3走前(天気)', '3走前(馬場状態)', '3走前(レース名)', '3走前(人気)', '3走前(着順)', '3走前(騎手)', '3走前(斤量)', '3走前(頭数)', '3走前(枠番)', '3走前(馬番)', '3走前(タイム)', '3走前(着差)', '3走前(上がり)', '3走前(ブリンカー)', '3走前(馬体重)', '3走前(変動)', '3走前(4角位置)',
              '4走前(開催日)', '4走前(競馬場)', '4走前(開催回数)', '4走前(コース)', '4走前(距離)', '4走前(天気)', '4走前(馬場状態)', '4走前(レース名)', '4走前(人気)', '4走前(着順)', '4走前(騎手)', '4走前(斤量)', '4走前(頭数)', '4走前(枠番)', '4走前(馬番)', '4走前(タイム)', '4走前(着差)', '4走前(上がり)', '4走前(ブリンカー)', '4走前(馬体重)', '4走前(変動)', '4走前(4角位置)',
              '5走前(開催日)', '5走前(競馬場)', '5走前(開催回数)', '5走前(コース)', '5走前(距離)', '5走前(天気)', '5走前(馬場状態)', '5走前(レース名)', '5走前(人気)', '5走前(着順)', '5走前(騎手)', '5走前(斤量)', '5走前(頭数)', '5走前(枠番)', '5走前(馬番)', '5走前(タイム)', '5走前(着差)', '5走前(上がり)', '5走前(ブリンカー)', '5走前(馬体重)', '5走前(変動)', '5走前(4角位置)']

# 全角の「ー」（U+30FC）と「＋」（U+FF0B）を半角のハイフンとプラスに変換する辞書を作成
plus_and_minus_translation_table = str.maketrans({
    '－': '-',
    '＋': '+',
})

def is_horse_weight(text):
    # 数字と「(」「)」「＋」「－」「-」以外の文字が含まれているか判定
    if re.search(r"[^\d()\uFF0B\uFF0D-]", text):
        return False
    return True

def separate_horse_weight(text):
    return_hw=[]
    # 正規表現パターンにマッチする部分を全て取得
    matches_hw = re.findall(r"(.+?)\((.*?)\)", text)
    # 区切られた部分を表示
    if matches_hw:
      for match in matches_hw:
         outside, inside = match
         if inside == '---':
            inside = '0'
         return_hw.append(outside)
         return_hw.append(inside)
      return return_hw
    else:
      return ["", ""]

def extract_pedigree(soup ,num):
  horse_ped_row = soup.select("#HorseBloodWrapnew > section > table > tr > td")[num]
  horse_ped_s = re.search(r'\((.*?)\)', horse_ped_row.get_text(strip=True))  # ()に囲まれた文字列を正規表現で抽出
  if horse_ped_s:
    horse_ped = horse_ped_s.group(1)
  else:
    horse_ped = ""
  return horse_ped

def split_string(string):
    match = re.match(r"\d+回(.+)", string)
    if match:
        location = match.group(1)
        digits = re.findall(r"\d+", string)
        return location, digits[0] if digits else None
    else:
        return None, None

def get_holidays(year):
    holidays = []
    # 休日のカレンダー情報を定義する
    holiday_calendar = {
        date(year, 1, 5): "年始の開催日",
        date(year, 1, 9): "成人の日",
        date(year, 9, 17): "敬老の日",
        date(year, 10, 1): "特別開催日",
        date(year, 10, 8): "スポーツの日",
        date(year, 12, 24): "年末の開催日",
        # ... 他の祝日を追加する ...
    }
    # 土曜日と日曜日を追加する
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    delta = timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
        if current_date in holiday_calendar or current_date.weekday() >= 5:
            holidays.append(current_date)
        current_date += delta
    return holidays

def FromCircle(str):
  if int(hex(ord(str)), 16) <= 9331 and int(hex(ord(str)), 16) >=9321:
    i = int(hex(ord(str)), 16)-9311
    return i
  else:
    return 99
  
# 開催日のリストを取得
holiday_list = get_holidays(2012)

# CSVファイルを書き込みモードで開く
with open("output_2012.csv", "w", newline="") as csvfile:
  writer = csv.writer(csvfile)

  # ヘッダーを書き込む
  writer.writerow(csv_header)
    
  race_url_1_1 ="https://www.keibalab.jp/db/race/"
  race_url_2 = [str(place).zfill(2) for place in range(1, 12)]
  race_url_3= [str(race).zfill(2) for race in range(1, 13)]
  race_url_4="/raceresult.html"
  for race_date in holiday_list:
    race_date_str = race_date.strftime("%Y/%m/%d") #1987/05/09
    race_date_str_url = race_date.strftime("%Y%m%d") #19870509
    race_url_1 = race_url_1_1 + race_date_str_url
    print(race_date_str)
    for place_num in race_url_2:
        race_url_part1 = race_url_1 + place_num
        res = requests.get(race_url_part1+"02"+race_url_4, headers=headers)
        soup_test = BeautifulSoup(res.text, "lxml")
        if not soup_test.select('#tab1 > div:nth-child(2) > div.clearfix.fL.racedatawrap.mr10 > div.raceaboutbox.clearfix > div.fL.racedatabox > div.fL.ml10 > div > h1'):
           continue
        for num_race in race_url_3:
            res = requests.get(race_url_part1+num_race+race_url_4, headers=headers)
            soup = BeautifulSoup(res.text, "lxml")

            horse_selector_1 = "#tab1 > div.RaceTableWrap > table > tbody > tr:nth-child("
            horse_selector_2 = [str(race).zfill(2) for race in range(1, 19)]
            horse_selector_3 = ") > td:nth-child(4) > a"
            for horse_url_num in horse_selector_2:
                horse_data_csv_row = []

                horse_url = soup.select(horse_selector_1 + horse_url_num + horse_selector_3)
                if not horse_url:
                    continue
                res_horse = requests.get("https://www.keibalab.jp" + horse_url[0]['href'], headers=headers)
                soup_horse = BeautifulSoup(res_horse.text, "lxml")

                if (not soup_horse.select("#HorseNamenewWrap > div > h1 > span.DBName.std12")) or (not soup_horse.select("#HorseBloodWrapnew > section > table > tr > td > a > span")):
                    break

                horse_name_row = soup_horse.select("#HorseNamenewWrap > div > h1 > span.DBName.std12")[0] #馬名
                horse_name = horse_name_row.text
                horse_data_csv_row.append(horse_name)
                horse_sire_row = soup_horse.select("#HorseBloodWrapnew > section > table > tr > td > a > span")[0] #父
                horse_sire = horse_sire_row.text
                horse_data_csv_row.append(horse_sire)
                horse_mare_row = soup_horse.select("#HorseBloodWrapnew > section > table > tr > td > a > span")[1] #母
                horse_mare = horse_mare_row.text
                horse_data_csv_row.append(horse_mare)
                horse_broodmare_row = soup_horse.select("#HorseBloodWrapnew > section > table > tr > td > a")[8] #母父
                horse_broodmare = (re.sub(r"\(.*?\)", "", horse_broodmare_row.get_text(strip=True))).strip()
                horse_data_csv_row.append(horse_broodmare)

                horse_ped0 = extract_pedigree(soup_horse ,0) #父の系統
                horse_data_csv_row.append(horse_ped0)
                horse_ped1 = extract_pedigree(soup_horse ,7) #母の系統
                horse_data_csv_row.append(horse_ped1)
                horse_ped01 = extract_pedigree(soup_horse ,4) #父母の系統
                horse_data_csv_row.append(horse_ped01)
                horse_ped11 = extract_pedigree(soup_horse ,11) #母母の系統
                horse_data_csv_row.append(horse_ped11)

                # 当該レースとそれ以前のレースデータを取得(各行を処理)
                result_table = soup_horse.find("table", id="HorseResultTable")
                race_result_limit_max = 6
                race_result_limit = 0
                last_race = []
                for row in result_table.find_all('tr'):
                    date_cell = row.find('td', class_='tL', itemprop='datePublished')
                    if date_cell:
                       if datetime.strptime(date_cell.get_text(strip=True), "%Y/%m/%d").date() <= datetime.strptime(race_date_str, "%Y/%m/%d").date():
                            extracted_row = [cell.get_text(strip=True) for cell in row.find_all('td')]

                            last_race.append(extracted_row[0]) #開催日

                            where_race = re.sub(r'^\d+', '', extracted_row[1]) # 先頭の数字を削除
                            where_race = re.sub(r'\d+$', '', where_race) # 末尾の数字を削除
                            where_race = where_race.replace('回', '') # 文字列中の「回」を削除
                            last_race.append(where_race) #場(e.g. 中山)

                            if re.findall(r"\d+$", extracted_row[1]):
                                if (re.findall(r"\d+$", extracted_row[1]))[0]:
                                    last_race.append((re.findall(r"\d+$", extracted_row[1]))[0]) #開催回数(e.g. 2)
                                else:
                                    last_race.append("")
                            else:
                                last_race.append("")
                            if re.match(r"(\D+)(\d+)", extracted_row[2]):
                                non_numeric_part = re.match(r"(\D+)(\d+)", extracted_row[2]).group(1)
                                numeric_part = re.match(r"(\D+)(\d+)", extracted_row[2]).group(2)
                                last_race.append(non_numeric_part)  # コース(e.g. ダ or 芝)
                                last_race.append(numeric_part)  # 距離(e.g. 1200)
                            else:
                                last_race.append("")
                                last_race.append("")
                            last_race.append(extracted_row[3]) #天気(e.g. 晴)
                            last_race.append(extracted_row[4]) #コンディション(e.g. 稍重)
                            last_race.append(extracted_row[5]) #レース名(e.g. 2歳未勝利)
                            last_race.append(extracted_row[6]) #人気(e.g. 12)
                            last_race.append(extracted_row[7]) #着順(e.g. 2)
                            last_race.append(extracted_row[8]) #騎手(e.g. 江田照男)
                            last_race.append(extracted_row[9]) #斤量(e.g. 52.0)
                            last_race.append(extracted_row[10]) #頭数(e.g. 18)
                            last_race.append(extracted_row[11]) #枠番(e.g. 1)
                            last_race.append(extracted_row[12]) #枠番(e.g. 2)
                            last_race.append(extracted_row[13]) #タイム(e.g. 1:53.5)
                            last_race.append(extracted_row[14]) #着差(e.g. 0.1)
                            last_race.append(extracted_row[16]) #上がり(e.g. 39.8)
                            last_race.append(extracted_row[17]) #ブリンカーの有無(B or "")

                            if is_horse_weight(extracted_row[18]):
                                horse_weight_list = separate_horse_weight(extracted_row[18])
                                last_race.append(horse_weight_list[0]) #馬体重(e.g. 500)
                                if horse_weight_list[1]:
                                    last_race.append(horse_weight_list[1].translate(plus_and_minus_translation_table)) #馬体重の増減(e.g. ー8)
                                else:
                                    last_race.append("")
                            else:
                                last_race.append("")
                                last_race.append("")
                            last_race.append(extracted_row[23]) #4角の位置(e.g. 2)
                            #print(last_race)

                            race_result_limit += 1
                            if race_result_limit >= race_result_limit_max: # レースは過去5走まで遡る
                              if len(last_race) < 22 * 6:
                                  last_race += [""] * (22 * 6 - len(last_race))
                              break
                
                horse_data_csv_row.extend(last_race)

                # ---csvファイルへの書き込み---
                if any(not c.isdigit() for c in horse_data_csv_row[17]):
                    continue        # 着順に数字以外の文字が含まれていたら、該当する行は飛ばす
                else:
                    writer.writerow(horse_data_csv_row) 
                    if extracted_row[0] and horse_name:
                        print("Finish Writing (" + extracted_row[0] + ", " + horse_name + ")")
                    else:
                        print("Something Wrong!")