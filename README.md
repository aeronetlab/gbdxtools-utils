# GBDXtools utilities

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