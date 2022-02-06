import csv
import xtools as xtools
import os
import sys

count=0
count_start=0
count_end=0
sufix=""
if len(sys.argv)>=2:
    count_start=int(sys.argv[1])
    sufix="-"+str(count_start)
if len(sys.argv)>=3:
    count_end=int(sys.argv[2])
    sufix+="-"+str(count_end)
num_q_p={}
prop_data={}
num_wikis={}
id_prop={}
prop={}
prop_stat={}
item_stat={}
wikidata_language={}

lang_stat={}
wiki_stat={}
item_wiki={}
matrix_langs_wikis={}
mapping_lang={}

top_n_langs=20
top_n_items=30



prefix="dataset-2022-01-13/"

# Read Wikidata items wikis-articles

with open(prefix+"wikidata-items-wikis-articles.csv") as data:
    exist_file=os.path.isfile(prefix+'results/wikidata-xtools-data'+sufix+'.csv')
    file_object = open(prefix+'results/wikidata-xtools-data'+sufix+'.csv', 'a')

    list_xtools_data=["project","characters","words","references","unique_references","sections","elapsed_time","watchers","pageviews","revisions","editors","minor_edits",
        "created_at","modified_at","links_ext_count","links_out_count","links_in_count","redirects_count"]

    if exist_file==False:
        file_object.write('item')
        for xtools_item in list_xtools_data:
            file_object.write(","+xtools_item)
        file_object.write("\n")


    for reg in csv.DictReader(data):
        count+=1
        if count>=count_start and (count_end==0 or count<=count_end):
            q=reg["item"].replace("http://www.wikidata.org/entity/","wd:")
            if not q in item_wiki:
                item_stat[q]={"item":""}
            item_stat[q]["item"]=q
            article=reg["article"].replace("https://","")
            query=article.split("/wiki/")
            try:
                inf=xtools.prose(query[0], query[1])
                inf.update(xtools.page.article_info(query[0], query[1]))
                inf.update(xtools.page.links(query[0], query[1]))
                print(count,q,reg["wiki"])
                file_object.write(q)
                for xtools_item in list_xtools_data:
                    file_object.write(",")
                    if xtools_item in inf:
                        file_object.write(str(inf[xtools_item]))
                file_object.write("\n")
            except KeyboardInterrupt:
                quit()
            except:
                file_object.write(q+","+query[0]+","+"ERROR\n")
                continue
quit()



# Write results of items wikis
with open(prefix+"results/results-items-wikis.csv","w") as file:
    sorted_wiki_stat=dict(sorted(wiki_stat.items(), reverse=True, key=lambda item: item[1]["num_items"]))
    print("wiki,num_items",file=file)
    for data in wiki_stat:
        print('"'+data+'",'+str(wiki_stat[data]["num_items"]),file=file)
file.close()



