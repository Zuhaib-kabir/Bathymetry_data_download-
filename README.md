# 🌊 GEBCO 2026 Global Bathymetry Data Download Pipeline

A Python-based automated workflow for downloading, validating, processing, visualizing, and creating an MP4 animation from **GEBCO 2026 Global Bathymetry and Topography** data.

This project enables efficient downloading of global bathymetry data without manually visiting the data website. It is designed for **Google Colab**, **Google Drive**, oceanographic research, marine mapping, and geospatial visualization.

---

## 📌 Overview

This repository provides a streamlined pipeline to:

* 📥 Download GEBCO 2026 global bathymetry data using Python
* 📦 Save the downloaded file directly to Google Drive
* 📂 Unzip and organize the NetCDF file
* ✅ Validate the downloaded NetCDF dataset
* 🌍 Create a global bathymetry verification map
* 🎥 Generate a rotating global bathymetry MP4 video

The workflow is useful for **oceanography, marine geoscience, bathymetric visualization, climate studies, GIS, and data-driven marine research**.

---

## ⚙️ Features

* Automated GEBCO 2026 global bathymetry download
* Download without manually visiting the website
* High-speed and resumable downloading using `aria2c`
* Google Drive-based data storage
* Automatic ZIP extraction
* NetCDF file validation
* Memory-safe plotting using `STRIDE`
* Global Plate Carrée bathymetry verification map
* Rotating Orthographic globe MP4 creation
* Output ready for research, presentation, and social media use

---

## 🛰️ Data Source

Dataset used:

**GEBCO 2026 Global Bathymetry and Topography Grid**

Download URL:

```text
https://dap.ceda.ac.uk/bodc/gebco/global/gebco_2026/ice_surface_elevation/netcdf/GEBCO_2026.zip?download=1
