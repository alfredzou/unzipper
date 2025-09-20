import os, re
import logging
from pathlib import Path
import shutil
import rarfile
import py7zr
from dotenv import load_dotenv
import os

def load_config():
    load_dotenv()

    config = {
        "LOGGING_LEVEL": os.getenv("LOGGING_LEVEL", "WARNING").upper(),
        "INPUT_DIRECTORY": Path(os.getenv("INPUT_DIRECTORY")),
        "OUTPUT_DIRECTORY": Path(os.getenv("OUTPUT_DIRECTORY")),
    }

    # Reads the logging level from the .env file, with default logging level of logging.WARNING
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config["LOGGING_LEVEL"] not in valid_levels:
        raise ValueError(f"Invalid LOGGING_LEVEL: {config["LOGGING_LEVEL"]}. Select a level from: {valid_levels}")

    setup_logging(config)

    if not config['INPUT_DIRECTORY'].is_dir():
        raise ValueError(f"Input directory does not exist: {config['INPUT_DIRECTORY']}")
    
    if not config['OUTPUT_DIRECTORY'].is_dir():
        raise ValueError(f"Input directory does not exist: {config['OUTPUT_DIRECTORY']}")
    
    return config

def setup_logging(config):
    log_path = Path(__file__).parent / 'logs' / 'app.log'
    log_path.parent.mkdir(parents=True, exist_ok=True)

    numeric_level = getattr(logging, config["LOGGING_LEVEL"])

    logging.basicConfig(
        filename = log_path,
        level = numeric_level,
        format = '%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info('=============================================================================')

class ZipList:
    def __init__(self, config):
        # Create list of zips 
        self.input_directory = config['INPUT_DIRECTORY']
        _,_,files = os.walk(self.input_directory).__next__()
        logging.info(f'Scanning {self.input_directory}')

        self.output_directory = config['OUTPUT_DIRECTORY']
        logging.info(f'Output directory set as {self.output_directory}')

        logging.info(f'There are {len(files)} files in the directory.')
        logging.debug(f'The files are: {files}')

        self.zips = [i for i in files if re.search(r'.(zip|rar|7z)$',i)]
        logging.info(f'There are {len(self.zips)} zips in the directory.')
        logging.debug(f'The zips are: {self.zips}')

    def cleaning_zips(self):
        # Remove first ()
        self.zips_new_name = [re.sub(r'^\(.*?\)\s*', '', i)
                                for i in self.zips]
        
        # Remove () within [] zip names
        self.zips_new_name = [re.sub(r'^\[(.*?)]', 
                                lambda m: "[{}]".format(re.sub(r' \(.*?\)', '', m.group(1))),
                                i, count=1)
                                for i in self.zips_new_name]

        # Strip first character if its a [
        self.zips_new_name = [i[1:] if i[0] == '[' else i for i in self.zips_new_name]
        logging.info('Starting cleaning.')

    def shorten_zips(self):
        # Reduce zips to specified number of characters
        threshold = 100
        self.zips_new_name = [i[:threshold].strip()+Path(i).suffix if len(i)>threshold 
                                else Path(i).stem.strip() + Path(i).suffix
                                for i in self.zips_new_name]
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
        # Scan output directory for zip and rar files
        # Check if enough space first
        # If rar file, then use rarfile module
        # Otherwise use shutil.unpack_archive for zip files
        # Check extraction completed correctly
        # If so remove the initial zip file
        file_list = os.listdir(self.output_directory)
        zips = [Path(i) for i in file_list if re.search(r'.(zip|rar|7z)$',i)]
        zips_path = [self.output_directory / i for i in zips]
        extracted_zips_path = [self.output_directory / '(processed)' / i.stem for i in zips]

        for zips, zip_input, zip_target in zip(zips, zips_path,extracted_zips_path):
            logging.debug(f"Attempting to extract {zip_input}")
            if self.space_check():
                try:
                    if zips.suffix == '.7z':
                        logging.debug(f'7z file detected.')
                        with py7zr.SevenZipFile(zip_input, mode='r') as szf:
                            szf.extractall(path=zip_target)
                    elif zips.suffix == '.rar':
                        logging.debug(f'Rar file detected.')
                        with rarfile.RarFile(zip_input) as rf:
                            rf.extractall(path=zip_target)
                    else:
                        shutil.unpack_archive(zip_input, zip_target)
            
                    if os.path.isdir(zip_target) and os.listdir(zip_target):
                        os.remove(zip_input)
                        logging.debug(f'Unpack verified, zip deleted.')
                except Exception as e:
                    logging.critical(f'Unpack failed: {e}')

def main():
    config = load_config()
    try:
        zip_list = ZipList(config)
        zip_list.cleaning_zips()
        zip_list.shorten_zips()
        zip_list.rename_zips()
        zip_list.extract_zips()
    except Exception as e:
        logging.critical(f'Error: {e}')

if __name__ == '__main__':
    main()