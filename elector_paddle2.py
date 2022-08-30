import requests
import json
import re
import cv2
from datetime import datetime
import time
import csv
import os
import numpy as np
from bs4 import BeautifulSoup
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from paddleocr import PaddleOCR,draw_ocr

warnings.simplefilter('ignore',InsecureRequestWarning)

from multiprocessing import Pool


class Scrapping:
    def __init__(self, pid):
        self.base_url = 'https://electoralsearch.in/Home/GetCaptcha?image=true&id=Wed%20May%2019%202021%2019:47:21%20GMT+0800%20(China%20Standard%20Time)'
        self.get_data_url = 'https://electoralsearch.in/Home/searchVoter?epic_no={}&page_no={}&results_per_page={}&reureureired=ca3ac2c8-4676-48eb-9129-4cdce3adf6ea&search_type=epic&state=S11&txtCaptcha={}'
        self.get_detail_url = 'https://electoralsearch.in/Home/VoterInformation'

        self.session = requests.Session()
        self.dx = [-1, -1, -1, 0, 0, 1, 1, 1]
        self.dy = [-1, 0, 1, -1, 1, -1, 0, 1]
        # self.dx = [-1, 0, 1, 0]
        # self.dy = [0, -1, 0, 1]
        self.custom_config_1 = r'--oem 3 --psm 6'
        self.custom_config_2 = r'--oem 3 --psm 7 -c tessedit_char_whitelist=023456789abcdefghjklmnopqrstuvwxyzABCDEFGHJKLMNOPQRXYZ'
        self.custom_config_3 = r'--oem 3 --psm 10 -c tessedit_char_whitelist=023456789abcdefghjklmnopqrstuvwxyzABCDEFGHJKLMNOPQRXYZ'

        self.prev_captcha = ""
        self.pid = pid
        self.paddleOCR = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False) 

    def create_folder_if_not_exists(self, foldername):
        if not os.path.exists(foldername):
            os.makedirs(foldername)

    def start(self, inputpath, outpath):
        self.create_folder_if_not_exists(outpath)

        filenames = os.listdir(inputpath)
        filenames.sort(key=lambda f: int(re.sub('\D', '', f)))

        outfilenames = os.listdir(outpath)
        outfilenames.sort(key=lambda f: int(re.sub('\D', '', f)))

        if len(outfilenames) > 0:
            outfilename = outfilenames[-1]
            outfilepath = outpath + "/" + outfilename
            os.remove(outfilepath)

        # flag = True
        for filename in filenames:
            # if filename == "S11A49P77.txt":
            #     flag = False
            # if flag:
            #     continue

            inputfilename = inputpath + "/" + filename
            outfilename = outpath + "/" + filename.replace(".txt", ".csv")

            if not os.path.exists(outfilename):
                self.pdf_filename = filename.replace(".txt", ".pdf")
                print(self.pid, self.get_current_time(), filename)
                self.process_file(inputfilename, outfilename)
            # if filename == "S11A49P150.txt":
            #     break

    def process_file(self, inputfilename, outfilename):
        self.inputfile = open(inputfilename, 'r')
        self.outfile = open(outfilename, 'w', newline='', encoding="utf-8")
        self.outwriter = csv.writer(self.outfile)

        self.outwriter.writerow(['filename', 'success', 'state', 'ac_acn', 'pc', 'name', 'name_v1', 'gender', 'age', 'epic_no', 'father_name', 'father_name_v1', 'part_number', 'part_name', 'pdf_serial_no', 'web_serial_no', 'polling_station'])

        cnt = 0
        while True:
            try:
                line = self.inputfile.readline()
            except Exception as e:
                print(e)
                print("It looks reached to the end")
                break
            if not line:
                break
            arr = line.strip().split(',')
            epic_id = arr[0]
            self.serial_no = arr[1]
            epic_id = epic_id.replace("O", "0")
            if epic_id == "":
                continue

            cnt += 1
            if cnt % 10 == 0:
                print(self.pid, self.get_current_time(), cnt, epic_id)

            ret = self.process_epic(epic_id)
            self.outfile.flush()


        self.outfile.close()
        self.inputfile.close()

    def process_epic(self, epic_id):
        if self.prev_captcha != "":
            ret, notagain = self.get_data(self.prev_captcha, epic_id)
            if notagain:
                return ret
    
        recnt = 0
        while True:
            self.session = requests.Session()
            self.prev_captcha = ""
            recnt += 1
            print(self.pid, "----> reconnecting ", recnt)
            try:
                ret = self.solve(epic_id)
            except:
                print(self.pid, "Sleeping")
                time.sleep(20)
                ret = False
            if ret:
                return ret
            if recnt > 50:
                return False
            time.sleep(20)

    def solve(self, epic_id):
        try:
            r = self.session.get(self.base_url, headers={}, verify=False, timeout=10)
        except Exception as e:
            return False
        # file = open("captcha.jpg", "wb")
        # file.write(r.content)
        # file.close()
        nparr = np.frombuffer(r.content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # cv2.imwrite("captcha.jpg", img)
        # print(self.pid, img.shape)
        H = img.shape[0]
        W = img.shape[1]
        
        # gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # ret, bimg = cv2.threshold(gray_img,200,255,cv2.THRESH_BINARY)
        # copied_bimg = bimg.copy()
        # cv2.imshow("binary", bimg)
        # cv2.waitKey(0)
        # print(self.pid, bimg[0, 0])

        val = self.DetectOCR(img)
        # print(self.pid, val)
        # cv2.imshow("captch", img)
        # cv2.waitKey(0)
        if len(val) != 6:
            return False
        return self.get_data(val, epic_id)[0]

        # print(self.pid, nseg)
        # simg = self.stitch_images(slice_images)
        # ret = self.image_to_string(simg, self.custom_config_2)
        # print(ret)
        # cv2.imshow("simg", simg)
        # cv2.imshow("bimg", copied_bimg)
        # cv2.waitKey(0)

    def DetectOCR(self, img):
        # res = self.paddleOCR.ocr(img, cls=True)
        res = self.paddleOCR.ocr(img, cls=True, det=False)
        if len(res) == 0:
            return None
        # pos, (text, acc) = res[0]
        (text, acc) = res[0]
        return text

    def get_data(self, txtCaptcha, epic_id):
        url = self.get_data_url.format(epic_id, 1, 10, txtCaptcha)
        # print(url)
        # print(self.pid, "->1")
        try:
            data = {
                # '__RequestVerificationToken' : 'BCoSaqxirZQMgrca7EBPF8kk8lLzEMNyShCzmhLC3Q2aAbQtX-sqIj0fi7-qF3vvrBOGAQEZ-FghNOsW4mpDCvHBeaWARAnUfFFt6VlmK0k1',
                'epic_no' : epic_id,
                'page_no' : 1,
                'results_per_page' : 10,
                'reureureired' : "ca3ac2c8-4676-48eb-9129-4cdce3adf6ea",
                'search_type' : "epic",
                'state' : "S11",
                'txtCaptcha' : txtCaptcha,
            }
            r = self.session.post(self.get_data_url, data = data, headers = {}, timeout=10)
        except Exception as e:
            print(self.pid, "Get MainData Failed", e)
            return False, False


        # print(self.pid, "->2")

        try:
            docs = json.loads(r.content)['response']['docs']
        except:
            self.prev_captcha = ""
            return False, False

        self.prev_captcha = txtCaptcha
        if len(docs) == 0:
            self.outwriter.writerow([self.pdf_filename, 0, "", "", "", "", "", "", "", epic_id, "", "", "", "", self.serial_no, "", ""])
            return True, True

        res = docs[0]
        try:
            data = {
                # '__RequestVerificationToken' : 'VU5pBHNxL_zONzi_xiNcW268l1qgdnCWmM6Ee3RistowL_rrH-wiEhjYHjFCh6atmrSYntDWmKYuuD5iOYXT2XdTjGX-uY1soFyGy7Yu-tc1',
                'h_info' : res['hashedInfo'],
                'id' : res['id'],
                'epic_no_plain' : res['epic_no'],
                'epic_no' : res['enc_epic_no'],
                'name' : res['name'],
                'name_v1' : res['name_v1'],
                'gender' : res['gender'],
                'age' : res['age'],
                'rln_name' : res['rln_name'],
                'last_update' : res['last_update'],
                'rln_name_v1' : res['rln_name_v1'],
                'state' : res['st_name'],
                'district' : res['dist_name'],
                'ac_name' : res['ac_name'],
                'ac_no' : res['ac_no'],
                'pc_name' : res['pc_name'],
                'ps_name' : res['ps_name'],
                'slno_inpart' : res['slno_inpart'],
                'st_code' : res['st_code'],
                'ps_lat_long' : res['ps_lat_long'],
                'part_no' : res['part_no'],
                'part_name' : res['part_name'],
                'rln_type' : res['rln_type'],
            }
        except:
            self.outwriter.writerow([self.pdf_filename, 0, "", "", "", "", "", "", "", epic_id, "", "", "", "", self.serial_no, "", ""])
            return True, True
        # print(data)
        # print(self.pid, "->3")
        try:
            r = self.session.post(self.get_detail_url, data = data, headers = {}, timeout=20)
            # print(self.pid, "->4")
            html = r.content.decode('utf-8')
        except:
            print(self.pid, "Get details Failed")
            return False, False

        soup=BeautifulSoup(html,'lxml')
        try:
            trs = soup.find('table', {'class':'responsive'}).find_all("tr")
            state = res['st_name']
            ac_acn = res['ac_name'] + " - " + res['ac_no']
            pc = res['pc_name']
            name = res['name']
            name_v1 = res['name_v1']
            gender = res['gender']
            age = res['age']
            epic_no = res['epic_no']
            father_name = trs[10].find_all('td')[0].text.strip()
            father_name_v1 = trs[9].find_all('td')[1].text.strip()
            part_number = res['part_no']
            part_name = res['part_name']
            serial_no = res['slno_inpart']
            polling_station = res['ps_name'] + " - " + res['ps_no']
            # polling_date = trs[14].find_all('td')[1].text.strip()
            self.outwriter.writerow([self.pdf_filename, 1, state, ac_acn, pc, name, name_v1, gender, age, epic_no, father_name, father_name_v1, part_number, part_name, self.serial_no, serial_no, polling_station])
        except:
            self.outwriter.writerow([self.pdf_filename, 0, "", "", "", "", "", "", "", epic_id, "", "", "", "", self.serial_no, "", ""])
        return True, True

    def cut_image(self, img, q, id):
        qb = len(q)
        mi_x = mi_y = 100
        ma_x = ma_y = 0 
        for x, y in q:
            mi_x = min(mi_x, x)
            mi_y = min(mi_y, y)
            ma_x = max(ma_x, x)
            ma_y = max(ma_y, y)

        padding = 10
        nW = ma_x - mi_x + 1 + padding * 2
        nH = ma_y - mi_y + 1 + padding * 2
        img = np.zeros((nH, nW), dtype=np.uint8)
        for y in range(nH):
            for x in range(nW):
                img[y, x] = 255
        for x, y in q:
            img[y - mi_y + padding, x - mi_x + padding] = 0

        img = self.rotate_image(img, 12)
        # cv2.imshow("img", img)
        # cv2.waitKey(0)
        return img

    def stitch_images(self, imgs):
        nimg = len(imgs)

        W = 0
        H = 0
        for img in imgs:
            hh = img.shape[0]
            ww = img.shape[1]
            W += ww
            H = max(H, hh)

        simg = np.zeros((H, W), dtype=np.uint8)
        for y in range(H):
            for x in range(W):
                simg[y, x] = 255

        sw = 0
        for img in imgs:
            hh = img.shape[0]
            ww = img.shape[1]
            dh = H - hh
            for x in range(ww):
                for y in range(hh):
                    simg[dh + y, sw + x] = img[y, x]
            sw += ww
        return simg

    def rotate_image(self, image, angle):
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR, borderValue=(255,255,255))
        return result

    def image_to_string(self, img, config):
        captcha = pytesseract.image_to_string(img, lang='eng', config=config)
        captcha = captcha.replace('\n', '')
        captcha = captcha.replace(' ', '')
        sumstr = ''
        cnt = 0
        for c in captcha:
            if c.isalpha() or c.isdigit():
                sumstr += c
                cnt += 1
            if cnt == 6:
                break
        return sumstr

    def get_current_time(self):
        return datetime.now().strftime("%H:%M:%S")


def f(x):
    scrap = Scrapping(x)
    scrap.start("epics{}".format(x), "save{}".format(x))
    return "Process {} - Completed!!!!!!".format(x)

def DetectOCR():
    paddleOCR = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)
    # res = paddleOCR.ocr("captcha.jpg", cls=True, det=False)
    img = cv2.imread("/home/troica/work/Test/captcha0.jpg")
    res = paddleOCR.ocr(img, cls=True, det=False)
    print(res)
    if len(res) == 0:
        return None
    (text, acc) = res[0]
    return text

if __name__ == "__main__":
    arr = [x for x in range(21, 41)]
    nPool = len(arr)
    with Pool(nPool) as p:
        print(p.map(f, arr))


    # res = DetectOCR()
    # print(res) 