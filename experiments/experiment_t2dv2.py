import os

if 't2dv2_dir' not in os.environ:
    print("ERROR: t2dv2_dir no in os.environ")

data_dir = os.environ['t2dv2_dir']
meta_dir = os.path.join(data_dir, '')

def get_numeric():
    """
    """

