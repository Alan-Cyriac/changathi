from django.contrib import admin
from .models import *

admin.site.register(QueryDB)
admin.site.register(IntentDB)
admin.site.register(Intent_Training_Set)
admin.site.register(EntityNameDB)
admin.site.register(EntityDB)
admin.site.register(StoriesDB)
admin.site.register(Interactive_Story_Temp)