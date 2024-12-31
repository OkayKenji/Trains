import pandas as pd
from geopy.distance import geodesic
from concurrent.futures import ThreadPoolExecutor

def shape_to_dist(ele):
    df = pd.read_csv(f'./{ele}/shapes.txt')
    # df_trips = pd.read_csv(f'./ace/trips.txt')
    # df_routes = pd.read_csv(f'./ace/routes.txt')

    shapes = list(set(df['shape_id'].to_list()))

    obj = {
        'shape_id' : [],
        'distance' : []
    }

    for _, shape in enumerate(shapes):
        if (not shape in obj):
            sub_df = df[df.shape_id.isin([shape])]
            if 'shape_pt_sequence' in df.columns:
                sub_df = sub_df.sort_values(by='shape_pt_sequence')

            coordinates = [(lat, lon) for lat, lon in zip(sub_df['shape_pt_lat'], sub_df['shape_pt_lon'])]
            distances = [
                geodesic(coordinates[i], coordinates[i + 1]).kilometers
                for i in range(len(coordinates) - 1)
            ]
            total_distance = sum(distances)
            obj['shape_id'].append(shape)
            obj['distance'].append(total_distance)
            
    df = pd.DataFrame(obj)
    df.to_csv(f'./{ele}/distances.txt',index=False)
# def fileWriter(ele):
#     with open(f'./junk/output_{ele}.txt', 'w') as output_file:
#         output_file.write(f"Processing element: {ele}\n")
#         linkedin(ele, output_file)
#         output_file.write("\n")  # Add a blank line after processing the element

def main():
    elements = ["ace", "exo", "lirr", "marc", "mnrr", "nicd", "njt", "septa", "trirail", "vre", "mbta", "sunrail", "sle", "amtrak", "hl", "go", "via"]
    max_threads = 17

    with ThreadPoolExecutor(max_threads) as executor:
        futures = [executor.submit(shape_to_dist, ele) for ele in elements]
        
        for future in futures:
            future.result()  # This will raise an exception if any task fails

if __name__ == "__main__":
    main()
