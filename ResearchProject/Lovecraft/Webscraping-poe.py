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
        label = str( l.string )
        if re.search( r', the$' , label , re.IGNORECASE ):
            label = 'The ' + label
            label = re.sub( r', the$' , '' , label )
        if re.search( r', a$' ,  label , re.IGNORECASE ):
            label = 'A ' + label
            label = re.sub( r', a$' , '' , label )

        label = re.sub( r'[,.\'\(\)\-]' , '' , str(label) )
        label = re.sub( '\s+' , '' , label )
        target = l.get("href")
        if not( re.search( r'^http' , target ) ):

            textUrl = baseUrl + target

            if re.search( '.' , textUrl ):
                print(f"{ target }: { label }")

                response = requests.get( textUrl )
                soup = BeautifulSoup( response.text ,"lxml")
                body = soup.find("body")
                title = soup.find_all( "title")
                storyTitle = title[0].string.strip()
                print(storyTitle)

                fullText = body.get_text()
                fullText = re.sub( 'E.A. Poe' , 'Edgar Allan Poe' , fullText)
                fullText = fullText.strip()
                fullText = fullText[ fullText.index( storyTitle ) + len(storyTitle) : ].strip()
                fullText = re.sub( r'Last modified.*$' , '' , fullText)

                out = open( join( 'Corpus' , label.lower() ) + '.txt' , 'w' , encoding = 'utf-8' )
                out.write( fullText.strip() )
                out.close()
