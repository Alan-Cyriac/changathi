from django.http import HttpResponse
class HttpResponseMixin(object):
    def render_to_http_response(self, json_data, status=200):
        #1000 lines of code
        return HttpResponse(json_data, content_type='application/json', status = status)

# From <--ner-->
class SerializerMixin(object):
    def serialize(self, qs):
        json_data = serialize('json', qs)
        p_data = json.loads(json_data)
        final_list = []
        for obj in p_data:
            emp_data = {}
            emp_data = obj['fields']
            emp_data['id'] = obj['pk']
            final_list.append(emp_data)
        json_data = json.dumps(final_list)
        return json_data
