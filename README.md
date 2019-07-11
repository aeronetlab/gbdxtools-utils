# GBDXtools utilities

### Loading example
```python
import os
import shutil
import logging
import datetime as dt
from gbdxtools_utils import (
    ImageryLoader,
    LoadStatus,
    ImagerySearcher,
    AreaOfInterest,
)

logger = logging.getLogger(__name__)

# GBDX_USERNAME and GBDX_PASSWORD env vars should be difined

searcher = ImagerySearcher(
    satellites=('WORLDVEIW02', 'WORLDVEIW03_VNIR'),
    max_cloud_cover=0,                                  # no clouds
    start_date=dt.date(2017, 1, 1),                     # imagery in range 01.01.2017 - now
)

loader = ImageryLoader(
    rda=True,
    pansharpen=True,
)

geojson = ... # load geojson


for feature in geojson["features"]:
    aoi = AreaOfInterest(geojson=feature)
    search_results = searcher.get(aoi=aoi)
    
    for result in search_results:
    
        dst_dir = ... # define dst dir
        os.makedirs(dst_dir)
        
        try:
            status = loader.load(
                image_id=result["identifier"],
                path=dst_dir,
                aoi=aoi,
                spec='rgb', # to load imagery in rgb
            )
        except Exception as e:
            status = LoadStatus.FAILED
            logger.exception(e)
        
        # remove directory if imagery is not loaded
        if status != LoadStatus.SUCCESS:
            shutil.rmtree(dst_dir) 
```

### API reference

#### 1) Searching utility

Search imagery in gbdx catalog. 

```python
gbdxtools_utils.ImagerySearcher
```
 
##### Support filters:
 - satellites
 - start/end date
 - cloud cover
 - nadir angle

other (str) filters according to gbdxtools docs

##### Methods:  
```python
    .get(aoi) 
    """
    Args:  
        - aoi (gbdxtools_utils.AreaOfInterest): area of interest  
        
    Return:  
        - List[dict]: each dict contain image metadata 
    """ 
``` 

#### 2) Loading utility

Load imagery and its meta and save on disk

```python
gbdxtools_utils.ImageryLoader
```

##### Parameters:

- cache_image_expiration_time: time to cache fetched image
- **image_params (pansharpen, dra, dtype, acomp, bands): image fetching parameters
    
##### Methods:  
```python
    .load(   
        image_id: str,
        path: str,
        aoi: aoi.AreaOfInterest = None,
        use_cache: bool = True,
        **load_kwargs,
    ) 
    """
    Args:  
        - image_id: catalog image id
        - path: direcotry to save `orthophoto.tif` and `meta.geojson` loaded files
        - aoi: area of interest
        - use_cache: - optional, use cached images or not
        - **load_kwargs: additional gbdx `.geotiff` method params (e.g. spec='rgb')
        
    Return:  
        - gbdxtools_utils.LoadStatus: loading status (success, fail, etc.)
    """ 
``` 