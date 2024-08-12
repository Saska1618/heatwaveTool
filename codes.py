import xarray as xr

netcdf_file = './data/tg_ens_mean_0.1deg_reg_2011-2023_v29.0e.nc'

xrds = xr.open_dataset(netcdf_file)

# dimensions = xrds.dims

variables = xrds.data_vars['tg']