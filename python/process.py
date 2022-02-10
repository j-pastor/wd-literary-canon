import csv
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
import pandas as pd
from scipy.spatial.distance import cosine
from math import log

count=0
num_q_p={}
prop_data={}
num_wikis={}
prop_stat={}
item_stat={}
wikidata_language={}

lang_stat={}
wiki_stat={}
item_wiki={}
matrix_langs_wikis={}
matrix_langs_wikis_W3DRank={}
mapping_lang={}

top_n_langs=20
top_n_items=30

prefix="dataset-2022-01-13/"

# Read mapping languages
with open("mapping-lang.csv") as data:
    for reg in csv.DictReader(data):
        mapping_lang[reg["source_lang"]]=reg["target_lang"]

# Read Wikidata properties
with open(prefix+"wikidata-properties.csv") as data:
    for reg in csv.DictReader(data):
        p=reg["property"].replace("http://www.wikidata.org/entity/","wdt:")
        prop_stat[p]={"label":reg["propertyLabel"],"num":0,"isID":False,"descripcion":reg["propertyDescription"],"total_use":0,"top_wikis":0,"top_props":0,"top_words":0,"top_W3DRank":0}

# Read Wikidata ID properties
with open(prefix+"wikidata-id-properties.csv") as data:
    for reg in csv.DictReader(data):
        p=reg["prop_id"].replace("http://www.wikidata.org/entity/","wdt:")
        if p.startswith("wdt:P"):
            prop_stat[p]["isID"]=True

# Read Wikidata items properties
current=""
with open(prefix+"wikidata-items-properties.csv","r") as data:
    for reg in csv.DictReader(data):
        count+=1
        print(count,end="\r")
        q=reg["item"].replace("http://www.wikidata.org/entity/","wd:")
        p=reg["prop"].replace("http://www.wikidata.org/prop/direct/","wdt:")

        if q in item_stat:
            if prop_stat[p]["isID"]==True:
                item_stat[q]["num_id"]+=1
            else:
                item_stat[q]["num_non_id"]+=1
        else:
            item_stat[q]={}
            if prop_stat[p]["isID"]==True:
                item_stat[q]={"item":q, "title":"","title_bis":"","date":0,"date_type":0,"precision_date":0, "langs":{}, "wikis":{}, "props_id":{}, "props_non_id":{}, "num_id":1,"num_non_id":0, "num_langs":0, "num_wikis":0, "total_num_words":0, "W3DRank":0}
            else:
                item_stat[q]={"item":q, "title":"","title_bis":"","date":0,"date_type":0,"precision_date":0, "langs":{}, "wikis":{}, "props_id":{}, "props_non_id":{}, "num_id":0,"num_non_id":1, "num_langs":0, "num_wikis":0, "total_num_words":0, "W3DRank":0}

        if prop_stat[p]["isID"]==True:
            item_stat[q]["props_id"][p]=p

        if prop_stat[p]["isID"]==False:
            item_stat[q]["props_non_id"][p]=p


# Read Wikidata items dates
with open(prefix+"wikidata-items-dates.csv") as data:
    for reg in csv.DictReader(data):
        q=reg["item"].replace("http://www.wikidata.org/entity/","wd:")
        if reg["pub_date"]!="":
            if int(reg["pub_date"])>item_stat[q]["date"] or item_stat[q]["date"]==0:
                item_stat[q]["date"]=int(reg["pub_date"])
                item_stat[q]["date_type"]="p"
                item_stat[q]["precision_date"]=reg["precision_Date"]
        
        if reg["inception_date"]!="":
            if item_stat[q]["date_type"]!="p" and (int(reg["inception_date"])>item_stat[q]["date"] or item_stat[q]["date"]==0):
                item_stat[q]["date"]=int(reg["inception_date"])
                item_stat[q]["date_type"]="i"
                item_stat[q]["precision_date"]=reg["precision_Inception"]                


# Read Wikidata items titles
with open(prefix+"wikidata-items-titles.csv") as data:
    for reg in csv.DictReader(data):
        q=reg["item"].replace("http://www.wikidata.org/entity/","wd:")
        t=reg["label"].replace('"',"'")
        item_stat[q]["title"]=t
with open(prefix+"wikidata-items-titles-bis.csv") as data:
    for reg in csv.DictReader(data):
        q=reg["item"].replace("http://www.wikidata.org/entity/","wd:")
        t=reg["label"].replace('"',"'")
        if q in item_stat:
            item_stat[q]["title_bis"]=t

# Read Wikidata items languages
with open(prefix+"wikidata-items-languages.csv") as data:
    for reg in csv.DictReader(data):
        q=reg["item"].replace("http://www.wikidata.org/entity/","wd:")
        if reg["lang"]!="":
            l=reg["lang"].replace("http://www.wikidata.org/entity/","wd:")
            if reg["code_lang"]!="":
                code=reg["code_lang"].split("-")[0]
            else:
                if l in mapping_lang:
                    code=mapping_lang[l]
                else:
                    code=l
        else:
            code="<none>"


        item_stat[q]["langs"][code]=code
        item_stat[q]["num_langs"]+=1

        if code in lang_stat:
            lang_stat[code]["num_items"]+=1
        else:
            lang_stat[code]={"num_items":1,"total_wikis":0,"total_id_props":0,"total_props":0,"total_words":0,"total_W3DRank":0}


# Read Wikidata items wikis-articles
with open(prefix+"wikidata-items-wikis-articles.csv") as data:
    for reg in csv.DictReader(data):
        q=reg["item"].replace("http://www.wikidata.org/entity/","wd:")
        wiki=reg["wiki"]
        if not q in item_wiki:
            item_wiki[q]={}

        item_stat[q]["wikis"][wiki]=wiki
        item_stat[q]["num_wikis"]+=1

        item_wiki[q][len(item_wiki[q])]=wiki

        if wiki in wiki_stat:
            wiki_stat[wiki]["num_items"]+=1
        else:
            wiki_stat[wiki]={}
            wiki_stat[wiki]["num_items"]=1


# Read Wikipedia Xtools file
with open(prefix+"wikidata-xtools-data.csv") as data:
    for reg in csv.DictReader(data):
        if reg["characters"]!="ERROR":
            try:
                num_words=int(reg["words"])
                item_stat[reg["item"]]["total_num_words"]+=num_words
            except:
                print(reg)

for item in item_stat:
    nwi=item_stat[item]["num_wikis"]
    np=item_stat[item]["num_non_id"]
    nwo=item_stat[item]["total_num_words"]
    item_stat[item]["W3DRank"]=log(1+nwi)+log(1+np)+log(1+nwo)


##############
# Sort items #
##############
sorted_item_stat=dict(sorted(item_stat.items(), reverse=True, key=lambda item: item[1]["num_wikis"]))
sorted_props=dict(sorted(item_stat.items(), reverse=True, key=lambda item: item[1]["num_non_id"]))
sorted_words=dict(sorted(item_stat.items(), reverse=True, key=lambda item: item[1]["total_num_words"]))
sorted_W3DRank=dict(sorted(item_stat.items(), reverse=True, key=lambda item: item[1]["W3DRank"]))

############################
# Write props in top items #
############################

top=1000
total=len(sorted_item_stat)
print("\n",total)

dict_items_stat=sorted_item_stat.items()
dict_props=sorted_props.items()
dict_words=sorted_words.items()
dict_W3DRank=sorted_W3DRank.items()

selected_items = list(dict_items_stat)[:top]
selected_props = list(dict_props)[:top]
selected_words = list(dict_words)[:top]
selected_W3DRank = list(dict_W3DRank)[:top]


for item in item_stat:
    props=item_stat[item]["props_non_id"]
    for p in props:
        prop_stat[p]["total_use"]+=1
for i in range(len(selected_items)):
    props=selected_items[i][1]["props_non_id"]
    for p in props:
        prop_stat[p]["top_wikis"]+=1
    props=selected_props[i][1]["props_non_id"]
    for p in props:
        prop_stat[p]["top_props"]+=1
        props=selected_words[i][1]["props_non_id"]
    for p in props:
        prop_stat[p]["top_words"]+=1
        props=selected_W3DRank[i][1]["props_non_id"]
    for p in props:
        prop_stat[p]["top_W3DRank"]+=1


for item in item_stat:
    props=item_stat[item]["props_id"]
    for p in props:
        prop_stat[p]["total_use"]+=1
for i in range(len(selected_items)):
    props=selected_items[i][1]["props_id"]
    for p in props:
        prop_stat[p]["top_wikis"]+=1
    props=selected_props[i][1]["props_id"]
    for p in props:
        prop_stat[p]["top_props"]+=1
        props=selected_words[i][1]["props_id"]
    for p in props:
        prop_stat[p]["top_words"]+=1
        props=selected_W3DRank[i][1]["props_id"]
    for p in props:
        prop_stat[p]["top_W3DRank"]+=1


sorted_prop_stat=dict(sorted(prop_stat.items(), reverse=True, key=lambda item: item[1]["total_use"]))


with open(prefix+"results/results-top-items-properties.csv","w") as file:
    print('"Property","Property Label","is ID","Total use","Percent by total","Top by wikis","Percent by wikis","Top by statements","Percent by statements","Top by words","Percent by words","Top by W3DRank","Percet by W3DRank"',file=file)
    for prop in sorted_prop_stat:
        print('"'+prop+'","'+prop_stat[prop]["label"]+'","'+str(prop_stat[prop]["isID"])+'",'+str(prop_stat[prop]["total_use"])+','+str(round(prop_stat[prop]["total_use"]/total*100,2))+','+str(prop_stat[prop]["top_wikis"])+','+str(round(prop_stat[prop]["top_wikis"]/top*100,2))+','+str(prop_stat[prop]["top_props"])+','+str(round(prop_stat[prop]["top_props"]/top*100,2))+','+str(prop_stat[prop]["top_words"])+','+str(round(prop_stat[prop]["top_words"]/top*100,2))+','+str(prop_stat[prop]["top_W3DRank"])+','+str(round(prop_stat[prop]["top_W3DRank"]/top*100,2)),file=file)
    file.close()



####################################
# Write results of items languages #
####################################
with open(prefix+"results/results-items-languages.csv","w") as file:
    sorted_lang_stat=dict(sorted(lang_stat.items(), reverse=True, key=lambda item: item[1]["num_items"]))
    print("language_normalized,num_items",file=file)
    for data in sorted_lang_stat:
        print('"'+data+'",'+str(lang_stat[data]["num_items"]),file=file)
    file.close()



################################
# Write results of items wikis #
################################
with open(prefix+"results/results-items-wikis.csv","w") as file:
    sorted_wiki_stat=dict(sorted(wiki_stat.items(), reverse=True, key=lambda item: item[1]["num_items"]))
    print("wiki,num_items",file=file)
    for data in wiki_stat:
        print('"'+data+'",'+str(wiki_stat[data]["num_items"]),file=file)
    file.close()

###################################
# Write the matrix wikis X langs #
###################################
for data_1 in sorted_lang_stat:
    matrix_langs_wikis[data_1]={}
    matrix_langs_wikis_W3DRank[data_1]={}

    for data_2 in sorted_wiki_stat:
        matrix_langs_wikis[data_1][data_2]=0
        matrix_langs_wikis_W3DRank[data_1][data_2]=0

for item in item_stat:
    for lang in item_stat[item]["langs"]:
        for wiki in item_stat[item]["wikis"]:
            matrix_langs_wikis[lang][wiki]+=1
            matrix_langs_wikis_W3DRank[lang][wiki]+=item_stat[item]["W3DRank"]

with open(prefix+"results/results-matrix-lang-wikis.csv","w") as file:
    print('"lang"',file=file,end='')
    for data_1 in sorted_wiki_stat:
        print(',"'+data_1+'"',file=file,end='')
    print("\n",file=file,end='')
    for data_1 in sorted_lang_stat:
        print('"'+data_1+'"',file=file, end='')
        for data_2 in sorted_wiki_stat:
            print(','+str(matrix_langs_wikis[data_1][data_2]),file=file, end='')
        print("\n",file=file,end='')
    file.close()

with open(prefix+"results/results-matrix-lang-wikis-W3DRank.csv","w") as file:
    print('"lang"',file=file,end='')
    for data_1 in sorted_wiki_stat:
        print(',"'+data_1+'"',file=file,end='')
    print("\n",file=file,end='')
    for data_1 in sorted_lang_stat:
        print('"'+data_1+'"',file=file, end='')
        for data_2 in sorted_wiki_stat:
            print(','+str(matrix_langs_wikis_W3DRank[data_1][data_2]),file=file, end='')
        print("\n",file=file,end='')
    file.close()


            
###########################
# Write items description #
###########################
sorted_item_stat=dict(sorted(item_stat.items(), reverse=True, key=lambda item: item[1]["num_wikis"]))
with open(prefix+"results/results-items-description.csv","w") as file:
    print("item,language,all_languages,title,title_bis,date,date_type,precision_date,num_wikis,num_non_id_props,num_id_props,total_num_words,W3DRank",file=file)
    for item in sorted_item_stat:
            all_languages=""
            for lang in sorted_item_stat[item]["langs"]:
                all_languages+=lang+" "
            all_languages=all_languages.strip()
            for lang in sorted_item_stat[item]["langs"]:
                print(item+','+lang+',"'+all_languages+'","'+sorted_item_stat[item]["title"]+'","'+sorted_item_stat[item]["title_bis"]+'",'+
                    str(sorted_item_stat[item]["date"])+","+str(sorted_item_stat[item]["date_type"])+","+str(sorted_item_stat[item]["precision_date"])+","+
                    str(sorted_item_stat[item]["num_wikis"])+','+str(sorted_item_stat[item]["num_non_id"])+","+str(sorted_item_stat[item]["num_id"])+","+
                    str(sorted_item_stat[item]["total_num_words"])+","+str(sorted_item_stat[item]["W3DRank"]),file=file)
                lang_stat[lang]["total_wikis"]+=sorted_item_stat[item]["num_wikis"]
                lang_stat[lang]["total_id_props"]+=sorted_item_stat[item]["num_id"]
                lang_stat[lang]["total_props"]+=sorted_item_stat[item]["num_non_id"]
                lang_stat[lang]["total_words"]+=sorted_item_stat[item]["total_num_words"]
                lang_stat[lang]["total_W3DRank"]+=sorted_item_stat[item]["W3DRank"]
    file.close()


###############################
# Write languages description #
###############################
with open(prefix+"results/results-languages-description.csv","w") as file:
    print("Language code,Total items,Wikis average,Statements average,ID Statements average,Words average,W3DRank average",file=file)
    for lang in lang_stat:
        tot_items=lang_stat[lang]["num_items"]
        avg_wikis=lang_stat[lang]["total_wikis"]/tot_items
        avg_id_props=lang_stat[lang]["total_id_props"]/tot_items
        avg_props=lang_stat[lang]["total_props"]/tot_items
        avg_words=lang_stat[lang]["total_words"]/tot_items
        avg_W3DRank=lang_stat[lang]["total_W3DRank"]/tot_items
        print(lang+","+str(tot_items)+","+str(avg_wikis)+","+str(avg_props)+","+str(avg_id_props)+","+str(avg_words)+","+str(avg_W3DRank),file=file)
    file.close()


###########################
# Write Rankings of Items #
###########################
sorted_nprops_item_stat=dict(sorted(item_stat.items(), reverse=True, key=lambda item: item[1]["num_non_id"]))
sorted_nwords_item_stat=dict(sorted(item_stat.items(), reverse=True, key=lambda item: item[1]["total_num_words"]))
sorted_W3DRank=dict(sorted(item_stat.items(), reverse=True, key=lambda item: item[1]["W3DRank"]))
list_by_nwikis=[]
values_by_nwikis=[]
list_by_nprops=[]
values_by_nprops=[]
list_by_nwords=[]
values_by_nwords=[]
list_by_W3DRank=[]
values_by_W3DRank=[]

for item in sorted_item_stat:
    list_by_nwikis.append(item)
    values_by_nwikis.append(sorted_item_stat[item]["num_wikis"])

for item in sorted_nprops_item_stat:
    list_by_nprops.append(item)
    values_by_nprops.append(sorted_item_stat[item]["num_non_id"])

for item in sorted_nwords_item_stat:
    list_by_nwords.append(item)
    values_by_nwords.append(sorted_item_stat[item]["total_num_words"])

for item in sorted_W3DRank:
    list_by_W3DRank.append(item)
    values_by_W3DRank.append(sorted_item_stat[item]["W3DRank"])

with open(prefix+"results/results-item-rankings.csv","w") as file:
    print("Ranking,Item by wikis,Title by wikis,Value by wikis,Item by props,Title by props,Value by props,Item by words,Title by words,Value by words,Item by W3DRank,Title by W3DRank,Value by W3DRank",file=file)

    for i in range(len(list_by_nwikis)):
        i_nwikis=list_by_nwikis[i]
        i_nprops=list_by_nprops[i]
        i_nwords=list_by_nwords[i]
        i_W3DRank=list_by_W3DRank[i]
        t_nwikis=item_stat[i_nwikis]["title"]
        t_nprops=item_stat[i_nprops]["title"]
        t_words=item_stat[i_nwords]["title"]
        v_nwikis=values_by_nwikis[i]
        v_nprops=values_by_nprops[i]
        v_nwords=values_by_nwords[i]
        v_W3DRank=values_by_W3DRank[i]
        
        print(str(i+1)+","+i_nwikis+",\""+item_stat[i_nwikis]["title"]+"\","+str(v_nwikis),file=file, end='')
        print(","+i_nprops+",\""+item_stat[i_nprops]["title"]+"\","+str(v_nprops),file=file, end='')
        print(","+i_nwords+",\""+item_stat[i_nwords]["title"]+"\","+str(v_nwords),file=file, end='')
        print(","+i_W3DRank+",\""+item_stat[i_W3DRank]["title"]+"\","+str(v_W3DRank),file=file)

    file.close()

###################################
# GET TOP n_lang with TOP n_items #
###################################
n_lang=0
selected_lang_items={}
selected_lang_items["<all>"]={"items":{}}
for lang in sorted_lang_stat:
    n_lang+=1;
    if n_lang>top_n_langs+1:
        break
    else:
        selected_lang_items[lang]={"items":{}}
        
for item in sorted_item_stat:
    for lang in sorted_item_stat[item]["langs"]:
        if lang in selected_lang_items and len(selected_lang_items[lang]["items"])<top_n_items:
            selected_lang_items[lang]["items"][item]=sorted_item_stat[item]["title"]
            selected_lang_items[lang]["items"][item]=sorted_item_stat[item]["num_wikis"]
        if len(selected_lang_items["<all>"]["items"])<top_n_items:
            selected_lang_items["<all>"]["items"][item]=sorted_item_stat[item]["title"]
            selected_lang_items["<all>"]["items"][item]=sorted_item_stat[item]["num_wikis"]

with open(prefix+"results/results-top-langs-items.csv","w") as file:
    print("language,item,title,num_wikis",file=file)
    for lang in selected_lang_items:
        for item in selected_lang_items[lang]["items"]:
            print(lang+',"'+item+'","'+sorted_item_stat[item]["title"]+'",'+str(sorted_item_stat[item]["num_wikis"]),file=file)
    file.close()

####################################################################
# Write similarity matrix between languages from presence in wikis #
####################################################################
'''
progress_total = len(matrix_langs_wikis)* len(matrix_langs_wikis)
progress_count = 0
with open(prefix+"results/matrix-sim-languages.csv","w") as file:
    for data_1 in matrix_langs_wikis:
        print(','+data_1,file=file, end='')
    print("\n",file=file)
    for data_1 in matrix_langs_wikis:
        print(progress_count/progress_total,end="\r")
        print(data_1,file=file, end='')
        a_dict=matrix_langs_wikis[data_1]
        for data_2 in matrix_langs_wikis:
            progress_count+=1
            b_dict=matrix_langs_wikis[data_2]
            a_s = pd.Series(a_dict)
            b_s = pd.Series(b_dict)
            print(','+str(1-cosine(a_s,b_s)),file=file,end='')
        print("\n",file=file,end='')
'''









'''



# count=0
# with open(prefix+"wikidata-item-lang-wiki-article.csv","r") as data:
#     for reg in csv.DictReader(data):
#         count+=1
#         print(count,end="\r")
#         q_item=reg["item"].replace("http://www.wikidata.org/entity/","wd:")

        if q_item in num_wikis:
            num_wikis[q_item]+=1
        else:
            num_wikis[q_item]=1



with open(prefix+"results-item-prop.csv","w") as file:
    print("prop,label,is_id_prop,num",file=file)
    for data in prop_num_items:
        print(prop_num_items[data]["prop"],',"',prop_data[prop_num_items[data]["prop"]]["propLabel"],'",',prop_data[prop_num_items[data]["prop"]]["isID"],",",prop_num_items[data]["num"],file=file)
file.close()

with open(prefix+"results-item_numwikis.csv","w") as file:
    print("item,num_wikis",file=file)
    for data in num_wikis:
        print('"',data,'",',num_wikis[data],file=file)
file.close()
'''



