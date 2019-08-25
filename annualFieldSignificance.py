import numpy as np
import pandas as pd
from trendmaster import trend
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

sor = openDict("sorlandet_final")
ost = openDict("ostlandet_final")
vest = openDict("vestlandet_final")
trond = openDict("trondelag_final")
nord = openDict("nordland_final")
finn = openDict("finnmark_final")

def annualSum(ts,years=30,endYear = 2012):
    """
    Calculates the annual total of a variable for a norwegian hydrological year.
    
    Parameters
    ----------
    ts: pandas.DataFrame
        table with time series data in column and datetime as index
    startYear: str
    endYear: str
        
    Returns
    -------
    pandas of total annual of variable
    """
    startYear = endYear-years+1
    years = np.arange(startYear,endYear+1)
    t = []
    for year in years:
        start = str(year)
        end = str(year+1)
        tslice = ts[f"{start}-09-01":f"{end}-08-31"]
        if pd.isnull(tslice).any():
            missing = pd.isnull(tslice).sum()
            total = tslice.shape[0]
            threshold = np.ceil(total*0.1)
            if missing>threshold:
                t.append(np.nan)
            else:
                t.append(tslice.sum(skipna=True))
        else:
            t.append(tslice.sum(skipna=False))
    return np.array(t)

def annualET(data, years = 30):
    df = data["metadata"]
    evapo = {}
    for c in data[f"final{years}"]:
        area = (df[df.snumber==c].areal).iloc[0]
        Q = annualSum((data["data"][c]["runoff"].runoff)*(86.4)/area,years=years)
        rainfall = annualSum(data["data"][c]["precip"],years=years)
        snowmelt = annualSum(data["data"][c]["snow"].qsw,years=years)
        P = rainfall + snowmelt
        ET = P - Q
        evapo[c] = ET
    return evapo

def annualAllVariables(data, years = 30):
    """
    Calculates annual data from daily data for runoff, rainfall, snowmelt, precipitation, and evapotraspiration.
    Evapotranspiration is calculated using the water balance equation, and assumes changes in annual storage is zero.
    """
    df = data["metadata"]
    evapo = {}
    runoff = {}
    rain = {}
    snow = {}
    precip = {}
    for c in data[f"final{years}"]:
        area = (df[df.snumber==c].areal).iloc[0]
        Q = annualSum((data["data"][c]["runoff"].runoff)*(86.4)/area,years=years)
        rainfall = annualSum(data["data"][c]["precip"],years=years)
        snowmelt = annualSum(data["data"][c]["snow"].qsw,years=years)
        P = rainfall + snowmelt
        ET = P - Q
        evapo[c] = ET
        runoff[c] = Q
        rain[c] = rainfall
        snow[c] = snowmelt
        precip[c] = P
    years = range(2013-years,2013)
    return pd.DataFrame(evapo,index=years),pd.DataFrame(runoff,index=years),pd.DataFrame(rain,index=years),pd.DataFrame(snow,index=years),pd.DataFrame(precip,index=years)

def resampling(df,years):
    """
        Resampling procedure after Burn and Hag Elnur, 2002.
        """
    years = np.arange(2013-years,2013)
    ## bootstrap procedure
    resampled = {}
    catchments = list(df.columns)
    
    for c in catchments:
        ts = []
        for i in range(len(years)):
            # select random year
            year = np.random.choice(years)
            # get values for that year
            resampled[i] = np.array(df.loc[year])

    return pd.DataFrame.from_dict(resampled,columns=catchments,orient="index")

def fieldSign(df, years, alpha = 0.05, q = 90, NS = 400, histogram=False):
    """
    Calculating the field significance after Burn and Hag Elnur, 2002.
    """
    catchments = list(df.columns)
    
    sign = []
    for i in range(NS):
        resampled = resampling(df,years=years)
        s = 0
        for col in catchments:
            ts = np.array(resampled[col])
            p = trend.mann_kendall(ts)
            if p<alpha:
                s += 1
        sign.append(s/len(catchments))

    distribution = np.array(sign)
    pcrit = np.percentile(distribution,q)
    
    # plot histogram
    if histogram:
        plt.hist(distribution,edgecolor="k", linewidth=1)
        plt.xlabel("% of catchments with significant trends")
        plt.ylabel("Frequency")
        #plt.vlines(pcrit,0,NS,color="k")
        #plt.ylim(n.max()+10)
    
    s = 0
    for col in catchments:
        ts = np.array(df[col])
        p = trend.mann_kendall(ts)
        if p<alpha:
            s += 1
    percentSign = s/len(catchments)
    
    return pcrit, percentSign, percentSign>pcrit

regionDF = {"sor":sor,
            "ost":ost,
            "vest":vest,
            "trond":trond,
            "nord":nord,
            "finn":finn}
regions = ["sor","ost","vest","trond","nord","finn"]
years = [30,50]
out = {}

print("\nStarting analysis...")
for year in years:
    print("-----")
    print(f"Analysing {year} year period...")
    out[f"{year}years"] = {}
    for region in regions:
        regDF = regionDF[region]
        varDF = annualAllVariables(regDF,years=year)
        variables = ("evapo","runoff","rain","snow","precip")
        FS = {}
        for i in range(len(varDF)):
            df = varDF[i]
            var = variables[i]
            results = fieldSign(df,year)
            FS[var] = results
        out[f"{year}years"][region] = pd.DataFrame.from_dict(FS,orient="index",columns=["pcrit","percentSignficant","FieldSignificant"])
        print(f"\tRegion {region} complete.")

saveDict(out,"Results/FS/FieldSignificanceAnnual")
print("-----")
print("Analysis complete.")
print("-----")
