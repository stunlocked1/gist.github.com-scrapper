import urllib.request, multiprocessing, random, http.client

def parse(url):
    broken_URL = False
    try:
        if url == 'ang=': return
        for i in range(3):
            try:
                results = urllib.request.urlopen(url).read().decode("utf-8")
                break
            except (http.client.IncompleteRead, ValueError): 
                print(f'{url} failed during attempt {i}')
                if i == 2: broken_URL = True
        if broken_URL is True: return
        s = results.find('<a href="/') + 100
        s = results.find('<a href="/', s) + len('<a href="')
        e = results.find('"', s)
        #print(s, e, results[s:e])
        url = 'https://gist.githubusercontent.com/' + results[s:e]
        if url == 'ang=': return
        for i in range(3):
            try:
                results = urllib.request.urlopen(url).read().decode("utf-8")
                break
            except http.client.IncompleteRead: print(f'{url} failed during attempt {i}')
        print(f'{url}')
        return results
    except http.client.IncompleteRead: return

def log_find(log, start, end, index=1):
    s = 0
    for _ in range(index):
        s = log.find(start, s) + len(start)
        e = log.find(end, s)
        #print(_, s, e, log[s:e])
        result = log[s:e]
        s += e-s
    return result

def mc(log):
    """returns [0] minecraft ver, [1] loader ver, [2] mods count, [3] mods"""
    if '[main/INFO]: Loading Minecraft' in log:
        minecraft = log_find(log, '[main/INFO]: Loading Minecraft ', ' with ')
        loader = log_find(log, ' with ', '\n')
        mods_count = log_find(log, '[main/INFO]: Loading ', ' mods:', index=2)
        mods = log_find(log, ' mods:', '[')
        return minecraft, loader, mods_count, mods
        
def mc_modcount(gists):
    """returns tuple of lists: [0] - mod id, [1] - mod id count, [2] - mod id+version, [3] - mod id+version count"""
    ids = []
    c_ids =[]
    ids_v = []
    c_ids_v = []
    for i in gists:
        if i == None: continue
        mods = mc(i)[3].split('\n')
        for i in mods:
            #print(i)
            if '| Index | Mod' in i or '|------' in i: continue
            if '|' in i:
                mod_id = log_find(i, '| ', ' ', 3)
                mod_ver = log_find(i, '| ', ' ', 4)
            else:
                mod_id = log_find(i, '- ', ' ')
                mod_ver = log_find(i, mod_id + ' ', ' ')

            if ' ' in mod_id or mod_id=='': continue
            if mod_id in ids:
                c_ids[ids.index(mod_id)] +=1
            else: 
                ids.append(mod_id)
                c_ids.append(1)
                
            if mod_id+' '+mod_ver in ids_v:
                c_ids_v[ids_v.index(mod_id+' '+mod_ver)] +=1
            else: 
                ids_v.append(mod_id+' '+mod_ver)
                c_ids_v.append(1)
    return ids, c_ids, ids_v, c_ids_v

def mc_top20(gists):
    """prints top20 without and top20 with version"""
    ids, c_ids, ids_v, c_ids_v = mc_modcount(gists)
    ids = [x for _, x in sorted(zip(c_ids, ids))]
    ids.reverse()
    c_ids.sort(reverse=True)
    ids_v = [x for _, x in sorted(zip(c_ids_v, ids_v))]
    ids_v.reverse()
    c_ids_v.sort(reverse=True)
    #print(c_ids)
    print('TOP 20 ignoring verions:')
    for i in range(min(len(c_ids), 20)):
        print(f'{c_ids[i]} - {ids[i]}')
    print()
    print('TOP 20 by verion:')
    for i in range(min(len(c_ids_v), 20)):
        print(f'{c_ids_v[i]} - {ids_v[i]}')

if __name__ == '__main__':
    #print(__name__, __name__=='__main__')

    gists=[]
    query = input('Query: ')
    pages = int(input('How many pages to parse? '))
    linksg=[]
    for page in range(pages):
        broken_URL = False
        links = []
        for i in range(3):
            try:
                results = urllib.request.urlopen(f'https://gist.github.com/search?p={page}&q={query.replace(" ","+")}').read().decode("utf-8") 
                break
            except http.client.IncompleteRead: 
                print(f'{page+1} failed during attempt {i}')
                broken_URL = True
        if broken_URL is True:
            break
        if 'We couldn’t find any gists matching' in results: 
            if page == 0: print(f'No results found for {query}')
            break
        print(f'Page {page+1} downloaded')
        s=0
        for i in range(10):
            s = results.find('<a class="link-overlay" href="', s) + len('<a class="link-overlay" href="')
            e = results.find('"', s)
            if results[s:e] not in linksg: 
                links.append(results[s:e])
                linksg.append(results[s:e])
            s += e-s
        #print(links)
        if len(links)>0:
            with multiprocessing.Pool(10) as p:
                gist = p.map(parse, links)

            gists.extend(gist)

    mc_top20(gists)