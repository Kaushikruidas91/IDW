import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
import numpy as np
from shapely.geometry import Point
from scipy.spatial import cKDTree
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

# Load point shapefile (must have 'Tmean' column)
points_gdf = gpd.read_file("C:/AgriWork/CHF Work Wheat/Wheat Strata code Work/Temperature_2km_IDW/abcd_ballia.shp")
points_gdf = points_gdf.to_crs(epsg=4326)  # or match your extent CRS

# Load extent polygon shapefile
extent_gdf = gpd.read_file("C:/AgriWork/District_Boundary_Seperately_UP/Boundary/Dist_Boundary_ballia.shp")
extent_gdf = extent_gdf.to_crs(points_gdf.crs)

# Get bounds
minx, miny, maxx, maxy = extent_gdf.total_bounds

# Set resolution (2km ~ 0.018 degrees approx at equator)
res = 0.018
grid_x, grid_y = np.meshgrid(
    np.arange(minx, maxx, res),
    np.arange(miny, maxy, res)
)

# Prepare input for IDW
xy = np.array([points_gdf.geometry.x, points_gdf.geometry.y]).T
z = points_gdf["grid_code"].values

# Distance-based weight interpolation
def idw(x, y, z, xi, yi, power=2):
    grid_z = np.zeros_like(xi)
    for i in range(xi.shape[0]):
        for j in range(xi.shape[1]):
            d = np.sqrt((x - xi[i, j])**2 + (y - yi[i, j])**2)
            w = 1 / (d ** power + 1e-12)
            grid_z[i, j] = np.sum(w * z) / np.sum(w)
    return grid_z

interp = idw(xy[:, 0], xy[:, 1], z, grid_x, grid_y)

# Mask outside the polygon
from shapely.geometry import box
from rasterio.features import geometry_mask

transform = from_origin(minx, maxy, res, res)
height, width = interp.shape
polygon_mask = geometry_mask([extent_gdf.unary_union],
                              transform=transform,
                              invert=True,
                              out_shape=interp.shape)

interp[~polygon_mask] = np.nan

output_path = "C:/AgriWork/CHF Work Wheat/Wheat Strata code Work/Temperature_2km_IDW/Ballia_Tmean_IDW_2km.tif"

with rasterio.open(
    output_path,
    "w",
    driver="GTiff",
    height=interp.shape[0],
    width=interp.shape[1],
    count=1,
    dtype=interp.dtype,
    crs="EPSG:4326",
    transform=transform,
    nodata=np.nan
) as dst:
    dst.write(interp, 1)

print(f"✅ IDW interpolation exported as: {output_path}")

