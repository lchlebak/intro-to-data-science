
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[1]:

import pandas as pd
import numpy as np
from scipy.stats import stats


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[2]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[3]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    #This reads the data and returns a dataframe with the correct "State" and "RegionName" columns.
    data = pd.read_csv('university_towns.txt', sep="\n", header=None)
    State = []
    RegionName = []
    for f in data[0]:
        if "[edit]" in f:
            state = f
        else:
            RegionName.append(f)
            State.append(state)
    State = pd.DataFrame(State)
    RegionName = pd.DataFrame(RegionName)
    df = pd.concat([State, RegionName], axis=1)
    df.columns = ["State", "RegionName"]
    
    #This cleans the data in the dataframe.
    df["State"] = df["State"].str.replace(r"\[.*","")
    df["RegionName"] = df["RegionName"].str.replace(r" \(.*","")
    
    return df


# In[23]:

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    #This reads the data and returns a DataFrame with the needed information.
    data = pd.ExcelFile("gdplev.xls")
    gdp = data.parse(skiprows=5)
    gdp = (gdp.drop(gdp.columns[[0,1,2,3,7]], 1)
           .drop([0,1])
           .reset_index(drop=True))
    gdp.columns = ["Quarters", "GDP in Billions of Current Dollars", "GDP in Billions of Chained 2009 Dollars"]
    value = gdp[gdp["Quarters"]=="2000q1"]
    gdp = gdp[value.index[0]:].reset_index(drop=True)
    
    #This finds the string value for the year and quarter where the recession starts.
    value = []
    new_value = []
    number = 0
    for i in range(1, len(gdp["GDP in Billions of Chained 2009 Dollars"])-3):
        if ((gdp.iloc[i-1]["GDP in Billions of Chained 2009 Dollars"]
             > gdp.iloc[i]["GDP in Billions of Chained 2009 Dollars"]) and
            (gdp.iloc[i]["GDP in Billions of Chained 2009 Dollars"]
             > gdp.iloc[i+1]["GDP in Billions of Chained 2009 Dollars"]) and
            (gdp.iloc[i+1]["GDP in Billions of Chained 2009 Dollars"]
             < gdp.iloc[i+2]["GDP in Billions of Chained 2009 Dollars"]) and
            (gdp.iloc[i+2]["GDP in Billions of Chained 2009 Dollars"]
             < gdp.iloc[i+3]["GDP in Billions of Chained 2009 Dollars"])):
            value.append(gdp.iloc[i]["Quarters"])
            number = i
    for i in range(number, 0, -1):
        if (gdp.iloc[i-1]["GDP in Billions of Chained 2009 Dollars"]
             < gdp.iloc[i]["GDP in Billions of Chained 2009 Dollars"]):
            new_value.append(gdp.iloc[i+1]["Quarters"])
            break

    return new_value[0]


# In[5]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    
    #This reads the data and returns a DataFrame with the needed information.
    data = pd.ExcelFile("gdplev.xls")
    gdp = data.parse(skiprows=5)
    gdp = (gdp.drop(gdp.columns[[0,1,2,3,7]], 1)
           .drop([0,1])
           .reset_index(drop=True))
    gdp.columns = ["Quarters", "GDP in Billions of Current Dollars", "GDP in Billions of Chained 2009 Dollars"]
    value = gdp[gdp["Quarters"]=="2000q1"]
    gdp = gdp[value.index[0]:].reset_index(drop=True)
    
    #This finds the string value for the year and quarter where the recession ends.
    value = []
    for i in range(1, len(gdp["GDP in Billions of Chained 2009 Dollars"])-3):
        if ((gdp.iloc[i-1]["GDP in Billions of Chained 2009 Dollars"]
             > gdp.iloc[i]["GDP in Billions of Chained 2009 Dollars"]) and
            (gdp.iloc[i]["GDP in Billions of Chained 2009 Dollars"]
             > gdp.iloc[i+1]["GDP in Billions of Chained 2009 Dollars"]) and
            (gdp.iloc[i+1]["GDP in Billions of Chained 2009 Dollars"]
             < gdp.iloc[i+2]["GDP in Billions of Chained 2009 Dollars"]) and
            (gdp.iloc[i+2]["GDP in Billions of Chained 2009 Dollars"]
             < gdp.iloc[i+3]["GDP in Billions of Chained 2009 Dollars"])):
            value.append(gdp.iloc[i+3]["Quarters"]) 

    return value[0]


# In[6]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    
    #This reads the data and returns a DataFrame with the needed information.
    data = pd.ExcelFile("gdplev.xls")
    gdp = data.parse(skiprows=5)
    gdp = (gdp.drop(gdp.columns[[0,1,2,3,7]], 1)
           .drop([0,1])
           .reset_index(drop=True))
    gdp.columns = ["Quarters", "GDP in Billions of Current Dollars", "GDP in Billions of Chained 2009 Dollars"]
    value = gdp[gdp["Quarters"]=="2000q1"]
    gdp = gdp[value.index[0]:].reset_index(drop=True)
    
    #This finds the string value for the year and quarter where the recession starts.
    value = []
    for i in range(1, len(gdp["GDP in Billions of Chained 2009 Dollars"])-3):
        if ((gdp.iloc[i-1]["GDP in Billions of Chained 2009 Dollars"]
             > gdp.iloc[i]["GDP in Billions of Chained 2009 Dollars"]) and
            (gdp.iloc[i]["GDP in Billions of Chained 2009 Dollars"]
             > gdp.iloc[i+1]["GDP in Billions of Chained 2009 Dollars"]) and
            (gdp.iloc[i+1]["GDP in Billions of Chained 2009 Dollars"]
             < gdp.iloc[i+2]["GDP in Billions of Chained 2009 Dollars"]) and
            (gdp.iloc[i+2]["GDP in Billions of Chained 2009 Dollars"]
             < gdp.iloc[i+3]["GDP in Billions of Chained 2009 Dollars"])):
            value.append(gdp.iloc[i+1]["Quarters"]) 

    return value[0]


# In[7]:

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    data = pd.read_csv('City_Zhvi_AllHomes.csv')
    data = data.replace(states).set_index(["State", "RegionName"]).sort_index()
    data = data.drop(data.columns[0:49], axis=1)
    data.columns = pd.to_datetime(data.columns)
    data = data.resample('Q', how='mean', axis=1)
    d1 = np.array(data.columns.year.astype(str), dtype=np.object)
    d2 = np.array(data.columns.quarter.astype(str), dtype=np.object)
    data.columns = d1 + 'q' + d2
    
    return data


# In[17]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivalent to a
    reduced market loss).'''
    
    #This reads the housing data and forms the price ratio value. It also uses
    #dictionary values to convert state names.
    data = convert_housing_data_to_quarters()
    value = get_recession_start()
    index_of_quarter_before_recession = np.where(data.columns == value)[0][0]-1
    quarter_before_recession = data.columns[index_of_quarter_before_recession]
    data["Price Ratio"] = data[quarter_before_recession].div(data[get_recession_bottom()])
    
    #This includes the data on university towns to split housing prices into two
    #subgroups.
    uni_towns = get_list_of_university_towns()
    data_uni_towns = pd.merge(uni_towns, data, how = 'left', right_index = True, left_on = ['State', 'RegionName'])
    data_uni_towns = data_uni_towns.set_index(["State", "RegionName"]).dropna(subset=["Price Ratio"])
    merged = pd.merge(uni_towns, data, indicator=True, how='outer', right_index = True, left_on =['State', 'RegionName'])
    data_non_uni_towns = merged[merged['_merge']=='right_only']
    del data_non_uni_towns["_merge"]
    data_non_uni_towns = data_non_uni_towns.set_index(["State", "RegionName"]).dropna(subset=["Price Ratio"])
    
    #This performs the statistical test.
    p_value = stats.ttest_ind(data_uni_towns["Price Ratio"], data_non_uni_towns["Price Ratio"])[1]
    different = False
    if p_value < 0.01:
        different = True
    uni_mean = data_uni_towns["Price Ratio"].mean()
    non_uni_mean = data_non_uni_towns["Price Ratio"].mean()
    better = "university town"
    if non_uni_mean < uni_mean:
        better = "non-university town"
    
    return (different, p_value, better)

