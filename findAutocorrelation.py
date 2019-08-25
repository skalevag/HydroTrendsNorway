"""
Script to find autocorrelated time series

Amalie Skålevåg
02.07.2019
"""

# moduel
import numpy as np
import pandas as pd
import datetime
import pickle
from statsmodels.tsa import stattools

def saveDict(dictionary,filename):
    """
        Saves dictionary to pickle file in working directory.
        
        Parameters
        ----------
        dictionary: dict
        filename: str
        filename without .pkl ending
        
        Returns
        -------
        Nothing
        """
    f = open(f"{filename}.pkl","wb")
    pickle.dump(dictionary,f)
    f.close()

def openDict(filename):
    """
        Opens dictionary from pickle file in working directory.
        
        Parameters
        ----------
        filename: str
        filename without .pkl ending
        
        Returns
        -------
        dictionary
        """
    pickle_in = open(f"{filename}.pkl","rb")
    loadedDict = pickle.load(pickle_in)
    return loadedDict

def reshapeToArray(data,MA,period=30):
    """
        Reshapes moving average smoothed data from dictionary to array.
        
        Parameters
        ----------
        data: dictionary
        for a certain region, containing 30 year timeseries for different moving averages
        MA: str
        {"5day","10day","30day"}
        
        Returns
        -------
        numpy.array
        array of shape (doy,year,catchment) with the catchments ordered by altitude
        """
    doy = np.arange(365)
    start = 2013-int(period)
    years = np.arange(start,2013)
    catchments = list(data.keys())
    x = len(catchments)
    # array with shape: doy,year,catchment
    arr = np.full((len(doy),len(years),x),np.nan)
    # filling array
    for c in range(x):
        for y in years:
            for d in doy:
                arr[d,y-start,c] = data[catchments[c]][MA][f"{y}"][d]
    return(arr)

def autocorrTest(ts,alpha=0.05):
    acf, qstat, p = stattools.acf(ts,qstat=True,nlags=1)
    ac = acf[1]
    p = p[0]
    sign = p < alpha
    return sign

def makeAutoCorrArray(array):
    acArray = []
    for catch in range(array.shape[2]):
        c = array[:,:,catch]
        autoc = np.full(c.shape[0],99)
        for i in range(c.shape[0]):
            ts = c[i,:]
            autoc[i] = autocorrTest(ts)
        acArray.append(autoc)
    autoCorrArray = np.array(acArray)
    return autoCorrArray

def getAClocation(array):
    autoCorrArray=makeAutoCorrArray(array)
    catch = np.where(autoCorrArray==1)[0]
    doy = np.where(autoCorrArray==1)[1]
    return doy,catch


varDict = input("Variable .pkl file without extention:")
variable, years = varDict.split("_")[1:]
data = openDict(varDict)

averages = ["5day","10day","30day"]
regions = ["ost","vest","sor","trond","nord","finn"]

output = {}
for region in regions:
    output[region] = {}
    for MA in averages:
        array = reshapeToArray(data[region],MA)
        output[region][MA] = getAClocation(array)

filename = f"autoCorr_{variable}_{years}"
saveDict(output,filename)
