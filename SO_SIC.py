# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Install libraries 
!pip -q install imageio-ffmpeg

import os, glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import imageio.v2 as imageio
import xarray as xr


# Path
DATA_DIR  = "/content/drive/MyDrive/YourPath"
CACHE_DIR = "/content/sic_cache_npy"
OUT_MP4   = "/content/SIC_seasons_yearly.mp4"


# Seasons (must match cache filenames)
SEASONS = [
    ("Summer (DJF)", "summer"),
    ("Autumn (MAM)", "autumn"),
    ("Winter (JJA)", "winter"),
    ("Spring (SON)", "spring"),
]


# Downsample for plotting ONLY
LAT_STEP = 2
LON_STEP = 10


# Timing
SECONDS_PER_YEAR = 2
FPS = 10                         # smooth enough
FRAMES_PER_YEAR = SECONDS_PER_YEAR * FPS


# Get lat/lon grid from one NetCDF file
rep_files = sorted(glob.glob(os.path.join(DATA_DIR, "OSTIA_sea_ice_fraction_????.nc")))
nrt_files = sorted(glob.glob(os.path.join(DATA_DIR, "OSTIA_NRT_sea_ice_fraction_*.nc")))
files = rep_files + nrt_files
if not files:
    raise FileNotFoundError("No SIC NetCDF files found in DATA_DIR.")

tmp = xr.open_dataset(files[0], engine="h5netcdf", decode_times=True)
lat = tmp["latitude"].values
lon = tmp["longitude"].values
tmp.close()

lat_ds = lat[::LAT_STEP]
lon_ds = lon[::LON_STEP]
lon2, lat2 = np.meshgrid(lon_ds, lat_ds)


# Find years available in cache
def cache_path(season_short, year):
    return os.path.join(CACHE_DIR, f"{season_short}_{year}.npy")

summer_files = glob.glob(os.path.join(CACHE_DIR, "summer_*.npy"))
if not summer_files:
    raise FileNotFoundError("No cache files found. Make sure /content/sic_cache_npy exists.")

years = sorted({int(os.path.basename(fp).split("_")[1].split(".")[0]) for fp in summer_files})
print("Years:", len(years), years[0], "→", years[-1])
print("Total video seconds:", len(years) * SECONDS_PER_YEAR)


# Polar axis helper (circular)
def polar_ax(fig, nrows, ncols, idx):
    proj = ccrs.SouthPolarStereo()
    ax = fig.add_subplot(nrows, ncols, idx, projection=proj)

    theta = np.linspace(0, 2*np.pi, 200)
    center = [0.5, 0.5]
    radius = 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T
    circle = mpath.Path(verts * radius + center)
    ax.set_boundary(circle, transform=ax.transAxes)

    ax.set_extent([-180, 180, -90, -60], ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND, facecolor="0.8", zorder=1)
    ax.coastlines(linewidth=0.6)

    lon_grid = [-180, -140, -100, -60, -20, 20, 60, 100, 140]
    lat_grid = [-60, -70, -80]
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
                      linewidth=0.5, linestyle=":", color="black", zorder=4)
    gl.xlocator = mticker.FixedLocator(lon_grid)
    gl.ylocator = mticker.FixedLocator(lat_grid)

    edge_lat = -57.0
    for L in lon_grid:
        text = f"{abs(L)}°W" if L < 0 else (f"{L}°E" if L > 0 else "0°")
        ax.text(L, edge_lat, text, transform=ccrs.PlateCarree(),
                ha="center", va="center", fontsize=6, fontweight="bold")
    for La in [-70, -80]:
        ax.text(0, La, f"{abs(La)}°S", transform=ccrs.PlateCarree(),
                ha="center", va="center", fontsize=6, fontweight="bold")
    return ax



# Build ONE figure once, reuse pcolormesh (1080p)
fig = plt.figure(figsize=(16, 9), dpi=120)    # ~1920x1080
axs = [polar_ax(fig, 2, 2, i) for i in range(1, 5)]

cmap = "turbo"
vmin, vmax = 0, 100

pcms = []
for ax, (title, _) in zip(axs, SEASONS):
    pcm = ax.pcolormesh(
        lon2, lat2, np.full(lon2.shape, np.nan, dtype=np.float32),
        transform=ccrs.PlateCarree(),
        cmap=cmap, vmin=vmin, vmax=vmax
    )
    ax.set_title(title, fontsize=12, fontweight="bold", y=1.06)
    cb = fig.colorbar(pcm, ax=ax, shrink=0.78, pad=0.06)
    cb.set_label("SIC (%)", fontsize=9, fontweight="bold")
    pcms.append(pcm)

supt = fig.suptitle("Year: ----", fontsize=16, fontweight="bold", y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])


# Write MP4 (pause/play works)
writer = imageio.get_writer(OUT_MP4, fps=FPS, codec="libx264", quality=8)

for y in years:
    # load 4 season arrays once per year
    year_maps = []
    for _, short in SEASONS:
        fp = cache_path(short, y)
        if os.path.exists(fp):
            arr = np.load(fp)
            arr_ds = arr[::LAT_STEP, ::LON_STEP]
        else:
            arr_ds = np.full(lon2.shape, np.nan, dtype=np.float32)
        year_maps.append(arr_ds)

    supt.set_text(f"SIC Seasonal Mean (%)  |  Year: {y}")
    for pcm, arr_ds in zip(pcms, year_maps):
        pcm.set_array(arr_ds.ravel())

  
    # render once, then repeat the same frame FRAMES_PER_YEAR times
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    img = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(h, w, 4)[:, :, :3]

    for _ in range(FRAMES_PER_YEAR):
        writer.append_data(img)

    print("Wrote year:", y)

writer.close()
plt.close(fig)

print("✅ Saved MP4:", OUT_MP4)
