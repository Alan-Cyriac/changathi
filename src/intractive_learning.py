import requests
import json
import action
import pdb
from colorama import init
init()
from colorama import Fore, Back, Style

# import story_handler
BASE_URL = 'http://127.0.0.1:8000/'

def insert_intent(query, intent):
    ENDPOINT = "insert_intent/"
    
    data = {
            "query": query,
            "intent": intent
            }
    
    resp = requests.post(BASE_URL+ENDPOINT, data=json.dumps(data))
    print(resp.status_code)
    print(resp.json())
    data = resp.json()
    return data["result"]
#add intent
def get_intent_id(intent):
    ENDPOINT = "get_intent_id/"
    intent = {
        "intent": intent
    }
    resp = requests.post(BASE_URL+ENDPOINT, data = json.dumps(intent))
    print(resp.status_code)
    print(resp.json())
    data = resp.json()
    return data["intent_id"]
# get intent id
def predict_intent(end_user_expression):
    ENDPOINT = "predict_intent/"
    #end_user_expression = "student"
    
    data = {
            "end_user_expression": end_user_expression,
            }

    resp = requests.post(BASE_URL+ENDPOINT, data=json.dumps(data))
    if resp.status_code == 200:
        data = resp.json()
        print(data)
        return data['result']['predicted'], data['result']['intent_id']
# predict_intent(end_user_expression = "add a student")
def pedict_ne(end_user_expression):
    ENDPOINT = "pedict_ne/"
    #end_user_expression = "add student named Alan of class 10"
    
    data= {
        "end_user_expression": end_user_expression
    }
    
    resp = requests.post(BASE_URL+ENDPOINT, data=json.dumps(data))
    if resp.status_code == 200:
        data = resp.json()
        return data['result']
# pedict_ne("add student named Alan of class 10")
def story_vector_training():
    ENDPOINT = "story_training/"
    resp = requests.post(BASE_URL+ENDPOINT)
    if resp.status_code == 200:
        data = resp.json()
        return data['result']
#story_vector_training, the same is there in API
def all_entity_names():
    ENDPOINT = "all_entity_names/"
    
    data = {
        "get_entity": False
    }
    
    resp = requests.post(BASE_URL+ENDPOINT, data=json.dumps(data))
    print(resp.status_code)
    print(resp.json())
    return resp.json()
#Get_All_Entity_Name
def insert_stories(feature_vector, response_action):
    ENDPOINT = "add_story/"
    feature_vector = ", ".join([str(x) for x in feature_vector])
    data= {
        "feature_vec": feature_vector,
        "action": response_action,
    }
    
    resp = requests.post(BASE_URL+ENDPOINT, data=json.dumps(data))
    print(resp.status_code)
    data = resp.json()
    print(data)
    return data["result"]

def predict_next_action(feature_vector):
    ENDPOINT = "predict_next_action/"
    # feature_vector = [4, 3, 7, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    s = [str(i) for i in feature_vector]                    
    s_feature_vector = ", ".join(s)
    data= {
            "feature_vec" : s_feature_vector
        }
        
    resp = requests.post(BASE_URL+ENDPOINT, data=json.dumps(data))
    data = resp.json()
    return data["result"]["predicted"]
class ChatBot:
    def train_chat():
        prev_action = 0
        prev_intent = 0
        
        feature_vector = []
        for i in range(100):
            feature_vector.append(0)
        while True:
            # create feature vector having 100 zeros
            
            print(Fore.YELLOW + "You(quit-q): ")
            end_user_exp = input()
            if end_user_exp == 'q':
                break
            print(Style.RESET_ALL)
            # 1. find intent
            intent, intent_id = predict_intent(end_user_exp)
            print(int(intent_id), intent)

            # Checking whether it is the correct intent; else give new intent and get its id;
            print(Fore.YELLOW + "Is the predicted intent correct:")
            is_correct_intent = input("Enter(n or y):")
            if is_correct_intent == "n":
                print(Fore.YELLOW + "Add New Intent")
                print(Style.RESET_ALL)
                print(Fore.YELLOW + "Please Enter New Intent:")
                new_intent = input()
                print(Style.RESET_ALL)
                result = insert_intent(end_user_exp, new_intent)
                print(Fore.YELLOW + "Is intent inserted" + str(result))
                print(Style.RESET_ALL)
                intent_id = get_intent_id(new_intent)
                print(Fore.YELLOW + "Intent Id: "+ str(intent_id))
                print(Style.RESET_ALL)

            feature_vector[1] = prev_intent
            feature_vector[0] = intent_id
            prev_intent = intent_id

            # 2. find entity
            ner_result = pedict_ne(end_user_exp)
            # create an API - return all entity name     --------------------
            print(ner_result)

            # 3. create vector
            entity_names = all_entity_names()
            
            
            for ner in ner_result:
                for ent in ner['entity']:
                    for unique_entity in entity_names:
                        if ent['type'] in unique_entity:

                            index = unique_entity[ent['type']]
                            feature_vector[ 2 + index ] = 1

            print(feature_vector)
            
            
            while True:
                feature_vector[2] = prev_action
                response_action = predict_next_action(feature_vector)

                print(Fore.GREEN + str(action.Response().actions(response_action)))
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
                    
    def chat():
        prev_action = 0
        prev_intent = 0
        
        feature_vector = []
        for i in range(100):
            feature_vector.append(0)
        while True:
            # create feature vector having 100 zeros
            
            print(Fore.YELLOW + "You(quit-q): ")
            end_user_exp = input()
            if end_user_exp == 'q':
                break
            print(Style.RESET_ALL)
            # 1. find intent
            intent, intent_id = predict_intent(end_user_exp)
            print(int(intent_id), intent)

            # Checking whether it is the correct intent; else give new intent and get its id;
            """print(Fore.YELLOW + "Is the predicted intent correct:")
            is_correct_intent = input("Enter(n or y):")
            if is_correct_intent == "n":
                print(Fore.YELLOW + "Add New Intent")
                print(Style.RESET_ALL)
                print(Fore.YELLOW + "Please Enter New Intent:")
                new_intent = input()
                print(Style.RESET_ALL)
                result = insert_intent(end_user_exp, new_intent)
                print(Fore.YELLOW + "Is intent inserted" + str(result))
                print(Style.RESET_ALL)
                intent_id = get_intent_id(new_intent)
                print(Fore.YELLOW + "Intent Id: "+ str(intent_id))
                print(Style.RESET_ALL)"""

            feature_vector[1] = prev_intent
            feature_vector[0] = intent_id
            prev_intent = intent_id

            # 2. find entity
            ner_result = pedict_ne(end_user_exp)
            # create an API - return all entity name     --------------------
            print(ner_result)

            # 3. create vector
            entity_names = all_entity_names()
            
            
            for ner in ner_result:
                for ent in ner['entity']:
                    for unique_entity in entity_names:
                        if ent['type'] in unique_entity:

                            index = unique_entity[ent['type']]
                            feature_vector[ 2 + index ] = 1

            print(feature_vector)
            
            
            while True:
                """print(Fore.YELLOW + "What is the next action:")
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
                    print(count, item)"""

                feature_vector[2] = prev_action
                """print(Fore.YELLOW + "Choose from options: ")
                print(Style.RESET_ALL)"""
                response_action = int(predict_next_action(feature_vector))
                
                
                # save training data
                # insert_stories(feature_vector, response_action)
                print(feature_vector, response_action)
                prev_action = response_action
                print(Fore.GREEN + str(action.Response().actions(response_action)))
                print(Style.RESET_ALL)

                if response_action == 3:
                    break
                    
                if response_action == 2 or response_action == 1 :
                    prev_action = 0
                    prev_intent = 0
                    feature_vector = []
                    for i in range(100):
                        feature_vector.append(0)
                    break

ChatBot.train_chat()