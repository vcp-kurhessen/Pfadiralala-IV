#!/usr/bin/env python3

# This script removes empty intersong / scripture environments.

import os, sys

def myprint(x):
    print(x)

                    
def strip_empty_part(lines, start="\\begin{intersong}", end="\\end{intersong}", margin=8):
    for i, line in enumerate(lines):
        if start in line:
            match_start = i
        if end in line:
            match_end = i

    try: 
        string = "".join(lines[match_start:match_end+1])
        print("{} lines, {} chars({})".format(match_end - match_start, len(string), filename))
    
        if len(string) < (len(start) + len(end) + margin):
            lines = lines[0:match_start] + lines[match_end+1:]
            return lines
    except UnboundLocalError:
        pass
        
    return lines

for root, dirnames, filenames in os.walk("Lieder"):
        for filename in filenames:
            if filename.endswith('.tex'):
                
                f = open(root+"/"+filename, "r")
                lines = f.readlines()
                f.close()
                
                cleaned = strip_empty_part(lines)
                cleaned2 = strip_empty_part(cleaned, start="\\beginscripture", end="\\endscripture")
                
                f = open(root+"/"+filename, "w")
                f.write("".join(cleaned2))
                f.close()