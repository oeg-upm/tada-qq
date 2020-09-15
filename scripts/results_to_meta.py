import pandas as pd

out_meta = "t2dv2_multi_meta.tsv"

def write_meta(attrs):
    line = "\t".join(attrs)
    f = open(out_meta,"a")
    f.write(line+"\n")
    f.close()
    print("Writing: ")
    print(line)


fname = "new_t2dv2_results_meta -- ya this one.csv"
df = pd.read_csv(fname, header=None)
f = open(out_meta, 'w')
f.close()


prev_fname = ""
prev_class_uri = ""
prev_colid = ""
candidates = []

for idx, row in df.iterrows():
    if len(row) < 6:
        break
    print(row)
    fname2 = row[0].strip()
    class_uri = row[1].strip()
    colid = str(row[2])
    g_property_uri = row[3].strip()  # gold standard property
    c_property_uri = row[4].strip()  # candidate property
    good_candidate = row[6].strip()
    is_good = good_candidate == 'y'
    if prev_fname == fname2 and prev_colid == colid:  # the same as the previous one
        print("as previous: "+str(idx))
        if is_good and c_property_uri not in candidates:
            candidates.append(c_property_uri)
    else:
        print("not as previous: "+str(idx))
        properties = ",".join(candidates)
        attrs = [
            prev_fname,
            prev_class_uri,
            prev_colid,
            properties
        ]
        if prev_fname != "":
            write_meta(attrs)
        prev_fname = fname2
        prev_class_uri = class_uri
        prev_colid = colid
        if good_candidate != '?':
            candidates = [g_property_uri]
        if is_good and c_property_uri not in candidates:
            candidates.append(c_property_uri)

    # print("idx: "+str(idx))
    # if idx>10:
    #     print(" -- idx: "+str(idx))
    #     break


properties = ",".join(candidates)
attrs = [
    prev_fname,
    prev_class_uri,
    prev_colid,
    properties
]
write_meta(attrs)

