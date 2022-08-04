import requests
import json
import re
import datetime
import csv
import os
from bs4 import BeautifulSoup
from datetime import datetime


class Scrapping:
    def __init__(self):
        self.domain = 'http://www.ceo.kerala.gov.in'
        self.base_url = self.domain + '/electoralrolls.html'
        # self.list_url = self.domain + '/electoralroll/partsListAjax.html?currentYear=2021&distNo=6&lacNo=60&sEcho=1&iColumns=5&sColumns=&iDisplayStart=0&iDisplayLength=500&iSortingCols=1&iSortCol_0=0&sSortDir_0=asc&bSortable_0=false&bSortable_1=false&bSortable_2=false&bSortable_3=false&bSortable_4=false&undefined=undefined'
        self.list_url = self.domain +   '/electoralroll/partsListAjax.html?currentYear=2021&distNo={}&lacNo={}&sEcho=1&iColumns=5&sColumns=&iDisplayStart=0&iDisplayLength=500&iSortingCols=1&iSortCol_0=0&sSortDir_0=asc&bSortable_0=false&bSortable_1=false&bSortable_2=false&bSortable_3=false&bSortable_4=false&undefined=undefined'
        self.session = requests.Session()

        self.site_key = None
        self.task = None
        self.laclist = [5, 16, 19, 32, 48, 60, 73, 87, 92, 101, 110, 115, 126, 140]
        self.save_file_name = "download_files.csv"

        f = open("0.districts_names.txt", "r")
        self.districts_names = []
        for x in f:
            self.districts_names.append(x.strip())
        print(self.districts_names)

        f = open("0.lac_names.txt", "r")
        self.lac_names = []
        for x in f:
            self.lac_names.append(x.strip())
        print(self.lac_names)

    def extract_url(self, s):
        match = re.search(r'href=[\'"]?([^\'" >]+)', s)
        if match:
            url = match.group(1)
            # print(url)
            return url
        return ""

    def start(self):
        self.save_file = open(self.save_file_name, "w", encoding="utf-8", newline="")
        self.saveFileWriter = csv.writer(self.save_file)
        self.saveFileWriter.writerow(["District", "LAC", "booth_id", "Polling Station Name", "Filename"])


        lacNo = 1
        for i in range(0, 14):
            distNo = i + 1
            self.dist_name = self.districts_names[distNo - 1]
            while lacNo <= self.laclist[i]:
                self.lac_name = self.lac_names[lacNo - 1]
                self.start_lac(distNo, lacNo)
                lacNo += 1
                if lacNo == 141:
                    return
        self.save_file.close()

    def start_lac(self, distNo, lacNo):

        list_url = self.list_url.format(distNo, lacNo)
        r = self.session.get(list_url)

        print(self.session.cookies.get_dict())
        # self.cookie = "PHPSESSID={}; rufc=false".format(self.session.cookies.get_dict()['PHPSESSID'])
        self.cookie = ""
        print(self.cookie)
        booths = json.loads(r.content)
        # soup=BeautifulSoup(html,'lxml')
        # print(booths)
        nbooths = len(booths["aaData"])
        print(nbooths)
        # self.token = soup.find('input', {'id':'token'}).get('value')
        # print(self.token)
        cnt = 0
        for i in range(cnt, nbooths):
            booth = booths["aaData"][i]
            booth_id = booth[0]
            booth_polling_station_name = booth[1]
            self.pdf_url = self.extract_url(booth[4])
            booth_filename = self.pdf_url.split('/')[-1]
            print(cnt, self.dist_name, self.lac_name, booth_id, booth_polling_station_name, booth_filename)
            self.saveFileWriter.writerow([self.dist_name, self.lac_name, booth_id, booth_polling_station_name, booth_filename])
            cnt += 1


if __name__ == "__main__":
    scrap = Scrapping()
    scrap.start()
