# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 12:05:01 2021

@author: Daniel
"""

def extractTractFigureDB(articleIndex, tractIndex, figIndex):
    #articleIndex: the index IN THIS JSON structure of the article of interest
    #tractIndex: the index IN THIS JSON structure of the tract of interest
    #figIndex: the index IN THIS JSON IN THE SPECIFIED TRACT RECORD 
    #of the figure URL of interest
    #NOTE:  assumes you are in root directory of WMAD repository
    
    # BEGIN CODE
    #load the DB
    import json
    import os
    with open(os.path.join('dbStore','WMAnatDB.json')) as json_data:
        DBJSONData = json.load(json_data)
    
    #throw errors if the requested indexes exceed available items
    if tractIndex>len(DBJSONData[list(DBJSONData.keys())[articleIndex]]['tractDepictions']):
        raise ValueError('Requested tract index exceeds available tracts')
    if figIndex>len(DBJSONData[list(DBJSONData.keys())[articleIndex]]['tractDepictions'][list(DBJSONData[list(DBJSONData.keys())[articleIndex]]['tractDepictions'].keys())[tractIndex]]['figures']):
        raise ValueError('Requested figure index exceeds available figure records')
    
    #import packages for viewing
    from PIL import Image
    import requests
    import io
    #extract figure links for current tract
    figLinks=DBJSONData[list(DBJSONData.keys())[articleIndex]]['tractDepictions'][list(DBJSONData[list(DBJSONData.keys())[articleIndex]]['tractDepictions'].keys())[tractIndex]]['figures']
    returnedImg = requests.get(figLinks[str(figIndex)], stream=True)
    imgOut = Image.open(io.BytesIO(returnedImg.content))
    
    #imgOut = Image.open(requests.get(figLinks[str(figIndex)], stream=True).raw)
    return imgOut

def extractTractDescriptionDB(articleIndex, tractIndex,descripIndex):
    #articleIndex: the index IN THIS JSON structure of the article of interest
    #tractIndex: the index IN THIS JSON structure of the tract of interest
    #figIndex: the index IN THIS JSON IN THE SPECIFIED TRACT RECORD 
    #of the figure URL of interest
    #NOTE:  assumes you are in root directory of WMAD repository
    
    # BEGIN CODE
    import json
    import os
    with open(os.path.join('dbStore','WMAnatDB.json')) as json_data:
        DBJSONData = json.load(json_data)
    
    #throw errors if the requested indexes exceed available items
    if tractIndex>len(DBJSONData[list(DBJSONData.keys())[articleIndex]]['tractDepictions']):
       raise ValueError('Requested tract index exceeds available tracts')
    if descripIndex>len(DBJSONData[list(DBJSONData.keys())[articleIndex]]['tractDepictions'][list(DBJSONData[list(DBJSONData.keys())[articleIndex]]['tractDepictions'].keys())[tractIndex]]['descriptions']):
       raise ValueError('Requested figure index exceeds available figure records')
 
    #import packages parsing google links
    #NOTE MAKE SURE YOU ARE IN THE REPO DIRECTORY IN ORDER FOR THIS TO WORK
    from pyWMAD import scrape

    #extract figure links for current tract
    descripLinks=DBJSONData[list(DBJSONData.keys())[articleIndex]]['tractDepictions'][list(DBJSONData[list(DBJSONData.keys())[articleIndex]]['tractDepictions'].keys())[tractIndex]]['descriptions']
    textOut=scrape.extractGoogleHighlightLinkText(descripLinks[str(descripIndex)])
    return textOut