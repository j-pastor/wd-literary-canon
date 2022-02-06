import requests
import xtools as xtools
from math import log
import asyncio
import aiohttp
import json


async def get(url, session):
    global n_words
    global count
    # try:
    async with session.get(url=url) as response:
        try:
            resp = await response.read()
            string=str(resp)[2:-1]
            inf=json.loads(string)
            n_words+=inf["words"]
        except:
            pass
        # except Exception as e:
        # print("Unable to get url {} due to {}.".format(url, e.__class__))


async def main(urls):
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get(url, session) for url in urls])



url=""

items=["Q2288360"]


for item in items:
    list_id_props=[]
    sparql_id_props="SELECT DISTINCT ?prop_id WHERE {?prop_id wdt:P31/wdt:P279*  wd:Q19847637 .}"
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
    data = requests.get(url, params={'query': sparql_id_props, 'format': 'json'}).json()
    for id_prop in data["results"]["bindings"]:
        list_id_props.append(id_prop["prop_id"]["value"].replace("http://www.wikidata.org/entity/",""))


    sparql_props='select ?prop WHERE {?p wikibase:directClaim ?prop . wd:'+item+' ?prop ?object.}'
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
    data = requests.get(url, params={'query': sparql_props, 'format': 'json'}).json()
    n_props=0
    for prop in data["results"]["bindings"]:
        if prop["prop"]["value"].replace("http://www.wikidata.org/prop/direct/","") not in list_id_props:
            n_props+=1


    sparql_sitelinks='SELECT DISTINCT ?article WHERE {wd:'+item+' ^schema:about ?article . FILTER (CONTAINS(str(?article),".wikipe"))}'
    url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
    data = requests.get(url, params={'query': sparql_sitelinks, 'format': 'json'}).json()

    urls=[]
    for sitelink in data["results"]["bindings"]:
        article=sitelink["article"]["value"]
        article=article.replace("https://","")
        query=article.split("/wiki/")
        urls.append("https://xtools.wmflabs.org/api/page/prose/"+query[0]+"/"+query[1])


    n_words=0
    n_wikis=len(data["results"]["bindings"])


    asyncio.run(main(urls))
    print("\n")
    print("Item: ",item)
    print("N-Wikis: ",n_wikis)
    print("N-Props: ",n_props)
    print("N-Words: ",n_words)
    print("WikiRank: ",log(1+n_props)+log(1+n_words)+log(1+n_wikis))
    print("\n")



'''

total_sitelinks=len(data["results"]["bindings"])
count=0
for sitelink in data["results"]["bindings"]:
    article=sitelink["article"]["value"]
    article=article.replace("https://","")
    query=article.split("/wiki/")
    try:
        # inf=xtools.prose(query[0], query[1])
        data=requests.get("https://xtools.wmflabs.org/api/page/prose/"+query[0]+"/"+query[1]).json()
        n_words+=data["words"]
        count+=1
        print("Sitelink",count,"/",total_sitelinks)
    except:
        continue

'''