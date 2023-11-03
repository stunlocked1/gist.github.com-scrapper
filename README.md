# gist.github.com-scrapper
can search and download public gists.

`download_query_gists` is the main function, it has all of the stuff explained


    Searches for `query` on gist.github.com and downloads first `count` gists as strings, returns list of strings.
    
    `query` - what will be searched for on gist.github.com
    
    `count` - how many gists to download
    
    `exact` - if True, adds `"` to start and end of query if it doesn't already have them, which causes github to search for exact matches.
    
    `sorting` - sorting method. Empty string for "Best match", `stars` for most/fewest stars, `forks` for most/fewest forks, `updated` for recently/least recently updated
    
    `order` - sort by ascending or descending order - `asc` or `desc`.
    
    `mp` - if `True`, uses multiprocessing instead of multithreading, so make sure to avoid recursive forking if you set this to `True`
    
    `poolsize` - pool size for multithreading/multiprocessing when downloading gists.
    
    `pagepoolsize` - pool size for multithreading/multiprocessing when downloading result pages.

