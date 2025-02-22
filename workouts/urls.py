from django.urls import path
from .views import WorkoutListView, WorkoutDetailView, UserWorkoutTrackingView, AssignWorkoutView, TrainerListView, \
    workout_list, workout_detail, my_workouts, trainer_dashboard, assign_workout, assign_clients, AssignWorkoutListView

urlpatterns = [
    path('workouts/', WorkoutListView.as_view(), name='workout-list'),
    path('workouts/<int:pk>/', WorkoutDetailView.as_view(), name='workout-detail'),
    path('track-workout/', UserWorkoutTrackingView.as_view(), name='track-workout'),
    path('assign-workout/', AssignWorkoutView.as_view(), name='assign_workout'),
    path('trainers/', TrainerListView.as_view(), name='trainer-list'),
    path('workout-plans/', workout_list, name='workout-list'),
    path('workout/<int:workout_id>/', workout_detail, name='workout-detail'),
    path('my-workouts/', my_workouts, name='my-workouts'),
    path('trainer-dashboard/', trainer_dashboard, name='trainer_dashboard'),
    path("assign-workout/<int:user_id>/", assign_workout, name="assign_workout"),
    path("assign-clients/", assign_clients, name="assign_clients"),
    path('workouts/assign-list/', AssignWorkoutListView.as_view(), name='assign_workout_list'),



]
