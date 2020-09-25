from django.db import models

class QueryDB(models.Model):
    query = models.TextField(primary_key=True)

    def __str__(self):
        return self.query

class IntentDB(models.Model):
    id = models.AutoField(primary_key=True)
    intent = models.CharField(max_length=250, unique=True)


    def __str__(self):
        return self.intent

class Intent_Training_Set(models.Model):
    id = models.AutoField(primary_key=True)
    intent = models.ForeignKey(IntentDB, on_delete=models.CASCADE)
    query = models.ForeignKey(QueryDB, on_delete=models.CASCADE)

    class Meta:
        # db_table = 'EntityDB'
        constraints = [
            models.UniqueConstraint(fields=['intent', 'query'], name='unique intent and query')
        ]
class StoriesDB(models.Model):
    id = models.AutoField(primary_key=True)
    feature_vector = models.CharField(max_length=500)
    action = models.CharField(max_length=100)
    is_trained = models.BooleanField(default=False)
    date_time = models.DateTimeField(auto_now_add=True, blank=True)
    class Meta:
        # db_table = 'EntityDB'
        constraints = [
            models.UniqueConstraint(fields=['feature_vector', 'action'], name='unique feature')
        ]
class EntityNameDB(models.Model):
    id = models.AutoField(primary_key=True)
    entity_name = models.CharField(max_length=64, unique=True)

class EntityDB(models.Model):
    id = models.AutoField(primary_key=True)
    query = models.ForeignKey(QueryDB, on_delete=models.CASCADE)
    entity_name = models.ForeignKey(EntityNameDB, on_delete=models.CASCADE)
    start_pos = models.IntegerField()
    end_pos = models.IntegerField()
    is_trained = models.BooleanField(default=False)

    class Meta:
        # db_table = 'EntityDB'
        constraints = [
            models.UniqueConstraint(fields=['query', 'start_pos', 'end_pos'], name='unique appversion')
        ]

class Interactive_Story_Temp(models.Model):
    id = models.AutoField(primary_key=True)
    story_id = models.CharField(max_length=100, unique = True)
    previous_intent = models.IntegerField()
    previous_action = models.IntegerField()    
    feature_vector = models.CharField(max_length=500)
    date_time = models.DateTimeField(auto_now_add=True, blank=True)
   