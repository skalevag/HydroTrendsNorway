import numpy as np
import pandas as pd
import pickle

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

file = input("Pickle file without extention:")
var = input("Variable:")
years = input("Number of years in period:")
years = int(years)
MA = input("If you wish to reshape only one MA please type the number of days, e.g. '5day', else press enter:")
if MA == "":
    averages = ["5day","10day","30day"]
else:
    averages = [MA]

data = openDict(file)


for region in data.keys():
    print(f"\nAnalysing {region}:")
    for MA in averages:
        array = reshapeToArray(data[region],MA,period=years)
        np.save(f"Reshaped/{var}_{region}_{MA}_{years}year",array)
        print(f"{MA} finshed.")
