import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
import matplotlib


matplotlib.rcParams["figure.figsize"] = [20, 10]

df = pd.read_csv("./assets/Bengaluru_House_Data.csv")


def convert_sqft_to_num(x):
    tokens = x.split("-")
    if(len(tokens) == 2):
       return (float(tokens[0]) + float(tokens[1])) / 2
    
    try:
      return float(x)
    except:
      return None


def is_float(x):
   try:
     float(x)
   except:
     return False

   return True

def remove_pps_outliers(df):
    df_out = pd.DataFrame()
    for key, subdf in df.groupby('location'):
        m = np.mean(subdf.price_per_sqft)
        st = np.std(subdf.price_per_sqft)
        reduced_df = subdf[(subdf.price_per_sqft>(m-st)) & (subdf.price_per_sqft<=(m+st))]
        df_out = pd.concat([df_out,reduced_df],ignore_index=True)
    return df_out

def remove_bhk_outliers(df):
    exclude_indices = np.array([])
    for location, location_df in df.groupby('location'):
        bhk_stats = {}
        for bhk, bhk_df in location_df.groupby('bhk'):
            bhk_stats[bhk] = {
                'mean': np.mean(bhk_df.price_per_sqft),
                'std': np.std(bhk_df.price_per_sqft),
                'count': bhk_df.shape[0]
            }
        for bhk, bhk_df in location_df.groupby('bhk'):
            stats = bhk_stats.get(bhk-1)
            if stats and stats['count']>5:
                exclude_indices = np.append(exclude_indices, bhk_df[bhk_df.price_per_sqft<(stats['mean'])].index.values)
    return df.drop(exclude_indices,axis='index')


def predict_price(location,sqft,bath,bhk):    
    loc_index = np.where(x.columns==location)[0][0]

    X = np.zeros(len(x.columns))
    X[0] = sqft
    X[1] = bath
    X[2] = bhk
    if loc_index >= 0:
        X[loc_index] = 1

    return lr_clf.predict([X])[0]


df2 = df.drop(["area_type", "society", "balcony", "availability"], axis="columns")
df3 = df2.dropna().copy(deep=True)
#print(df3.isnull().sum())
#print(df3['size'].unique())
df3['bhk'] = df3['size'].apply(lambda x: int(x.split(' ')[0]))

#df3[~df3['total_sqft'].apply(is_float)]
df4 = df3.copy(deep=True)
df4['total_sqft'] = df4['total_sqft'].apply(convert_sqft_to_num)
df5 = df4.copy(deep=True)
df5['price_per_sqft'] = df5['price'] * 100000 / df5['total_sqft'] 
df5.location.apply(lambda x: x.strip())
location_stat = df5.groupby('location')['location'].agg('count').sort_values(ascending = False)
localtion_stat_lesthan_10 = location_stat[location_stat <= 10]
df5.location = df5['location'].apply(lambda x: 'other' if x in localtion_stat_lesthan_10 else x)
df6 = df5[~(df5.total_sqft / df5.bhk < 300)]
df7 = remove_pps_outliers(df6)

df8 = remove_bhk_outliers(df7)
df9 = df8[df8.bath < df8.bhk + 2]
df10 = df9.drop(['size', 'price_per_sqft'], axis='columns')
dummies = pd.get_dummies(df10.location)
df11 = pd.concat([df10, dummies.drop(['other'], axis='columns')], axis='columns')
df12 = df11.drop(['location'], axis='columns')

x = df12.drop(['price'], axis='columns')
y = df12.price

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=10 )
#print(df11.head())

from sklearn.linear_model import LinearRegression
lr_clf = LinearRegression()
lr_clf.fit(x_train, y_train)



#print(predict_price('1st Phase JP Nagar',1000, 2, 2))

#print(df3.head())
import pickle

with open('banglore_home_prices_model.pickle', 'wb') as f:
     pickle.dump(lr_clf, f)

import json 

columns = {
  'data_columns': [col.lower() for col in x.columns]
}

with open("columns.json", "w") as f:
     f.write(json.dumps(columns))

