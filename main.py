from pdf2image import convert_from_path

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
        self.sx = int(self.config['DEFAULT']['sx'])
        self.sy = int(self.config['DEFAULT']['sy'])
        self.sw = int(self.config['DEFAULT']['sw'])
        self.sh = int(self.config['DEFAULT']['sh'])

        self.px1 = int(self.config['DEFAULT']['px1'])
        self.px2 = int(self.config['DEFAULT']['px2'])

        self.dw = int(self.config['DEFAULT']['dw'])
        self.dh = int(self.config['DEFAULT']['dh'])

        self.cntw = int(self.config['DEFAULT']['cntw'])
        self.cnth = int(self.config['DEFAULT']['cnth'])

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
                if len(ret)>0 and ret[-1] + 20 > h:
                    ret.pop()
                ret.append(h)
        # print(ret)
        return ret

    def process_pdf(self, filename, save_file_path):
        self.outfile = open(save_file_path, "w")
        pages = convert_from_path(filename, 500)
        cnt = 0
        nPages = len(pages)
        print(self.get_current_time())
        for i in range(2, nPages - 1):
            page = pages[i]
            cnt += 1
            # page.save('out2/out{}.jpg'.format(cnt), 'JPEG')
            # print("{}.jpg saved".format(cnt))
            savepath = 'out/tmp.jpg'
            page.save(savepath, 'JPEG')
            print("[process_pdf] Processing {}th page".format(cnt))
            self.process_img(savepath)
            self.outfile.flush()
        self.outfile.close()
        print(self.get_current_time())

    def validate_epic(self, epic_id):
        n = len(epic_id)
        ret = ""
        for i in range(n):
            c = epic_id[i]
            if c.isalpha() or c.isdigit() or c == "/":
                ret += c
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
                

                custom_config = r'--oem 3 --psm 6'
                epic_id = pytesseract.image_to_string(epic_img, config=custom_config)
                epic_id = self.validate_epic(epic_id)
                print(epic_id)                                                                                                                                                              

                if epic_id != "":
                    self.outfile.write(epic_id + "\n")

                # cv2.imshow("EPIC_IMG", epic_img)
                # cv2.waitKey(0)


        img = cv2.resize(img, dsize=(0,0), fx=0.2, fy=0.2, interpolation=cv2.INTER_LINEAR)
        # cv2.imshow('image',img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
    def process_pdfs(self, path, savepath):
        filenames = os.listdir(path)
        filenames.sort(key=lambda f: int(re.sub('\D', '', f)))
        flag = True
        for name in filenames:
            if name == "S11A49P100.pdf":
                flag = False
            if flag:
                continue

            full_pdf_path = path + name
            save_file_path = savepath + name.replace(".pdf", ".txt")
            print("->", full_pdf_path, save_file_path)
            self.process_pdf(full_pdf_path, save_file_path)

if __name__ == "__main__":
    epicReader = EpicReader()
    epicReader.process_pdfs("pdfs2/", "epics2/")
    # epicReader.process_pdf("a1.pdf", "out.txt")
    # epicReader.process_img("out/out40.jpg")