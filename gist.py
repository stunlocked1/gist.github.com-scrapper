import urllib.request, urllib.error, urllib.parse, http.client, multiprocessing, re, os, html, logging, time, random
from multiprocessing import dummy
#DOWNLOADED = "rimworld_scrapper/downloaded"
DOWNLOADED = None # If string, it will download gists to this location and load them from there instead of downloading if they've already been downloaded
logging.getLogger().setLevel(logging.INFO)

def between(string: str, start: str, end: str) -> str:
    """finds all occurences between start and end"""
    return re.findall(f'{re.escape(start)}(.*?){re.escape(end)}', string)

def download_url(url:str, tries = 3) -> str:
    """Downloads url, returns string with pages HTML"""
    assert url.startswith('https://'), f"`{url}` doesn't start with https://"
    errors = []
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})) as webpage:
                logging.info(f'Downloading `{url}`, trying for the {i} time...')
                content = webpage.read().decode("utf-8")
                return content
        except (http.client.IncompleteRead, ValueError) as e:
            errors.append(e)
        except urllib.error.HTTPError as e:
            errors.append(e)
            time.sleep(random.uniform(tries+1, (tries+1)*2))
    logging.error(f'Failed to load `{url}`, tried {tries} times:\n{errors}')

def download_urls(urls:list, poolsize = 4, mp = False) -> [str]:
    """Downloads all urls in a list using multithreading/multiprocessing, returns list of HTML strings"""
    if mp:
        with multiprocessing.Pool(min(poolsize, len(urls))) as p:
            logging.info(f'multiprocessing downloading URLs: {urls}')
            results = p.map(download_url, urls)
    else:
        with dummy.Pool(min(poolsize, len(urls))) as p:
            logging.info(f'multithreaded downloading URLs: {urls}')
            results = p.map(download_url, urls)
    return results


def download_gist(url: str, cache=DOWNLOADED) -> str:
    """Downloads a github gist, returns string. Also if `cache` is not None or False, saves gist to `cache` folder, and loads it instead of downloading if it already exists there."""
    assert url.startswith('https://gist.github.com/'), f'`{url}` doesn\'t start with https://gist.github.com/'
    source = url.replace('https://gist.github.com/', '').replace('/', ' ')
    if cache:
        if f'{source}.log' in os.listdir(cache):
            with open(f'{cache}/{source}.log', 'r', encoding='utf8') as f: return f.read()

    text = download_url(url)
    with open('test.html', 'w', encoding = 'utf8') as f: f.write(text)
    raw_url = between(text, '<a href="', '" data-view-component="true"')[0]
    contents = download_url(f'https://gist.githubusercontent.com/{raw_url}')
    if cache:
        with open(f'{cache}/{source}.log', 'w', encoding='utf8') as f: f.write(contents)
    return contents

def download_gists(urls: [str], poolsize = 4, mp = False) -> [str]:
    """downloads list of github gists using multithreading/multiprocessing, returns list of strings."""
    if mp:
        with multiprocessing.Pool(min(poolsize, len(urls))) as p:
            results = p.map(download_gist, urls)
    else:
        with dummy.Pool(min(poolsize, len(urls))) as p:
            results = p.map(download_gist, urls)
    return results

def download_query_page(query: str, page: int, sorting = 'updated', order = 'desc') -> str:
    """Searches for `query` on gist.github.com and downloads `page`-th results page."""
    safe = ' "'
    return download_url(f'https://gist.github.com/search?o={order}&p={page}&q={urllib.parse.quote(query, safe=safe).replace(" ","+")}&s={sorting}')

def get_gist_urls_from_page(page: str) -> [str]:
    """Get a list with links to all gists on the results page so that you can download actual gists"""
    fil = '/ <a href="[^"]*"'
    #logging.info([f'https://gist.github.com/{i[12:-1]}' for i in re.findall(fil, page)])
    return [f'https://gist.github.com/{i[12:-1]}' for i in re.findall(fil, page)]

def download_query_gists(query: str, count = 100, exact = False, sorting = 'updated', order = 'desc', mp = False, poolsize = 10, pagepoolsize = 10) -> [str]:
    """Searches for `query` on gist.github.com and downloads first `count` gists as strings, returns list of strings.
    
    `query` - what will be searched for on gist.github.com
    
    `count` - how many gists to download
    
    `exact` - if True, adds `"` to start and end of query if it doesn't already have them, which causes github to search for exact matches.
    
    `sorting` - sorting method. Empty string for "Best match", `stars` for most/fewest stars, `forks` for most/fewest forks, `updated` for recently/least recently updated
    
    `order` - sort by ascending or descending order - `asc` or `desc`.
    
    `mp` - if `True`, uses multiprocessing instead of multithreading, so make sure to avoid recursive forking if you set this to `True`
    
    `poolsize` - pool size for multithreading/multiprocessing when downloading gists.
    
    `pagepoolsize` - pool size for multithreading/multiprocessing when downloading result pages."""
    if exact and not(query.startswith('"') and query.endswith('"')): query = f'"{query}"'
    query_url = urllib.parse.quote(query, safe=' "').replace(" ","+")

    # get 1st page
    logging.info(f'download_query_gists: Downloading first results page: `{query_url}`')
    first_page = download_query_page(query, 1, sorting, order)

    # get page count
    page_count = between(first_page, 'data-total-pages="', '"')[0]
    logging.info(f'download_query_gists: total page count = {page_count}')
    page_count = min(int(page_count), count // 10 + (count % 10 != 0))
    logging.info(f'download_query_gists: page_count = {page_count}')

    # multithreaded download result pages
    page_urls = [f'https://gist.github.com/search?o={order}&p={i}&q={query_url}&s={sorting}' for i in range(1, page_count + 1)]
    logging.info(f'download_query_gists: Downloading {page_count} pages with pool size = {pagepoolsize}: {page_urls}')
    pages = download_urls(page_urls, pagepoolsize, mp)
    
    # get urls
    urls = []
    for i in pages: urls.extend(get_gist_urls_from_page(i))

    logging.info(f'download_query_gists: Downloading {count} gists with pool size = {poolsize}: {urls[:count]}')
    gists = download_gists(urls[:count], poolsize = poolsize, mp = mp)
    return gists