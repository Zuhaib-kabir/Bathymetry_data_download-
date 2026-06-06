# Drive Mount
from google.colab import drive
drive.mount('/content/drive')





import os
# OUTPUT DIRECTORY
BASE_DIR = "/content/drive/MyDrive/YourPath"   # this need to edit as your path address 
OUT_DIR = f"{BASE_DIR}/Data/Bathymetry/GEBCO_2026_Global"

os.makedirs(OUT_DIR, exist_ok=True)


# GEBCO 2026 GLOBAL BATHYMETRY DOWNLOAD
URL = "https://dap.ceda.ac.uk/bodc/gebco/global/gebco_2026/ice_surface_elevation/netcdf/GEBCO_2026.zip?download=1"

ZIP_FILE = f"{OUT_DIR}/GEBCO_2026_Global_NetCDF.zip"

!apt-get -qq update
!apt-get -qq install -y aria2

!aria2c -x 8 -s 8 -c \
  -o "GEBCO_2026_Global_NetCDF.zip" \
  -d "{OUT_DIR}" \
  "{URL}"

print("Download finished:")
print(ZIP_FILE)





# Unzip the downloded file
import zipfile
import os

ZIP_FILE = "/content/drive/MyDrive/YourPath/Bathymetry/GEBCO_2026_Global/GEBCO_2026_Global_NetCDF.zip"
UNZIP_DIR = "/content/drive/MyDrive/YourPath/Bathymetry/GEBCO_2026_Global/unzipped"

os.makedirs(UNZIP_DIR, exist_ok=True)

with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
    zip_ref.extractall(UNZIP_DIR)

print("Unzipped files:")
for f in os.listdir(UNZIP_DIR):
    print(f)






# Check the downloded file 
import xarray as xr
import os

UNZIP_DIR = "/content/drive/MyDrive/YourPath/Bathymetry/GEBCO_2026_Global/unzipped"

nc_files = []
for root, dirs, files in os.walk(UNZIP_DIR):
    for file in files:
        if file.endswith(".nc"):
            nc_files.append(os.path.join(root, file))

print("NetCDF files found:")
print(nc_files)

ds = xr.open_dataset(nc_files[0])
print(ds)






# ploting code for Verifying
# install library 
!pip -q install cartopy netCDF4






# helper code 
import os
import zipfile

BASE_DIR = "/content/drive/MyDrive"
GEBCO_DIR = f"{BASE_DIR}/YourPath/Bathymetry/GEBCO_2026_Global"

ZIP_FILE = f"{GEBCO_DIR}/GEBCO_2026_Global_NetCDF.zip"
UNZIP_DIR = f"{GEBCO_DIR}/unzipped"

os.makedirs(UNZIP_DIR, exist_ok=True)

# Unzip only if needed
if os.path.exists(ZIP_FILE):
    if len(os.listdir(UNZIP_DIR)) == 0:
        print("Unzipping GEBCO file...")
        with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
            zip_ref.extractall(UNZIP_DIR)
    else:
        print("Already unzipped.")
else:
    print("ZIP file not found:", ZIP_FILE)

# Find NetCDF file
nc_files = []
for root, dirs, files in os.walk(UNZIP_DIR):
    for file in files:
        if file.endswith(".nc"):
            nc_files.append(os.path.join(root, file))

print("Found NetCDF files:")
for f in nc_files:
    print(f)

nc_path = nc_files[0]
print("\nUsing:")
print(nc_path)






#plot code

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset

import cartopy.crs as ccrs
import cartopy.feature as cfeature


# SETTINGS
OUT_DIR = f"{BASE_DIR}/Map"
os.makedirs(OUT_DIR, exist_ok=True)

OUT_PNG = f"{OUT_DIR}/GEBCO_2026_Global_Bathymetry_PlateCarree.png"

# Use lower resolution to avoid crash
# GEBCO native = 15 arc-second ~ 0.0041667 degree
# stride 60 gives ~0.25 degree global map
STRIDE = 60


# READ ONLY STRIDED DATA
with Dataset(nc_path) as nc:
    lon = nc.variables["lon"][::STRIDE]
    lat = nc.variables["lat"][::STRIDE]
    elev = nc.variables["elevation"][::STRIDE, ::STRIDE]

# Convert masked array to normal array
elev = np.array(elev, dtype=np.float32)

# Ocean depth positive: ocean = positive depth, land = NaN
depth = np.where(elev < 0, -elev, np.nan)

print("Longitude shape:", lon.shape)
print("Latitude shape:", lat.shape)
print("Depth shape:", depth.shape)
print("Depth min/max:", np.nanmin(depth), np.nanmax(depth))


# PLOT
fig = plt.figure(figsize=(16, 8.5), dpi=300)

ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()

# Bathymetry map
im = ax.pcolormesh(
    lon,
    lat,
    depth,
    transform=ccrs.PlateCarree(),
    shading="auto",
    cmap="Blues",
    vmin=0,
    vmax=6000
)

# Land and coastlines
ax.add_feature(cfeature.LAND, facecolor="lightgray", edgecolor="black", linewidth=0.3)
ax.add_feature(cfeature.COASTLINE, linewidth=0.4)
ax.add_feature(cfeature.BORDERS, linewidth=0.2)

# Gridlines
gl = ax.gridlines(
    draw_labels=True,
    linewidth=0.3,
    linestyle="--",
    alpha=0.5
)
gl.top_labels = False
gl.right_labels = False

# Colorbar
cbar = plt.colorbar(
    im,
    ax=ax,
    orientation="horizontal",
    pad=0.06,
    shrink=0.75
)
cbar.set_label("Ocean depth (m)", fontsize=11)

# Title
ax.set_title(
    "Global Bathymetry from GEBCO 2026",
    fontsize=16,
    fontweight="bold",
    pad=14
)

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
plt.show()

print("Saved map:")
print(OUT_PNG)









