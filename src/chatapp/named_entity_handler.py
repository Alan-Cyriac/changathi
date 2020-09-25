from __future__ import unicode_literals, print_function
from chatapp.forms import *
# training
import plac
import random
from pathlib import Path
import spacy
from tqdm import tqdm # loading bar
import os
import sqlite3
from nltk.tokenize import sent_tokenize
from bs4 import BeautifulSoup
import pdb
from pprint import pprint
from chatapp import db_handler
import pickle

path_unique_entity = os.path.join("model","unique_entities.pickle")
class NerPreprocessing:    

    def assure_path_exists(self, path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
            flag = False
        else:
            flag = True
        return flag

    def data_preperation(self, data):
        result = []
        n_iter = data["n_iter"]
        # TRAIN_DATA creation
        obj_Entity = EntityDB.objects.all()
        TRAIN_DATA = []
        print("[+] Start training data prepration...")

        # select all entity name - QueryDB

        for obj_query in obj_Entity: 
            obj_EntityDB = EntityDB.objects.filter(query = obj_query.query) 
            ent = []
            prev_end_index = 0
            for obj_ent in obj_EntityDB:
                if prev_end_index <= obj_ent.start_pos:
                    if obj_ent.start_pos != obj_ent.end_pos:
                        ent.append((obj_ent.start_pos, obj_ent.end_pos, obj_ent.entity_name.entity_name))
                        prev_end_index = obj_ent.end_pos

                # change training status
                # self.update_training_status(obj_ent, status=True)
                # if self.update_training_status(obj_entity = obj_ent, status=True):
                #     print("can't update training status of ", obj_ent.query.query, (obj_ent.start_pos, obj_ent.end_pos))
            if (len(ent) > 0):
                TRAIN_DATA.append((obj_query.query.query,{'entities' : ent}))
        print("[+] End training data prepration")

        f = open("training_data.txt", "w")
        f.write(str(TRAIN_DATA))
        f.close()

        output_dir = 'ner_model/'
        model = 'ner_model/'
        m_flag = self.assure_path_exists(path = model)
        if not m_flag:
            model = None
        print("[+] training_data.txt is going to be trained...")
        result = NerTraining().Train(TRAIN_DATA = TRAIN_DATA, model=model, new_model_name='ORG', output_dir=output_dir, n_iter=n_iter)
        return result

class NerTraining:

    # new entity label
    @plac.annotations(
        model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
        new_model_name=("New model name for model meta.", "option", "nm", str),
        output_dir=("Optional output directory", "option", "o", Path),
        n_iter=("Number of training iterations", "option", "n", int))
    def Train(self, TRAIN_DATA, model=None, new_model_name='ORG', output_dir=None, n_iter=20):
        result = []
        """Set up the pipeline and entity recognizer, and train the new entity."""
        print("[+] Training started...")
        if model is not None:
            nlp = spacy.load(model)  # load existing spaCy model
            print("[+] Loaded model '%s'" % model)
        else:
            nlp = spacy.blank('en')  # create blank Language class
            print("[+] Created blank 'en' model")
        print("[Flag] just before connecting to scheduler.db...")
        conn = sqlite3.connect('scheduler.db')
        db_handler.obj_SqliteSchedulerDB.update_is_in_progress(status=1, conn=conn)

        # Add entity recognizer to model if it's not in the pipeline
        # nlp.create_pipe works for built-ins that are registered with spaCy
        if 'ner' not in nlp.pipe_names:
            ner = nlp.create_pipe('ner')
            nlp.add_pipe(ner)
        # otherwise, get it, so we can add labels to it
        else:
            ner = nlp.get_pipe('ner')

        # ner.add_label(LABEL)   # add new entity label to entity recognizer
        # add entity labels to model
        obj_cur_data = EntityNameDB.objects.all()  
        LABELS = []
        
        for obj in obj_cur_data:
            LABELS.append(obj.entity_name)        
        # pdb.set_trace()
        for ent_name in LABELS:
            ner.add_label(ent_name)
        if model is None:
            optimizer = nlp.begin_training()
        else:
            # Note that 'begin_training' initializes the models, so it'll zero out
            # existing entity types.
            optimizer = nlp.entity.create_optimizer()

        # get names of other pipes to disable them during training
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
        with nlp.disable_pipes(*other_pipes):  # only train NER
            for itn in range(n_iter):
                random.shuffle(TRAIN_DATA)
                losses = {}
                for text, annotations in tqdm(TRAIN_DATA):
                    nlp.update([text], [annotations], sgd=optimizer, drop=0.35,
                            losses=losses)
                print(losses)
        # save model to output directory
        if output_dir is not None:
            output_dir = Path(output_dir)
            if not output_dir.exists():
                output_dir.mkdir()
            nlp.meta['name'] = new_model_name  # rename model
            nlp.to_disk(output_dir)
            print("Saved model to", output_dir)

            # update training status to False.
            # The scheduler will not call training data function
            db_handler.obj_SqliteSchedulerDB.update_training(status=0, conn=conn) 
            db_handler.obj_SqliteSchedulerDB.update_is_in_progress(status=0, conn=conn)
            conn.close()
            # # test the saved model
            # print("Loading from", output_dir)
            # nlp2 = spacy.load(output_dir)
            # doc2 = nlp2(test_text)
            # for ent in doc2.ents:
            #     print(ent.label_, ent.text)

            result.append("[+] Training completed...")
            return result

class NerPredicting:
    def Test(self, test_text, model=None):
        if model is not None:
            nlp = spacy.load(model)  # load existing spaCy model
        else:
            nlp = spacy.blank('en')  # create blank Language class
            # print("Created blank 'en' model")
        # test the trained model
        # remove html tags
        # pdb.set_trace()
        soup = BeautifulSoup(test_text)
        test_text = soup.get_text()
        sent_token = sent_tokenize(test_text) 
        final_res = []
        
        # pdb.set_trace()
        for sent in sent_token:
            result = {}
            doc = nlp(sent)
            res = []
            for ent in doc.ents:
                res.append({"type" :ent.label_,
                "value" : ent.text}) 
            result["entity"] = res
            final_res.append(result)
        print(final_res)
        return final_res

    def predict(self, data):
        model = 'ner_model/'
        dir = os.path.dirname(model)
        if not os.path.exists(dir):
            model = None
        final_res_list = self.Test(test_text = data["end_user_expression"], model=model)
        return final_res_list

class Get_All_Entity_Name_Handler:
    def get_all_entity_names(self):
        all_entities = EntityNameDB.objects.all()
        result = []
        for entity in all_entities:
            temp = {
                entity.entity_name : entity.id,
            }
            result.append(temp)
        return result

class Delete_Trained_Data_handler:
    def deleting(self):
        result = []
        obj_cur_data = EntityDB.objects.filter(is_trained = True).delete()  
        result.append("[+] Deleted...")
        return result

class Get_Entity__handler:
    def get_all_entities(self):
        # all_entities = EntityDB.objects.filter(is_trained = flag).order_by('-id')
        all_entities = EntityDB.objects.all()
        result = []
        for entity in all_entities:
            temp = {
                "id": entity.id,
                "query": entity.query.query,
                "entity_name": entity.entity_name.entity_name,
                "start_pos": entity.start_pos,
                "end_pos": entity.end_pos,
                "is_trained": entity.is_trained,
            }
            result.append(temp)
        return result

class Delete_Entities_By_ID_handler:
    def get_object_by_id(self,id):
        try:
            emp = EntityDB.objects.get(id=id)
        except EntityDB.DoesNotExist:
            emp = None
        return emp

    def delete_data(self, id):
        error = []
        result = []
        entity = self.get_object_by_id(id)
        if entity is None:
            error.append("[-] No matched ID found for deletion")
            status=404
        else:
            status,deleted_item = entity.delete()
            if status == 1:
                result.append("[+] %d deleted successfully"%id)
                status = 200
            else:
                error.append("[-] Unable to delete.")
                status=404
        return result, error, status

class Update_Entities_handler:
    def get_obj_entity_by_id(self,id):
        try: obj_entity = EntityNameDB.objects.get(id=id)
        except EntityDB.DoesNotExist: obj_entity = None
        return obj_entity


    def get_query_by_id(self, id):
        try: query = QueryDB.objects.get(query=id)
        except QueryDB.DoesNotExist: query = None
        return query


    def add_entity(self, data):
        error = []
        result = []
        flag = True

        if data["query"] in data:
            query = data["query"]
        else:
            error.append("query is not given")
            flag = False

        if data["entity_name"] in data:
            entity_name = data["entity_name"]
        else:
            error.append("entity_name is not given")
            flag = False

        if data["start_pos"] in data:
            start_pos = data["start_pos"]
        else:
            error.append("start_pos is not given")
            flag = False

        if data["end_pos"] in data:
            end_pos = data["end_pos"]
        else:
            error.append("start_pos is not given")
            flag = False
        if flag:
            obj_entity = self.get_obj_entity_by_id(entity_name)
            if obj_entity is None:
                entity_data = {
                    "entity_name" : data['entity_name']
                }
                entity_form = EntityNameDBForm(entity_data)
                if entity_form.is_valid():
                    obj_entity = EntityNameDBForm.save(commit=True)
                    result["is_the_entity_new"] = True
                if entity_form.errors:                
                    error.append(entity_form.errors)
                    result["is_the_entity_new"] = False
                    status = 400
            query_form = QueryForm(query)
            if query_form.is_valid():
                obj_query = QueryForm.save(commit=True)
                result["is_the_query_new"] = True
                status = 200
            if query_form.errors:
                obj_query = self.get_query_by_id(query)
                error.append(query_form.errors)
                result["is_the_query_new"] = False
                status = 400
                
            entity_data = {
                'id' : id,
                'query' : obj_query,
                'entity_name' : obj_entity,
                'start_pos' : start_pos,
                'end_pos' : end_pos,
                'is_trained' : False
            } 
            entity_form = EntityForm(entity_data) # EntityForm(entity_data, instance = entity) <--- This was there initially
            if entity_form.is_valid():
                entity_form.save(commit=True)
                result.append('%d added successfully'%(id))
                status = 200
            if entity_form.errors:
                error.append(entity_form.errors)
                status = 400

        return result, error, status