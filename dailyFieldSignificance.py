"""
    Calculated fieldsignificance for all arrays Reshaped folder.
    """

import numpy as np
import pandas as pd
import datetime
import pickle
from trendmaster import trend
from pathlib import Path

def findFiles(variable="_",region="_",MA="day",years="year",resultDir="Reshaped"):
    """
    Finds .npy-files for a specific variable and moving average smoothing (MA) in a directory.
    
    Parameters
    ----------
    variable: str
    MA: str
    
    Returns
    -------
    list of files
    """
    # set folder
    folder = Path(resultDir)
    
    # make list of strings
    files = []
    for item in sorted(folder.glob(f"*{variable}*{region}*{MA}*{years}*")):
        files.append(str(item))
    
    return files

def resamplingDaily(array):
    """
        Resampling procedure after Burn and Hag Elnur, 2002.
        
        Parameters
        ----------
        array: 3D numpy array in the shape (DOY,years,catchments)
        years: int
        MA: str
        
        Returns
        -------
        dataframe with resampled data
        """
    years = np.arange(0,array.shape[1])
    days = np.arange(0,array.shape[0])
    resampled = np.full_like(array,np.nan)
    for DOY in days:
        for i in range(len(years)):
            # select random year
            year = np.random.choice(years)
            # get values for that year
            resampled[DOY,i,:] = array[DOY,year,:]

    return resampled

def fieldSignDaily(array, alpha = 0.1, q = 90, NS = 400):
    """
    Calculating the field significance after Burn and Hag Elnur, 2002.
    """
    days = np.arange(0,array.shape[0])
    
    significant = []
    print("Iternation number:")
    for i in range(NS):
        if i in np.arange(0,400,50):
            print(i,"of 400")
        resampledArray = resamplingDaily(array)
        sign = np.full(resampledArray.shape[0],np.nan)
        for d in days:
            if np.isfinite(resampledArray[d,:,0]).all():
                s = 0
                for c in range(resampledArray.shape[2]):
                    p = trend.mann_kendall(resampledArray[d,:,c])
                    if p<alpha:
                        s += 1
                # proportion of catchments with signifcant trend
                sign[d] = s/resampledArray.shape[2]
        significant.append(sign)
    
    distribution = np.array(significant)
    
    pcrit = []
    for d in days:
        if np.isfinite(distribution[:,d]).all():
            pcrit.append(np.percentile(distribution[:,d],q))
        else:
            pcrit.append(np.nan)
    pcrit = np.array(pcrit)
    
    percentSign = []
    for d in days:
        s = 0
        for c in range(array.shape[2]):
            p = trend.mann_kendall(array[d,:,c])
            if p<alpha:
                s += 1
        percentSign.append(s/array.shape[2])
    percentSign = np.array(percentSign)
    
    output = {"pcrit":pcrit,"percentSign":percentSign,"fieldSignificant":percentSign>pcrit}
    return pd.DataFrame(output)

variable = input("\n\n-----\nIf selecting files by VARIABLE please enter 'streamflow','rainfall' or 'snowmelt', else press Enter\n")
region = input("\nIf selecting files by REGION please enter shortend name of region,e.g. 'ost' etc, else press Enter\n")
MA = input("\nIf selecting files by MA smoothing please enter shortend window size,e.g. '5', else press Enter\n")
period = input("\nIf selecting files by period please enter number of years,e.g. '30', else press Enter\n")


if variable == "":
    variable="_"
if region == "":
    region="_"
if MA == "":
    MA="day"
if period == "":
    period = "year"

files = findFiles(variable=variable,region=region,MA=MA,years=period)
print("\n---------------------------------")
print(f"Analysing {len(files)} files.")
for file in files:
    print(file)
print("---------------------------------\n")

for file in files:
    var,region,MA,period = tuple(file.split("/")[-1].split(".")[0].split("_"))
    # checking if file already exists
    exists = findFiles(variable=var,region=region,MA=MA,years=period,resultDir="Results/FS")
    if len(exists)>0:
        print("-----","\nFile already exists in Results/FS directroy","\nField significance not calculated for",file,"\n-----")
        continue
    else:
        print(file,"calculating...")
    # opening array file
    array = np.load(file)
    # calculating field significance
    result = fieldSignDaily(array)
    result.to_csv(f"Results/FS/fieldSignificance_{var}_{region}_{MA}_{period}.csv")
    print(var,region,MA,period,"finished.\n")
