#!/usr/bin/env python
# coding: utf-8

# In[31]:


from bs4 import BeautifulSoup
import requests
import re
import string
from os.path import join


baseUrl = "http://www.poedecoder.com/Qrisse/works/"

soup = ""

response = requests.get( baseUrl )

soup = BeautifulSoup( response.text ,"lxml")
links = soup.find_all( "a")

for l in links:


    if l.get("href") is not None:

        target = l.get("href")
        if not( re.search( r'^http' , target ) ):

            textUrl = baseUrl + target

            if re.search( '.' , textUrl ):


                response = requests.get( textUrl )
                soup = BeautifulSoup( response.text ,"lxml")
                body = soup.find("body")
                title = soup.find_all( "title")
                storyTitle = title[0].string.strip()
                fileName = re.sub( r'[,.\'\(\)\-]' , '' , str(storyTitle) )
                fileName = fileName.lower().title()
                fileName = re.sub( '\s+' , '' , fileName )
                print(f"{ storyTitle }: { target }")

                fullText = body.get_text()
                fullText = re.sub( 'E.A. Poe' , 'Edgar Allan Poe' , fullText)
                fullText = fullText.strip()

                flag = 0
                lines = re.split( r'\n' , fullText )
                fullText = ''
                for line in lines:

                    if re.search( r'(<!\-\-)|(\/\/\-\->)|(google_)' , line ):
                        line = ''

                    if re.search( r'^{}$'.format(storyTitle) , line.strip() , re.IGNORECASE ):
                        flag = 1
                    if re.search( r'Last modified' , line.strip() ):
                        flag = 0
                    if flag == 1 and len(line) > 0:
                        fullText += line + ' \n'
                fullText = fullText[ fullText.index(storyTitle) + len(storyTitle) : ]

                out = open( join( 'Corpus' , fileName ) + '.txt' , 'w' , encoding = 'utf-8' )
                out.write( fullText.strip() )
                out.close()
