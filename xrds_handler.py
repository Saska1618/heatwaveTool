import xarray as xr

class XRDS_handler:
    def __init__(self, filename):

        if filename is None:
            raise ValueError

        self.netcdf_file = filename
        self.xrds = xr.open_dataset(self.netcdf_file)

        self.attributes = self.xrds.attrs
        self.variables = self.xrds.data_vars

        self.min_lat = min(self.xrds['tg']['latitude']).values.item() ## TODO
        self.max_lat = max(self.xrds['tg']['latitude']).values.item() ## TODO

        self.min_lon = min(self.xrds['tg']['longitude']).values.item() ## TODO
        self.max_lon = max(self.xrds['tg']['longitude']).values.item() ## TODO

    def get_attrs(self):
        return self.attributes
    
    def get_variable_names(self):
        return [key for key in self.variables]

    def get_latlon_matrix_at_given_time(self, variable, given_time):
        if given_time is None or variable is None:
            raise ValueError
        
        return self.xrds[variable].sel(time=given_time)
    
    def get_ds_at_spec_latlon(self, variable, lat, lon):
        if variable is None or lat is None or lon is None:
            raise ValueError
        
        return self.xrds[variable].sel(latitude=lat, longitude=lon, method='nearest')
    
    def get_minmax_latitude(self, variable='tg'):
        # if variable is None:
        #     raise ValueError
        
        return self.min_lat, self.max_lat
    
    def get_minmax_longitude(self, variable='tg'):
        # if variable is None:
        #     raise ValueError

        return self.min_lon, self.max_lon
    

