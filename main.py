import os, re
import logging

def setup_logging():
    logging.basicConfig(
        filename='./logs/app.log',
        level = logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class ZipList:
    def __init__(self, zip_path):
        # Create list of zips 
        _,_,files = os.walk(zip_path).__next__()
        logging.info(f'There are {len(files)} files in the root directory.')
        logging.debug(f'The files are: {files}')

        self.zips = [i for i in files if re.search(r'.(zip|rar)$',i)]
        logging.info(f'There are {len(self.zips)} zips in the root directory.')
        logging.debug(f'The zips are: {self.zips}')

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
        pass
        # for i,j in zip(self.zips,f2):
        #     os.rename(src=i,dst=j)

def main():
    setup_logging()
    zip_path = './input/'
    zip_list = ZipList(zip_path)
    zip_list.manipulate_zips()
    zip_list.shorten_zips()

if __name__ == '__main__':
    main()