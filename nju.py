import os
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.pyplot as plt
import json
import pytesseract
from tempfile import NamedTemporaryFile
import argparse

ID = ''
PASSWORD = ''

URL = 'http://elite.nju.edu.cn/jiaowu/'
LOGIN = 'login.do'
IMG = 'ValidateCode.jsp'
GRADE = 'student/studentinfo/achievementinfo.do?method=searchTermList&termCode='
HEADER = {
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
             }
DATA = {
    'userName': ID,
    'password': PASSWORD,
    'returnUrl': 'null',
    'ValidateCode': ''
}
YEAR = ['20181' , '20172', '20171']
poj_session = requests.session()

def genImage():
    with NamedTemporaryFile('wb') as f:
        r = poj_session.get(URL + IMG, stream=True)
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
        img = Image.open(f.name)
        img_gray = img.convert('L')
        table = []
        for i in range(256):
            if i < 140:
                table.append(0)
            else:
                table.append(1)
        img_bi = img_gray.point(table, '1')
        width = img_bi.size[0]  # 图片大小
        height = img_bi.size[1]
        img_bi = img_bi.crop((1,1,width-1,height-1))
        img_bi.save('valcode.png', 'PNG')
    return img_bi

def getValcode():
    genImage()
    code = pytesseract.image_to_string(Image.open('valcode.png'),lang='eng', config='--psm 12 --oem 3')
    return code


def getGrade():
    semester = {}
    alltotalCredit = 0.0
    allweightGrade = 0.0
    allreading = 0
    alltongshi = 0
    for year in YEAR: # 处理每个学年
        totalCredit = 0.0
        weightGrade = 0.0
        res = poj_session.get(URL+GRADE+year, headers=HEADER)
        soup = BeautifulSoup(res.text, 'lxml')
        trs = soup.find_all('tr', class_=['TABLE_TR_01', 'TABLE_TR_02'])
        grade = {}
        for tr in trs: # 处理每个科目
            reading = False
            subject = tr.findAll('td')[2].get_text().strip()
            grade[subject] = {}
            for j, td in enumerate(tr.findAll('td')):
                td_c = td.get_text().strip()
                if j == 1:
                    grade[subject]['id'] = td_c
                elif j == 4:
                    grade[subject]['type'] = td_c
                elif j == 5:
                    try:
                        credit = float(td_c)
                        if grade[subject]['id'].startswith(('002','003','004','005','37','500')):
                            alltongshi += credit
                        totalCredit += credit
                    except ValueError:
                        reading = True
                        grade[subject]['type'] = '阅读'
                        allreading+=1
                elif j == 6:
                    grade[subject]['grade'] = td_c
                    if not reading:
                        weightGrade += credit * float(td_c)/100.0
        alltotalCredit += totalCredit
        allweightGrade += weightGrade
        print("Semester {}:\n\t Total credit: {}\n\t GPA: {:.3f}\n---------\n".format(year, totalCredit, weightGrade/totalCredit * 5))
        semester[year] = grade

    print("Until Now:\n\t Total credit: {}\n\t GPA: {:.3f}\n\t 阅读经典: {}(6)\n\t 通识: {}(12)\n---------\n".format(alltotalCredit, allweightGrade/alltotalCredit * 5, allreading, int(alltongshi)))

    jsObj = json.dumps(semester, ensure_ascii=False, sort_keys = True, indent = 7, separators = (',', ': '))
    with open('grade.json', 'w') as f:
        f.write(jsObj)
    
    return semester

def main():
    login = False
    while (not login):
        # 验证码
        valcode = getValcode().strip()
        if args.manual:
            valcode = getValcode().strip()
            img = Image.open('valcode.png')
            plt.ion()
            plt.figure("img")
            plt.imshow(img)
            plt.show()
            print("验证码的机器识别结果为：{}".format(valcode))
            valcode = input("请输入验证码：")
    
        # 登录
        DATA['ValidateCode'] = valcode
        res = poj_session.post(URL + LOGIN, data=DATA, headers=HEADER)
        soup = BeautifulSoup(res.text, 'lxml')
        if '验证码错误' in soup.get_text():
            if args.manual: print('验证码错误!')
        else:
            login = True

    # 获得成绩
    getGrade()

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--manual", help="enter valid code by yourself",
                    action="store_true")
    return parser.parse_args()                

if __name__ == "__main__":
    args = parseArgs()
    main()