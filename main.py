import os, re
import logging
from pathlib import Path

def setup_logging():
    logging.basicConfig(
        filename='./logs/app.log',
        level = logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class ZipList:
    def __init__(self, input_directory, output_directory=None):
        # Create list of zips 
        self.input_directory,_,files = os.walk(input_directory).__next__()
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
            input_path = f'{self.input_directory}{i}'
            output_path = self.output_directory / "outputs" / j

            if i != j:
                logging.debug(i)
                logging.debug(j)
                logging.debug('-----------------------------------------------------------------------------')
            
            os.rename(src=input_path, dst=output_path)

def main():
    setup_logging()
    logging.info('=============================================================================')
    input_directory = './'
    output_directory = Path.home() / "Desktop"
    try:
        zip_list = ZipList(input_directory, output_directory)
        zip_list.cleaning_zips()
        zip_list.shorten_zips()
        zip_list.rename_zips()
    except Exception as e:
        logging.critical(f'Error: {e}')

if __name__ == '__main__':
    main()