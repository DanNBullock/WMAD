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


def parseAllTextQueries(WMAnatDB,textQueriesList,forceProduce=False):
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
    import xmltodict
    import itertools
    
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
    u, ind=np.unique(queriesStemList, return_index=True)
    uniqueArticleURLs= u[np.argsort(ind)]
   
    #create a mapping to these unique entries from the queries, as proxied by 
    #the entries in queriesStemList
    query_PageCorrespondances=np.zeros(len(queriesStemList)).astype(int)
    for iQueries in range(len(textQueriesList)):
        query_PageCorrespondances[iQueries]=np.where([queriesStemList[iQueries]==iUniquePages for  iUniquePages in uniqueArticleURLs])[0][0]
    
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
    #danEmail='bullo092@umn.edu'
    #the name of our tool here
    #toolID='WMAD'
    #the URL stem to the idConverter service
    efetchStemQuery='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='
    #the composition of the query itself
    #queryString='?tool='+toolID+'&email='+danEmail+'&ids='+doi
    #set the string that we'll search for to see if we've been fooled by pmc
    pmcPublisherXMLForbidString='The publisher of this article does not allow downloading of the full text in XML form.'
    #begin cycling through the articles
    # we do it one at the time so as to not anger the journals
    returnedTextExerpts=[None]*len(queriesCleaned )
    for iQueryArticles in range(len(uniqueArticleURLs)):
        #get the url
        #currentArticleUrl=uniqueArticleURLs[iQueryArticles]
        #
        #get the queries
        #I don't know why I have to do it this way, it was getting angry about 
        #"only integer scalar arrays can be converted to a scalar index" otherwie
        #currentQueries=[queriesCleaned[iQuery] for iQuery in range(queriesCleaned) if query_PageCorrespondances[iQuery]==iQueryArticles]
        #ok we'll do it the hard way
        currentQueries=[]
        for iQuery in range(len(queriesCleaned)):
            if query_PageCorrespondances[iQuery]==iQueryArticles:
                currentQueries.append(queriesCleaned[iQuery])
        queryIndexes= list(np.where(query_PageCorrespondances==iQueryArticles)[0])
        #if it is available in pub med database get it from there
        if not pmcID[iQueryArticles]==None:
            #query the PMC database to get the article (hopefully)
            page = requests.get(efetchStemQuery+pmcID[iQueryArticles])
            
            #if the querry as succesful
            if page.status_code==200:
                #check to see if the article is ACTUALLY there.  Very silly.  Why have it
                #in the database as an entry if it's not actually there,
                #just leave it as a standard PMD entry.  /{rant_over}
                pageContent=page.content.decode(page.encoding)
                #check to see if we've been tricked
                if pmcPublisherXMLForbidString in pageContent:
                    #we've been tricked!  Fill in the entries with the relevant boilerplate text
                    #I guess just use the sum as an iterator
                    for iQueries in range(np.sum(query_PageCorrespondances==iQueryArticles)):
                        returnedTextExerpts[queryIndexes[iQueries]]=pmcPublisherXMLForbidString
                else:
                    #iterate across the queries and use regex to find the sections
                    for iQueries in range(np.sum(query_PageCorrespondances==iQueryArticles)):
                        returnedTextExerpts[queryIndexes[iQueries]]=parseTextQueryFromRawText(page.content,currentQueries[iQueries])
            #in case something gose extra wrong        
            else:
                for iQueries in range(np.sum(query_PageCorrespondances==iQueryArticles)):
                    returnedTextExerpts[queryIndexes[iQueries]]='Pub Med querry failed'
                
        #if it isnt there OR IF it came back with the XML forbidden response
        if forceProduce:
            #do a check to see the entries for this index have already been added by the pub med section
            #and if they are the XML forbidden status
            #PMC_Check=len(returnedTextExerpts)==np.sum(query_PageCorrespondances>=iQueryArticles)
            PMC_XML_forbiddenFlag=np.any([ pmcPublisherXMLForbidString==iReturnedExerpts for iReturnedExerpts in list(itertools.compress(returnedTextExerpts, list(query_PageCorrespondances==iQueryArticles)))])
            if PMC_XML_forbiddenFlag:
                #locations to replace
                locationsToReplace=np.where(query_PageCorrespondances==iQueryArticles)[0]
                #use requests go get the article data
                page = requests.get(uniqueArticleURLs[iQueryArticles])
                #status code 200 == ok
                if page.status_code==200:
                    #iterate across the current quries
                    for iQueries in range(np.sum(query_PageCorrespondances==iQueryArticles)):
                        returnedTextExerpts[locationsToReplace[iQueries]]=parseTextQueryFromRawText(page.content,currentQueries[iQueries])
                    #status code 403 == forbidden
                elif page.status_code==403:
                    for iQueries in range(np.sum(query_PageCorrespondances==iQueryArticles)):
                        #here we might want to say that neither the PMC method nor the ping method worked
                        returnedTextExerpts[locationsToReplace[iQueries]]='PMC XML Forbidden and journal 403 forbidden'
                        #or maybe instead use the xml decode functionality of xmltodict
                        #errorResponse=xmltodict.parse(page.content)
                        #returnedTextExerpts[locationsToReplace[iQueries]]=errorResponse['html']['body']['#text']
                        #returnedTextExerpts.append(page.reason)
                elif page.status_code==503:
                     for iQueries in range(np.sum(query_PageCorrespondances==iQueryArticles)):
                         #or maybe instead use the xml decode functionality of xmltodict
                         #errorResponse=xmltodict.parse(page.reason)
                         #returnedTextExerpts.append(errorResponse['html']['body']['#text'])
                         returnedTextExerpts[queryIndexes[iQueries]]=page.reason
                        
            #in the normal case when there is no pub med entry and forceProduce is true
            else:
                #use requests go get the article data
                page = requests.get(uniqueArticleURLs[iQueryArticles])
                #status code 200 == ok
                if page.status_code==200:
                    #iterate across the current quries
                    for iQueries in range(np.sum(query_PageCorrespondances==iQueryArticles)):
                        returnedTextExerpts[queryIndexes[iQueries]]=parseTextQueryFromRawText(page.content,currentQueries[iQueries])
                    #status code 403 == forbidden
                elif page.status_code==403:
                    for iQueries in range(np.sum(query_PageCorrespondances==iQueryArticles)):
                        #or maybe instead use the xml decode functionality of xmltodict
                        #errorResponse=xmltodict.parse(page.reason)
                        #returnedTextExerpts.append(errorResponse['html']['body']['#text'])
                        returnedTextExerpts[queryIndexes[iQueries]]=page.reason
                elif page.status_code==503:
                     for iQueries in range(np.sum(query_PageCorrespondances==iQueryArticles)):
                         #or maybe instead use the xml decode functionality of xmltodict
                         #errorResponse=xmltodict.parse(page.reason)
                         #returnedTextExerpts.append(errorResponse['html']['body']['#text'])
                         returnedTextExerpts[queryIndexes[iQueries]]=page.reason
        #in the case that you're not forcing it, and it isn't in the pub med database
        #you're not getting anything
        else:
            #you'll be setting an output to say something like
            outString='article not available in pub med open data base \n set "forceProduce" option to True to force direct query of journal \n WARNING: This may result in the journal limiting access to you specifically or others more generally'
            for iQueries in range(np.sum(query_PageCorrespondances==iQueryArticles)):
                returnedTextExerpts[queryIndexes[iQueries]]=outString
                
    return returnedTextExerpts

        
        
    
def parseTextQueryFromRawText(sourceText,regexComponents):
    """
    

    Parameters
    ----------
    sourceText : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    from bs4 import BeautifulSoup
    import re

    
    
    if type(regexComponents)==list:
        #get the soup output
        soup = BeautifulSoup(sourceText, "html.parser")
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
    
#with open('/media/dan/storage/gitDir/WMAD/dbStore/WMAnatDB.json') as json_data:
#    WMAnatDB = json.load(json_data)
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
    else:
        imgOut=None
        print(str(returnedImg.status_code )+' request error')
    return imgOut