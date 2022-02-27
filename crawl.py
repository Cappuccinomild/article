import requests
from bs4 import BeautifulSoup
import datetime
import time
import re
import ast
import multiprocessing
import os

# 텍스트 정제 함수
def text_cleaning(text, office):

    author = r'[(]?\w{2,4}[ ]?기자[)]?'

    result_list = []
    for item in text:
        #cleaned_text = re.sub('[a-zA-Z]', '', item)
        cleaned_text = item.replace('[', '')
        cleaned_text = cleaned_text.replace(']', '')
        cleaned_text = cleaned_text.replace('\n', '')#엔터 삭제

        cleaned_text = re.sub('[(].+?'+office+'[)]', '', cleaned_text)#신문사 삭제
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

    _html = ""
    resp = requests.get(url)
    if resp.status_code == 200:
        _html = resp.text
    return _html

def parsedata(html, write_filename):#return list

    front_link = 'https://news.naver.com'

    soup = BeautifulSoup(html, 'lxml')

    broadcast = ['연합뉴스TV','채널A','한국경제TV','JTBC','KBS','MBC','MBN','SBS','SBS CNBC','TV조선','YTN']

    office = soup.find_all("div", class_='ranking_office')#언론사 이름확인

    my_titles = soup.find_all("div", class_="ranking_headline")#기사 링크

    count = 0

    if(len(office) != len(my_titles)):
        err = open("office_len_error.txt", "a")
        err.write("len err : "+ write_filename + '\n')
        err.write("office len : "+str(len(office)))
        err.write("my_titles len : "+str(len(my_titles)))

        for i in office:
            err.write(i.text)

        for i in my_titles:
            err.write(i.text)

        err.close()
    else:
        for title in my_titles:
            print(front_link + title.find('a')['href'])
            if office[count].text not in broadcast:#TV방송국 제외
                get_article(get_html(front_link + title.find('a')['href']), front_link + title.find('a')['href'], office[count].text, write_filename)
            count += 1


def cut_tail(word_corpus):

    if('@' in word_corpus):#이메일 삭제
        word_corpus = re.sub('\w+[@].+', '', word_corpus)

    elif('ⓒ' in word_corpus):
        word_corpus = re.sub('\w+[ⓒ].+', '', word_corpus)

    word_corpus = word_corpus[:word_corpus.rfind('.')+1]

    return word_corpus


def get_article(html, link, office, write_filename):#return list
    write_filename = date_to_str(datetime.datetime.now() - datetime.timedelta(days=int(write_filename)))
    output = open("culture"+ write_filename + ".txt", "a")
    errorlog = open("errorlog_culture" + write_filename + ".txt", "a")

    #사진 설명 삭제
    html = re.sub('<em class="img_desc.+?/em>', '', html)

    # 각 기사에서 텍스트만 정제하여 추출
    soup = BeautifulSoup(html, 'lxml')
    text = ''
    img_desc = []
    doc = None

    for item in soup.find_all('div', id='articleBodyContents'):

        text = text + str(item.find_all(text=True))
    try:

        text = ast.literal_eval(text)

        doc = text_cleaning(text[8:], office)

        word_corpus = (' '.join(doc))

        word_corpus = cut_tail(word_corpus)

        output.write(word_corpus + '\n')
        print(write_filename)


    except UnicodeEncodeError:
        errorlog.write('UnicodeEncodeError : ')
        errorlog.write(link + '\n')
    except SyntaxError:
        errorlog.write('SyntaxError : ')
        errorlog.write(link + '\n')
    except ValueError:
        errorlog.write(text)
        errorlog.write(link + '\n')

    output.close()

def merge(parsecount):
    to_write = open('culture'+"_"+date_to_str(datetime.datetime.now())+".txt", "w")
    to_write_err = open('errorlog_culture'+"_"+date_to_str(datetime.datetime.now())+".txt", "w")

    for i in parsecount:
        to_read = open("culture"+str(i+10)+".txt", "r")
        to_read_err = open("errorlog_culture"+str(i+10)+".txt", "r")

        to_write.write(to_read.read())
        to_write_err.write(to_read_err.read())

        to_read.close()
        to_read_err.close()
        os.remove("errorlog_culture"+str(i+10)+".txt")
        os.remove("culture"+str(i+10)+".txt")

def start_parse(id):
    
    #sid1 = 정치:100   경제:101  사회:102  생활/문화:103   세계:104   IT/과학:105

    #정치sid2 = 청와대:264  국회/정당:265   북한:268 행정:266 국방/외교:267  정치일반:269
    #경제sid2 = 금융:259    증권:258  산업/재계:261   중기/벤처:771   부동산:260 글로벌 경제:262  생활경제:310    경제일반:263
    #사회sid2 = 사건사고:249  교육:250  노동:251  언론:254  환경:252  인권/복지:59b   식품/의료:255   지역:256  인물:276  사회일반:257
    #생활/문화sid2 = 건강정보:241   자동차/시승기:239    도로/교통:240  여행/레저:237 음식/맛집:238  패션/뷰티:376  공연/전시:242  책:243  종교:244  날씨:248  생활문화 일반:245
    #세계sid2 = 아시아/호주:231    미국/중남미:232  유럽:233   중동/아프리카:234    세계일반:322
    #IT/과학sid2 = 모바일:731    인터넷/SNS:226    통신/뉴미디어:227    IT일반:230   보안/해킹:732  컴퓨터:283    게임/리뷰:229  과학 일반:228
    sid = {
    100:["264","265","268","266","267","269"],
    101:["259","258","261","771","260","262","310","263"],
    102:["249","250","251","254","252","59b","255","256","276","257"],
    103:["241","239","240","237","238","376","242","243","244","248","245"],
    104:["231","232","233","234","322"],
    105:["731","226","227","230","732","283","229","228"]
    }

    #https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2=+sid2+&sid1=+sid1+&date=20220226

    sid1 = str(id)
    sid2 = sid[id]
    #link = "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2="+sid2+"&sid1="+sid1+"&date=20220226"

    print(sid1, sid2)
    print(date[0], date[1])



    '''
    for sid in sid2:
        parsedata(get_html("https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2=264&sid1=100&date= + date_s)), str(end))
        print("culture" + str(end) +' : '+str(count))
        count += 1
    '''

if __name__ == '__main__':

    global date

    start = time.time()

    date = ["20220228", "20220110"]

    #sid1[sid2]
    #[정치, 경제, 사회, 생활/문화, IT/과학, 세계, 칼럼] = 7
    pool = multiprocessing.Pool(processes=6)
    pool.map(start_parse, list(range(100,106)))

    pool.close()
    pool.join()

    print(time.time() - start)

    '''
    print('merge start...')
    merge(parsecount)
    print('crawling end : ',end='')
    print(time.time()-start, end='')
    print(' sec')
    '''
