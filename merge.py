import os
import re
import csv
import sys
maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

class Merge:
    def __init__(self, path):
        self.dir = path
        self.outPath = "final/"

    def start(self, epic_id):

        self.create_folder_if_not_exists(self.outPath)

        path = self.dir + "/save" + str(epic_id)
        filenames = os.listdir(path)
        filenames.sort(key=lambda f: int(re.sub('\D', '', f)))
        outFilename = self.outPath + "/Final{}.csv".format(epic_id)
        self.outfile = open(outFilename, 'w', newline='', encoding="utf-8")
        self.outwriter = csv.writer(self.outfile)
        self.outwriter.writerow(['filename', 'LAC', 'Boost', 'success', 'state', 'ac_acn', 'pc', 'name', 'name_v1', 'gender', 'age', 'epic_no', 'father_name', 'father_name_v1', 'part_number', 'part_name', 'pdf_serial_no', 'web_serial_no', 'polling_station'])

        for filename in filenames:
            inFilepath = path + "\\" + filename
            booth_id = re.search(r'P(.*?)\.', filename).group(1)
            print(booth_id)
            self.inputfile = open(inFilepath, 'r', encoding="utf8")
            self.inreader = csv.reader(self.inputfile, delimiter=',', quotechar='|')
            isFirstRow = True
            for row in self.inreader:
                if isFirstRow:
                    isFirstRow = False
                    continue
                # print(row)
                row.insert(1, epic_id)
                row.insert(2, booth_id)
                self.outwriter.writerow(row)
            self.outfile.flush()
            self.inputfile.close()

        self.outfile.close()



    def create_folder_if_not_exists(self, foldername):
        if not os.path.exists(foldername):
            os.makedirs(foldername)

if __name__ == "__main__":
    path = "D:/git/EpicData/archive"
    merge = Merge(path)
    for i in range(66, 67):
        merge.start(i)