from h3 import h3
import json



def get_h3_components(df,hex_size=3):
    df['h3_hex_id'] = df.apply(lambda row: h3.geo_to_h3(row['lat'], row['lon'], hex_size), axis=1)
    df['geometry'] = df['h3_hex_id'].apply(lambda x: {"type": "Polygon",
                "coordinates":[h3.h3_to_geo_boundary(x, geo_json = True)]})
    
def get_geojson_from_h3(df):
    features = []
    for i, row in df.iterrows():
        feature = {"type": "Feature",
                   "geometry": row['geometry'],
                   "properties": {"h3_hex_id": row['h3_hex_id']}}
        features.append(feature)
    feature_collection = {"type": "FeatureCollection", "features": features}

    geojson_str = json.dumps(feature_collection)
    geojson_dict = json.loads(geojson_str)

    return geojson_dict