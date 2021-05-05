import scrapy
from scrapy.crawler import CrawlerProcess
import requests
import json
import re
import pytesseract
import cv2
from datetime import datetime
import csv
import os
import numpy as np
from bs4 import BeautifulSoup
import logging
logging.getLogger('scrapy').propagate = False

class ElectorSpider(scrapy.Spider):
    def __init__(self, par=None):
        self.par = par
        # logging.getLogger('scrapy').setLevel(logging.ERROR)
        
    def start_requests(self):
        while True:
            line = self.par.inputfile.readline()
            if not line:
                break
            arr = line.strip().split(',')
            epic_id = arr[0]
            self.serial_no = arr[1]
            epic_id = epic_id.replace("O", "0")
            if epic_id == "":
                continue

            self.par.cnt += 1
            if self.par.cnt % 1 == 0:
                print(self.par.get_current_time(), self.par.cnt, epic_id)

            url = self.par.get_data_url.format(epic_id, 1, 10, self.par.prev_captcha)
            yield scrapy.Request(url=url, callback=self.parse)
            # yield self.par.session.get(url, headers = {})
            break

    def parse(self, r):
        try:
            print(json.loads(r.content))
            return False
            # docs = json.loads(r.text)['response']['docs']
            docs = json.loads(r.content)['response']['docs']
        except:
            print('empty', r.text)
            html_file = open('out.html', 'w')
            html_file.write(r.text)
            html_file.close()
            return False
        
        if len(docs) == 0:
            self.outwriter.writerow([0, "", "", "", "", "", "", "", epic_id, "", "", "", "", self.serial_no, ""])
            self.failedfile.write(epic_id + "\n")
            return True

        res = docs[0]
        # print(res)
        self.prev_captcha = txtCaptcha
        data = {
            # '__RequestVerificationToken' : 'BCoSaqxirZQMgrca7EBPF8kk8lLzEMNyShCzmhLC3Q2aAbQtX-sqIj0fi7-qF3vvrBOGAQEZ-FghNOsW4mpDCvHBeaWARAnUfFFt6VlmK0k1',
            'id' : res['id'],
            'epic_no' : res['epic_no'],
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
            'acno' : res['ac_no'],
            'pc_name' : res['pc_name'],
            'ps_name' : res['ps_name'],
            'slno_inpart' : res['slno_inpart'],
            'stcode' : res['st_code'],
            'ps_lat_long' : res['ps_lat_long'],
            'partno' : res['part_no'],
            'part_name' : res['part_name'],
            'rln_type' : res['rln_type'],
        }
        print(data)
        # self.par.outfile.flush()
        # r = self.session.post(self.get_detail_url, data = data, headers = {})
        # html = r.content.decode('utf-8')
        # # print(html)
        # soup=BeautifulSoup(html,'lxml')
        # trs = soup.find('table', {'class':'responsive'}).find_all("tr")
        # state = res['st_name']
        # ac_acn = res['ac_name'] + " - " + res['ac_no']
        # pc = res['pc_name']
        # name = res['name']
        # name_v1 = res['name_v1']
        # gender = res['gender']
        # age = res['age']
        # epic_no = res['epic_no']
        # father_name = trs[9].find_all('td')[0].text.strip()
        # father_name_v1 = trs[8].find_all('td')[1].text.strip()
        # part_number = res['part_no']
        # part_name = res['part_name']
        # serial_no = res['slno_inpart']
        # polling_station = res['ps_name'] + " - " + res['ps_no']
        # # polling_date = trs[14].find_all('td')[1].text.strip()
        # self.outwriter.writerow([1, state, ac_acn, pc, name, name_v1, gender, age, epic_no, father_name, father_name_v1, part_number, part_name, serial_no, polling_station])
        # return True

class Scrapping:
    def __init__(self):
        self.base_url = 'https://electoralsearch.in/Home/GetCaptcha?image=true&id=Wed%20Apr%2007%202021%2004:50:30%20GMT+0800%20(China%20Standard%20Time)'
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

    def create_folder_if_not_exists(self, foldername):
        if not os.path.exists(foldername):
            os.makedirs(foldername)

    def start(self, inputpath, outpath, failedpath):
        self.create_folder_if_not_exists(outpath)
        self.create_folder_if_not_exists(failedpath)

        filenames = os.listdir(inputpath)
        filenames.sort(key=lambda f: int(re.sub('\D', '', f)))

        flag = False
        for filename in filenames:
            if filename == "S11A60P130.txt":
                flag = False
            if flag:
                continue

            inputfilename = inputpath + "/" + filename
            outfilename = outpath + "/" + filename.replace(".txt", ".csv")
            failedfilename = failedpath + "/" + filename


            print(self.get_current_time(), filename)
            self.process_file(inputfilename, outfilename, failedfilename)
            # if filename == "S11A60P130.txt":
            #     break
            break

    def process_file(self, inputfilename, outfilename, failedfilename):
        self.inputfile = open(inputfilename, 'r')
        self.outfile = open(outfilename, 'w', newline='', encoding="utf-8")
        self.outwriter = csv.writer(self.outfile)
        self.failedfile = open(failedfilename, 'w')

        self.outwriter.writerow(['success', 'state', 'ac_acn', 'pc', 'name', 'name_v1', 'gender', 'age', 'epic_no', 'father_name', 'father_name_v1', 'part_number', 'part_name', 'serial_no', 'polling_station'])


        self.cnt = 0
        while True:
            line = self.inputfile.readline()
            if not line:
                break
            arr = line.strip().split(',')
            epic_id = arr[0]
            self.serial_no = arr[1]
            epic_id = epic_id.replace("O", "0")
            if epic_id == "":
                continue

            self.cnt += 1
            print(self.get_current_time(), self.cnt, epic_id)
            ret = self.process_epic(epic_id)
            self.outfile.flush()
            break

        self.process = CrawlerProcess()
        self.process.crawl(ElectorSpider, par=self)
        self.process.start(self)

        self.failedfile.close()
        self.outfile.close()
        self.inputfile.close()

    def process_epic(self, epic_id):
        cnt = 0
        while True:
            cnt += 1
            print("----> Trying ", cnt)
            if self.solve(epic_id):
                break
        return True

    def solve(self, epic_id):
        r = self.session.get(self.base_url, headers={})
        # file = open("captcha.jpg", "wb")
        # file.write(r.content)
        # file.close()
        nparr = np.frombuffer(r.content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imwrite("captcha.jpg", img)
        print(img.shape)
        H = img.shape[0]
        W = img.shape[1]
        
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, bimg = cv2.threshold(gray_img,200,255,cv2.THRESH_BINARY)
        copied_bimg = bimg.copy()
        # cv2.imshow("binary", bimg)
        # cv2.waitKey(0)
        print(bimg[0, 0])
        nseg = 0

        slice_images = []

        for x in range(W):
            for y in range(H):
                if bimg[y, x] == 255:
                    continue

                q = []
                qb = qf = 0
                q.append([x, y])

                bimg[y, x] = 255
                qb += 1

                while qb > qf:
                    ux, uy = q[qf]
                    qf += 1

                    for r in range(len(self.dx)):
                        vx = ux + self.dx[r]
                        vy = uy + self.dy[r]
                        if vx < -1 or vy < -1 or vx >= W or vy >= H:
                            continue
                        if bimg[vy, vx] == 255:
                            continue
                        bimg[vy, vx] = 255
                        q.append([vx, vy])
                        qb += 1
                
                print('size = ', qb)
                if qb > 2:
                    sub_img = self.cut_image(bimg, q, nseg)
                    slice_images.append(sub_img)
                    nseg += 1

        val = ""
        for img in slice_images:
            ret = self.image_to_string(img, self.custom_config_3)
            if len(ret) > 0:
                val += ret[0]
        print(val)
        if len(val) != 6:
            return False
        return self.get_data(val, epic_id)
        # print(nseg)
        # simg = self.stitch_images(slice_images)
        # ret = self.image_to_string(simg, self.custom_config_2)
        # print(ret)
        # cv2.imshow("simg", simg)
        # cv2.imshow("bimg", copied_bimg)
        # cv2.waitKey(0)

    def get_data(self, txtCaptcha, epic_id):
        url = self.get_data_url.format(epic_id, 1, 10, txtCaptcha)
        # print(url)
        r = self.session.get(url, headers = {})
        try:
            docs = json.loads(r.content)['response']['docs']
        except:
            return False
        
        if len(docs) == 0:
            self.outwriter.writerow([0, "", "", "", "", "", "", "", epic_id, "", "", "", "", self.serial_no, ""])
            self.failedfile.write(epic_id + "\n")
            return True

        res = docs[0]
        # print(res)
        self.prev_captcha = txtCaptcha
        data = {
            # '__RequestVerificationToken' : 'BCoSaqxirZQMgrca7EBPF8kk8lLzEMNyShCzmhLC3Q2aAbQtX-sqIj0fi7-qF3vvrBOGAQEZ-FghNOsW4mpDCvHBeaWARAnUfFFt6VlmK0k1',
            'id' : res['id'],
            'epic_no' : res['epic_no'],
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
            'acno' : res['ac_no'],
            'pc_name' : res['pc_name'],
            'ps_name' : res['ps_name'],
            'slno_inpart' : res['slno_inpart'],
            'stcode' : res['st_code'],
            'ps_lat_long' : res['ps_lat_long'],
            'partno' : res['part_no'],
            'part_name' : res['part_name'],
            'rln_type' : res['rln_type'],
        }
        # print(data)
        r = self.session.post(self.get_detail_url, data = data, headers = {})
        html = r.content.decode('utf-8')
        # print(html)
        soup=BeautifulSoup(html,'lxml')
        trs = soup.find('table', {'class':'responsive'}).find_all("tr")
        state = res['st_name']
        ac_acn = res['ac_name'] + " - " + res['ac_no']
        pc = res['pc_name']
        name = res['name']
        name_v1 = res['name_v1']
        gender = res['gender']
        age = res['age']
        epic_no = res['epic_no']
        father_name = trs[9].find_all('td')[0].text.strip()
        father_name_v1 = trs[8].find_all('td')[1].text.strip()
        part_number = res['part_no']
        part_name = res['part_name']
        serial_no = res['slno_inpart']
        polling_station = res['ps_name'] + " - " + res['ps_no']
        # polling_date = trs[14].find_all('td')[1].text.strip()
        self.outwriter.writerow([1, state, ac_acn, pc, name, name_v1, gender, age, epic_no, father_name, father_name_v1, part_number, part_name, serial_no, polling_station])
        return True

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
    
if __name__ == "__main__":
    scrap = Scrapping()
    scrap.start("epics1", "pass1", "failed1")

