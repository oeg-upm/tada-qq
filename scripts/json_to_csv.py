# import sys
# sys.path.append("../")
import os
import json
import sys

import csv
# import unicodecsv as csv
import logging
import chardet


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def json_to_csv(fname, t2dv2_dir , dest_dir, overwrite=False):
    """
    :param fname: of the json file
    :return:
    """
    csv_fname = fname[:-4] + "tar.gz.csv"
    csv_dest = os.path.join(dest_dir, csv_fname)
    if os.path.exists(csv_dest) and not overwrite:
        logger.info("%s already exists" % csv_dest)
        return
    json_fdir = os.path.join(t2dv2_dir, "tables", fname)
    f = open(json_fdir, 'rb')

    s = f.read()
    detected_encoding = chardet.detect(s)['encoding']
    decoded_s = s.decode(detected_encoding)
    j = json.loads(decoded_s)
    f.close()
    table = zip(*j["relation"])
    with open(csv_dest, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for row in table:
            writer.writerow(row)
    logger.debug("generate csv %s" % csv_dest)


def export_files_to_csv(t2dv2_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    classes_dir = os.path.join(t2dv2_dir, "classes_GS.csv")
    with open(classes_dir, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            json_fname = row[0].strip()[:-6]+"json"
            json_to_csv(json_fname, t2dv2_dir, dest_dir, overwrite=False)
            logger.info("export: " + json_fname)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(sys.argv)
        print("Error: expecting the directory to the t2dv2 folder and the directory for the destination")
    else:
        export_files_to_csv(t2dv2_dir=sys.argv[1], dest_dir=sys.argv[2])