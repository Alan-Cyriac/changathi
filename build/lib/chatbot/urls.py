"""chatbot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from chatapp import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('interactive_learning/', views.InteractiveLearningView.as_view(), name="interactive_learning"),
    path('correct_intent/', views.Correct_Intent.as_view(), name="correct_intent"),
    path('insert_intent/', views.Insert_Intent.as_view(), name="insert_intent"),
    path('all_intent/', views.Get_Intent.as_view(), name="all_intent"),
    path('get_intent_id/', views.Get_Intent_Id.as_view(), name="get_intent_by_id"),
    path('train_intent/', views.Train_Queries_With_Intents.as_view(), name="train_intent"),
    path('predict_intent/', views.Predict_Intent.as_view(), name="predict_intent"),

    path('insert_named_entity/', views.Insert_Named_Entity.as_view(), name='insert_named_entity'),
    path('get_unique_entities/', views.GetUniqueEntities.as_view(), name='get_unique_entities'),

    path('train_ne/', views.Train_Queries_With_NE.as_view(), name='train_ne'),
    path('pedict_ne/', views.Predict_NE.as_view(), name='pedict_ne'),
    path('delete_trained_data/', views.Delete_Trained_Data.as_view(), name='delete_trained_data'),
    path('all_entity_names/', views.Get_Entity_Names.as_view(), name='all_entity_names'),
    path('all_entities/', views.Get_Entities.as_view(), name='all_data'),
    path('delete_entities_by_id/', views.Delete_Entities_By_ID.as_view(), name='delete_entities_by_id'),
    path('update_entities/', views.Update_Entities.as_view(), name='update_entities'),

    path('story_training/', views.Train_Stories.as_view(), name='story_training'),
    path('add_story/', views.AddStories.as_view(), name='add_story'),
    path('predict_next_action/', views.PredictNextAction.as_view(), name='predict_next_action'),
]