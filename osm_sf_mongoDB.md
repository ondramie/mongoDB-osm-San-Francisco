#An Examination of the OpenStreetMap (OSM) area of San Francisco, CA with MongoDB 
###OSM Map Area
The map is from here:  

+  https://www.openstreetmap.org/relation/396487

I chose this area because I live in San Francisco and I am familiar with the area.  My familiarity helped reconcile process irregularities.  Due to the size of the map area, I was not permitted to download the data from OpenStreetMap directly, and I had to download the data from Mapzen.  The file size is: 

+ (OSM XML 41.6MB compressed; 658.1MB uncompressed). 
 
### Problems Encountered in the OSM
A reduced data set was created by utilizing the provided code that extracts every 10th level element.  The number of elements and the names of the elements in the reduced data set are below: 
```
{'member': 3526,
 'nd': 370848,
 'node': 305544,
 'osm': 1,
 'relation': 344,
 'tag': 125620,
 'way': 32977}
```
Looping through the tags of the data elements to check for acceptable and unacceptable regular expressions produced:
```
{'lower': 66469, 
 'lower_colon': 56473, 
 'other': 2665, 
 'problemchars': 13}
```
The tags that produced ‘problemchars’ were: 
```
k= sfgov.org:OBJECTID
k= sfgov.org:OFFICE_TYP
k= sfgov.org:OBJECTID
k= sfgov.org:OFFICE_TYP
k= Lydian Academy
k= addr.source:housenumber
k= Sign Legen
k= Street Fro
k= Street Ont
k= addr.source:housenumber
k= addr.source:housenumber
k= addr.source:housenumber
k= addr.source:housenumber
```
Sign Legen (above) looks to be short for Sign Legend.  Two data sets exist on Mapzen: one for San Francisco, and another one for the San Francisco Bay.  I downloaded the San Francisco data set but it appears to consist of regions outside of San Francisco, as the Lydian Academy is located south of San Francisco based on GPS coordinates.  Nevertheless, these problemchars were barred entry into the JSON output file.  My reason for exclusion is that the ‘problemchar’ data is superfluous when compared to the majority of the data, meaning that little would be gleaned from inclusion. 

Running python code on the “addr:street” keys of the reduced data set, I noticed that some of the entries were not capitalized such as “street” and “avenue." These were corrected.  I noticed a misspelling such as “Abenue” that I corrected; and I noticed over abbreviations such  as “W 25th Ave” and “W & E Of Us 101 N of Seminary Avenue” that I changed to “West 25th Avenue” and “West and East Of US 101 North of Seminary Avenue”, respectively.  The changes were accomplished by handing the addresses in python:
```
def fix_abbrev(name, list1, list2):
        name_array = name.split()
        for index, item in enumerate(name_array):
                if item in list1:
                        name_array[index] = list1.get(item)
                if item in list2:         
                        name_array[index] = list2.get(item)
        new_name = ' '.join(name_array)
        return new_name        
```
Here list1, and list2 are the dictionaries of acceptable abbreviations such as “Street” for “St.” or “St” and “North” for “N” or “N.”  Manipulating the addresses with the split() function was an acceptable alternative to scanning strings for regular expressions that could produced unseemly concatenated white space.  Processing this data through MongoDB could have been accomplished as well through regular expression scans omitting case sensitivity.  

The production of the JSON file took 25.987596035 seconds.  The resulting JSON file is 75.8MB and is called: 
```
sample-sf-california-osm.json
```
I experienced the following problems when trying to use Mongo DB locally: (1) wrong initial path; (2) incorrect shutdown; (3) terminal and python shell obfuscation; (4) emulator code and local code irregularities; (5)  a Non-ASCII characters syntax error; (6) and indentation errors arising from X-code or TextWrangler.  Oddly enough, I had no issues with the text editor Sublime.  Woohoo! 

## Data Overview:
A table of relevant statistics using MongoDB queries: 

|Metric|Value|
|:---|:--:|
|Number of Documents|338521|
|Number of Nodes|305533|
|Number of Ways|32975|
|Number of Unique Users|1152|
|Number of Users Appearing Once|316|

The MongoDB queries used: 
```
db.sf.find().count() 
db.sf.find({"type":"node"}).count()
db.sf.find({"type":"way"}).count()
len(db.sf.distinct("created.user"))

def find_no_users_with_one_entry():
    pipeline = [{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, 
                {"$group":{"_id":"$count", "num_users":{"$sum":1}}}, 
                {"$sort":{"_id":1}}, 
                {"$limit":1}]
    return pipeline

list(sf_sources(db, find_no_users_with_one_entry()))
```
The top five contributors to the reduced data set were:
```
[{u'_id': u'ediyes', u'count': 71076},
 {u'_id': u'Luis36995', u'count': 55803},
 {u'_id': u'Rub21', u'count': 42034},
 {u'_id': u'oldtopos', u'count': 33574},
 {u'_id': u'KindredCoda', u'count': 13555}]
```
User `edieyes` has contributed 71,076 entries; this seems exorbitant.  An examination of time span of the user’s first entry timestamp (2014-01-10) and last entry timestamp (2015-08-17) reveal that the user created the 71,076 entries in approximately a little more than a year and half, meaning that the user was generating ~5 entries/hour.  He or she seems like an above-and-beyond contributor.   Here is the MongoDB query: 
```
def top_contributor():
    pipeline = [{"$group":{'_id': '$created.user','count':{'$sum': 1}}},
                {"$sort": {'count': -1}},
                {"$limit": 5}]
    return pipeline
    
list(top_contributors = list(sf_sources(db, top_contributor()))
```

##Additional Ideas
Though the data set is incomplete, it holds potential for use in: (1) targeted marketing, (2) city and government planning, (3) gamification, and (4) route planning.  

Marketers could utilize the maps to understand community demographics and scarcities in real-time to optimize marketing campaigns.  Likewise, city and government planning could use the data to zone districts for hospitals, public facilities, residential areas based on real-time input.  As the example OSM project alluded to, gamification could be done to increase participation such as the checking-in phenomena which earns badges or prizes. And last but not least, planned routes for long distance bicycle touring, trekking, etc. associated with nearby services would benefit from a real-time ever evolving data set.  

A way to improve the data set is by having a more complete and consistent data set that would facilitate the future uses above.  A preemptive data set cleansing before the analyst cleanses the data would be beneficial.  The additional ways to analyze the data set are regionally, continentally, or internationally.  I could analyze the data by local neighborhood and compare that to the city statistics or compare the city to another city in the same continent or that is internationally located.  The benefits of implementing the improvements are that more people could readily analyze the data faster or other services could use them as well.  An anticipated problem with implementing the improvement is allocating man-hours.  Given no incentive to contribute, some rather not contribute to cleaning up the data set for analysts.  Since the data set was taken from an open source, the comparison of local city statistics to an international city may be complicated by local naming conventions. 


## Additional Data Exploration using MongoDB
Top 10 appearing amenities are: 
```
[{u'_id': u'parking', u'count': 378},
 {u'_id': u'restaurant', u'count': 244},
 {u'_id': u'school', u'count': 147},
 {u'_id': u'place_of_worship', u'count': 102},
 {u'_id': u'cafe', u'count': 76},
 {u'_id': u'bench', u'count': 67},
 {u'_id': u'post_box', u'count': 63},
 {u'_id': u'fuel', u'count': 43},
 {u'_id': u'fast_food', u'count': 42},
 {u'_id': u'toilets', u'count': 39}]
```
I live in San Francisco, where a lot of cafes exist.  I am surprised that more amenities are labeled as restaurants rather than labeled as cafes.  Could amenities have two labels such as ['cafe', restaurant']? The dictionary ‘amenity’ only has string values. To ensure that amenities were not labeled as cafes and restaurants a query was ran to check data type:
```
db.sf.find({"amenity":{"$type": 4}}).count()
```
The result is 0.  Perhaps, the amenity dictionary should take arrays.  

Top 5 appearing religions for `places_of_worship` are:
```
[{u'_id': u'christian', u'count': 92},
 {u'_id': u'buddhist', u'count': 3},
 {u'_id': u'jewish', u'count': 2},
 {u'_id': u'unitarian_universalist', u'count': 2},
 {u'_id': None, u'count': 2}]
```
A considerable number of places of worship are Christian.  Out of all places of worship that have religion classification, 82 percent are labeled as Christian.  The data can be corroborated with census data - perhaps. 

The Top 5 most popular cuisines are:
```
[{u'_id': None, u'count': 95},
 {u'_id': u'mexican', u'count': 25},
 {u'_id': u'italian', u'count': 13},
 {u'_id': u'indian', u'count': 10},
 {u'_id': u'chinese', u'count': 10}]
```
The most popular cuisine is None, followed by Mexican.  The None designation points to incompleteness of the reduced data set.  A follow-up exercise would be to see the most popular cuisines per neighborhood districts and compare that data to census demographics.  Some other interesting entries follow. 

The Top 5 barriers are: 
```
[{u'_id': u'gate', u'count': 112},
 {u'_id': u'fence', u'count': 80},
 {u'_id': u'retaining_wall', u'count': 13},
 {u'_id': u'wall', u'count': 13},
 {u'_id': u'bollard', u'count': 8}]
```     
Gates look to be labeled the most.  I haven't been on the lookout for gates.  I predict that more than 112 gates exist in San Francisco.  How about buildings? 

The Top 5 buildings are:  
```
[{u'_id': u'yes', u'count': 21315},
 {u'_id': u'house', u'count': 726},
 {u'_id': u'residential', u'count': 638},
 {u'_id': u'apartments', u'count': 81},
 {u'_id': u'retail', u'count': 80}]
```
YAAAAAAS!  It looks like 'yes' is the most popular entry for a building.   

##Conclusion
Though the data set seems to be incomplete and needs editing, which could be expected from a community data set, the data munging objective was met by exporting data, cleaning that data, importing that data into MongoDB, and then querying the database for insights.  As data munging is an new endeavor for me, I am surprised that a lot of the processes of exporting and importing data are not automated or at least my scope into this endeavor is limited that I am unaware of the automation at hand to streamline these tasks.  The New York Times article provided insight and the learn-by-doing provided practice.  

> Written with [StackEdit](https://stackedit.io/).