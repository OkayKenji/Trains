import pandas as pd
import json

elements = ["njt","exo","lirr","marc","metrolink","mnrr","nicd","ace","septa","trirail","vre","mbta","sunrail","sle","amtrak","sle","hl","go","via","metra"]

for ele in elements:
    df = pd.read_csv(f"./gtfs_data/{ele}/shapes.txt")
    shapes = list(set(df['shape_id'].to_list()))
    former = len(shapes)
    temp_list = []
    obj = {}
    obj_2 = {}
    index = 0
    for shape in shapes:
        temp = df[df['shape_id'] == shape].reset_index(drop=True).drop('shape_id',axis=1).to_csv()
        
        if temp in temp_list:
            ind = temp_list.index(temp)
            obj_2[f'{shape}'] = obj[f'{ind}'][0]
            ahhhh = obj[f'{ind}'] 
            ahhhh.append(shape)
            obj[f'{ind}'] =ahhhh
        else:
            obj[f'{index}'] = [shape]
            obj_2[f'{shape}'] = shape
            temp_list.append(temp)
            index = index + 1
    print(f'{ele}: {former} -> {len(temp_list)}')
    pretty_json = json.dumps(obj_2,indent=2)

    with open(f'./junk/est_{ele}.json', 'w') as file:
        file.write(pretty_json)
