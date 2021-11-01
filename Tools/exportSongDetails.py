# Export song details as csv

import os, re
from csv import DictWriter, writer

headers = ["title"]
songs = []
song_list_file = "songlist.csv"

def append_list_as_row(file_name, list_of_elem):
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(list_of_elem)

def append_dict_as_row(file_name, dict_of_elem, field_names):
    with open(file_name, 'a+', newline='') as write_obj:
        dict_writer = DictWriter(write_obj, fieldnames=field_names)
        dict_writer.writerow(dict_of_elem)

if os.path.exists(song_list_file):
  os.remove(song_list_file)

for root, dirnames, filenames in os.walk("Lieder"):
        for filename in filenames:
            if filename.endswith('.tex'):
                f = open(root+"/"+filename, "r")
                lines = f.readlines()
                f.close()

                song = {}
                for line in lines:
                    title = re.search(r'\\beginsong{([\s\S]+)}', line)
                    datum = re.search(r'(\w+)={([ \S]*)}', line)
                
                    if title:
                        song["title"] = title.group(1)

                    if datum:
                        key = datum.group(1)
                        value = datum.group(2)
                        song[key] = value

                        if key not in headers:
                            headers.append(key)
                songs.append(song)

append_list_as_row(song_list_file,headers)
print("Found " + str(len(songs)) + " songs. Writing to file " + song_list_file)
for song in songs:
    append_dict_as_row(song_list_file, song, headers)

