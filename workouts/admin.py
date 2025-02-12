from django.contrib import admin
from .models import Workout, Exercise, UserWorkoutTracking, Trainer

admin.site.register(Workout)
admin.site.register(Exercise)
admin.site.register(UserWorkoutTracking)
admin.site.register(Trainer)
