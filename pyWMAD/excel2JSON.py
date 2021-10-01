# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 13:58:56 2021

@author: Daniel
"""

pathToDocExcelFile='D:\Documents\gitDir\WMAD\CompleteExample\doc1\doc.xlsx'
docDir='D:\Documents\gitDir\WMAD\CompleteExample\doc1\\'

def excelDoc2JSON(docExcelPath):
    import pandas
    import json
    from habanero import Crossref
    
    #read excel file
    docExcelData=pandas.read_excel(docExcelPath, header=None,index_col=0)
    #extract doi from the pandas array
    currentDOI=docExcelData.loc['doi',docExcelData.loc['doi'].notnull()].values[0]
    
    #create subset dataframe and convert to JSON
    #extract relevant columns
    subsetDataframe=pandas.DataFrame(docExcelData.loc[['curator','doi', 'species', 'methods']])
    #convert to json
    #NOTE: Currently can't distinguish between "index" and "columns" method
    #initialJSON=subsetDataframe.apply(lambda x: [x.dropna()], axis=1).to_json(orient="index")
    initialDict=subsetDataframe.to_dict(orient="index")
    #ugly method for cleaning null values, but it works                     
    for k in list(initialDict.keys()):
        for j in list(initialDict[k].keys()):
            if pandas.isnull(initialDict[k][j]):
                del initialDict[k][j]
                
    #use doi to get metadata
    cr = Crossref()
    cr.works()
    crossRefQueryOut=cr.works(ids = currentDOI)
    crossRefMetaData=crossRefQueryOut['message']
    
    #extract relevant dictionary entries
    #need to make robust against unavailable entries
    soughtEntries=['title','author','published', 'container-title','publisher', 'license']
    subsetDict={}
    for iSoughtEntries in soughtEntries:
        if iSoughtEntries in crossRefMetaData:
            subsetDict[iSoughtEntries]=crossRefMetaData[iSoughtEntries]
        else:
            subsetDict[iSoughtEntries]='unknown'
    
    #update the initial dict with the new data
    initialDict.update(subsetDict)
    
    #convert/read to json and output
    metadataJSON=json.dumps(initialDict)
    return metadataJSON

def mergeTracts2JSON(docDir):
    import json
    import pandas
    import os
    dirContents=os.listdir(docDir)
    #use regex to find valid files, should ignore ~ cases
    import re
    r = re.compile("^tract")
    validFiles = list(filter(r.match, dirContents))
    
    tractDict={}
    for iTracts in validFiles:
        #parse path to current tract excel record
        currentExcelPath=os.path.join(docDir,iTracts)
        #read data in
        tractExcelData=pandas.read_excel(currentExcelPath, header=None,index_col=0)
        #convert to dict
        initialTractDict=tractExcelData.to_dict(orient="index")
        #ugly method for cleaning null values, but it works                     
        for k in list(initialTractDict.keys()):
            for j in list(initialTractDict[k].keys()):
                if pandas.isnull(initialTractDict[k][j]):
                    del initialTractDict[k][j]
        
        tractDict[iTracts.replace('.xlsx','')]=initialTractDict
        
    outDict={}
    outDict['tractDepictions']=tractDict
    tractsJSON=json.dumps(outDict, indent=4)
    return tractsJSON
        
def convertDocExcelDir2JSON(docDir):
    import os
    import json
    #generate JSON strings for both the doc and the tracts discussed
    docJSON=excelDoc2JSON(os.path.join(docDir,'doc.xlsx'))
    tractsJSON=mergeTracts2JSON(docDir)

    #convert to dict structures and merge
    docDict = json.loads(docJSON)
    tractsDict = json.loads(tractsJSON)
    docDict.update(tractsDict)

    #JSON string of merged dict objects
    docRecordJSON = json.dumps(docDict, indent=4)
    return docRecordJSON

def processDocDir(docDir):
    
    outJSON=convertDocExcelDir2JSON(docDir)
    import os
    outPath= os.path.join(docDir,'doc.json')
    text_file = open(outPath, "w")
    text_file.write(outJSON)
    text_file.close()
    
def createOmibusJSON():
    import glob
    targetJSONS = glob.glob('completedArticles'+ "/**/doc.json", recursive = True)
    import json
    #create blank output object
    WMAnatDB={}
    for iArticleJSONs in targetJSONS:
        with open(iArticleJSONs) as json_data:
            currentArticleData = json.load(json_data)
        #get doi in order to create viable dict entry listings
        currentDOi=currentArticleData['doi']['1']
        #replace slashes with underscores
        recordTitle=currentDOi.replace('/','_')
        #replace slashes with underscores
        recordTitle=recordTitle.replace('.','-')
        WMAnatDB[recordTitle]=currentArticleData
    
    #now save it down
    WMAnatDBJSON = json.dumps(WMAnatDB, indent=4)
    import os
    text_file = open(os.path.join('dbStore','WMAnatDB.json'), "w")
    text_file.write(WMAnatDBJSON)
    text_file.close()

def convertDOI2pubMed(doi):
    #my email adress
    danEmail='bullo092@umn.edu'
    #the name of our tool here
    toolID='WMAD'
    #the URL stem to the idConverter service
    convertStem='https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/'
    #the composition of the query itself
    queryString='?tool='+toolID+'&email='+danEmail+'&ids='+doi
    #the full url
    fullURL=convertStem+queryString
    import requests
    
    
    ?tool=my_tool&email=my_email@example.com&ids=23193287
from bs4 import BeautifulSoup
import requests
import re 

testDoi='10.1007/s00429-019-01907-8'   