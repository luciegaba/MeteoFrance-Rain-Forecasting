import h3
import plotly.graph_objects as go

def plot_hexagons_on_mapbox(stations, hex_resolution=7, color='red'):
    # Create a list of unique hexagons
    hexagons = stations['h3_hex_id'].unique().tolist()

    # Create a list of GeoJSON features for the hexagons
    hexagon_features = []
    for hex in hexagons:
        polygon = h3.h3_to_geo_boundary(hex, geo_json=True)
        hexagon_feature = {"type": "Feature",
                           "geometry": {"type": "Polygon", "coordinates": [polygon]}}
        hexagon_features.append(hexagon_feature)

    # Create a GeoJSON FeatureCollection from the hexagon features
    hexagon_collection = {"type": "FeatureCollection", "features": hexagon_features}

    # Create a list of trace objects for the hexagons
    hexagon_traces = []
    for feature in hexagon_collection['features']:
        trace = go.Scattermapbox(
            lat=[feature['geometry']['coordinates'][0][i][1] for i in range(7)],
            lon=[feature['geometry']['coordinates'][0][i][0] for i in range(7)],
            mode='lines',
            line=dict(width=1, color=color),
            fill='none',
            showlegend=False,
            hoverinfo='none')
        hexagon_traces.append(trace)

    # Create a trace object for the stations
    station_trace = go.Scattermapbox(
        lat=stations['lat'],
        lon=stations['lon'],
        mode='markers',
        showlegend=False,
        marker=dict(size=3, color='black', opacity=0.5),
        hoverinfo='text',
        text=stations['number_sta'])

    # Create a layout object for the map
    layout = go.Layout(mapbox_style="open-street-map",mapbox_zoom=4,  # Set the initial zoom level
        mapbox_center={"lat": stations['lat'].mean(), "lon": stations['lon'].mean()})

    # Create a figure object and add the traces and layout
    fig = go.Figure(data=hexagon_traces + [station_trace], layout=layout)

    # Show the figure
    fig.show()
