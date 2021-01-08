import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

df = pd.read_csv('processed_individual_cases_Sep20th2020.csv')
df1 = pd.read_csv('processed_location_Sep20th2020.csv')

######################################
#### 1.1 Exploratory Data Analysis####
######################################
#### printing missing value
def data_cleaning(df):
    mis_attr_count_1 = {}

    for attr in df:
        for mis_val in pd.isnull(df[attr]):
            if attr not in mis_attr_count_1:
                mis_attr_count_1[attr] = 1
            if mis_val == True:
                mis_attr_count_1[attr]+=1
    print(mis_attr_count_1)

    return df

#### data_cleaning function example
data_cleaning(df) 
data_cleaning(df1) 

######################################################
#### 1.2 Data cleaning and Imputing missing values####
######################################################
#
#################################################
####### cleaning and Imputing data for df #######
#################################################
########## convert all the age to integer
#filter invalid data and convert str num to int
def filter(filterd_df):
    len_df = len(filterd_df.index)
    for i in range(len_df):
        if isinstance(filterd_df['age'][i],str):
            if '-' in filterd_df['age'][i]:                  # calculate '20-25' mean and round up, convert '80-' to 80
                split_num = filterd_df['age'][i].split('-')
                if '' in split_num:                         #convert '80-' to 80
                    split_num.remove('')
                    filterd_df['age'][i] = int(split_num[0])
                else:
                    split_num = list(map(int, split_num))   #calculate '20-25' mean and round up      
                    total = sum(split_num)
                    mean = round(total/2)
                    filterd_df['age'][i] = mean
            elif '+' in filterd_df['age'][i]:               # convert '80+' to 80
                split_num = filterd_df['age'][i].split('+')
                split_num = list(map(int, split_num[0])) 
                filterd_df['age'][i] = split_num[0]
            elif '.' in filterd_df['age'][i]:               # convert '70.0' to 70
                split_num = filterd_df['age'][i].split('.')
                split_num = list(map(int, split_num))  
                filterd_df['age'][i] = split_num[0]
            elif filterd_df['age'][i].isdigit():            #convert str num to int   '70' to 70
                filterd_df['age'][i] = int(filterd_df['age'][i])
            elif 'month' in filterd_df['age'][i]:           #convert 18 month to 1.5 years old round up => 2 age
                split_num = filterd_df['age'][i].split(' ')
                temp_age = round(int(split_num[0]))
                filterd_df['age'][i] = temp_age
            else:                                           #invalid str data  '5月14日'
                filterd_df = filterd_df.drop([i], axis=0)
        if filterd_df['age'][i] < 1:                      #age<1 invalid data
            filterd_df = filterd_df.drop([i])
        else:                                               #round age up   10.3->11
            filterd_df['age'][i] = round(filterd_df['age'][i])
    return filterd_df

##### conver the age to integer
temp = df.dropna()
temp = temp.reset_index(drop = True)
temp = filter(temp)

########## deciding the male and female
def filling_sex(df):
    count_male = 0
    count_female = 0
    total_count = 0
    for item in df['sex']:
      if item == 'female':
        count_female += 1
        total_count += 1
      elif item == 'male':
        count_male += 1
        total_count += 1
    female = 'female'
    male = 'male'

    male_percent = int((count_male/total_count)*100)
    missing_value = pd.isnull(df['sex'])
    for i in range(len(df['sex'])):
      random_number = random.randint(0,100)
      if missing_value[i]:
        if random_number>male_percent:
          df['sex'][i] = female
        else:
          df['sex'][i] = male 

    print(df['sex'])
    return df

filling_sex(df)

########## fill in the missing age
age_median = int(temp['age'].median())
df['age'] = df['age'].fillna(age_median)
df = df.reset_index(drop=True)

df = filter(df)

########## check if the age column is all filled and they are all integer
def check(df):
    data_cleaning(df)
    df['age'] = pd.to_numeric(df['age'])
    if df['age'].dtype != np.number:
        print('yes')
    else:
        print('no')

check(df)

########## drop unused columns
df.drop(['additional_information','source'],inplace = True, axis = 1)
df = df.dropna()
#################################################
####### cleaning and Imputing data for df1#######
#################################################
def missing_index_list(df1):            #find the index of missing value in a column (df1 is a column)
    temp = pd.isnull(df1)
    index = []
    for i in range(len(temp)):
        if temp[i]:
            index.append(i)
    return index

##### following are the list of index of missing value in 'Active', 'Incidence_Rate', 'Case-Fatality_Ratio', and 'Province_State'
active_index = missing_index_list(df1['Active'])
IR_index = missing_index_list(df1['Incidence_Rate'])
CF_index = missing_index_list(df1['Case-Fatality_Ratio'])

def Active_cal(index):                  #fill in the missing value for 'Active'
    for i in range(len(index)):
        cal = df1['Confirmed'][index[i]] - df1['Deaths'][index[i]] - df1['Recovered'][index[i]]
        if cal >= 0:
            df1['Active'][index[i]] = cal
        else:
            df1['Active'][index[i]] = 0

def IR_cal(index):                         #have calculate the Incidence Rate if the numbers are feasible
    for i in range(len(index)):
        cal = df1['Confirmed'][index[i]] / 100000
        df1['Incidence_Rate'][index[i]] = cal


def CF_cal(index):                          #calculate the case fatality ratio and check the condition
    for i in range(len(index)):
        if df1['Confirmed'][index[i]] == 0:
            df1['Case-Fatality_Ratio'][index[i]] = 0
        else:
            cal = df1['Confirmed'][index[i]] - (df1['Deaths'][index[i]]/df1['Confirmed'][index[i]])
            if cal>=0:
                df1['Case-Fatality_Ratio'][index[i]] = cal
            else:
                df1['Case-Fatality_Ratio'][index[i]] = 0

Active_cal(active_index)
IR_cal(IR_index)
CF_cal(CF_index)

def cal_province_in_us(index):              #find all the province in US and return a dict value
    province_count = {}
    tar = 'US'
    to = 'United States'
    for i in range(len(index)):
        if df1['Country_Region'][i] == tar:
            df1['Country_Region'][i] = to
            if df1['Province_State'][i] not in province_count:
                province_count[df1['Province_State'][i]] = 1
            else:
                province_count[df1['Province_State'][i]] += 1
    return province_count

US_province = cal_province_in_us(df1['Province_State'])
df1 = df1.dropna()

#####################################
##### 1.3 Dealing with outliers #####
#####################################
######## remove outlier for both df and df1
def outlier_remove(df,df1):
    df_status = df.describe()
    print(df_status)
    df1_status = df1.describe()
    print(df1_status)

    df['age'] = Trim(df, 'age', np.inf, 0) #remove data below 0
    df['age'] = flooring(df, 'age', 0.1, 0.90) #remove data below 0

    df1['Confirmed'] = Trim(df1, 'Confirmed', np.inf, 0) #remove data below 0
    df1['Confirmed'] = flooring(df1, 'Confirmed', 0.1, 0.90) #remove data below 0
    df1['Deaths'] = Trim(df1, 'Deaths', np.inf, 0) #remove data below 0
    df1['Deaths'] = flooring(df1, 'Deaths', 0.1, 0.90) #remove data below 0
    df1['Recovered'] = Trim(df1, 'Recovered', np.inf, 0) #remove data below 0
    df1['Recovered'] = flooring(df1, 'Recovered', 0.1, 0.90) #remove data below 0
    df1['Active'] = Trim(df1, 'Active', np.inf, 0) #remove data below 0
    df1['Active'] = flooring(df1, 'Active', 0.1, 0.90) #remove data below 0
    df1['Incidence_Rate'] = Trim(df1, 'Incidence_Rate', np.inf, 0) #remove data below 0
    df1['Incidence_Rate'] = flooring(df1, 'Incidence_Rate', 0.1, 0.90) #remove data below 0
    df1['Case-Fatality_Ratio'] = Trim(df1, 'Case-Fatality_Ratio', np.inf, 0) #remove data below 0
    df1['Case-Fatality_Ratio'] = flooring(df1, 'Case-Fatality_Ratio', 0.1, 0.90) #remove data below 0

    #print(df1_status)

    return df,df1

def flooring(df, att, lower, upper):            # Remove top and lowest percentage of the data
    median = df[att].median()
    print(median)
    lower_bound = df[att].quantile(lower)
    upper_bound = df[att].quantile(upper)
    df[att] = df[att].mask(df[att] >= upper_bound, median)
    df[att] = df[att].mask(df[att] <= lower_bound, median)

    return df[att]

def Trim(df, att, lower, upper):                # Remove data with values outside of this range ex.(age)
    index = df[(df[att] >= lower)|(df[att] <= upper)].index
    df.drop(index, inplace=True)

    return df[att]

df.to_csv('cleaned_cases.csv', index = False)
##############################
##### 1.4 Transformation #####
##############################
#
######### aggregate value for the state level
df2 = df1.groupby(['Province_State','Country_Region']).sum()
df2.to_csv('temp.csv')

df3 = pd.read_csv('temp.csv')
US = 'US'
for i in range(len(df3['Country_Region'])):
    if df3['Country_Region'][i] == US:
        province = df3['Province_State'][i]
        df3['Incidence_Rate'][i] = df3['Incidence_Rate'][i]/US_province[province]
        df3['Case-Fatality_Ratio'][i] = df3['Case-Fatality_Ratio'][i]/US_province[province]
        df3['Lat'][i] = df3['Lat'][i]/US_province[province]
        df3['Long_'][i] = df3['Long_'][i]/US_province[province]

df3.to_csv('location_aggregated.csv', index = False)

######################################################
##### 1.5 Joining the cases and loctaion dataset #####
######################################################
case_data = pd.read_csv('cleaned_cases.csv')
location_data = pd.read_csv('location_aggregated.csv')
def Joint(df,df1):
    
    size = len(df)
    #print(size)

    for i in range(size):
        print(i)
        country = df.loc[i,'country']
        province = df.loc[i,'province']

        if (pd.notnull(df.loc[i,'country'])) & pd.notnull(df.loc[i,'province']):
            #print(country)
            #print(province)
            df2 = df1[df1['Country_Region'].str.contains(country)]
            df3 = df2[df2['Province_State'].str.contains(province)]
            if len(df3)!=0:

                df3.reset_index(drop=True, inplace=True)
                for row in df3.columns:
                    df.at[i,row]= df3.at[0, row]

    return df, df1 

case_data, location_data = Joint(case_data, location_data)
#case_data.drop(['Unnamed'], inplace=True, axis = 1)
case_data.drop(['Province_State', 'Country_Region'], inplace = True, axis = 1)
case_data.to_csv('result.csv', index = False)
