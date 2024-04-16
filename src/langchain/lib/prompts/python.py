PYTHON_CHECKLIST = """Checklist when generating Python code for GIS-tasks: 
    - All input data uses is EPSG:4326 (WGS84). Use the appropriate UTM projection when working with distances, area etc.
    - ALWAYS save results as GeoJSON in EPSG:4326 (WGS84) 
    - Do not forget to import both geopandas (gpd) and pandas (pd), when using both
    - Using SQL when reading very large files (bbox query, etc.): `gdf = gpd.read_file(shapefile_path, bbox=(10.3457, 63.3983, 10.4217, 63.4405))`
"""
