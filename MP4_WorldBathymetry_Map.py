# Mount Drive
from google.colab import drive
drive.mount('/content/drive')



#install Library 
!apt-get -qq update
!apt-get -qq install -y ffmpeg
!pip -q install cartopy netCDF4 matplotlib




# ONTINUOUS ROTATING GEBCO MP4
import os
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.colors import LinearSegmentedColormap
import cartopy.crs as ccrs


# FILE PATHS
nc_path = "/content/drive/MyDrive/YourFile/Bathymetry/GEBCO_2026_Global/unzipped/GEBCO_2026.nc"  #this need to edit as your path 

OUT_DIR = "/content/drive/MyDrive/YourFile/Map"
os.makedirs(OUT_DIR, exist_ok=True)

OUT_MP4 = f"{OUT_DIR}/GEBCO_2026_Global_Bathymetry_Slow_Continuous_Rotation.mp4"


# SETTINGS=
STRIDE = 60

FRAMES_PER_ROTATION = 240
ROTATIONS = 4
N_FRAMES = FRAMES_PER_ROTATION * ROTATIONS

FPS = 15
DPI = 180

print("Total frames:", N_FRAMES)
print("Video duration:", round(N_FRAMES / FPS, 2), "seconds")



# LOAD GEBCO DATA
with Dataset(nc_path) as nc:
    lon = np.array(nc.variables["lon"][::STRIDE], dtype=np.float32)
    lat = np.array(nc.variables["lat"][::STRIDE], dtype=np.float32)
    elev_raw = nc.variables["elevation"][::STRIDE, ::STRIDE]

elev = np.ma.filled(elev_raw, np.nan).astype(np.float32)

print("Loaded GEBCO:")
print("lon shape:", lon.shape)
print("lat shape:", lat.shape)
print("elev shape:", elev.shape)


# TOPO-BATHY COLORMAP
colors = [
    (0.00, "#031525"),
    (0.10, "#063263"),
    (0.22, "#075c9f"),
    (0.34, "#1389c9"),
    (0.44, "#63c6e7"),
    (0.50, "#e2f8ff"),
    (0.505, "#d8cba6"),
    (0.62, "#b59b62"),
    (0.75, "#80633b"),
    (0.88, "#aaa49a"),
    (1.00, "#ffffff")
]

cmap = LinearSegmentedColormap.from_list("gebco_topobathy", colors)

vmin = -11000
vmax = 8000


# CREATE MP4
fig = plt.figure(figsize=(12.8, 7.2), facecolor="black")

writer = FFMpegWriter(
    fps=FPS,
    metadata={"title": "GEBCO 2026 Global Bathymetry"},
    bitrate=9000,
    extra_args=[
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart"
    ]
)

longitudes = np.linspace(
    -180,
    -180 + 360 * ROTATIONS,
    N_FRAMES,
    endpoint=False
)

print("Creating slow continuous MP4...")

with writer.saving(fig, OUT_MP4, dpi=DPI):

    for i, clon in enumerate(longitudes):

        fig.clf()
        fig.patch.set_facecolor("black")

        ax = fig.add_axes(
            [0.02, 0.04, 0.80, 0.92],
            projection=ccrs.Orthographic(
                central_longitude=clon,
                central_latitude=15
            )
        )

        ax.set_global()
        ax.set_facecolor("black")

        try:
            ax.spines["geo"].set_edgecolor("white")
            ax.spines["geo"].set_linewidth(0.9)
        except Exception:
            pass

        mesh = ax.pcolormesh(
            lon,
            lat,
            elev,
            transform=ccrs.PlateCarree(),
            cmap=cmap,
            shading="auto",
            vmin=vmin,
            vmax=vmax
        )

        ax.coastlines(
            resolution="110m",
            color="white",
            linewidth=0.35
        )

        ax.gridlines(
            color="white",
            alpha=0.15,
            linewidth=0.35,
            linestyle="--"
        )

        cax = fig.add_axes([0.855, 0.22, 0.025, 0.56])

        cb = fig.colorbar(
            mesh,
            cax=cax,
            orientation="vertical"
        )

        cb.set_label(
            "Elevation / Depth (m)",
            color="white",
            fontsize=10,
            labelpad=10
        )

        cb.ax.tick_params(
            colors="white",
            labelsize=8
        )

        cb.outline.set_edgecolor("white")

        writer.grab_frame()

        print(f"Frame {i+1}/{N_FRAMES}")

print("MP4 saved successfully:")
print(OUT_MP4)
