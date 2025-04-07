from django.urls import path
from . import views
from .views import create_workout_plan, workout_goals_view, goal_workout_plans

urlpatterns = [
    path('dashboard/', views.workout_dashboard, name='workout_dashboard'),
    path("workout-plans/", views.workout_plan_view, name="workout_plans"),
    path("myplan/", views.my_plan_view, name="my_plan_view"),
    path("calccalories/", views.calc_calories, name="calc_calories"),
    path("assign/<int:client_id>/", views.assign_workout_view, name="assign_workout"),
    path("trainer-dashboard/", views.trainer_dashboard_view, name="trainer_dashboard"),
    # path("assign/", views.select_student_for_assignment, name="assign_workout_select"),
    # path("assign/", views.select_student_for_assignment, name="assign_workout"),
    path("create/", create_workout_plan, name="create_workout_plan"),
     path("assign-clients/", views.get_assigned_clients, name="assign_clients"),
    path("api/", views.get_all_workouts, name="api_workouts"),
    path('filtered-workouts/<int:user_id>/', views.get_filtered_workouts, name='filtered_workouts'),
    path("goals/", workout_goals_view, name="workout_goals_view"),
    path("goals/<str:goal_name>/", goal_workout_plans, name="goal_workout_plans"),
    path('students-progress/', views.students_progress_view, name='students_progress'),
    path('mark-workout-done/<int:workout_id>/', views.mark_workout_done, name='mark_workout_done'),





]
