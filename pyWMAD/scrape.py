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


def parseAllQueries(WMAnatDB,textQueriesList,forceProduce=False):
    """
    

    Parameters
    ----------
    WMAnatDB : TYPE
        WMAnatDB, as produced by json.load(json_data)
    textQueriesList : list, strings
        DESCRIPTION.
    forceProduce : Bool, optional
        Forces the function to produce records for entries that are not in the
        pub med database.  This may cause issues in the case that this function is being used
        on binder, or if the journals become angry with being pinged so many times. The default is False.

    Returns
    -------
    textExerptsOut=a pandas array with the relevant text exerpts

    """
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    import re
    import numpy as np
    from urllib.parse import unquote
    
    queriesStemList=[]
    queriesCleaned=[]
    #specify the google query stem for doing a highlight of text
    highlightTag='#:~:text='
    #iQueries='https://www.sciencedirect.com/science/article/pii/S0006899316304085?casa_token=g_fm9d1i4bgAAAAA:ecM--Go8sXr9LJ8BQSTmhX6ivyQoT4Wr_-UxLcEzC3wsNJmLYvvYnwRbnKw-kZHNo5vICcJ7dtw#:~:text=The%20VOF%20was%20identified,the%20superior%20occipital%20lobe.'
    for iQueries in textQueriesList:
        #split url from query separator
        splitComponents=iQueries.split('?')
        #if the split did nothing, that's because the ? isn't there, but the highlightTag still is
        if len(splitComponents)==1:
            queriesStemList.append(splitComponents[0].split(highlightTag)[0])
            currentQuery=splitComponents[0].split(highlightTag)[1]
        else:
            queriesStemList.append(splitComponents[0].split(highlightTag)[0])
            currentQuery=splitComponents[1].split(highlightTag)[1]
        #set the url as the stem
        #queriesStemList.append(splitComponents[0])
        #split out any extraneous token stuff from the query itself
        #queryAndOther=iQueries.split(highlightTag)
        #currentQuery=queryAndOther[1]
        #compose the url component into corresponding regex query component(s)
        if ',' in currentQuery:
            regexComponents=currentQuery.split(',')
            regexComponents[0]=unquote(regexComponents[0])
            regexComponents[1]=unquote(regexComponents[1])
        else:
            regexComponents=unquote(currentQuery)
        queriesCleaned.append(regexComponents)
    
    #find the unique articles
    uniqueArticleURLs=np.unique(queriesStemList)
    
    #generate the url correspondances of the dois
    doi_url_correspondance=pd.DataFrame(columns=['doi', 'url'] )
    for iDocs in list(WMAnatDB.keys()):
        currentDoi=WMAnatDB[iDocs]['doi']
        #get rid of unnecessary components
        currentDoi=currentDoi.replace('https://doi.org/','')
        #or if the https has been removed
        currentDoi=currentDoi.replace('doi.org/','')   
        #use a while loop and a counter to find the first tract description entry that isn't empty
        #and do the same split procedure as above
        currentURL=[]
        tractsChecked=0
        while not currentURL:
            #if there's something there, truth value of 
            if WMAnatDB[iDocs]['tractDepictions'][list(WMAnatDB[iDocs]['tractDepictions'].keys())[tractsChecked]]['descriptions']:
                urlSplit=WMAnatDB[iDocs]['tractDepictions'][list(WMAnatDB[iDocs]['tractDepictions'].keys())[tractsChecked]]['descriptions']['1'].split('?')
                querySplit=urlSplit[0].split(highlightTag)
                currentURL=querySplit[0]
            
            #if you've checked all of the available entries, just set the url to None
            elif tractsChecked+1==len(WMAnatDB[iDocs]['tractDepictions']):
                currentURL=[None] 
            else:
                tractsChecked=tractsChecked+1
        #checking 

        #add them to the dataframe
        doi_url_correspondance.loc[len(doi_url_correspondance.index)] = [currentDoi, currentURL]
    
    #get the list of dois as they ordered in the WMAanatDB
    allDOIs=[WMAnatDB[iArticles]['doi'] for iArticles in list(WMAnatDB.keys())]

    #we check to see if it is available on pub med
    pmcID=[]
    for iQueryArticles in uniqueArticleURLs:
        #first we check to see if it is in the pub med database
        currentDoi=doi_url_correspondance['doi'][doi_url_correspondance['url']==iQueryArticles]
        #could probably do the conversion back that was done earlier, but whatever
        currentKey=list(WMAnatDB.keys())[np.where([currentDoi==iDOI for iDOI in allDOIs])[0][0]]
        #append the current pmc id to the list if it exists 
        pmcID.append(WMAnatDB[currentKey]['pmcid'])
        
    #setting some things in case we use the pmc database
    #set my email
    danEmail='bullo092@umn.edu'
    #the name of our tool here
    toolID='WMAD'
    #the URL stem to the idConverter service
    efetchStemQuery='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='
    #the composition of the query itself
    queryString='?tool='+toolID+'&email='+danEmail+'&ids='+doi
    
    #begin cycling through the articles
    # we do it one at the time so as to not anger the journals    
    for iQueryArticles in range(len(uniqueArticleURLs)):
        #get the url
        currentArticleUrl=uniqueArticleURLs[iQueryArticles]
        #if it is available in pub med database get it from there
        if not pmcID[iQueryArticles]==None:
            #efetch stem
            
            page = requests.get(efetchStemQuery+pmcID[iQueryArticles])
            
        elif forceProduce:

            #use requests go get the article data
            page = requests.get(iQueryArticles)
            #status code 200 == ok
            if page.status_code==200:
                queryLocations=np.where( [iQueryArticles in iQueryStems for iQueryStems in queriesStemList])[0]
            #status code 403 == forbidden
            elif page.status_code==403:
                CLEANR = re.compile('<.*?>') 
        
                def cleanhtml(raw_html):
                  cleantext = re.sub(CLEANR, '', raw_html)
                  return cleantext
                        #status code 200 == ok
        
            #in the case that you're not forcing it, and it isn't in the pub med database
    else:
        #you'll be setting an output to say something like
        outString='article not available in pub med open data base \n set "forceProduce" option to True to force direct query of journal'
        
        
# as per recommendation from @freylis, compile once only

        
        
    

    
with open('/media/dan/storage/gitDir/WMAD/dbStore/WMAnatDB.json') as json_data:
    WMAnatDB = json.load(json_data)
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