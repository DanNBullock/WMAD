# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 12:05:01 2021

@author: Daniel
"""

def extractTractFigure(articleJSONData,tractIndex,figIndex):
    #articleJSONData: JSON formatted data for a single article, in the
    #standard format for articles
    #tractIndex: the index IN THIS JSON structure of the tract of interest
    #figIndex: the index IN THIS JSON IN THE SPECIFIED TRACT RECORD 
    #of the figure URL of interest
    
    # BEGIN CODE
    #throw errors if the requested indexes exceed available items
    if tractIndex>len(articleJSONData['tractDepictions']):
        raise ValueError('Requested tract index exceeds available tracts')
    if figIndex>len(articleJSONData['tractDepictions'][list(articleJSONData['tractDepictions'].keys())[tractIndex]]['figures']):
        raise ValueError('Requested figure index exceeds available figure records')
    
    #import packages for viewing
    from PIL import Image
    import requests

    #extract figure links for current tract
    figLinks=articleJSONData['tractDepictions'][list(articleJSONData['tractDepictions'].keys())[tractIndex]]['figures']
    imgOut = Image.open(requests.get(figLinks[str(figIndex)], stream=True).raw)
    return imgOut

def extractTractDescription(articleJSONData,tractIndex,descripIndex):
    #articleJSONData: JSON formatted data for a single article, in the
    #standard format for articles
    #tractIndex: the index IN THIS JSON structure of the tract of interest
    #figIndex: the index IN THIS JSON IN THE SPECIFIED TRACT RECORD 
    #of the figure URL of interest
    
    # BEGIN CODE
    #throw errors if the requested indexes exceed available items
    if tractIndex>len(articleJSONData['tractDepictions']):
        raise ValueError('Requested tract index exceeds available tracts')
    if descripIndex>len(articleJSONData['tractDepictions'][list(articleJSONData['tractDepictions'].keys())[tractIndex]]['descriptions']):
        raise ValueError('Requested figure index exceeds available figure records')
    
    #import packages parsing google links
    #NOTE MAKE SURE YOU ARE IN THE REPO DIRECTORY IN ORDER FOR THIS TO WORK
    from pyWMAD import scrape

    #extract figure links for current tract
    descripLinks=articleJSONData['tractDepictions'][list(articleJSONData['tractDepictions'].keys())[tractIndex]]['descriptions']
    textOut=scrape.extractGoogleHighlightLinkText(descripLinks[str(descripIndex)])
    return textOut