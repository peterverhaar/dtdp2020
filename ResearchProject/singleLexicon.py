
import dtdpTdm as tdm
import os
from os.path import join
import requests
import re

csv = open( 'lexicon.csv' , 'w' , encoding = 'utf-8' )

## print header
csv.write( 'title,occurrences' )
csv.write('\n')

dir = 'Corpus'
lexicon = 'Religion.txt'


for file in os.listdir( dir ):
    if re.search( r'\.txt$' , file ):
        print( 'Performing semantic tagging for {} ...'.format( file ) )
        csv.write( tdm.getTitle( file ) )
        path = join( dir, file )
        tokens = tdm.numberOfTokens(path)
        count = tdm.countOccurrencesLexicon( path , lexicon )
        csv.write( ',{}'.format( count / tokens ) )
        csv.write('\n')

csv.close()

print("Done!")
