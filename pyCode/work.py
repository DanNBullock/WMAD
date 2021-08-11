# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 13:58:56 2021

@author: Daniel
"""

pathToDocExcelFile='D:\Documents\gitDir\WMAD\CompleteExample\doc1\doc.xlsx'
def excelDoc2JSON
    import pandas
    import json
    from habanero import Crossref
    
    #read excel file
    docExcelData=pandas.read_excel(pathToDocExcelFile, header=None,index_col=0)
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
    subsetDict={k: crossRefMetaData[k] for k in ('title','author','published', 'container-title','publisher', 'license')}
    
    #update the initial dict with the new data
    initialDict.update(subsetDict)
    
    #convert/read to json and output
    metadataJSON=json.dumps(initialDict)
    return metadataJSON

    

