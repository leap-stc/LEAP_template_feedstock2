"""
A synthetic prototype recipe
"""

import apache_beam as beam
from leap_data_management_utils.data_management_transforms import (
    get_catalog_store_urls,
)
from pangeo_forge_recipes.patterns import pattern_from_file_sequence
from pangeo_forge_recipes.transforms import (
    ConsolidateDimensionCoordinates,
    ConsolidateMetadata,
    OpenURLWithFSSpec,
    OpenWithXarray,
    StoreToZarr,
)
import xarray as xr

# parse the catalog store locations (this is where the data is copied to after successful write (and maybe testing)
catalog_store_urls = get_catalog_store_urls('feedstock/catalog.yaml')

###########################
## Start Modifying here ###
###########################

## Monthly version
input_urls_a = [
    'gs://cmip6/pgf-debugging/hanging_bug/file_a.nc',
    'gs://cmip6/pgf-debugging/hanging_bug/file_b.nc',
]


file_pattern = pattern_from_file_sequence(input_urls_a, concat_dim='time')

class Proprocess(beam.PTransform):
    @staticmethod
    def _process_func(ds: xr.Dataset) -> xr.Dataset:
        # add any processing logic here
        return ds

    def expand(self, pcoll: beam.PCollection) -> beam.PCollection:
        return pcoll | "open and process file" >> beam.MapTuple(
            lambda k, v: (k, self._process_func(v))
        )


small = (
    beam.Create(file_pattern.items())
    | OpenURLWithFSSpec()
    | OpenWithXarray()
    | StoreToZarr(
        # Make sure to change this name!
        store_name='<name_of_your_dataset>.zarr',
        # Note:  This name must exactly match the name in meta.yaml
        combine_dims=file_pattern.combine_dim_keys,
        # Note: You can modify the chunking structure here. Ex: {'time':-1, 'lat':180, 'lon':360}
        # You should aim for 100MB chunks
        target_chunks={},
    )
    | ConsolidateDimensionCoordinates()
    | ConsolidateMetadata()
)
