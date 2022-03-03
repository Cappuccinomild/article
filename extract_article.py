import os
import re

def search_keyword(map_val):

    #map_val = [폴더 경로, 키워드, 반복]
    path = "./" + map_val[0]
    keyword = map_val[1]
    rept = map_val[2]

    for fname in os.listdir(path):

        #폴더 내의 파일 읽어오기
        f = open(path + "/" + fname, "r", encoding="utf-8")

        output = open("_".join([fname.replace(".txt", ""), keyword, str(rept)]) + ".txt", "w", encoding = "utf-8")
        line = f.readline()
        while line:
            p = re.compile(keyword)

            #키워드와 매치되는 단어가 원하는 반복횟수 이상
            if len(p.findall(line)) >= rept:
                output.write(fname)
                output.write(line)

            line = f.readline()

        output.close()


def search_keyword_test(map_val):
    #map_val = [폴더 경로, 키워드, 반복]
    path = "./" + map_val[0]
    keyword = map_val[1]
    rept = map_val[2]

    fname = os.listdir(path)[0]

    #폴더 내의 파일 읽어오기
    f = open(path + "/" + fname, "r", encoding="utf-8")

    output = open("_".join([fname.replace(".txt", ""), keyword, str(rept)]) + ".txt", "w", encoding = "utf-8")

    line = f.readline()
    while line:
        p = re.compile(keyword)

        #키워드와 매치되는 단어가 원하는 반복횟수 이상
        if len(p.findall(line)) >= rept:
            output.write(fname)
            output.write(line)

        line = f.readline()

    output.close()


if __name__ == '__main__':

    #map_val = [폴더 경로, 키워드, 반복]
    search_keyword(["./100264", "대통령", 3])
    search_keyword(["./100264", "대통령", 2])
