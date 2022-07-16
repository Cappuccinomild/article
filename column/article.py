import requests
from bs4 import BeautifulSoup
import datetime
import time
import re
import ast
import multiprocessing
import os
import math
import sys
from tqdm import tqdm

def str_to_date(input):#yyyymmdd 문자열을 datetime 객체로 변경
    #                             yyyy              mm              dd
    return datetime.datetime(int(input[:4]), int(input[4:6]), int(input[6:]))

# 텍스트 정제 함수
def text_cleaning(text, office):

    author = r'[(]?\w{2,4}[ ]?기자[)]?'

    result_list = []

    for item in text:
        #cleaned_text = re.sub('[a-zA-Z]', '', item)
        p = re.compile('[([]'+office+'[])]')
        cleaned_text = p.sub('', item)#신문사 삭제
        cleaned_text = cleaned_text.replace('[', '')
        cleaned_text = cleaned_text.replace(']', '')
        cleaned_text = cleaned_text.replace('\n', '')#엔터 삭제
        cleaned_text = re.sub(author, '', cleaned_text)#기자이름 삭제

        result_list.append(cleaned_text)

    return result_list

def date_to_str(input):
    output = ''
    output += str(input.year)

    if(input.month < 10):
        output +='0'

    output += str(input.month)
    if(input.day < 10):
        output +='0'
    output += str(input.day)

    return output

def get_html(url):

    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49'}
    _html = ""

    while True:

        try:
            resp = requests.get(url, headers = hdr, timeout=10)
        except requests.exceptions.Timeout as timeout:

            print(timeout)
            print(url)
            time.sleep(10)
            continue

        except requests.exceptions.ConnectionError as cut:

            print(cut)
            print(url)
            #연결 끊김 발생시 15분 대기
            time.sleep(900)
            continue

        if resp.status_code == 200:
            _html = resp.text
            break

    return _html

def cut_tail(word_corpus):

    if('@' in word_corpus):#이메일 삭제
        word_corpus = re.sub('\w+[@].+', '', word_corpus)

    elif('ⓒ' in word_corpus):
        word_corpus = re.sub('\w+[ⓒ].+', '', word_corpus)

    word_corpus = word_corpus[:word_corpus.rfind('.')+1]

    return word_corpus

#기사 본문 추출
def get_article(map_val):#return list
    print(map_val)
    #map_val[시작날짜, 종료날짜]
    date_s = map_val[0]
    date_e = map_val[1]

    #저장할 폴더
    path = './Column_link'
    output_path = './Column'
    os.makedirs(output_path, exist_ok=True)
    #분할된 날짜 내의 파일만 가져옴
    link_set = []
    for fname in os.listdir(path):

        fdate = fname[:-4]
        fdate = str_to_date(fdate)

        if date_s >= fdate and fdate >= date_e:
            link_set.append(fname)


    for i in tqdm(range(len(link_set))):
        fname = link_set[i]
        f = open(path + "/" + fname)

        #파일 형식
        #line -> 언론사_날짜_페이지_기사링크
        line = f.readline()

        while line:
            if not line:
                break

            if line == "\n":
                break


            try:
                line = line.split("_")
            except:
                print("------------------ split err ------------------")
                print(line)
                line = f.readline()
                print(line)
                continue

            os.makedirs(output_path + "/" + line[0], exist_ok=True)
            output = open(output_path + "/" + line[0] + "/" + fname, "a", encoding='utf-8')
            #저장된 링크를 통한 기사 크롤링
            html = get_html(line[3].replace("\n", ''))#끝부분 줄바꿈문자 제거


            #사진 설명 삭제
            html = re.sub('<em class="img_desc.+?/em>', '', html)

            # 각 기사에서 텍스트만 정제하여 추출
            soup = BeautifulSoup(html, 'lxml')
            text = ''
            img_desc = []
            doc = None

            output.write("_".join(line[:1]) + " ")

            for item in soup.find_all('div', id='dic_area'):

                text = text + str(item.find_all(text=True))
            try:

                text = ast.literal_eval(text)

                doc = text_cleaning(text[8:], line[1])#본문 내 언론사 삭제

                word_corpus = (' '.join(doc))

                word_corpus = cut_tail(word_corpus)

                output.write(word_corpus + '\n\n')

            #오류 예외처리
            except UnicodeEncodeError as encode:
                print(fname)
                print(encode)
                print(line)
                errorlog = open(output_path + "/" + fname +"_err", "a")
                errorlog.write('UnicodeEncodeError : ')
                errorlog.write(line[4][:-1] + '\n')
                errorlog.close()
            except SyntaxError as syntx: #id가 다른 기사가 존재함

                try:
                    for item in soup.find_all('div', id='articleBodyContents'):

                        text = text + str(item.find_all(text=True))

                        text = ast.literal_eval(text)

                        doc = text_cleaning(text, line[1])#본문 내 언론사 삭제

                        word_corpus = (' '.join(doc))

                        word_corpus = cut_tail(word_corpus)

                        output.write(word_corpus + '\n\n')
                except:
                    try:
                        for item in soup.find_all('div', id='articleBody'):

                            text = text + str(item.find_all(text=True))
                            text = ast.literal_eval(text)
                            doc = text_cleaning(text, line[1])#본문 내 언론사 삭제
                            word_corpus = (' '.join(doc))
                            word_corpus = cut_tail(word_corpus)
                            output.write(word_corpus + '\n\n')

                    except:
                        try:
                            for item in soup.find_all('div', id='newsEndContents'):

                                text = text + str(item.find_all(text=True))
                                text = ast.literal_eval(text)
                                doc = text_cleaning(text, line[1])#본문 내 언론사 삭제
                                word_corpus = (' '.join(doc))
                                word_corpus = cut_tail(word_corpus)
                                output.write(word_corpus + '\n\n')
                        except:
                            print(fname)
                            print(val)
                            print(line)
                            errorlog = open(output_path + "/" + fname +"_err", "a")
                            errorlog.write('SyntaxError : ')
                            errorlog.write(line[4][:-1] + '\n')
                            errorlog.close()
            except ValueError as val:
                print(fname)
                print(val)
                print(line)
                errorlog = open(output_path + "/" + fname +"_err", "a")
                errorlog.write(text)
                errorlog.write(line[4][:-1] + '\n')
                errorlog.close()
            except:
                print(fname)
                print("unexpect")
                print(line)

            output.close()
            line = f.readline()

    f.close()


if __name__ == '__main__':

    print(datetime.datetime.now())

    #cmd 입력으로 crawl.py 2022-03-06 2022-01-01 [언론사 목록]실행
    if len(sys.argv) == 3:
        date_s = sys.argv[1]
        date_e = sys.argv[2]

    else:
        print("날짜를 입력해주세요.")
        sys.exit()

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
    pool.map(get_article, map_val)

    pool.close()
    pool.join()



    print(datetime.datetime.now())
