#!/usr/bin/env python3

import argparse
from PyPDF2 import PdfFileReader, PdfFileWriter

parser = argparse.ArgumentParser(description='Reorder an A5 document for double-sided printing on to-be-cut A4 pages.\n\n Print using 2 pages per sheet with short-edge binding.')
parser.add_argument("pdf", help="The pdf of the document to be printed")
parser.add_argument("-o", "--out", help="Output file path.")
args = parser.parse_args()

if not args.out:
    args.out = args.pdf[:-4]+"-a4print.pdf"

with open(args.pdf, "rb") as pdf_file, open(args.out, "wb") as out_file:
    out_pdf = PdfFileWriter()
    in_pdf = PdfFileReader(pdf_file)

    def add_page(i):
        try:
            out_pdf.addPage(in_pdf.getPage(i))
        except IndexError:
            out_pdf.addBlankPage()

    n = in_pdf.getNumPages()
    m = int(n / 4) + 1
    print("Opened {}, read {} pages, resulting in {} A4 pages.".format(args.pdf, n, m))

    for i in range(m):
        add_page(      i*2)
        add_page(m*2 + i*2)
        add_page(m*2 + i*2 + 1)
        add_page(      i*2 + 1)

    out_pdf.write(out_file)