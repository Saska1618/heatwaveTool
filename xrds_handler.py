import xarray as xr

class XRDS_handler:
    def __init__(self, filename):

        if filename is None:
            raise ValueError

        self.netcdf_file = filename
        self.xrds = xr.open_dataset(self.netcdf_file)

        self.attributes = self.xrds.attrs
        self.variables = self.xrds.data_vars

    def get_attrs(self):
        return self.attributes
    
    def get_variable_names(self):
        return [key for key in self.variables]

    def get_latlon_matrix_at_given_time(self, variable, given_time):
        if given_time is None or variable is None:
            raise ValueError
        
        return self.xrds[variable].sel(time=given_time)
