import pandas as pd
import random
from scipy.stats import norm

lod = [{'lat': 23.729834537496934, 'lng': 90.41024689175083}, {'lat': 23.730266693647955, 'lng': 90.41013960339023}, {'lat': 23.730340356485303, 'lng': 90.41018251873447}, {'lat': 23.730600631510512, 'lng': 90.4101342389722}, {'lat': 23.730723402568408, 'lng': 90.4101342389722}, {'lat': 23.731081893395594, 'lng': 90.41006986595585}, {'lat': 23.73136672102108, 'lng': 90.41009132362797}, {'lat': 23.73146002648718, 'lng': 90.41016642548038}, {'lat': 23.73184788206071, 'lng': 90.41017715431644}, {'lat': 23.732216154364856, 'lng': 90.41015569664432}, {'lat': 23.73257464108598, 'lng': 90.41006986595585}, {'lat': 23.732879108485662, 'lng': 90.41021470524265}, {'lat': 23.733202820388193, 'lng': 90.41012887455418}, {'lat': 23.733496155922197, 'lng': 90.41022006966068}, {'lat': 23.733805531892873, 'lng': 90.4102415273328}, {'lat': 23.734144371398983, 'lng': 90.41027371384098}, {'lat': 23.734272049824913, 'lng': 90.41034345127537}, {'lat': 23.734563621626627, 'lng': 90.4103488156934}, {'lat': 23.734937931912256, 'lng': 90.41038100220158}, {'lat': 23.735242393790365, 'lng': 90.41023079849674}, {'lat': 23.73553212298153, 'lng': 90.41028444267704}, {'lat': 23.73576292374062, 'lng': 90.41035954452946}, {'lat': 23.735900421870866, 'lng': 90.4104400107999}]

def filter(filename):
    df = pd.read_csv(f'data/{filename}.csv')

    df = df.dropna()
    df['csq'] = df['csq'].str.replace('"', '').str.replace(',', '.').astype(float)
    df = df.drop_duplicates(subset=['lat', 'lng'])
    df.to_csv(f'data/f_{filename}.csv', index=False)

    print(df)

def create_csv_from_list_of_dict(lod, low_lim, up_lim):
    df = pd.DataFrame(lod)
    df['csq'] = [random.randint(low_lim, up_lim) + 0.99 for _ in range(len(df))]
    df['lat'] = df['lat'].round(7)
    df['lng'] = df['lng'].round(7)
    
    df.to_csv('data/output_data.csv', index=False)

def remove_column():
    input_file = 'data/raw.csv' 
    output_file = 'data/raw.csv'

    df = pd.read_csv(input_file)

    columns_to_remove = [3, 4, 5, 6] 
    df = df.drop(df.columns[columns_to_remove], axis=1)
    df.to_csv(output_file, index=False)
    
def switch_column():
    df = pd.read_csv('data/raw.csv')
    column1_index = 0
    column2_index = 2
    df[df.columns[column1_index]], df[df.columns[column2_index]] = df[df.columns[column2_index]].copy(), df[df.columns[column1_index]].copy()
    df.to_csv('data/raw.csv', index=False)
    
def find_range():
    df = pd.read_csv('data/raw.csv')

    column_number = 2  
    
    column_data = df.iloc[:, column_number]
    column_range = column_data.max() - column_data.min()
    column_max = column_data.max()
    column_min = column_data.min()

    print(f"Column Range: {column_range}")
    print(f"Column Maximum: {column_max}")
    print(f"Column Minimum: {column_min}")

def map_values():
    input_file = 'data/raw.csv'  
    output_file = 'data/raw_modified.csv'

    df = pd.read_csv(input_file)

    column_number = 2  

    df.iloc[:, column_number] = df.iloc[:, column_number].apply(lambda x: (31 - round(1 + (x - 1) * (31 - 1) / (7 - 1))) + 0.99)

    df.to_csv(output_file, index=False)

def filter_by_coor():
    input_file = 'data/data_3.csv'  
    output_file = 'data/raw_modified_coor.csv' 

    start_lat = 23.7570727
    start_lng = 90.3620938
    end_lat = 23.7231314 
    end_lng = 90.4052417


    df = pd.read_csv(input_file)

    df = df[df['lat'] >= 23.72] 
    df = df[df['lat'] <= 23.75] 
    df = df[df['lng'] >= 90.36] 
    df = df[df['lng'] <= 90.4] 
    print(df)
    
    df.to_csv(output_file, index=False)

def remove_by_bounding_box():               #needs a bit more work
    input_file = 'data/f_data_0.csv'  
    output_file = 'data/f_data_1.csv' 

    start_lat = 23.7390973
    start_lng = 90.3949544
    end_lat = 23.7293607 
    end_lng = 90.4028937


    df = pd.read_csv(input_file)

    cut_df = df[(df['lat'] < 23.7390973) & (df['lat'] > 23.7293607)]
    
    result_df = df.merge(cut_df, on=['lat'], how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)

    print(result_df)
    
    result_df.to_csv(output_file, index=False)
