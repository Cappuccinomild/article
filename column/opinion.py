import requests
from bs4 import BeautifulSoup
import datetime
import time
import os
from tqdm import tqdm
import math
import multiprocessing
import sys
from tqdm import tqdm


def str_to_date(input):#yyyymmdd 문자열을 datetime 객체로 변경
    #                             yyyy              mm              dd
    return datetime.datetime(int(input[:4]), int(input[4:6]), int(input[6:]))

def date_to_str(input):#datetime 객체를 yyyymmdd 형식으로 변경
    output = ''
    output += str(input.year)

    if(input.month < 10):
        output +='0'

    output += str(input.month)
    if(input.day < 10):
        output +='0'
    output += str(input.day)

    return output


def get_link(map_val):#일별 기사 페이지 링크를 추출함

    #map_val[시작날짜, 종료날짜]
    date_s = map_val[0]
    date_e = map_val[1]

    naver_Column = "https://news.naver.com/main/opinion/todayColumn.naver"

    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}

    #get 인자
    datas={
        'date':date_to_str(date_s),
        'page':'1' }

    print(datas)

    #전체코드세부코드 디렉토리를 만든 후 파일 저장
    dir = "./Column_link"
    os.makedirs(dir, exist_ok=True)


    #날짜별로 탐색
    date_desc = date_s
    for x in tqdm(range((date_s - date_e).days+1)):

        #페이지를 증가시키며 탐색
        link_set = []
        while True:

            try:
                resp = requests.get(naver_Column, headers = hdr, params=datas, timeout=10)

            except requests.exceptions.Timeout as timeout:

                print(timeout)
                print(datas)
                time.sleep(10)
                continue

            #html 추출
            if resp.status_code == 200:
                _html = resp.text

            #페이지 파싱
            soup = BeautifulSoup(_html, 'lxml')

            #페이지 번호를 위한 파싱
            page_list = soup.find("div", class_='paging')

            #현재페이지
            page_now = page_list.find('strong').text
            if page_now is None:
                print("null page")
                time.sleep(10)
                continue
            #print(page_now, datas['page'])

            #현재페이지와 탐색페이지가 다르면 종료
            if page_now != datas['page']:
                datas['page'] = '1'
                break

            #현재 페이지에서 기사 링크 목록 추출
            for link in soup.find("div", class_="todaycolumn").find_all("li"):

                #메이저 언론사인지 확인
                media = link.find('em', class_="todaycolumn_press").text
                #링크모음 저장
                #저장태그
                #100273_media_20200101_2_link
                link_set.append("_".join([media, datas['date'], datas['page'], link.find('a')['href']]))


            #페이지 증가
            datas['page'] = str(int(datas['page']) + 1)

        #파일명
        fname = "_".join([datas['date']])+".txt"


        f = open(dir+'/'+fname, "w")
        f.write("\n".join(link_set))
        f.write("\n")

        #종료조건
        if datas['date'] == date_e:
            break

        #날짜 감소
        date_desc = date_desc - datetime.timedelta(days=1)

        datas['date'] = date_to_str(date_desc)


if __name__ == '__main__':

    start = time.time()


    '''
    date_s = input("start:")
    date_e = input("end:")
    '''

    #cmd 입력으로 opinion.py 2022-03-06 2022-01-01실행
    if len(sys.argv) == 3:
        date_s = sys.argv[1]
        date_e = sys.argv[2]

    else:
        print("날짜를 입력해주세요.")
        sys.exit()
    #yyyy-mm-dd의 양식 날짜를 받음
    '''
    #탐색 시작 날짜
    date_s = "2022-03-06"

    #탐색 종료 날짜
    date_e = "2021-01-01"

    #date_s = 2022-01-01
    #date_e = 2021-01-01
    #->2022년 1월 1일부터 2021년 1월 1일까지의 데이터 수집
    '''

    date_s = date_s.split("-")
    date_e = date_e.split("-")

    for i in range(0, 3):
        date_s[i] = int(date_s[i])
        date_e[i] = int(date_e[i])

    date_s = datetime.datetime(date_s[0],date_s[1],date_s[2])
    date_e = datetime.datetime(date_e[0],date_e[1],date_e[2])

    #날짜를 N개의 묶음으로 나눔
    days = (date_s - date_e).days

    #process의 개수
    N = 10

    temp_e = []
    for i in range(0,days, math.ceil(days/N)):

        temp_e.append(date_s - datetime.timedelta(days=i))

    map_val=[]
    for i in range(len(temp_e)-1):
        map_val.append([temp_e[i], temp_e[i+1] - datetime.timedelta(days=1)])

    map_val.append([temp_e[-1], date_e])

    process_num = len(map_val)
    print(map_val, "process : ", process_num)

    pool = multiprocessing.Pool(processes=N)
    pool.map(get_link, map_val)

    pool.close()
    pool.join()
