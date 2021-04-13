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

        flag = False
        for filename in filenames:
<<<<<<< HEAD
            if filename == "S11A60P4.txt":
=======
<<<<<<< HEAD
            if filename == "S11A49P127.txt":
=======
            if filename == "S11A60P63.txt":
>>>>>>> ebebdada32a3d3bf352ea2d7b14db3b060ecd7cc
>>>>>>> 3a29c6067178353718e7d753e0ec89683e6567eb
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

        self.outwriter.writerow(["epic_id", "serial_no", "success", "constituency", "booth", "section", "slno", "votername", "gender", "age"])
        cnt = 0
        self.serial_no = 0
        while True:
            line = self.inputfile.readline()
            if not line:
                break
            arr = line.strip().split(',')
            epic_id = arr[0]
            serial_no = arr[1]
            epic_id = epic_id.replace("O", "0")
            ret = self.get_data(epic_id, serial_no)

            cnt += 1
            if cnt % 100 == 0:
                print(self.get_current_time(), cnt)

        self.failedfile.close()
        self.outfile.close()
        self.inputfile.close()

    def get_data(self, epic_id, serial_no):
        data = {'EPIC1' : epic_id}
        r = self.session.post(self.base_url, json=data, headers={})
        data = json.loads(r.content)
        info = data["d"]
        if epic_id == "":
            print("x :", epic_id, serial_no) 
            self.failedfile.write(epic_id + "," + serial_no + "\n")
            self.outwriter.writerow([epic_id, serial_no, 0, "", "", "", "", "", "", ""])
            return False

        try:
            constituency = re.search('<F1>(.*?)</F1>', info).group(1).strip()
            booth = re.search('<F2>(.*?)</F2>', info).group(1).strip()
            section = re.search('<F3>(.*?)</F3>', info).group(1).strip()
            slno = re.search('<F4>(.*?)</F4>', info).group(1).strip()
            votername = re.search('<F6>(.*?)</F6>', info).group(1).strip()
            gender = re.search('<F12>(.*?)</F12>', info).group(1).strip()
            age = re.search('<F13>(.*?)</F13>', info).group(1).strip()
        except:
            print("x :", epic_id, serial_no) 
            self.failedfile.write(epic_id + "," + serial_no + "\n")
            self.outwriter.writerow([epic_id, serial_no, 0, "", "", "", "", "", "", ""])
            return False

        self.outwriter.writerow([epic_id, serial_no, 1, constituency, booth, section, slno, votername, gender, age])
        return True
    def get_current_time(self):
        return datetime.now().strftime("%H:%M:%S")

if __name__ == "__main__":
    scrap = Scrapping()
    # scrap.get_data('UVF0905497')
    scrap.start('epics1', 'final1', 'failed1')