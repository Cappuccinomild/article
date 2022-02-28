import requests
from bs4 import BeautifulSoup
import datetime
import time
import re
import ast
import os
from tqdm import tqdm

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

#테스팅 중
#100 264에 대한 오늘부터 2021년 1월 1일까지의 기사 링크 추출
def get_link_test(map_val):#일별 기사 페이지 링크를 추출함

    #대분류코드 = 정치:100   경제:101  사회:102  생활/문화:103   세계:104   IT/과학:105

    #소분류코드
    #정치sid2 = 청와대:264  국회/정당:265   북한:268 행정:266 국방/외교:267  정치일반:269
    #경제sid2 = 금융:259    증권:258  산업/재계:261   중기/벤처:771   부동산:260 글로벌 경제:262  생활경제:310    경제일반:263
    #사회sid2 = 사건사고:249  교육:250  노동:251  언론:254  환경:252  인권/복지:59b   식품/의료:255   지역:256  인물:276  사회일반:257
    #생활/문화sid2 = 건강정보:241   자동차/시승기:239    도로/교통:240  여행/레저:237 음식/맛집:238  패션/뷰티:376  공연/전시:242  책:243  종교:244  날씨:248  생활문화 일반:245
    #세계sid2 = 아시아/호주:231    미국/중남미:232  유럽:233   중동/아프리카:234    세계일반:322
    #IT/과학sid2 = 모바일:731    인터넷/SNS:226    통신/뉴미디어:227    IT일반:230   보안/해킹:732  컴퓨터:283    게임/리뷰:229  과학 일반:228

    #대분류 소분류에 사용되는 sid 목록
    sid = {
    '100':["264","265","268","266","267","269"],
    '101':["259","258","261","771","260","262","310","263"],
    '102':["249","250","251","254","252","59b","255","256","276","257"],
    '103':["241","239","240","237","238","376","242","243","244","248","245"],
    '104':["231","232","233","234","322"],
    '105':["731","226","227","230","732","283","229","228"]
    }

    #map_val[대분류코드, 시작날짜, 종료날짜]
    sid1 = map_val[0]
    date_s = map_val[1]
    date_e = map_val[2]
    sid2 = sid[sid1][0]


    #전체코드세부코드 디렉토리를 만든 후 파일 저장
    dir = './'+sid1+sid2
    os.makedirs(dir, exist_ok=True)

    naver_news = "https://news.naver.com/main/list.naver"
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}


    #get 인자
    datas={
        'mode':'LS2D',
        'mid':'shm',
        'sid2':sid2,
        'sid1':sid1,
        'date':date_to_str(date_s),
        'page':'1' }


    #날짜별로 탐색
    for x in tqdm(range((date_s - date_e).days+1)):

        #페이지를 증가시키며 탐색
        link_set = []
        while True:

            resp = requests.get(naver_news, headers = hdr, params=datas)

            #html 추출
            if resp.status_code == 200:
                _html = resp.text

            #페이지 파싱
            soup = BeautifulSoup(_html, 'lxml')

            #페이지 번호를 위한 파싱
            page_list = soup.find("div", class_='paging')

            #현재페이지
            page_now = page_list.find('strong').text
            #print(page_now, datas['page'])

            #현재페이지와 탐색페이지가 다르면 종료
            if page_now != datas['page']:
                datas['page'] = '1'
                break

            #현재 페이지에서 기사 링크 목록 추출
            for link in soup.find("div", id="main_content").find_all("li"):

                #메이저 언론사인지 확인
                media = link.find('span', class_="writing").text
                if media in ["경향신문","국민일보","동아일보","문화일보","서울신문","세계일보","조선일보","중앙일보","한겨례","한국일보"]:

                    #링크모음 저장
                    #저장태그
                    #100273_media_20200101_2_link
                    link_set.append(datas['sid1']+datas['sid2']+"_"+media+"_"+datas['date']+"_"+datas['page']+"_"+link.find('a')['href'])


            #페이지 증가
            datas['page'] = str(int(datas['page']) + 1)

        #파일명
        fname = sid1+sid2+"_"+datas['date']+".txt"


        f = open(dir+'/'+fname, "w")
        f.write("\n".join(link_set))

        #종료조건
        if date_s == date_e:
            break

        #날짜 감소
        date_s = date_s - datetime.timedelta(days=1)
        datas['date'] = date_to_str(date_s)


if __name__ == '__main__':

    start = time.time()

    '''
    date_s = input("start:")
    date_e = input("end:")
    '''

    date_s = "2021-08-20"
    date_e = "2021-01-01"

    date_s = date_s.split("-")
    date_e = date_e.split("-")


    for i in range(0, 3):
        date_s[i] = int(date_s[i])
        date_e[i] = int(date_e[i])

    print(date_s, date_e)
    #map_val = [대분류, 시작날짜, 종료날짜]
    #분할처리를 위해 대분류 코드가 들어간 map_val을 6개 만듦
    map_val = []
    for i in range(100,106):
        map_val.append([
        str(i),
        datetime.datetime(date_s[0],date_s[1],date_s[2]),
        datetime.datetime(date_e[0],date_e[1],date_e[2])
        ])


    print(map_val[0])


    get_link_test(map_val[0])
    '''
    #[정치, 경제, 사회, 생활/문화, IT/과학, 세계] = 6
    pool = multiprocessing.Pool(processes=6)
    pool.map(get_link, map_val)

    pool.close()
    pool.join()
    '''
