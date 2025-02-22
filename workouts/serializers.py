from rest_framework import serializers
from .models import Workout, Exercise, UserWorkoutTracking, Trainer

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'


class WorkoutSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = Workout
        fields = '__all__'


class UserWorkoutTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWorkoutTracking
        fields = '__all__'


class TrainerSerializer(serializers.ModelSerializer):
    assigned_users = serializers.PrimaryKeyRelatedField(many=True, queryset=Trainer.objects.all())

    class Meta:
        model = Trainer
        fields = '__all__'
