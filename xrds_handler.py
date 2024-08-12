import xarray as xr

class XRDS_handler:
    def __init__(self, filename):
        self.netcdf_file = filename
        self.xrds = xr.open_dataset(self.netcdf_file)

        self.attributes = self.xrds.attrs
        self.variables = self.xrds.data_vars

    def get_attrs(self):
        return self.attributes
    
    def get_variables(self):
        return self.variables