# Generated by Django 5.1.5 on 2025-02-14 04:37

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0014_remove_fitnessstats_user_delete_mealplanreminder_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MealPlanReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal_name', models.CharField(max_length=255)),
                ('scheduled_time', models.TimeField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='allergies',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='dietary_preferences',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='fitness_goals',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='two_factor_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='verification_token',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='activity_level',
            field=models.CharField(blank=True, choices=[('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High')], max_length=20),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='first_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='profile_pics/default.jpg', null=True, upload_to='profile_pics/'),
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='custom_user_groups', to='auth.group'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, default='profile_pics/default-profile.png', null=True, upload_to='profile_pics/'),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, related_name='custom_user_permissions', to='auth.permission'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='allergies',
            field=models.TextField(blank=True, default='None', null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='dietary_preferences',
            field=models.CharField(blank=True, choices=[('vegetarian', 'Vegetarian'), ('vegan', 'Vegan'), ('keto', 'Keto'), ('paleo', 'Paleo'), ('none', 'No Preference')], default='None', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='fitness_goals',
            field=models.CharField(blank=True, choices=[('strength_training', 'Strength Training'), ('fat_burn', 'Fat Burn & Weight Loss'), ('endurance', 'Endurance & Stamina Boost'), ('flexibility', 'Flexibility & Mobility'), ('functional', 'Functional & Core Strength'), ('personalized', 'Personalized Workout & Meal Planning')], default='General Fitness', max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='FitnessStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_calories_burned', models.IntegerField(default=0)),
                ('workouts_completed', models.IntegerField(default=0)),
                ('last_updated', models.DateField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WorkoutProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workout_type', models.CharField(max_length=100)),
                ('duration_minutes', models.IntegerField()),
                ('calories_burned', models.IntegerField()),
                ('date', models.DateField(default=datetime.date.today)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
