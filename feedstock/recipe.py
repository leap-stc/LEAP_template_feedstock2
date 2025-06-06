"""Example recipe"""

import xarray as xr
from distributed import Client
import dask

client = Client()


""" 

Note: there are lots of ways to create a Zarr store from a collection of archival files.
Chat with the data and compute team if you have questions. A couple of rough guidelines to consider: 

- Is the data accessible by HTTP? What is the minimal reproducible example for loading a tiny subset of the data? 
Often, it might be easieet to prototype ingestion by loading subsets in a Jupyter Notebook to experiment with methods. 
- Is the data divided into multiple files? If so, how many and what is their average size. 
Performance wise, loading a few very large files suggests a very different approach than thousands of small ones! 

"""




## let's say I have daily outputs saved at various links. Define how to get each one. 
@dask.delayed
def get_url(time):
    # return f"http://data-provider.org/data/{variable}/{variable}_{time:02d}.nc" 
    # TO DO: put logic for accessing each file, i.e. input_urls = ['https://<data-provider>/../../<file1.nc>']

urls = [get_url(time) for time in range(1, 10)]

@dask.delayed
def open_dataset(url):
    # The example here opens up a collection of file urls with Xarray's open_mfdataset
    # which.. can be difficult for very large datasets.
    """
    ds = xr.open_mfdataset(
        input_urls, chunks={}, parallel=True, 
        coords='minimal', data_vars='minimal', compat='override'
    )
    """

    # TODO : put logic for loading single URL


    # TODO : add logic for any processing (renaming dimensions, adding metadata, cleaning)

    # Note: Chunking your dataset is important for your analysis use case! ie. time-series vs spatial analysis
    # A good rule of thumb 100MB chunk sizes.
    return ds

datasets = [open_dataset(url) for url in urls]

## Aggregate the datasets

# aggregated_ds = xr.concat(datasets, dim='time')


# aggregated_ds.compute() # dask scheduler

# Good practice is trying to build a smaller Zarr from a subset of your inputs files for testing.
# Note: This writes to leap-scratch. Once we all feel good about the recipe, we can write to leap-persistant.
aggregated_ds.to_zarr(
    'gs://leap-scratch/<your_user_name>/<dataset_name.zarr>',
    zarr_format=3,
    consolidated=False,
    mode='w',
)
