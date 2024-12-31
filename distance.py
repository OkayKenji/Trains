import pandas as pd
from geopy.distance import geodesic
from concurrent.futures import ThreadPoolExecutor

def linkedin(ele, output_file):
    df = pd.read_csv(f'./{ele}/shapes.txt')
    df_trips = pd.read_csv(f'./{ele}/trips.txt')
    df_routes = pd.read_csv(f'./{ele}/routes.txt')

    shapes = list(set(df['shape_id'].to_list()))

    for i, shape in enumerate(shapes):
        df_trips_sub = df_trips[df_trips.shape_id.isin([shape])]
        train_line = ''
        if not df_trips_sub.empty:
            route_to_look_for = df_trips_sub['route_id'].to_list()[0]
            
            first_occurrence_index = df_routes[df_routes['route_id'] == (route_to_look_for)].index[0]
            
            train_line = df_routes.loc[first_occurrence_index, 'route_long_name']



        output_file.write(f'{shape} {i+1}/{len(shapes)} - {train_line}\n')

        sub_df = df[df.shape_id.isin([shape])]
        if 'shape_pt_sequence' in df.columns:
            sub_df = sub_df.sort_values(by='shape_pt_sequence')

        coordinates = [(lat, lon) for lat, lon in zip(sub_df['shape_pt_lat'], sub_df['shape_pt_lon'])]
        distances = [
            geodesic(coordinates[i], coordinates[i + 1]).kilometers
            for i in range(len(coordinates) - 1)
        ]
        total_distance = sum(distances)

        if 'shape_dist_traveled' in df.columns:
            if (ele == 'exo' or ele == 'marc' or ele == 'njt'):
                provided = sub_df['shape_dist_traveled'].max() 
            else:
                provided = sub_df['shape_dist_traveled'].max() / 1000



        output_file.write(f"Total Est. Distance: {total_distance:.2f} kilometers\n")
        if 'shape_dist_traveled' in df.columns:
            output_file.write(f"Total Given Distance: {provided:.2f} kilometers\n")
            output_file.write(f"%error: { (total_distance - provided) / provided * 100 :.2f}%\n")

        output_file.write("\n")  # Add a blank line between shapes

def fileWriter(ele):
    with open(f'./junk/output_{ele}.txt', 'w') as output_file:
        output_file.write(f"Processing element: {ele}\n")
        linkedin(ele, output_file)
        output_file.write("\n")  # Add a blank line after processing the element

def main():
    elements = ["ace", "exo", "lirr", "marc", "mnrr", "nicd", "njt", "septa", "trirail", "vre", "mbta", "sunrail", "sle", "amtrak", "hl", "go", "via"]
    max_threads = 10

    with ThreadPoolExecutor(max_threads) as executor:
        futures = [executor.submit(fileWriter, ele) for ele in elements]
        
        for future in futures:
            future.result()  # This will raise an exception if any task fails

if __name__ == "__main__":
    main()
