import numpy as np
import pandas as pd
from trendmaster import trend
import pickle
from statsmodels.tsa import stattools

varDict = input("Pickle dictionary filename (with .pkl extention):")
name = input("Variable name:")
period = input("Number of years in period:")

def openDict(filename):
    """
    Opens dictionary from pickle file in working directory.
    
    Parameters
    ----------
    filename: str
        filename with .pkl ending
    
    Returns
    -------
    dictionary
    """
    pickle_in = open(f"{filename}","rb")
    loadedDict = pickle.load(pickle_in)
    return loadedDict

final = openDict("finalSelectionList.pkl")

def reshapeToArray(data,MA,fullList):
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
    x = len(fullList)
    # array with shape: doy,year,catchment
    arr = np.full((len(doy),len(years),x),np.nan)
    
    if period == "30":
        # filling array
        for c in range(x):
            for y in years:
                for d in doy:
                    arr[d,y-start,c] = data[fullList[c]][MA][f"{y}"][d]
    
    if period == "50":
        # filling array
        for c in range(x):
            if fullList[c] in catchments:
                for y in years:
                    for d in doy:
                        arr[d,y-start,c] = data[fullList[c]][MA][f"{y}"][d]
            else:
                for y in years:
                    for d in doy:
                        arr[d,y-start,c] = -99
    return(arr)

def autocorrTest(ts,alpha=0.05):
    """
        Ljung-Box test for significant autocorrelation in a time series.
        """
    acf, qstat, p = stattools.acf(ts,qstat=True,nlags=1)
    p = p[0]
    sign = p < alpha
    return sign

def prewhiten(ts):
    """
        Pre-whitening procedure of a time series.
        
        After Wang&Swail, 2001:
        https://doi.org/10.1175/1520-0442(2001)014%3C2204:COEWHI%3E2.0.CO;2
        """
    r = stattools.acf(ts,nlags=1)[1]
    pw = ts.copy()
    for i in range(ts.shape[0]-1):
        if i > 0:
            pw[i] = (ts[i] - r*ts[i-1])/(1 - r)
    return pw

def trendMagnitude(array,alpha=0.1):
    """
        Calculated the trend magnitude for each doy if a significant trend is detected
        
        Parameters
        ----------
        array: numpy.array
        array of shape: (doy,year,catchment) containing data to be analysed
        
        Returns
        -------
        numpy.array
        array of trend magnitude, shape: (catchments,doy)
        """
    output = []
    for c in range(array.shape[2]):
        arr = array[:,:,c] # slicing array by catchment
        if (arr==-99).all():
            out = np.full(arr.shape[0],-99)
        else:
            out = np.full(arr.shape[0],np.nan) # create empty array
            for day in range(arr.shape[0]):
                ts = arr[day,:]
                if autocorrTest(ts):
                    ts = prewhiten(ts)
                p = trend.mann_kendall(ts) #calculate p-value
                if p < alpha: #calculate trend magnitude if significant trend is detected
                    out[day] = trend.sen_slope(ts)
        output.append(out)
    return np.array(output)

def trendArrays(varDict,variable=name,averages=["5day","10day","30day"]):
    """
    Calculates trend arrays and saves them to .npy file in "Results" folder.
    """
    for region in varDict.keys():
        print("-------------------------")
        print(f"Analysing region {region}.")
        for MA in averages:
            array = reshapeToArray(varDict[region],MA,final[region][30])
            result = trendMagnitude(array)
            np.save(f"Results/trendAnalysis_{variable}_{region}_{MA}_{period}years",result)
            print(f"\t{MA} completed.")
        print(f"Region {region} complete.")
    print("-------------------------")
    print("Trend analysis complete.")
    print("-------------------------")

df = openDict(varDict) #open dictionary with data from spesific varaible
trendArrays(df) #analyse trends for all regions
