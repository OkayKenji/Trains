import pandas as pd

df = pd.read_csv('./mnrr/shapes.txt')

shapes = list(set(df['shape_id'].to_list()))

for _, shape in enumerate(shapes):
    sub_df = df[df.shape_id.isin([shape])]
    if 'shape_pt_sequence' in df.columns:
        sub_df = sub_df.sort_values(by='shape_pt_sequence')
    lat_lon_list = sub_df[['shape_pt_lat', 'shape_pt_lon']].values.tolist()

    file_path = f'./junk/{shape}.txt'

    with open(file_path, 'w') as f:
        for lat_lon in lat_lon_list:
            f.write(f"{lat_lon},")

    print(f"Written shape {shape} data to {file_path}")

            