#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run multiple queries for the database OpenStreetMap (oms) in the
collection San Francisco (sf)  
"""

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

######################### pipelines begin ######################################
def top_contributor():
    pipeline = [{"$group":{'_id': '$created.user','count':{'$sum': 1}}},
                {"$sort": {'count': -1}},
                {"$limit": 5}]
    return pipeline
    
def max_min_dates():
    pipeline = [{"$match": {"created.user": 'ediyes'}},
    			{"$group": {"_id": "$created.timestamp"}},
    			{"$sort" : {"_id": -1}}]
    return pipeline

def find_no_users_with_one_entry():
    pipeline = [{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, 
                {"$group":{"_id":"$count", "num_users":{"$sum":1}}}, 
                {"$sort":{"_id":1}}, 
                {"$limit":1}]
    return pipeline

def find_ammenties():
    pipeline = [{"$match":{"amenity":{"$exists":1}}}, 
                {"$group":{"_id":"$amenity","count":{"$sum":1}}},
                {"$sort":{"count": -1}},
                {"$limit":10}]
    return pipeline

def find_ammenties_religion():
    pipeline = [{"$match":{"amenity":{"$exists": 1}, 
                                     "amenity":"place_of_worship"}}, 
                {"$group":{"_id":"$religion", "count":{"$sum":1}}}, 
                {"$sort":{"count": -1}}, 
                {"$limit":5}]
    return pipeline

def find_ammenties_cuisine():
    pipeline = [{"$match":{"amenity":{"$exists": 1}, 
                                     "amenity":"restaurant"}}, 
                {"$group":{"_id":"$cuisine", "count":{"$sum":1}}}, 
                {"$sort":{"count": -1}}, 
                {"$limit":5}]
    return pipeline

def find_barrier():
    pipeline = [{"$match":{"barrier":{"$exists": 1}}}, 
                {"$group":{"_id":"$barrier","count":{"$sum":1}}},
                {"$sort":{"count": -1}},
                {"$limit":5}]
    return pipeline

def find_building():
    pipeline = [{"$match":{"building":{"$exists": 1}}}, 
                {"$group":{"_id":"$building","count":{"$sum":1}}},
                {"$sort":{"count": -1}},
                {"$limit":5}]
    return pipeline

######################### pipelines end ########################################

def sf_sources(db, pipeline):
    result = db.sf.aggregate(pipeline)
    return result


if __name__ == '__main__':
    from pprint import pprint

    # get database
    db = get_db('oms')
    
    # print queries
    print 'Number of Documents: ',
    pprint(db.sf.find().count())
    print 'Number of Nodes: ', 
    pprint(db.sf.find({"type":"node"}).count())
    print "Number of ways: ", 
    pprint(db.sf.find({"type":"way"}).count())    
    print 'Number of unique users: ', 
    # using dot notation
    pprint(len(db.sf.distinct("created.user")))
    print 
    print 'top 5 contributors'
    top_contributors = list(sf_sources(db, top_contributor()))
    pprint(top_contributors)
    print 
    greatest_contributor_count = top_contributors[0]['count']
    
    print 'timescale of the largest contributor:'
    timestamp_info = list(sf_sources(db, max_min_dates()))
    print 'last entry:', timestamp_info[0]['_id']
    print 'first enty:', timestamp_info[len(timestamp_info)-1]['_id']
    print 
    print 'Number of users appearing once:'
    pprint(list(sf_sources(db, find_no_users_with_one_entry())))
    print
    print 'Top 10 appearing amenities:'
    pprint(list(sf_sources(db, find_ammenties())))
    print
    print 'Number of amenities with an array type:'
    does_amentiy_have_array = db.sf.find({"amenity":{"$type": 4}}).count()
    print does_amentiy_have_array
    print 
    print 'Top 5 most labeled religion:'
    pprint(list(sf_sources(db, find_ammenties_religion())))
    print 
    print 'Most popular cuisines:'
    pprint(list(sf_sources(db, find_ammenties_cuisine())))
    print 
    print "Top 5 Labeled Barriers"
    pprint(list(sf_sources(db, find_barrier())))
    print
    print "Top 5 Labeled Buildings"
    pprint(list(sf_sources(db, find_building())))
    print 