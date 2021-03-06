"""
Using the BeautifulSoup library covid 19 tabular data is extracted (Scrapped) from worldometer website.
Data modification performed according to requirment and then data is appended to database
Created on Tue Apr 14 16:06:44 2020
@author: nachiketkale
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from  datetime import datetime
from _4_saving_worldometer_data_to_database import DataframetoMysql 
from _5_countriesByContinent import countryByContinent

def dataScrappingWorldometer():   
     #MAke a get request to url
    url=requests.get("https://www.worldometers.info/coronavirus/")
    # checking the status  
    print (url.status_code)
    #html.parser is a type of parser we can use different parsers once we know the difference between them
    soup=BeautifulSoup(url.content,'html.parser')
    table=soup.find('table',id="main_table_countries_today")
    get_table_data=table.tbody.find_all("tr")
    #creatign  the dictionary to store key value data
    dic={}
    #extracting ketys of the dict
    for i in range(len(get_table_data)):
        # try except to collect all relevant data since for some countries 
        #data is under 'a' tag and for some it is under 'td' tag
        try:
            key=get_table_data[i].find_all("a",href=True)[0].string
        except:
            key=get_table_data[i].find_all("td")[0].string
    #extracting values for tkeys        
        values=[j.string for j in get_table_data[i].find_all("td")]
        dic[key]=values
    #Transposing the dataframe and storing the data from dictionary in dataframe df
    df=pd.DataFrame(dic).iloc[1:11,:].T
    #Change Index as a column
    df=df.reset_index()
    # Updating column names
    df.columns=["country","total_cases","new_cases","total_deaths", "new_deaths","total_recovered","active_cases","serious","total_cases_per_million","total_deaths_per_million","total_tests"]
    #Insert new column date with time stamp
    df.insert(1,'date', np.full(len(df),datetime.date(datetime.now())))
    
    df=df.reset_index(drop=True)
    df.replace(',', '', regex=True,inplace=True)
    df[["total_cases","new_cases","total_deaths", "new_deaths","total_recovered","active_cases","serious","total_tests"]]=df[["total_cases","new_cases","total_deaths", "new_deaths","total_recovered","active_cases","serious","total_tests"]].apply(pd.to_numeric,errors='coerce') 
    #Creating new column continent
    countries_list=df['country'].tolist()
    continent=[]
    for i in countries_list:
        continent.append(countryByContinent(i))

    #Inserting contient list to dataframe
    df.insert(0,"continent",continent)

    #inserting data to existing database table
    DataframetoMysql(df)