from django import forms
from chatapp.models import *

class QueryForm(forms.ModelForm):
    class Meta:
        model = QueryDB
        fields = '__all__'

class IntentForm(forms.ModelForm):
    class Meta:
        model = IntentDB
        fields = '__all__'

class Intent_Training_SetForm(forms.ModelForm):
    class Meta:
        model = Intent_Training_Set
        fields = '__all__'

class EntityForm(forms.ModelForm):
    class Meta:
        model = EntityDB
        fields = '__all__'

class EntityNameDBForm(forms.ModelForm):
    class Meta:
        model = EntityNameDB
        fields = '__all__'

class StoriesDBForm(forms.ModelForm):
    class Meta:
        model = StoriesDB
        fields = '__all__'

class Interactive_Story_TempForm(forms.ModelForm):
    class Meta():
        model = Interactive_Story_Temp
        fields = '__all__'