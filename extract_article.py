import os
import re
from tqdm import tqdm
import multiprocessing

def search_keyword(map_val):

    #map_val = [저장폴더 이름, 키워드, 탐색 폴더]
    output_dir = map_val[0]
    keyword = map_val[1]
    path = map_val[2]

    keyword = keyword.split("&")

    for i in range(len(keyword)):
        #부정일 경우
        if "!" in keyword[i]:
            keyword[i] = [re.compile(keyword[i].replace("!", '')), 0]

        else:
            keyword[i] = [re.compile(keyword[i]), 1]


    print(keyword)
    flist = os.listdir(path)
    for i in tqdm(range(len(flist))):
        fname = flist[i]

        f = open(path + "/" + fname, encoding = 'utf-8')

        line = f.readline()
        while line:

            #매치 확인
            match = False
            for key in keyword:

                #not이 있을 경우
                if key[1] == 0:
                    if len(key[0].findall(line)) >= 1:
                        match = False
                        break
                    else:
                        match = True

                #not이 없을 경우
                else:
                    if len(key[0].findall(line)) >= 1:
                        match = True
                    else:
                        match = False
                        break

            #매칭되어 저장함
            if match:
                output = open("./" + output_dir + "/" + fname, "a", encoding = "utf-8")
                output.write(fname)
                output.write(line)
                output.close()

            #엔터 제거
            f.readline()
            line = f.readline()

if __name__ == '__main__':


    '''
    #test

    f = open("검색어.txt", encoding = 'utf-8')
    line = f.readline()

    while line:
        dirname = line.replace("&", "AND").replace("|", "OR").replace("\n", "")
        os.makedirs(dirname, exist_ok=True)
        path = "경향신문/100/100264"
        #[dir, keyword, mode]
        search_keyword([dirname, line.replace("\n", ''), path])
        line = f.readline()
    '''

    f = open("검색어.txt", encoding = 'utf-8')
    line = f.readline()

    while line:
        #저장폴더 이름
        dirname = line.replace("&", "AND").replace("|", "OR").replace("\n", "")
        os.makedirs(dirname, exist_ok=True)

        #신문사
        for newspaper in os.listdir("./기사"):
            #sid1
            for sid1 in os.listdir("/".join(["./기사", newspaper])):
                #sid2
                map_val = []
                for sid2 in os.listdir("/".join(["./기사", newspaper, sid1])):
                    #map_val = [저장폴더 이름, 키워드, 탐색 폴더]
                    path = "/".join(["./기사", newspaper, sid1, sid2])
                    map_val.append([dirname, line.replace("\n", ""), path])


                process_num = len(map_val)
                print(map_val, "process : ", process_num)

                pool = multiprocessing.Pool(processes=process_num)
                pool.map(search_keyword, map_val)

                pool.close()
                pool.join()

        line = f.readline()
