# Generated by Django 3.1 on 2020-08-11 06:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EntityDB',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start_pos', models.IntegerField()),
                ('end_pos', models.IntegerField()),
                ('is_trained', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='EntityNameDB',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('entity_name', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Intent_Training_Set',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='IntentDB',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('intent', models.CharField(max_length=250, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='QueryDB',
            fields=[
                ('query', models.TextField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='StoriesDB',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('feature_vector', models.CharField(max_length=500)),
                ('action', models.CharField(max_length=100)),
                ('is_trained', models.BooleanField(default=False)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddConstraint(
            model_name='storiesdb',
            constraint=models.UniqueConstraint(fields=('feature_vector', 'action'), name='unique feature'),
        ),
        migrations.AddField(
            model_name='intent_training_set',
            name='intent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatapp.intentdb'),
        ),
        migrations.AddField(
            model_name='intent_training_set',
            name='query',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatapp.querydb'),
        ),
        migrations.AddField(
            model_name='entitydb',
            name='entity_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatapp.entitynamedb'),
        ),
        migrations.AddField(
            model_name='entitydb',
            name='query',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatapp.querydb'),
        ),
        migrations.AddConstraint(
            model_name='intent_training_set',
            constraint=models.UniqueConstraint(fields=('intent', 'query'), name='unique intent and query'),
        ),
        migrations.AddConstraint(
            model_name='entitydb',
            constraint=models.UniqueConstraint(fields=('query', 'start_pos', 'end_pos'), name='unique appversion'),
        ),
    ]