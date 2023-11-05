import pandas as pd
import random
from scipy.stats import norm

lod = [{'lat': 23.733927419134954, 'lng': 90.40372156378976}, {'lat': 23.734310454675153, 'lng': 90.40377520797006}, {'lat': 23.734664024943722, 'lng': 90.40378593680612}, {'lat': 23.734997951538713, 'lng': 90.40378593680612}, {'lat': 23.73539912439019, 'lng': 90.40374838587991}, {'lat': 23.73586316900613, 'lng': 90.40382885215035}, {'lat': 23.73616271808744, 'lng': 90.40382885215035}, {'lat': 23.73647324436531, 'lng': 90.40389322516671}, {'lat': 23.736901021442083, 'lng': 90.40397905585519}, {'lat': 23.73691084265613, 'lng': 90.40374838587991}, {'lat': 23.737269316462143, 'lng': 90.40407561537972}, {'lat': 23.73726440586872, 'lng': 90.40437602278939}, {'lat': 23.73759341521864, 'lng': 90.40411014079439}, {'lat': 23.73809429352931, 'lng': 90.40385801314699}, {'lat': 23.73840365858278, 'lng': 90.40383655547487}, {'lat': 23.738501869557243, 'lng': 90.40356833457338}, {'lat': 23.73879159150059, 'lng': 90.40319818972932}, {'lat': 23.739154970654326, 'lng': 90.40295679091798}, {'lat': 23.739334028988438, 'lng': 90.4025276374756}, {'lat': 23.739594800007872, 'lng': 90.40223259448396}, {'lat': 23.739805951580923, 'lng': 90.40169615268098}, {'lat': 23.74005638672391, 'lng': 90.40147621154176}, {'lat': 23.74008584965026, 'lng': 90.40108997344362}, {'lat': 23.740424672824336, 'lng': 90.40075201510774}, {'lat': 23.74056707650405, 'lng': 90.40027994632112}, {'lat': 23.740602544201458, 'lng': 90.40005464076387}, {'lat': 23.740819028140738, 'lng': 90.39979178428041}, {'lat': 23.74117749119348, 'lng': 90.39956111430513}, {'lat': 23.74136408800864, 'lng': 90.3991963338791}, {'lat': 23.741727459986915, 'lng': 90.39905685901033}, {'lat': 23.741840399719628, 'lng': 90.39892160248525}, {'lat': 23.741909145595944, 'lng': 90.39858780920514}, {'lat': 23.74215957669573, 'lng': 90.3981479269267}, {'lat': 23.742002443512924, 'lng': 90.39807818949231}, {'lat': 23.741977891435983, 'lng': 90.39765440046796}, {'lat': 23.74189932475869, 'lng': 90.39770804464825}, {'lat': 23.741820758034017, 'lng': 90.39734862864026}, {'lat': 23.74175692253532, 'lng': 90.39715550959119}, {'lat': 23.74156050542006, 'lng': 90.39659427916166}, {'lat': 23.741383729763115, 'lng': 90.39611246632984}, {'lat': 23.74110383448233, 'lng': 90.39604221019215}, {'lat': 23.74075028168913, 'lng': 90.39616559180683}, {'lat': 23.740534221176475, 'lng': 90.39598320159382}, {'lat': 23.74023244433116, 'lng': 90.39601002368397}, {'lat': 23.739990700502716, 'lng': 90.39609048995442}, {'lat': 23.73964696569634, 'lng': 90.39617095622486}, {'lat': 23.739435813865605, 'lng': 90.39611731204457}, {'lat': 23.739259035325517, 'lng': 90.39614949855275}, {'lat': 23.738998777593856, 'lng': 90.39620850715107}, {'lat': 23.738826908995467, 'lng': 90.39610121879048}, {'lat': 23.738596390039316, 'lng': 90.39597247275776}, {'lat': 23.738459931072434, 'lng': 90.3961226764626}, {'lat': 23.73834698840906, 'lng': 90.39611194762654}, {'lat': 23.73827824065298, 'lng': 90.39617095622486}, {'lat': 23.738710368802852, 'lng': 90.39602611693806}, {'lat': 23.73884786382269, 'lng': 90.39600465926594}, {'lat': 23.739024642920704, 'lng': 90.39616559180683}, {'lat': 23.73820458230264, 'lng': 90.39629970225758}]

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
map_values()