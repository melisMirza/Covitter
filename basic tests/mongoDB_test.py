#!/usr/bin/env python
# coding: utf-8

# In[2]:


from pymongo import MongoClient
import json


# In[15]:


dbURL = "mongodb+srv://melis:XXXXXXXXXXXX@cluster0.dqeax.mongodb.net"#/sample_airbnb?retryWrites=true&w=majority"


# In[31]:


client = MongoClient(dbURL)
db = client.sample_airbnb#listingsAndReviews

#Get Collection Names at that DB
cols = db.list_collection_names()
print(cols)


# In[32]:


#Count all records/documents şn collection
docs = db.listingsAndReviews.count_documents({})
print("all docs:",docs)
#with certain parameter
res = db.listingsAndReviews.count_documents({"bedrooms":3})
print("with 3 bedroom:",res)


# In[45]:


#Add entry to DB
entry = {"name":"hotel melis",
        "bedrooms":6,
         "city":"istanbul"}
db.listingsAndReviews.insert_one(entry)
#check
res = db.listingsAndReviews.count_documents({"name":"hotel melis"})
print(res)


# In[51]:


#View Results
hotelmelis = db.listingsAndReviews.find({"name":"hotel melis"}) #returns cursor
for i in range(res):
    doc = hotelmelis.next()
    print(doc)
    #print a certain attribute
    print(doc["city"])


# In[53]:


import datetime
#Add many documents
entries = [{"name":"hotel melis","bedrooms":6,"city":"istanbul"},
          {"name":"hotel ali","location":"Turkey","city":"adana", "init":datetime.datetime.now()},
          {"name":"hotel veli","minimum_nights":3,"city":"ankara"},
          {"name":"hotel deli","maximum_nights":600,"city":"tekirdag"}]

db.listingsAndReviews.insert_many(entries)
#check
res = db.listingsAndReviews.find({"name":"hotel ali"})
print(res.next())


# In[67]:


from bson.objectid import ObjectId

#Update single document
db.listingsAndReviews.update_one({'_id': ObjectId('5fc3f672d968864bddfaf615')}, {'$set': {'location': "usa"}}, upsert=True) #Upsert
#check
res = db.listingsAndReviews.find({"name":"hotel ali"})
print(res.next())


# In[68]:


#Update Multiple Values
updateResult = db.listingsAndReviews.update_many({'name': "hotel melis"}, {'$set': {'location': "earth"}})
#check
res = db.listingsAndReviews.find({"name":"hotel melis"})
print(res.next())


# In[71]:


#Delete
before = db.listingsAndReviews.count_documents({'name': "hotel melis"})
print("before delete:",before)
db.listingsAndReviews.delete_one({'_id': ObjectId('5fc3f019d968864bddfaf60f')})
after = db.listingsAndReviews.count_documents({'name': "hotel melis"})
print("after delete:",after)                           


# In[ ]:




