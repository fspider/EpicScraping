from pdf2image import pdfinfo_from_path, convert_from_path

import configparser
import cv2
import pytesseract
from datetime import datetime
import numpy as np
import os
import re

class EpicReader:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.w = int(self.config['DEFAULT']['w'])
        self.h = int(self.config['DEFAULT']['h'])
        self.w1 = int(self.config['DEFAULT']['w1'])
        self.h1 = int(self.config['DEFAULT']['h1'])

        self.sx = int(int(self.config['DEFAULT']['sx']) * self.w / self.w1)
        self.sy = int(int(self.config['DEFAULT']['sy']) * self.h / self.h1)
        self.sw = int(int(self.config['DEFAULT']['sw']) * self.w / self.w1)
        self.sh = int(int(self.config['DEFAULT']['sh']) * self.h / self.h1)

        self.sx2 = int(int(self.config['DEFAULT']['sx2']) * self.w / self.w1)
        self.sy2 = int(int(self.config['DEFAULT']['sy2']) * self.h / self.h1)
        self.sw2 = int(int(self.config['DEFAULT']['sw2']) * self.w / self.w1)
        self.sh2 = int(int(self.config['DEFAULT']['sh2']) * self.h / self.h1)

        self.px1 = int(int(self.config['DEFAULT']['px1']) * self.w / self.w1)
        self.px2 = int(int(self.config['DEFAULT']['px2']) * self.h / self.h1)

        self.dw = int(int(self.config['DEFAULT']['dw']) * self.w / self.w1)
        self.dh = int(int(self.config['DEFAULT']['dh']) * self.h / self.h1)

        self.cntw = int(self.config['DEFAULT']['cntw'])
        self.cnth = int(self.config['DEFAULT']['cnth'])

    def create_folder_if_not_exists(self, foldername):
        if not os.path.exists(foldername):
            os.makedirs(foldername)

    def find_hts(self, img):
        # w = int(self.w / 2)
        ret = []
        for h in range(self.h):
            fFound = True
            for w in range(self.px1, self.px2):
                if sum(img[h, w]) > 300:
                    fFound = False
                    break 
            if fFound is True:
                if len(ret)>0 and ret[-1] + 20 >= h:
                    ret.pop()
                ret.append(h)
        # print(ret)
        return ret

    def process_pdf(self, filename, save_file_path, folder_id):
        self.serial_no = 0
        self.outfile = open(save_file_path, "w")
        try:
            info = pdfinfo_from_path(filename, userpw=None, poppler_path=None)
        except Exception as e:
            print("ERROR!!!", e)
            return False

        nPages = info["Pages"]
        page_no = 0
        while page_no < nPages:
            pages = convert_from_path(filename, dpi=200, first_page=page_no + 1, last_page = min(page_no + 10, nPages))
            for page in pages:
                page_no += 1
                if page_no <= 2 or page_no == nPages:
                    continue
                savepath = 'tmp{}.jpg'.format(folder_id)
                page.save(savepath, 'JPEG')
                print("[process_pdf] Processing {}th page".format(page_no))
                self.process_img(savepath)
                self.outfile.flush()

        # pages = convert_from_path(filename, 500)
        # cnt = 0
        # nPages = len(pages)
        # print(self.get_current_time())
        # for i in range(2, nPages - 1):
        #     page = pages[i]
        #     cnt += 1
        #     # page.save('out2/out{}.jpg'.format(cnt), 'JPEG')
        #     # print("{}.jpg saved".format(cnt))
        #     savepath = 'tmp.jpg'
        #     page.save(savepath, 'JPEG')
        #     print("[process_pdf] Processing {}th page".format(cnt))
        #     self.process_img(savepath)
        #     self.outfile.flush()
        self.outfile.close()
        print(self.get_current_time())
        return True

    def validate_epic(self, epic_id):
        n = len(epic_id)
        ret = ""
        cnt = 0
        # print("--->>", epic_id)
        for i in range(n):
            c = epic_id[i]
            if c.isdigit() and cnt < 3:
                if c == "2":
                    c = "Z"
                elif c == "1":
                    c = "I"
                else:
                    continue

            if c.isalpha() or c.isdigit() or c == "/":
                ret += c
                cnt += 1
        if cnt < 4:
            return ""
        return ret

    def get_current_time(self):
        return datetime.now().strftime("%H:%M:%S")
                                                                                                        
    def process_img(self, imgpath = 'out/out6.jpg'):
        img = cv2.imread(imgpath)
        hts = self.find_hts(img)

        # for ny in range(self.cnth):
        for ht in hts:
            if ht == hts[-1]:
                break
            for nx in range(self.cntw):
                rst = (self.sx + self.dw * nx, ht + 9)
                red = (rst[0] + self.sw, rst[1] + self.sh)
                # img = cv2.rectangle(img, rst, red, (255, 0, 0), 5)
                epic_img = img[rst[1]:red[1], rst[0]:red[0]]
                
                custom_config1 = r'--oem 3 --psm 6'
                epic_id = pytesseract.image_to_string(epic_img, config=custom_config1)
                epic_id = self.validate_epic(epic_id)

                rst2 = (self.sx2 + self.dw * nx, ht + 9)
                red2 = (rst2[0] + self.sw2, rst2[1] + self.sh2)
                serial_img = img[rst2[1]:red2[1], rst2[0]:red2[0]]
                if epic_id == "":
                    if self.check_image_empty(serial_img):
                        continue

                # custom_config2 = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
                # serial_no = pytesseract.image_to_string(serial_img, config=custom_config2)
                # serial_no = self.validate_epic(serial_no)
                self.serial_no += 1
                serial_no = self.serial_no
                print(epic_id, serial_no)

                self.outfile.write("{},{}\n".format(epic_id, serial_no))
                # cv2.imshow("EPIC_IMG", epic_img)
                # cv2.waitKey(0)


        img = cv2.resize(img, dsize=(0,0), fx=0.2, fy=0.2, interpolation=cv2.INTER_LINEAR)
        # cv2.imshow('image',img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
    def check_image_empty(self, img):
        if np.mean(img) == 255:
            return True
        return False

    def process_pdfs(self, path, savepath, i):
        self.create_folder_if_not_exists(savepath)

        filenames = os.listdir(path)
        filenames.sort(key=lambda f: int(re.sub('\D', '', f)))
        flag = False
        # if i == 25:
        #     flag = True
        for name in filenames:
            if name == "S11A25P96.pdf":
                flag = False
            if flag:
                continue

            full_pdf_path = path + name
            save_file_path = savepath + name.replace(".pdf", ".txt")
            print("->", full_pdf_path, save_file_path)
            if not self.process_pdf(full_pdf_path, save_file_path, i):
                print("Stopping in the middle")
                return False

if __name__ == "__main__":
    epicReader = EpicReader()
    for i in range(7, 8):
        epicReader.process_pdfs("pdfs{}/".format(i), "epics{}/".format(i), i)
    # epicReader.process_pdf("a1.pdf", "out.txt")
    # epicReader.process_img("out/out40.jpg")