
import pandas as pd
import pydeck as pdk
import random

elements = ["ace","exo","lirr","marc","metrolink","mnrr","nicd","njt","septa","trirail","vre","mbta","sunrail","amtrak","sle","hl","go","via","rtd/RTD_Denver_Direct_Operated_Commuter_Rail_GTFS", "rtd/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS","metra"]
# elements = ["amtrak"]
for ele in elements:
    print(ele)

    # Get stops and their info
    df = pd.read_csv(f'./data/csv/{ele}.csv') # assuming running form root
    df_ref = pd.read_csv(f'./gtfs_data/{ele}/stops.txt')
    # df_ace = pd.read_csv(f'./gtfs_data/{ele}/shapes.txt')
  
    # Clean and calculate max trains per stop
    df.drop('Unnamed: 0', axis=1, inplace=True)
    row_stop_counts = df.drop(columns=["stop_name"]).notna().sum(axis=1)
    df_ref['height'] = row_stop_counts
    df_ref['stop_lat'] = df_ref['stop_lat'].apply(pd.to_numeric, errors='coerce')

    # Generate map
    view = pdk.data_utils.compute_view(df_ref[["stop_lon", "stop_lat"]])
    view.pitch = 75
    view.bearing = 0

    # def hex_to_rgb(h):
    #     h = h.lstrip("#")
    #     return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))

    # shapes = list(set(df_ace["shape_id"].to_list()))

    # # Initialize an empty list to store DataFrames
    # new_dfs = []

    # for shape in shapes:
    #     # Filter the DataFrame for the current shape
    #     if shape != 174:
    #         continue
    #     shape_df = df_ace[df_ace["shape_id"] == 174]
    #     if 'shape_pt_sequence' in shape_df.columns:
    #         shape_df = shape_df.sort_values(by='shape_pt_sequence')
    #     lat_lon_list = shape_df[['shape_pt_lon', 'shape_pt_lat']].values.tolist()
        
    #     # Create a new DataFrame for the current shape
    #     new_df = pd.DataFrame({
    #         'name': [f"exo{shape}"],
    #         'color': ["#782a7d"],
    #         'path': [lat_lon_list],
    #     })
    #     new_df["color"] = new_df["color"].apply(hex_to_rgb)
        
    #     # Append the new DataFrame to the list
    #     new_dfs.append(new_df)

    # # Concatenate all the DataFrames into a single DataFrame
    # final_df = pd.concat(new_dfs, ignore_index=True)


    # layer = pdk.Layer(
    #     type="PathLayer",
    #     data=final_df,
    #     pickable=True,
    #     get_color="color",
    #     width_scale=20,
    #     width_min_pixels=2,
    #     get_path="path",
    #     get_width=5,
    # )


    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df_ref,
        get_position=["stop_lon", "stop_lat"],
        get_elevation="height",
        elevation_scale=50,
        radius=200,
        get_fill_color=[255,255,255,255],
        pickable=True,
        auto_highlight=True,
    )

    tooltip = {
        "html": "{stop_name}: <b>{height}</b> trains stop",
        "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
    }

    r = pdk.Deck(
        layers=[column_layer],
        initial_view_state=view,
        tooltip=[tooltip],
        map_style=pdk.map_styles.DARK_NO_LABELS, 
    )


    r.to_html(f"./maps/column_layer_{ele}.html")