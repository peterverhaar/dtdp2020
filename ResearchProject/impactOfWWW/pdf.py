import requests
import re
import os
from nltk.tokenize import sent_tokenize, word_tokenize

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import unicodedata, codecs
from os.path import join
from io import StringIO






def getPDFText(pdfFilenamePath):
    retstr = StringIO()
    parser = PDFParser(open(pdfFilenamePath,'r+b'))
    try:
        document = PDFDocument(parser)
    except Exception as e:
        print(pdfFilenamePath,'is not a readable pdf')
        return ''
    if document.is_extractable:
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr,retstr, codec='ascii' , laparams = LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
        return retstr.getvalue()
    else:
        print(pdfFilenamePath,"Warning: could not extract text from pdf file.")
        return ''


for pdf in os.listdir('PDF'):
    print(pdf)
    fullText = getPDFText( join( 'PDF' , pdf ) )
    lines = re.split( r'\n' , fullText )
    fullText = ''

    for line in lines:
        if not( re.search( '^\d{1,4}$' , line.strip() ) ):
            fullText += line + ' '

    fileNameTxt = re.sub( r'[.]pdf$' , '.txt', pdf )
    sentences = sent_tokenize( fullText )
    out = open( fileNameTxt , 'w' , encoding = 'utf-8' )
    for s in sentences:
        out.write( s + '\n')
    out.close()
