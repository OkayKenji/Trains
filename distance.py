import pandas as pd
from geopy.distance import geodesic
from concurrent.futures import ThreadPoolExecutor

def linkedin(ele, output_file):
    df = pd.read_csv(f'./{ele}/shapes.txt')
    shapes = list(set(df['shape_id'].to_list()))

    for i, shape in enumerate(shapes):
        output_file.write(f'{shape} {i+1}/{len(shapes)}\n')

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
            provided = sub_df['shape_dist_traveled'].max() 

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
    # elements = ["ace", "exo", "lirr", "marc", "mnrr", "nicd", "njt", "septa", "trirail", "vre", "mbta", "sunrail", "sle", "amtrak", "hl", "go", "via"]
    elements = ["exo"]
    max_threads = 17

    with ThreadPoolExecutor(max_threads) as executor:
        futures = [executor.submit(fileWriter, ele) for ele in elements]
        
        for future in futures:
            future.result()  # This will raise an exception if any task fails

if __name__ == "__main__":
    main()