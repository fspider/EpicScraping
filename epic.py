import requests
import json
import re
from datetime import datetime
import csv
import os

class Scrapping:
    def __init__(self):
        self.base_url = 'https://www.keralabjp.in/code.aspx/Getdtls'
        self.session = requests.Session()


    def create_folder_if_not_exists(self, foldername):
        if not os.path.exists(foldername):
            os.makedirs(foldername)

    def start(self, inputpath, outpath, failedpath):
        self.create_folder_if_not_exists(outpath)
        self.create_folder_if_not_exists(failedpath)

        filenames = os.listdir(inputpath)
        filenames.sort(key=lambda f: int(re.sub('\D', '', f)))

        flag = True
        for filename in filenames:
            if filename == "S11A49P127.txt":
                flag = False
            if flag:
                continue

            inputfilename = inputpath + "/" + filename
            outfilename = outpath + "/" + filename.replace(".txt", ".csv")
            failedfilename = failedpath + "/" + filename


            print(self.get_current_time(), filename)
            self.process_file(inputfilename, outfilename, failedfilename)

    def process_file(self, inputfilename, outfilename, failedfilename):
        self.inputfile = open(inputfilename, 'r')
        self.outfile = open(outfilename, 'w', newline='', encoding="utf-8")
        self.outwriter = csv.writer(self.outfile)
        self.failedfile = open(failedfilename, 'w')

        self.outwriter.writerow(["epic_id", "constituency", "booth", "section", "slno", "votername", "gender", "age"])
        cnt = 0
        while True:
            line = self.inputfile.readline()
            if not line:
                break
            epic_id = line.strip()
            epic_id = epic_id.replace("O", "0")
            if epic_id == "":
                continue
            ret = self.get_data(epic_id)

            cnt += 1
            if cnt % 100 == 0:
                print(self.get_current_time(), cnt)

        self.failedfile.close()
        self.outfile.close()
        self.inputfile.close()

    def get_data(self, epic_id):
        data = {'EPIC1' : epic_id}
        r = self.session.post(self.base_url, json=data, headers={})
        data = json.loads(r.content)
        info = data["d"]
        try:
            constituency = re.search('<F1>(.*?)</F1>', info).group(1).strip()
            booth = re.search('<F2>(.*?)</F2>', info).group(1).strip()
            section = re.search('<F3>(.*?)</F3>', info).group(1).strip()
            slno = re.search('<F4>(.*?)</F4>', info).group(1).strip()
            votername = re.search('<F6>(.*?)</F6>', info).group(1).strip()
            gender = re.search('<F12>(.*?)</F12>', info).group(1).strip()
            age = re.search('<F13>(.*?)</F13>', info).group(1).strip()
        except:
            print("x :", epic_id) 
            self.failedfile.write(epic_id + "\n")
            return False

        self.outwriter.writerow([epic_id, constituency, booth, section, slno, votername, gender, age])
        return True
    def get_current_time(self):
        return datetime.now().strftime("%H:%M:%S")

if __name__ == "__main__":
    scrap = Scrapping()
    # scrap.get_data('UVF0905497')
    scrap.start('epics2', 'final2', 'failed2')