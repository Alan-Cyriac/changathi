from django.shortcuts import render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from chatapp.mixins import HttpResponseMixin, SerializerMixin
from chatapp.utils import is_json
from chatapp import db_handler
from chatapp import story_handler
from chatapp import intent_handler #<---uncomment when necessary
from chatapp import named_entity_handler
from chatapp import interactive_handler
import pdb
import json

#________________________________________________________________________________
"""
Create Dataset - for intent
    url: insert_intent/
    input
    {
        "query":   <string intent>,
        "intent" : <string intent>,
    }
"""
#________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class Insert_Intent(View, HttpResponseMixin):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'message':'This is from get method'})
        return self.render_to_http_response(json_data)

    def post(self, request, *args, **kwargs):
        result = {}
        error = []
        status = 200
        data = request.body
        if is_json(data):
            # pdb.set_trace()
            data = json.loads(data)
            result, error = db_handler.Intent().insert_intent(data)
        else:
            status = 400
            error.append("This is not a valid json")
            print("[-] This is not a valid json")
        json_data = json.dumps({"result" : result, "error" : error})
        return self.render_to_http_response(json_data, status = status)
#________________________________________________________________________________

#________________________________________________________________________________
"""Retrieve all intents 
    url: all_intent/
    input
    {
    }
    """
#________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class Get_Intent(View, HttpResponseMixin):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'message':'This is from get method'})
        return self.render_to_http_response(json_data)

    def post(self, request):
        result = {}
        error = []
        status = 200
        result, error = db_handler.Get_Intent_Handler().get_all_intent()
        json_data = json.dumps({"result" : result, "error" : error})
        return self.render_to_http_response(json_data, status = status)
#________________________________________________________________________________

#________________________________________________________________________________
"""Retrieve all intents 
    url: all_intent/
    input
    {
        "intent": intent
    }
    """
#________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class Get_Intent_Id(View, HttpResponseMixin):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'message':'This is from get method'})
        return self.render_to_http_response(json_data)

    def post(self, request):
        # result = {}
        error = []
        status = 200
        data = request.body
        if is_json(data):
            # pdb.set_trace()
            data = json.loads(data)
            intent_id = db_handler.Get_Intent_Handler().get_intent_id(data["intent"])
        else:
            status = 400
            error.append("This is not a valid json")
            print("[-] This is not a valid json")
        json_data = json.dumps({"intent_id" : intent_id, "error" : error})
        return self.render_to_http_response(json_data, status = status)
#________________________________________________________________________________

#________________________________________________________________________________
"""
Train all intents 
    url: train_intent/
    input
    {
    }
    """
#________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class Train_Queries_With_Intents(View, HttpResponseMixin):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'message':'This is from get method'})
        return self.render_to_http_response(json_data)

    def post(self, request):
        result = {}
        error = []
        status = 200
        result, error = intent_handler.Training().train()
        json_data = json.dumps({"result" : result, "error" : error})
        return self.render_to_http_response(json_data, status = status)
#________________________________________________________________________________

#________________________________________________________________________________
"""
Predict intents 
    url: predict_intent/
    input
    {
        "end_user_expression": "Hi"
    }
    """
#________________________________________________________________________________

@method_decorator(csrf_exempt, name='dispatch')
class Predict_Intent(View, HttpResponseMixin):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'message':'This is from get method'})
        return self.render_to_http_response(json_data)

    def post(self, request, *args, **kwargs):
        result = {}
        error = []
        status = 200

        data = request.body
        if is_json(data):
            data = json.loads(data)
            result, error = intent_handler.Prediction().predict_KNN(data)
        else:
            status = 400
            error.append("This is not valid json")
            print("[-] This is not valid json")
        json_data = json.dumps({"result" : result, "error" : error})
        return self.render_to_http_response(json_data, status = status)
#________________________________________________________________________________

#______________________________________________________________________________________________________
"""
Save Training data to db Ner
    ========================
    url: save_data2db/
    table 1: QueryDB
    attributes: id, query
    table 2: EntityDB
    attributes: id, query(foregn field:- QueryDB),entity_name, start_pos, end_pos
    input format
    ============
    {
    'query' : <query :: str>,
    'entity_list' : [(<start pos :: int>, <end pos :: int>, <entity :: str>)]
    }
    eg:
    {
    'query' :"Horses are too tall and horses are pretend to care about your feelings",
    'entity_list' : [(0, 6, 'ANIMAL'), (25, 31, 'ANIMAL')]
    }
    output
    ======
    {
    'result' : result,
    'error' : error
    }

"""
#______________________________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class Insert_Named_Entity(HttpResponseMixin, SerializerMixin, View):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'msg':'This is from get method'})
        return HttpResponse(json_data, content_type='application/json')

    def post(self, request, *args, **kwargs):
        result = {}
        error = []
        data = request.body
        valid_json = is_json(data)
        if valid_json:
            data = json.loads(data)
            result, error, status = db_handler.Named_Entity_DB().save_data(data)
        else:
            status = 400
            error.append("[-] Please sent valid json data")
        f_result = {
                    'result' : result,
                    'error' : error
                    }
        json_data = json.dumps(f_result)
        return self.render_to_http_response(json_data, status=status)
#______________________________________________________________________________________________________

#______________________________________________________________________________________________________
# HardTrainData Ner
    # This is for scheduler to start training data
    # input 
    # =====
    # ENDPOINT = 'hard_train/'
    # context = {
    #     'train' : True,
    #     'n_iter' : 100 # optional parameter. Default value is 100
    # }
    # output
    # ======
    # {'result': ['Training completed'], 
    #  'error': []}
#______________________________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class Train_Queries_With_NE(HttpResponseMixin, SerializerMixin, View):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'msg':'This is from get method'})
        return self.render_to_http_response(json_data)

    def post(self, request, *args, **kwargs):
        result = []
        error = []

        data = request.body
        valid_json = is_json(data)
        if valid_json:
            data = json.loads(data)
            # TRAIN_DATA creation
            result = named_entity_handler.NerPreprocessing().data_preperation(data) #training is happening in the named_entity_handler.py don't worry
            # First it will process the data and from there itself it will give data for training and return the result...
        else:
            error.append("Please sent valid json data")

        json_data = json.dumps({'result': result, 'error' : error})
        return self.render_to_http_response(json_data)
#______________________________________________________________________________________________________

#______________________________________________________________________________________________________
# Predict Ner data
    # =============
    # input 
    # =====
    # ENDPOINT = 'pedictdata/'
    # context = {
    #     'test_text' : "Do you know Zerone-consulting?"
    # }
    # output
    # ======
    # {'result': {'test_text': 'Do you know Zerone-consulting?', 
    #             'entities': [['ORG', 'Zerone-consulting']]}, 
    #  'error': []}
#______________________________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class Predict_NE(HttpResponseMixin, SerializerMixin, View):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'msg':'This is from get method'})
        return HttpResponse(json_data, content_type='application/json')

    def post(self, request, *args, **kwargs):
        error = []
        result = {}
        n_iter = 100

        data = request.body
        valid_json = is_json(data)
        if valid_json:
            data = json.loads(data)
            final_res_list = named_entity_handler.NerPredicting().predict(data)
        else:
            error.append("[-] please send a valid json data")
        json_data = json.dumps({'result':final_res_list,
                        'error' : error})
        return self.render_to_http_response(json_data)
#______________________________________________________________________________________________________

#______________________________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class Delete_Trained_Data(View, HttpResponseMixin):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'msg':'This is from get method'})
        return HttpResponse(json_data, content_type='application/json')

    def post(self, request):
        result = []
        error = []
        result = named_entity_handler.Delete_Trained_Data_handler.deleting()
        json_data = json.dumps({'result': result, 'error' : error})
        return self.render_to_http_response(json_data, content_type='application/json')
#______________________________________________________________________________________________________




#______________________________________________________________________________________________________
# All_entity_names
    # =============
    # input 
    # =====
    # ENDPOINT = 'all_entity_names/'
    # context = {     
    # }
    # output
    # ======
    # {<EntityDB datas sorted descending>}, 
    #  'error': []}
#______________________________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class Get_Entity_Names(View, HttpResponseMixin):        
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'msg':'This is from get method'})
        return HttpResponse(json_data, content_type='application/json')

    def post(self, request, *args, **kwargs):
        error = []
        data = request.body
        valid_json = is_json(data)
        status = 200
        all_entity_names = []
        flag = False
        if valid_json:
            flag = True
            data = json.loads(data)
            all_entity_names = named_entity_handler.Get_All_Entity_Name_Handler().get_all_entity_names()
        else:
            status = 400
            error.append("[-] error 404")
        # json_data = SerializerMixin.serialize('json', all_datas)
        json_data = json.dumps(all_entity_names)
        return self.render_to_http_response(json_data,status)







#______________________________________________________________________________________________________
# AllDatasinDB
    # =============
    # input 
    # =====
    # ENDPOINT = 'all_data/'
    # context = {     
    # }
    # output
    # ======
    # {<EntityDB datas sorted descending>}, 
    #  'error': []}
#______________________________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class Get_Entities(View, HttpResponseMixin):        
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'msg':'This is from get method'})
        return HttpResponse(json_data, content_type='application/json')

    def post(self, request, *args, **kwargs):
        data = request.body
        valid_json = is_json(data)
        status = 200
        all_entities = []
        flag = False
        if valid_json:
            data = json.loads(data)
            all_entities = named_entity_handler.Get_Entity__handler().get_all_entities()
        else:
            status = 400
            error.append("[-] Please sent valid json data")
        # json_data = SerializerMixin.serialize('json', all_datas)
        json_data = json.dumps(all_entities)
        return self.render_to_http_response(json_data,status)
#______________________________________________________________________________________________________
#______________________________________________________________________________________________________
# GetUnique Entities
    # =============
    # input 
    # =====
    # ENDPOINT = 'get_unique_entities/'
    # context = {     
    # }
    # output
    # ======
    # {<EntityDB datas sorted descending>}, 
    #  'error': []}
#______________________________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class GetUniqueEntities(View, HttpResponseMixin):        
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'msg':'This is from get method'})
        return HttpResponse(json_data, content_type='application/json')

    def post(self, request, *args, **kwargs):
        result = {}
        error = []
        data = request.body
        valid_json = is_json(data)
        status = 200
        all_entities = []
        flag = False
        if valid_json:
            data = json.loads(data)
            all_entities = named_entity_handler.Get_Entity__handler().get_unique_entities()
            result["all_entities"] = all_entities
        else:
            status = 400
            error.append("[-] Please sent valid json data")
        # json_data = SerializerMixin.serialize('json', all_datas)
        json_data = json.dumps({'result': result, 'error' : error})
        return self.render_to_http_response(json_data,status)
#______________________________________________________________________________________________________
#______________________________________________________________________________________________________
# Delete_Entities_By_ID
    # =============
    # input 
    # =====
    # ENDPOINT = 'delete_data/'
    # context = {
    #     'id' : <id of entity_db>
    # }
    # output
    # ======
    # {'result': {"<id> deleted successfully"}, 
    #  'error': []}
#______________________________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class Delete_Entities_By_ID(HttpResponseMixin,View):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'msg':'This is from get method'})
        return HttpResponse(json_data, content_type='application/json')

    def post(self, request, *args, **kwargs):
        error = []
        result = []
        status = 200

        data = request.body
        valid_json = is_json(data)
        if valid_json:
            data = json.loads(data)
            id = data["id"]
            result, error, status = named_entity_handler.Delete_Entities_By_ID_handler.delete_data(id)
        else:
            status = 400
            error.append("[-] Please sent valid json data")

        json_data = json.dumps({'result':result,
                        'error' : error})
        return self.render_to_http_response(json_data, content_type='application/json', status=status)
#______________________________________________________________________________________________________

#______________________________________________________________________________________________________
# UpdateDatasinDB
    # =============
    # input 
    # =====
    # ENDPOINT = 'update_data/'
    # context = {
    #     'id' : "<id>",
    #     'query' : "<query>" # optional arg
    #     'start_pos' : <start_pos> # optional arg
    #     'end_pos' : <end_pos> # optional arg
    # }
    # output
    # ======
    # {'result': ["<id updated successfully>"], 
    #  'error': []}
#______________________________________________________________________________________________________
@method_decorator(csrf_exempt, name='dispatch')
class Update_Entities(HttpResponseMixin, SerializerMixin, View): 
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'msg':'This is from get method'})
        return self.render_to_http_response(json_data)

    def post(self, request, *args, **kwargs):
        error = []
        result = []

        data = request.body
        valid_json = is_json(data)
        if valid_json:
            status = 200
            data = json.loads(data)
            id = data["id"]
            result, error, status = named_entity_handler.Update_Entities_handler().add_entity(data)
        else:
            status = 400
            error.append("[-] Please sent valid json data")

        json_data = json.dumps({'result':result,
                        'error' : error})
        return self.render_to_http_response(json_data, status=status)
#______________________________________________________________________________________________________

#______________________________________________________________________________________________________
#Training Story
#______________________________________________________________________________________________________

@method_decorator(csrf_exempt, name='dispatch')
class Train_Stories(View, HttpResponseMixin):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'message':'This is from get method'})
        return self.render_to_http_response(json_data)

    def post(self, request, *args, **kwargs):
        result = []
        error = []

        result, error = story_handler.Story_Trainer().story_feature_vector_training()

        json_data = json.dumps({'result': result, 'error' : error})
        return self.render_to_http_response(json_data)
#______________________________________________________________________________________________________

#______________________________________________________________________________________________________
#Add Story
# url: add_story/
#______________________________________________________________________________________________________

@method_decorator(csrf_exempt, name='dispatch')
class AddStories(View, HttpResponseMixin):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'message':'This is from get method'})
        return self.render_to_http_response(json_data)

    def post(self, request, *args, **kwargs):
        result = []
        error = []
        data = request.body
        valid_json = is_json(data)
        if valid_json:
            status = 200
            data = json.loads(data)            
            result, error = story_handler.Story_Feature_Vector().story_feature_vector_Create(data)
        else:
            error.append("Please sent valid json data")

        json_data = json.dumps({'result': result, 'error' : error})
        return self.render_to_http_response(json_data)
#______________________________________________________________________________________________________
#______________________________________________________________________________________________________
#Add Story
# url: predict_next_action/
#______________________________________________________________________________________________________

@method_decorator(csrf_exempt, name='dispatch')
class PredictNextAction(View, HttpResponseMixin):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'message':'This is from get method'})
        return self.render_to_http_response(json_data)

    def post(self, request, *args, **kwargs):
        result = []
        error = []
        data = request.body
        valid_json = is_json(data)
        if valid_json:
            status = 200
            data = json.loads(data)            
            result, error = story_handler.Story().Prediction(data)
        else:
            error.append("Please sent valid json data")

        json_data = json.dumps({'result': result, 'error' : error})
        return self.render_to_http_response(json_data)
#______________________________________________________________________________________________________
class Interactive_Learning:    
    def expression(self, data):
        result = {}
        error = []
        flag = True

        if "story_id" in data:
            obj_get_story_interactive = interactive_handler.Interactive_Learning().get_story_interactive(data["story_id"])
        else:
            flag = False
            error.append("story_id is not given")

        if flag:
            
            if obj_get_story_interactive:
                
                prev_intent = obj_get_story_interactive.previous_intent
                prev_action = obj_get_story_interactive.previous_action                    
                feature_vector = [int(x) for x in obj_get_story_interactive.feature_vector.split(", ")]
            else:
                prev_intent = 0
                prev_action = 0
                feature_vector = []
                for i in range(100):
                    feature_vector.append(0)
            pdb.set_trace()
            #predict intent
            intent_result, intent_error = intent_handler.Prediction().predict_KNN(data)
            intent_id = int(intent_result["intent_id"])
            intent = intent_result["predicted"]
            print(intent_id, intent)
            intent_data = {
                "intent_id": intent_id,
                "intent": intent
            }

            feature_vector[1] = prev_intent
            feature_vector[0] = intent_id
            
            result["intent_data"] = intent_data

            feature_vector, data, result = interactive_handler.Interactive_Learning().entity_feature_vec(feature_vector, data, result)
            print(feature_vector)
            result["feature_vector"] = feature_vector
            orginal_data = {
                'story_id':data["story_id"],
                'previous_intent':intent_id,
                'previous_action':prev_action,
                'feature_vector': ", ".join([str(x) for x in feature_vector])
            }            
            print(orginal_data)
            interactive_handler.Interactive_Learning().update_prev_intent(orginal_data, obj_get_story_interactive)
        return result, error
    

@method_decorator(csrf_exempt, name='dispatch')
class InteractiveLearningView(View, HttpResponseMixin):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'message':'This is from get method'})
        return self.render_to_http_response(json_data)

    def post(self, request, *args, **kwargs):
        result = []
        error = []
        data = request.body
        valid_json = is_json(data)
        if valid_json:
            status = 200
            data = json.loads(data)
            result, error = Interactive_Learning().expression(data)
        else:
            error.append("Please sent valid json data")

        json_data = json.dumps({'result': result, 'error' : error})
        return self.render_to_http_response(json_data)
#______________________________________________________________________________________________________

@method_decorator(csrf_exempt, name='dispatch')
class Correct_Intent(View, HttpResponseMixin):
    def get(self, request, *args, **kwargs):
        json_data = json.dumps({'message':'This is from get method'})
        return self.render_to_http_response(json_data)

    def post(self, request, *args, **kwargs):
        result = []
        error = []
        data = request.body
        valid_json = is_json(data)
        if valid_json:
            status = 200
            data = json.loads(data)
            result, error = interactive_handler.Interactive_Learning().correct_intent(data)
        else:
            error.append("Please sent valid json data")

        json_data = json.dumps({'result': result, 'error' : error})
        return self.render_to_http_response(json_data)
#______________________________________________________________________________________________________