mkdir -p local_data
mkdir -p local_data/t2dv2
mkdir -p local_data/t2dv2/data
mkdir -p local_data/t2dv2/raw
cd local_data/t2dv2/raw
wget http://webdatacommons.org/webtables/extended_instance_goldstandard.tar.gz
tar -xvzf extended_instance_goldstandard.tar.gz
rm extended_instance_goldstandard.tar.gz
ls
rm classes_GS.csv
wget -O classes_GS.csv https://raw.githubusercontent.com/oeg-upm/tada-gam/master/experiments/t2dv2/classes_GS.fixed
#cp classes_GS.csv ../meta.csv
wget -O ../meta.csv https://raw.githubusercontent.com/oeg-upm/ttla/master/meta/T2Dv2_typology.csv
cd ../../..
python scripts/t2dv2_json_to_csv.py local_data/t2dv2/raw local_data/t2dv2/data