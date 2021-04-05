import requests
import json
import re
import datetime
import csv
import os

class Scrapping:
    def __init__(self):
        self.base_url = 'https://www.keralabjp.in/code.aspx/Getdtls'
        self.session = requests.Session()


    def start(self):
        pass


    def get_data(self, epic_id):
        epic_id.replace("O", "0")
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
            return False

        print([epic_id, constituency, booth, section, slno, votername, gender, age])
        return True

if __name__ == "__main__":
    scrap = Scrapping()
    # scrap.get_data('UVF0905497')
    scrap.start()