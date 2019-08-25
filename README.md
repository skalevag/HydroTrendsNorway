# Daily hydrological trend analysis

Python code used as part of a research project and dissertation for the MSc Environmental Modelling at UCL.

Streamflow, rainfall, snowmelt and temperature data from 207 catchments in Norway were analysed using a daily trend analysis procedure developed by [Kormann et al., 2014](https://doi.org/10.2166/wcc.2014.099). For the Mann-Kendall test and Sen's Slope Estimator the [USGS *trend* module](https://github.com/USGS-python/trend) was used.

*Contents:* 
* [Selection of catchments and assesments of data quality](Catchment-selection.ipynb)
* [Annual trend analysis](Annual-trends.ipynb)
* Daily trend analysis [with significance level](runTrendAnalysis.py) and [without significance level](runTrendMagnitude.py) and [plotting](Daily trends.ipynb)
* Various figures
