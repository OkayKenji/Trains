
import pandas as pd
import pydeck as pdk

elements = ["ace","exo","lirr","marc","metrolink","mnrr","nicd","njt","septa","trirail","vre","mbta","sunrail","amtrak","sle","hl","go","via","rtd/RTD_Denver_Direct_Operated_Commuter_Rail_GTFS", "rtd/RTD_Denver_Purchased_Transportation_Commuter_Rail_GTFS","metra"]
for ele in elements:
    # Get stops and their info
    df = pd.read_csv(f'./data/csv/{ele}.csv') # assuming running form root
    df_ref = pd.read_csv(f'./gtfs_data/{ele}/stops.txt')
    
    # Clean and calculate max trains per stop
    df.drop('Unnamed: 0', axis=1, inplace=True)
    row_stop_counts = df.drop(columns=["stop_name"]).notna().sum(axis=1)
    df_ref['height'] = row_stop_counts
    df_ref['stop_lat'] = df_ref['stop_lat'].apply(pd.to_numeric, errors='coerce')

    # Generate map
    view = pdk.data_utils.compute_view(df_ref[["stop_lon", "stop_lat"]])
    view.pitch = 75
    view.bearing = 0

    print(df_ref[['stop_lat', 'stop_lon', 'height']].head())
    print(df_ref[['stop_lat', 'stop_lon', 'height']].isnull().sum())

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
        column_layer,
        initial_view_state=view,
        tooltip=tooltip,
        map_style=pdk.map_styles.DARK_NO_LABELS, 
    )


    r.to_html(f"./maps/column_layer_{ele}.html")