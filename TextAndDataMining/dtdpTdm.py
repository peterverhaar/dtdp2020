
import string
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import xml.etree.ElementTree as ET
import requests
import zipfile
import math
import os
from os.path import isfile, join , isdir
import string

lines = list()
taggedLines = list()
lemmatisedLines = list()
currentFile = ''


freqText = dict()

sentiments = dict()

def initalise():
    lines.clear()
    taggedLines.clear()
    lemmatisedLines.clear()


def readFile( file ):

    global lines
    global currentFile

    currentFile = file

    initalise()

    if re.search( r'\.txt$' , file ):
        try:
            text = open( file , encoding = 'utf-8' , errors = 'ignore' )

            for line in text:
                lines.append(line)
        except:
            print( "Cannot read " + file + " !" )


def sortedByValue( dict ):
    return sorted( dict , key=lambda x: dict[x])


def concordance( file , searchTerm , window ):

    global lines
    global currentFile

    if file != currentFile:
        readFile(file)

    concordance = []
    regex = searchTerm

    for line in lines:
        line = line.strip()

        if re.search( regex , line , re.IGNORECASE ):

            extract = ''

            position = re.search( regex , line , re.IGNORECASE ).start()
            start = position - len( searchTerm ) - window ;
            fragmentLength = start + 2 * window  + len( searchTerm )
            if fragmentLength > len( line ):
                fragmentLength = len( line )

            if start < 0:

                whiteSpace = ''
                i = 0
                while i < abs(start):
                    whiteSpace += ' '
                    i += 1
                extract = whiteSpace + line[ 0 : fragmentLength ]
            else:
                extract = line[ start : fragmentLength ]

            if re.search( '\w' , extract ) and re.search( regex , extract ):
                concordance.append( extract )
    return concordance



def divideIntoSegments( file , numberOfSegments ):

    segments = []

    textFile = open( file , encoding = 'utf-8' , errors = 'ignore' )

    ## The read() function can read in the entire file as a single string
    fullText = textFile.read()
    allWords = re.split( r'\s+' , fullText )

    segmentSize = int( len(allWords) / numberOfSegments )

    countWords = 0
    text = ''

    for word in allWords:
        countWords += 1
        text += word + ' '

        ## This line below used the modulo operator:
        ## We can use it to test if the first number is
        ## divisible by the second number
        if countWords % segmentSize == 0:
            segments.append(text.strip())
            text = ''
    return segments


def getTitle( fileName ):
    fileName = os.path.basename(fileName)
    title = re.sub( r'[.]txt$' , '' , fileName )
    return title


def collocation( file , regex , distance ):

    global lines
    global currentFile

    if file != currentFile:
        readFile(file)


    freq = dict()

    paragraph = ''

    parLength = 0

    for line in lines:
        line = line.strip()
        if parLength < 100:
            parLength += len(line)
            paragraph += line + ' '
        else:
            parLength = 0
            words = tokenise( paragraph )
            i = 0
            for w in words:
                if re.search( regex , w , re.IGNORECASE ):

                    match = re.search( regex , w , re.IGNORECASE )
                    searchTerm = match.group(0)

                    for x in range( i - distance , i + distance ):
                        if x >= 0 and x < len(words) and searchTerm != words[x]:
                            if len(words[x]) > 0:
                                freq[ words[x] ] = freq.get( words[x] , 0 ) + 1

                i += 1
            paragraph = ''


    sortedWords = reversed( sorted( freq , key=lambda x: freq[x]) )
    sortedFreq = dict()

    for w in sortedWords:
        sortedFreq[w] = freq[w]

    return sortedFreq


def numberOfSentences(file):
    fullText = open( file , encoding = 'utf-8' )
    s = sent_tokenize(fullText.read())
    return len(s)

def averageSentenceLength(file):
    sentences = numberOfSentences(file)
    return numberOfTokens(file) / sentences


# function to tokenise a string into words
def tokenise2( text ):
    tokens = []
    text = text.lower()
    text = re.sub( '--' , ' -- ' , text)
    text = re.sub( '-' , ' - ' , text)
    words = re.split( r'\s+' , text )
    for w in words:
        w = w.strip( string.punctuation )
        if re.search( r"[a-zA-Z]" , w ):
            tokens.append(w)
    return tokens

def tokenise( text ):
    return word_tokenize( text )


def averageNumberOfSyllables(file):

    global lines
    global currentFile

    if file != currentFile:
        readFile(file)

    fullText = ''
    for line in lines:
        fullText += line + ' '

    nrSyllables = 0
    words = word_tokenize(fullText)
    for w in words:
        syll = countSyllables(w)
        if syll > 1:
            nrSyllables += countSyllables(w)
        elif( re.search( r'\w' , w ) ):
            nrSyllables += 1
    return ( nrSyllables / len(words))


def countSyllables( word ):
    pattern = "e?[aiou]+e*|e(?!d$|ly).|[td]ed|le$|ble$|a$"
    syllables = re.findall( pattern , word )
    return len(syllables)

def fleschKincaid( file ):

    global lines
    global currentFile

    if file != currentFile:
        readFile(file)

    fk = 0.39 * (  averageSentenceLength(file) )
    fk = fk + 11.8 * ( averageNumberOfSyllables(file) )
    fk = fk - 15.59
    return fk


def calculateWordFrequencies( file ):

    global lines
    global currentFile

    if file != currentFile:
        readFile(file)

    freq = dict()

    for line in lines:
        words = tokenise( line )
        for w in words:
            freq[w] = freq.get( w , 0 ) + 1

    return freq

def mostFrequentWords( file , maxNrWords ):

    freq = calculateWordFrequencies( file )
    freq = removeStopWords( freq )

    sortedWords = reversed( sorted( freq , key=lambda x: freq[x]) )
    mostFreq = dict()

    count = 0
    for w in sortedWords:
        mostFreq[w] = freq[w]
        count += 1
        if count == maxNrWords:
            break

    return mostFreq


def removeStopWords( freq ):

    filtered = dict()
    stopWords = set(stopwords.words('english'))

    for w in freq:
            if w not in stopWords:
                filtered[w] = freq[w]

    return filtered


def countOccurrences( regex , file ):

    global lines
    global currentFile
    count = 0

    if file != currentFile:
        readFile(file)

    for l in lines:
        if re.search( regex , l , re.IGNORECASE ):
            count += 1
    return count


def numberOfTypes( file ):

    global lines
    global currentFile

    if file != currentFile:
        readFile(file)

    nrTypes = 0
    freq = calculateWordFrequencies( file )
    nrTypes =  len(freq)
    return ( nrTypes )


def typeTokenRatio( file , cap ):

    global lines
    global currentFile

    if file != currentFile:
        readFile(file)

    fullText = ''
    for line in lines:
        fullText += line

    words = word_tokenize(fullText)
    words = words[ 0 : cap ]
    unique = dict()
    for w in words:
        unique[w] = 'temp'
    return len(unique) / len(words)


def typeTokenRatio2( file , cap ):

    global lines
    global currentFile

    if file != currentFile:
        readFile(file)
    fullText = ''
    for line in lines:
        fullText += line
        if len(fullText) > cap:
            break

    fullText = fullText[ 0 : cap ]
    types = set( tokenise(fullText) )
    return len(types) / cap


def typeTokenRatioCurve( file , step ):

    text = open( file , encoding = 'utf-8' , errors = 'ignore' )
    fullText = text.read()
    allWords = tokenise( fullText )

    ttr = dict()

    count = 0
    freq = dict()

    for w in allWords:
        count += 1
        freq[w] = freq.get( w ,0 ) + 1
        if count % step == 0:
            ttr[ count ] = len(freq)
    return ttr

def numberOfTokens(  file ):

    global lines
    global currentFile

    if file != currentFile:
        readFile(file)

    fullText = ''
    for line in lines:
        fullText += line + ' '

    words = word_tokenize(fullText)
    return len(words)


def tdIdf( corpus , file ):

    global freqText
    file = os.path.basename( file )

    freq = dict()


    txt = []

    ## Formula is as follows: tf-idf= log⁡(⁡ N /df ),
    # tf being the number of times a term appears in a document,
    # N being the total number of documents
    # df being the number of documents in which the term appears.

    if len( freqText ) == 0:

        fnames = os.listdir( corpus )
        for i in fnames:
            if re.search( '[.]txt$' , i):
                txt.append( i )

        ## N is total number of texts
        N = len(txt)

        for t in txt:
            textWords = []
            text = open( join( corpus , t ) , encoding = 'utf-8' )

            for line in text:
                words = tokenise( line )
                for w in words:
                    freq[w] = freq.get( w , 0 ) + 1
                    freqText[ (t , w ) ] = freq.get( (t , w ) , 0 ) + 1


        idf = dict()
        ## df is number of texts in which the term appears

        for word in freq:
            df = 0

            for text in txt:
                if ( text , word ) in freqText:
                    df += 1

            idfW = math.log( N / df )
            idf[ word ] = idfW

            for text in txt:
                if ( text , word ) in freqText:
                    freqText[ ( text , word ) ] = 1 + freqText[ ( text , word ) ] * idf[ word ]

        print( 'Done: Calculations made.' )


    freqIdf = dict()
    allWords = dict()

    for w in freqText:
        print(freqText[w][1])
        allWords.append( freqText[w][1] )

    for w in allWords:
        if( file , w ) in freqText:
            freqIdf[w] = freqText[ ( file , w ) ]
            i += 1
            if i == max:
                break

    return freqIdf


from nltk.corpus import wordnet

def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return ''


def lemmatiser( file ):

    global lines
    global lemmatisedLines

    global currentFile
    if file != currentFile:
        readFile(file)

    print("Lemmatising {} ...".format(file)  )
    lemmatiser = WordNetLemmatizer()

    for line in lines:

        lemmas = ''
        words = word_tokenize(line)
        pos = nltk.pos_tag(words)

        for i in range( 0 , len(words) ):
            if re.search( r'^[JVNR]', pos[i][1] , re.IGNORECASE ):
                lemmas += lemmatiser.lemmatize( words[i] , get_wordnet_pos(pos[i][1]) )
                lemmas += ' '

        lemmatisedLines.append( lemmas )




def posTagger( file ):

    global lines
    global taggedLines

    global currentFile
    if file != currentFile:
        readFile(file)

    print("Adding POS tags for {} ...".format(file)  )

    for line in lines:
        taggedLine = ''
        words = word_tokenize(line)
        pos = nltk.pos_tag(words)

        for p in pos:
            taggedLine += p[0] + '/' + p[1] + ' '
        taggedLines.append( taggedLine )



def countPosTags( text , tagList ):
    tokens = showPosTags( text , tagList )
    return len( tokens )


def showPosTags( file , tagList ):

    tokens = []

    global taggedLines
    global currentFile

    tagList = [each_tag.lower() for each_tag in tagList]

    if file != currentFile:
        readFile(file)
        taggedLines.clear()

    if len(taggedLines) == 0:
        posTagger( file )

    for line in taggedLines:
        #print(line)
        words = tokenise(line.lower())
        for w in words:
            #print(w)
            if re.search( '/' , w ):
                token = w[ 0 : w.index('/') ]
                tag = w[ w.index('/')+1 : len(w)  ]
                if tag in tagList:
                    tokens.append( token )

    return tokens



def countOccurrencesLexicon( file , lexiconFile ):

    global lines
    global currentFile
    global lemmatisedLines

    if file != currentFile:
        readFile(file)
        lemmatisedLines.clear()

    if len(lemmatisedLines) == 0:
        lemmatiser( file )

    countOccurrences = 0
    lexicon = open( lexiconFile , encoding = 'utf-8')

    listOfWords = []
    for line in lexicon:
        line = line.strip()
        listOfWords.append(line.lower() )

    for line in lemmatisedLines:
        words = tokenise(line)
        for w in words:
            if w in listOfWords:
                countOccurrences += 1

    return countOccurrences



def tdIdf( corpus , focusText ):

    ## freqText is a dictionary with frequencies of all Words in the corpus
    global freqText

    freq = dict()

    #list to kep track of all the texts in the corpus
    txt = []

    ## Formula is as follows: tf-idf= tf * log⁡(⁡ N /df ),
    # tf being the number of times a term appears in a document,
    # N being the total number of documents
    # df being the number of documents in which the term appears.

    if len( freqText ) == 0:

        fnames = os.listdir( corpus )
        for i in fnames:
            if re.search( '[.]txt$' , i):
                txt.append( i )

        ## N is total number of texts
        N = len(txt)

        if focusText not in txt:
            print("The file you mentioned is not in the corpus!")

        for t in txt:
            textWords = []
            text = open( join( corpus , t ) , encoding = 'utf-8' )

            for line in text:
                words = tokenise( line )
                for w in words:
                    freq[w] = freq.get( w , 0 ) + 1
                    freqText[ (t , w ) ] = freq.get( (t , w ) , 0 ) + 1


        idf = dict()
        ## df is number of texts in which the term appears

        for word in freq:
            df = 0

            for text in txt:
                if ( text , word ) in freqText:
                    df += 1

            idfW = math.log( N / df )
            idf[ word ] = idfW

            for text in txt:
                if ( text , word ) in freqText:
                    freqText[ ( text , word ) ] = freqText[ ( text , word ) ] * idf[ word ]

        print( 'Done: Calculations made.' )


    freqIdf = dict()
    allWords = []


    for w in freqText:
        allWords.append(w[1])

    for w in allWords:

        if ( focusText , w ) in freqText:
            if freqText[ ( focusText , w ) ] > 0 and not( re.search( '[-]' , w ) ):
                freqIdf[w] = freqText[ ( focusText , w ) ]


    return freqIdf
