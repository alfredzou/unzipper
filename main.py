import os, re
import logging
from pathlib import Path
import shutil

def setup_logging():
    logging.basicConfig(
        filename='./logs/app.log',
        level = logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class ZipList:
    def __init__(self, input_directory, output_directory=None):
        # Create list of zips 
        self.input_directory = input_directory
        _,_,files = os.walk(input_directory).__next__()
        logging.info(f'Scanning {self.input_directory}')

        if output_directory == None:
            self.output_directory = self.input_directory
        else:
            self.output_directory = output_directory
        logging.info(f'Output directory set as {self.output_directory}')

        logging.info(f'There are {len(files)} files in the directory.')
        logging.debug(f'The files are: {files}')

        self.zips = [i for i in files if re.search(r'.(zip|rar)$',i)]
        logging.info(f'There are {len(self.zips)} zips in the directory.')
        logging.debug(f'The zips are: {self.zips}')

    def cleaning_zips(self):
        # Remove () within [] zip names
        # Strip first character if its a [
        self.zips_new_name = [re.sub(r'^\[(.*?)]', 
                                lambda m: "[{}]".format(re.sub(r' \(.*?\)', '', m.group(1))),
                                i, count=1)
                                for i in self.zips]
        self.zips_new_name = [i[1:] if i[0] == '[' else i for i in self.zips_new_name]
        logging.info('Starting cleaning.')

    def shorten_zips(self):
        # Reduce zips to specified number of characters
        threshold = 100
        prefix_length = threshold - 4
        self.zips_new_name = [i[:prefix_length]+i[-4:] if len(i)>threshold else i for i in self.zips_new_name]
        logging.info(f'There are {len([i for i in self.zips if len(i)>threshold])} zips longer than {threshold} characters.')
        logging.info('Starting shortening.')

    def rename_zips(self):
        # renames within current directory or moves to another directory
        logging.info(f'Writing to {self.output_directory}')
        logging.debug(f'Renamed zips are:')

        for i, j in zip(self.zips,self.zips_new_name):
            input_path = self.input_directory / i
            output_path = self.output_directory  / j

            if i != j:
                logging.debug(i)
                logging.debug(j)
                logging.debug('-----------------------------------------------------------------------------')
            
            os.rename(src=input_path, dst=output_path)

    def space_check(self):
        # Check if more than 5 gbs
        _,_,free = shutil.disk_usage(self.output_directory)
        free_gb = free // 2**30
        space_check = free_gb > 5
        logging.debug(f"Free space (gb) is {free_gb}. Sufficient space: {space_check}.")
        return space_check

    def extract_zips(self):
        file_list = os.listdir(self.output_directory)
        zips = [i for i in file_list if re.search(r'.(zip|rar)$',i)]
        zips_path = [self.output_directory / i for i in zips]
        extracted_zips_path = [self.output_directory / '(processed)' / i for i in zips]

        for zip_name, i, j in zip(zips, zips_path,extracted_zips_path):
            logging.debug(f"Attempting to extract {i}")
            if self.space_check():
                try:
                    extracted_path = self.output_directory / '(processed)' / str.strip(zip_name[:len(zip_name)-4])
                    shutil.unpack_archive(i, extracted_path)
                    if os.path.isdir(extracted_path) and os.listdir(extracted_path):
                        os.remove(i)
                        logging.debug(f'Unpack verified, zip deleted.')
                except Exception as e:
                    logging.critical(f'Unpack failed: {e}')

def main():
    setup_logging()
    logging.info('=============================================================================')
    input_directory = Path.home() / 'Downloads' / 'finished'
    output_directory = Path.home() / 'Desktop' / 'outputs'
    try:
        zip_list = ZipList(input_directory, output_directory)
        zip_list.cleaning_zips()
        zip_list.shorten_zips()
        zip_list.rename_zips()
        zip_list.extract_zips()
    except Exception as e:
        logging.critical(f'Error: {e}')

if __name__ == '__main__':
    main()