import requests
import json
import re
import datetime
import csv
import os
from bs4 import BeautifulSoup
from datetime import datetime
# from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask


class Scrapping:
    def __init__(self):
        self.domain = 'http://www.ceo.kerala.gov.in'
        self.base_url = self.domain + '/electoralrolls.html'
        # self.list_url = self.domain + '/electoralroll/partsListAjax.html?currentYear=2021&distNo=6&lacNo=60&sEcho=1&iColumns=5&sColumns=&iDisplayStart=0&iDisplayLength=500&iSortingCols=1&iSortCol_0=0&sSortDir_0=asc&bSortable_0=false&bSortable_1=false&bSortable_2=false&bSortable_3=false&bSortable_4=false&undefined=undefined'
        self.list_url = self.domain +   '/electoralroll/partsListAjax.html?currentYear=2021&distNo={}&lacNo={}&sEcho=1&iColumns=5&sColumns=&iDisplayStart=0&iDisplayLength=500&iSortingCols=1&iSortCol_0=0&sSortDir_0=asc&bSortable_0=false&bSortable_1=false&bSortable_2=false&bSortable_3=false&bSortable_4=false&undefined=undefined'
        self.session = requests.Session()

        self.api_key = "e00923a245a141aabc38bf7031e7d35b"
        self.site_key_pattern = 'data-sitekey="(.+?)"'
        # self.client = AnticaptchaClient(self.api_key)
        self.site_key = None
        self.task = None
        self.laclist = [5, 16, 19, 32, 48, 60, 73, 87, 92, 101, 110, 115, 126, 140]
    def extract_url(self, s):
        match = re.search(r'href=[\'"]?([^\'" >]+)', s)
        if match:
            url = match.group(1)
            # print(url)
            return url
        return ""

    def start(self):
        lacNo = 100
        for i in range(0, 14):
            distNo = i + 1
            while lacNo <= self.laclist[i]:
                self.start_lac(distNo, lacNo)
                lacNo += 1
                if lacNo == 141:
                    return

    def start_lac(self, distNo, lacNo):
        self.save_path = "pdfs{}".format(lacNo)
        self.create_folder_if_not_exists(self.save_path)

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
            self.pdf_url = self.extract_url(booth[4])
            print(cnt, self.pdf_url)
            self.download_pdf()
            cnt += 1

    def create_folder_if_not_exists(self, foldername):
        if not os.path.exists(foldername):
            os.makedirs(foldername)

    def download_pdf(self):
        # self.pdf_url = "http://www.ceo.kerala.gov.in:80/pdf/voterslist/2021/FINAL/KLA2021/AC060/S11A60P1.pdf"

        # token = self.solve_captcha1()
        # if token == None:
        #     print("Solving Captcha Failed")
        #     return False
        # print("Token = {}".format(token))

        html = self.session.get(self.pdf_url).text
        soup=BeautifulSoup(html,'lxml')
        self.pdf_download_url = soup.find('form', {'id':'eRollDownloadFormId'}).get('action')
        print(self.pdf_download_url)

        # self.pdf_download_url = "{}?download={}".format(self.pdf_url, 'GFM0u%2Fb%2F41P59Jkt0qxLAw%3D%3D')
        self.download_file()

    def download_file(self):
        local_filename = self.save_path + "/" + self.pdf_url.split('/')[-1]
        # NOTE the stream=True parameter below
        if os.path.exists(local_filename):
            return local_filename

        with requests.get(self.pdf_download_url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)
        return local_filename


    def solve_captcha1(self):
        print("Solving Captcha Started !")
        try:
            task = self.get_task()
            job = self.client.createTaskSmee(task, timeout=10 * 60)
            token = job.get_solution_response()
            print("Solving Captcha Completed !")
            return token
        except Exception as e:
            print("Get Captcha Token error !")
            print(e)
            return None

    def get_task(self):
        if self.task is None:
            site_key = self.get_site_key()
            self.task = NoCaptchaTaskProxylessTask(website_url=self.pdf_url, website_key=site_key)
        return self.task

    def get_site_key(self):
        if self.site_key is None:
            html = self.session.get(self.pdf_url).text
            # self.cookie = "PHPSESSID={};".format(self.session.cookies.get_dict()['PHPSESSID'])

            # self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
            #                 'Cookie': self.cookie,
            #                 'Upgrade-Insecure-Requests': '1'}

            self.site_key = re.search(self.site_key_pattern, html).group(1)
        return self.site_key


if __name__ == "__main__":
    scrap = Scrapping()
    scrap.start()
    # scrap.download_pdf()
