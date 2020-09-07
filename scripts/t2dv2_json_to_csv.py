# This code is adapted from https://github.com/oeg-upm/tada-gam
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import json
import unicodecsv as csv
# import csv
import logging
import chardet


def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger

print("name: ")
# print(logging.getLogger(__name__))
logger = get_logger(__name__)

DATA_DIR = None  # "data"
DEST_DIR = None  # "../../local_data/t2dv2"


def json_to_csv(fname, overwrite=False):
    """
    :param fname: of the json file
    :return:
    """
    csv_fname = fname[:-4] + "csv"
    csv_dest = os.path.join(DEST_DIR, csv_fname)
    if os.path.exists(csv_dest) and not overwrite:
        logger.info("%s already exists" % csv_dest)
        return
    json_fdir = os.path.join(DATA_DIR, "tables", fname)
    f = open(json_fdir)
    s = f.read()
    detected_encoding = chardet.detect(s)['encoding']
    logger.debug("detected encoding %s for %s" % (detected_encoding, fname))
    decoded_s = s.decode(detected_encoding)
    j = json.loads(decoded_s)
    f.close()
    table = zip(*j["relation"])
    with open(csv_dest, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for row in table:
            writer.writerow(row)

    logger.debug("generate csv %s" % csv_dest)


def export_files_to_csv():
    if not os.path.exists(DEST_DIR):
        os.mkdir(DEST_DIR)
    classes_dir = os.path.join(DATA_DIR, "classes_GS.csv")
    with open(classes_dir, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            json_fname = row[0].strip()[:-6]+"json"
            json_to_csv(json_fname, overwrite=False)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Invalid number of arguments. Expects the SOURCE_DIR and the DESTINATION_DIR ")
    else:
        source_dir = sys.argv[1]
        dest_dir = sys.argv[2]
        DATA_DIR = source_dir
        DEST_DIR = dest_dir
        export_files_to_csv()
