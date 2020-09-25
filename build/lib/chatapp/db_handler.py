from chatapp.forms import *
import sqlite3
import schedule
import time
import requests
import json
import pdb

class IntentTrainingSetHandler:
    def training_set(self, obj_query, intent_obj):
        train_set = {
            "query": obj_query,
            "intent" : intent_obj,
        }
        # insert into Training_Set_DB
        training_set_obj = Intent_Training_SetForm(train_set)
        if training_set_obj.is_valid():
            training_set_obj.save(commit=True)
            is_trainset_inserted = True
        if training_set_obj.errors:
            is_trainset_inserted = False            
        return is_trainset_inserted 

class Intent:
    def get_intent_by_id(self, id):
        try: intent = IntentDB.objects.get(intent=id)
        except IntentDB.DoesNotExist: intent = None
        return intent
    def get_query_by_id(self, id):
        try: query = QueryDB.objects.get(query=id)
        except QueryDB.DoesNotExist: query = None
        return query

    def insert_intent(self, data):
        result = {}
        error = []
        query = {
                    "query": data["query"]
                }
        query_form = QueryForm(query)
        if query_form.is_valid():
            obj_query = query_form.save(commit=True)
            result["is_the_query_new"] = True
        if query_form.errors:
            obj_query = self.get_query_by_id(data["query"])
            error.append(query_form.errors)
            result["is_the_query_new"] = False
            status = 400

        insert_intent = {
                            "intent" : data["intent"]
                        }

        # insert intent into intentDB
        intent_form = IntentForm(insert_intent)
        if intent_form.is_valid():
            intent_obj = intent_form.save(commit=True)
            result["is_intent_inserted"] = True
        if intent_form.errors:
            intent_obj = self.get_intent_by_id(data["intent"])
            result["is_intent_inserted"] = False
            error.append(intent_form.errors)
        
        is_trainset_inserted = IntentTrainingSetHandler().training_set(obj_query, intent_obj)
        result["is_trainset_inserted"] = is_trainset_inserted
        return result, error

class Get_Intent_Handler:
    def get_all_intent(self):
        result = {}
        error = []
        # retrieve all data from intent db
        intents = []
        intent_obj = IntentDB.objects.all()
        for intent in intent_obj:
            intents.append(intent.intent)
        result["intent"] = intents
        return result, error
    
    def get_intent_id(self, intent_name):
        intent_id = None
        # retrieve all data from intent db  
             
        intent_obj = IntentDB.objects.filter(intent= intent_name)
        for obj in intent_obj:
            intent_id = obj.id
        return intent_id

class Intent_Training_Dataset:
    def intent_training_data(self):
        # retrieve all data from intent db
        X = []
        y = []
        obj_trainingset_db = Intent_Training_Set.objects.all()
        for dataset in obj_trainingset_db:
            X.append(dataset.query.query)
            y.append(dataset.intent.intent)
        return X, y

class Named_Entity_DB:
    def get_entity_by_id(self, entity_name):
        try: obj_entity_name = EntityNameDB.objects.get(entity_name=entity_name)
        except EntityNameDB.DoesNotExist: obj_entity_name = None
        return obj_entity_name

    def get_query_by_id(self, id):
        try: query = QueryDB.objects.get(query=id)
        except QueryDB.DoesNotExist: query = None
        return query

    def save_entity(self, entity):
        entity_data = {
            "entity_name" : entity
        }
        entity_form = EntityNameDBForm(entity_data)
        if entity_form.is_valid():
            obj_entity = entity_form.save(commit=True)                        
        if entity_form.errors: 
            obj_entity = self.get_entity_by_id(entity)           
            print(entity_form.errors)            
        return obj_entity
    

    def save_data(self, data):
        result = {}
        error = []
        query = {
                    "query": data["query"]
                }
        query_form = QueryForm(query)

        if query_form.is_valid():
            obj_query = query_form.save(commit=True)
            result["is_the_query_new"] = True
            status = 200
        if query_form.errors:
            obj_query = self.get_query_by_id(data["query"])
            #error.append(query_form.errors)
            result["is_the_query_new"] = False
            status = 400
        # pdb.set_trace()
        # save entity
        for entity in data["entity_list"]:
            obj_entity = self.get_entity_by_id(entity[2])
            if obj_entity is None:
                obj_entity = self.save_entity(entity[2])
            entity_data = {
                            'query' : obj_query,
                            'entity_name' : obj_entity,
                            'start_pos' : int(entity[0]),
                            'end_pos' : int(entity[1]),
                            'is_trained' : False
                        }
            entity_form = EntityForm(entity_data)
            if entity_form.is_valid():
                entity_form.save(commit=True)
                result["is_entity_entered"] = True
                status = 200
            if entity_form.errors:
                error.append(entity_form.errors)
                result["is_entity_entered"] = False
                status = 400
        return result, error, status

#______________________________________________________________________________________________________
#______________________________________________________________________________________________________
# scheduler for training
#______________________________________________________________________________________________________
conn = sqlite3.connect('scheduler.db')
print ("[+] scheduler database Opened successfully")

class SqliteSchedulerDB:
    def create_db(self):
        
        conn.execute('''CREATE TABLE scheduler
                (ID INT PRIMARY KEY     NOT NULL,
                start_training           BOOLEAN,
                is_in_progress           BOOLEAN,
                num_iter INT);''')
        print ("Table created successfully")
    def insert_value(self):
        conn.execute("INSERT INTO scheduler (ID,start_training,is_in_progress,num_iter) \
            VALUES (1, 0, 0, 100)");

        conn.commit()
        print ("Records created successfully")
    def update_training(self, status, num_iter = 100,conn=conn):
        conn.execute("UPDATE scheduler set start_training = %d, num_iter = %d where ID = 1"%(status, num_iter))
        conn.commit()
        print ("Total number of rows updated :", conn.total_changes)
    def update_is_in_progress(self, status,conn=conn):
        conn.execute("UPDATE scheduler set is_in_progress = %d where ID = 1"%(status))
        conn.commit()
        print ("Total number of rows updated :", conn.total_changes)

    def check_status(self, conn=conn):
        cursor = conn.execute("SELECT start_training,is_in_progress, num_iter  from scheduler")
        for row in cursor:
            print ("start_training = ", row[0])
            print ("is_in_progress = ", row[1])
            print ("num_iter = ", row[2])
        return row

obj_SqliteSchedulerDB = SqliteSchedulerDB()
try:
    obj_SqliteSchedulerDB.check_status(conn=conn)
except:
    obj_SqliteSchedulerDB.create_db()
    obj_SqliteSchedulerDB.insert_value()

conn.close()
#______________________________________________________________________________________________________
class Story:
    def is_feature_exist(self, feature_vec):
        obj_story = StoriesDB.objects.filter(feature_vector = feature_vec)
        obj_feature_vec = None
        for obj in obj_story:
            obj_feature_vec = obj
        return obj_feature_vec
    def get_dataset(self):
        obj_story = StoriesDB.objects.all()
        X = []
        y = []
        for obj in obj_story:

            X.append([int(x) for x in obj.feature_vector.split(", ")])
            y.append(int(obj.action))
        return X, y
        
    def add_features(self, data):
        result = {}
        error = []
        obj_feature_vec = self.is_feature_exist(data["feature_vec"])
        query = {
                    "feature_vector": data["feature_vec"],
                    "action": data["action"]
                }
        form = StoriesDBForm(query)
        if obj_feature_vec:
            if form.is_valid():
                obj_query = form.save(commit=True, instance = obj_feature_vec)
                result["is_updated"] = True
        else:
        
            if form.is_valid():
                obj_query = form.save(commit=True)
                result["is_saved"] = True
        
            
        if form.errors:            
            error.append(form.errors)
            result["is_saved"] = False            
        return result, error