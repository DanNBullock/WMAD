# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 11:38:00 2021

@author: Daniel
"""
def decodeGoogleHighlight(inputURL):
    from urllib.parse import unquote
    import re
    #specify url stem
    highlightTag='#:~:text='
    #create regex phrase using stem
    searchPhrase='(?<='+highlightTag+').*$'
    #compile regex search phrase
    prog = re.compile(searchPhrase)
    #search the url for the 
    regexComponents = prog.search(inputURL).group(0)
    if (',') in regexComponents:
        regexComponents=regexComponents.split(',')
        regexComponents[0]=unquote(regexComponents[0])
        regexComponents[1]=unquote(regexComponents[1])
    else:
        regexComponents=unquote(regexComponents)
    return(regexComponents)

def extractGoogleHighlightLinkText(inputURL):
    from bs4 import BeautifulSoup
    import requests
    import re
    #use requests to get html data
    page = requests.get(inputURL)
    #use the decode function to extract the regex components
    regexComponents=decodeGoogleHighlight(inputURL)
    #if there are two outputs then they are to be interpreted as bounds
    regexResult=[]
    if type(regexComponents)==list:
        #get the soup output
        soup = BeautifulSoup(page.content, "html.parser")
        #interpret it ina comprehensible fashion
        articleText = ''.join(soup.findAll(text=True))
        #create a regex search string for the bounds and whatis between them
        searchFormation=re.escape(regexComponents[0])+'.+?'+re.escape(regexComponents[1])
        #compile the search string
        prog = re.compile(searchFormation)
        #perform the search and extract the match result; could possibly be empty
        if prog.search(articleText) is None:
            regexResult ='Regex search failed to return match;\nPossible redirect issue, check host publisher\'s website'
        else:
            regexResult = prog.search(articleText).group(0)
    elif type(regexComponents)==str:
        #if it's only one item long, its simply a text string, ...
        #no comma separating it, not to be interpreted as bounds
        regexResult=regexComponents
    return regexResult

def queryImage(imageURL):
    from PIL import Image
    import requests
    import io
    #extract figure links for current tract
    
    returnedImg = requests.get(imageURL, stream=True)
    if returnedImg.status_code == 200:
        imgOut = Image.open(io.BytesIO(returnedImg.content))
    elif returnedImg.status_code == 403:
        imgOut=None
        print('403 request error: forbidden by host')
    return imgOut