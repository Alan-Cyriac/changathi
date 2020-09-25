import requests
import json
import action
import pdb
from chatapp.intent_handler import Prediction
from chatapp import named_entity_handler
from chatapp.forms import *

# # import story_handler
    # BASE_URL = 'http://127.0.0.1:8000/'

    # def insert_intent(query, intent):
    #     ENDPOINT = "insert_intent/"
        
    #     data = {
    #             "query": query,
    #             "intent": intent
    #             }
        
    #     resp = requests.post(BASE_URL+ENDPOINT, data=json.dumps(data))
    #     print(resp.status_code)
    #     print(resp.json())
    #     data = resp.json()
    #     return data["result"]
    # #add intent
    # def get_intent_id(intent):
    #     ENDPOINT = "get_intent_id/"
    #     intent = {
    #         "intent": intent
    #     }
    #     resp = requests.post(BASE_URL+ENDPOINT, data = json.dumps(intent))
    #     print(resp.status_code)
    #     print(resp.json())
    #     data = resp.json()
    #     return data["intent_id"]
    # # get intent id
    # def predict_intent(end_user_expression):
    #     ENDPOINT = "predict_intent/"
    #     #end_user_expression = "student"
        
    #     data = {
    #             "end_user_expression": end_user_expression,
    #             }

    #     resp = requests.post(BASE_URL+ENDPOINT, data=json.dumps(data))
    #     if resp.status_code == 200:
    #         data = resp.json()
    #         print(data)
    #         return data['result']['predicted'], data['result']['intent_id']
    # # predict_intent(end_user_expression = "add a student")
    # def pedict_ne(end_user_expression):
    #     ENDPOINT = "pedict_ne/"
    #     #end_user_expression = "add student named Alan of class 10"
        
    #     data= {
    #         "end_user_expression": end_user_expression
    #     }
        
    #     resp = requests.post(BASE_URL+ENDPOINT, data=json.dumps(data))
    #     if resp.status_code == 200:
    #         data = resp.json()
    #         return data['result']
    # # pedict_ne("add student named Alan of class 10")
    # def story_vector_training():
    #     ENDPOINT = "story_training/"
    #     resp = requests.post(BASE_URL+ENDPOINT)
    #     if resp.status_code == 200:
    #         data = resp.json()
    #         return data['result']
    # #story_vector_training, the same is there in API
    # def all_entity_names():
    #     ENDPOINT = "all_entity_names/"
        
    #     data = {
    #         "get_entity": False
    #     }
        
    #     resp = requests.post(BASE_URL+ENDPOINT, data=json.dumps(data))
    #     print(resp.status_code)
    #     print(resp.json())
    #     return resp.json()
    # #Get_All_Entity_Name
    # def insert_stories(feature_vector, response_action):
    #     ENDPOINT = "add_story/"
    #     feature_vector = ", ".join([str(x) for x in feature_vector])
    #     data= {
    #         "feature_vec": feature_vector,
    #         "action": response_action,
    #     }
        
    #     resp = requests.post(BASE_URL+ENDPOINT, data=json.dumps(data))
    #     print(resp.status_code)
    #     data = resp.json()
    #     print(data)
    #     return data["result"]


class Interactive_Learning:
    def entity_feature_vec(self, feature_vector, data, result):
        ner_result = named_entity_handler.NerPredicting().predict(data)
        result["ner"] = ner_result
        entity_names = named_entity_handler.Get_All_Entity_Name_Handler().get_all_entity_names()
        for ner in ner_result:
            for ent in ner['entity']:
                for unique_entity in entity_names:
                    if ent['type'] in unique_entity:
                        index = unique_entity[ent['type']]
                        feature_vector[ 2 + index ] = 1
        return feature_vector, data, result
    def update_prev_intent(self, original_data, obj_get_story_interactive):   
        if obj_get_story_interactive:     
            form = Interactive_Story_TempForm(original_data, instance=obj_get_story_interactive)
        else:
            form = Interactive_Story_TempForm(original_data)
        if form.is_valid():
            form.save(commit=True)
            is_saved = True
        if form.errors:
            is_saved = False
            print(form.errors)
        return is_saved

    def get_story_interactive(self, story_id):
        obj_story = None
        # retrieve all data from intent db  
        story_obj = Interactive_Story_Temp.objects.filter(story_id= story_id)
        for obj in story_obj:
            obj_story = obj
        return obj_story

    def expression(self, data):
        result = {}
        error = []
        flag = True

        if "story_id" in data:
            obj_get_story_interactive = self.get_story_interactive(data["story_id"])
        else:
            flag = False
            error.append("story_id is not given")

        if flag:
            if obj_get_story_interactive:
                for obj in obj_get_story_interactive:
                    prev_intent = obj.previous_intent
                    prev_action = obj.previous_action                    
                    feature_vector = [int(x) for x in obj.feature_vector.split(", ")]
            else:
                prev_intent = 0
                prev_action = 0
                feature_vector = []
                for i in range(100):
                    feature_vector.append(0)

            #predict intent
            intent, intent_id = intent_handler.Prediction().predict_KNN(data)
            print(int(intent_id), intent)
            intent_data = {
                "intent_id": intent_id,
                "intent": intent
            }

            feature_vector[1] = prev_intent
            feature_vector[0] = intent_id
            
            result["intent_data"] = intent_data

            ner_result = named_entity_handler.NerPredicting().predict(data)
            result["ner"] = ner_result
            entity_names = named_entity_handler.Get_All_Entity_Name_Handler.get_all_entity_names()
            for ner in ner_result:
                for ent in ner['entity']:
                    for unique_entity in entity_names:
                        if ent['type'] in unique_entity:
                            index = unique_entity[ent['type']]
                            feature_vector[ 2 + index ] = 1
            print(feature_vector)
            result["feature_vector"] = feature_vector
            original_data = {
                'story_id':data["story_id"],
                'previous_intent':intent_id,
                'previous_action':prev_action,
                'feature_vector': feature_vector
            }            
            print(orginal_data)
            self.update_prev_intent(orginal_data, obj_get_story_interactive)
        return result, error

    def correct_intent(self, new_intent, end_user_exp):
        result = {}
        data = {
            "query": end_user_exp,
            "intent": new_intent,
        }
        insert_intent_result = db_handler.Intent().insert_intent(data)
        result["is_intent_inserted"] = insert_intent_result
        get_intent_id = db_handler.Get_Intent_Handler().get_intent_id(new_intent)
        result["intent_id"] = get_intent_id
        return result

    def create_feature_vector(self):
        feature_vector[2] = prev_action
        while True:
            feature_vector[2] = prev_action
            response_action = predict_next_action(feature_vector)

            action.Response().actions(response_action)
            print(Style.RESET_ALL)

            print(Fore.YELLOW +"(c- continue, e - edit): ")
            print(Style.RESET_ALL)
            inp_tmp = input()
            if inp_tmp == "e":
                print(Fore.YELLOW + "What is the next action:")
                print(Style.RESET_ALL)
                response = ["utter_start",
                            "utter_restart",
                            "utter_stop",
                            "utter_action_listener",
                            "utter_greet", 
                            "utter_askname", 
                            "utter_askclass", 
                            "utter_askdivision"]

                for count, item in enumerate(response):
                    print(count, item)
                print(Fore.YELLOW + "Choose from options: ")
                response_action = input()
                print(Style.RESET_ALL) 
            
                                                                            
                # save training data
                insert_stories(feature_vector, response_action)
                print(feature_vector, response_action)
            prev_action = response_action
            
            if response_action == 3:
                break
                
            if response_action == 2 or response_action == 1 :
                prev_action = 0
                prev_intent = 0
                feature_vector = []
                for i in range(100):
                    feature_vector.append(0)
                break