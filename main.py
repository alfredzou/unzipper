import os
import re

class ZipList:
    def __init__(self, zip_path):
        files = os.walk(zip_path).__next__()
        self.zips = [zip for zip in files if re.search(r'^.*.(zip|rar)$',zip)]


    def manipulate_zips(self):
        self.rename_zips()
        pass
        # input_zip_zips = [file for file in zips if re.search(r'^\(.*?\).*\.(zip|rar)$',file)]
        # f2 = [re.sub('^\(.*?\) ','',file) for file in input_zip_zips]
        # f2

    def shorten_zips(self):
        self.rename_zips()
        pass

    def rename_zips(self):
        # for i,j in zip(input_zip_zips,f2):
        #     os.rename(src=i,dst=j)

def main():
    zip_path = '.'
    zip_list = ZipList(zip_path)
    zip_list.manipulate_zips()
    zip_list.shorten_zips()

if __name__ == '__main__':
    main()