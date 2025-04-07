from django.urls import path

from admin_panel import views
from admin_panel.views import admin_dashboard_view, get_admin_dashboard_data, get_users_list, assign_trainer_to_student, \
    get_students, get_trainers, delete_user, add_user, assign_student_to_trainer, \
    get_reviews, get_all_workouts_and_mealplans, add_workout, add_meal_plan, view_all_users

urlpatterns = [

    path("dashboard/", admin_dashboard_view, name="admin_dashboard"),
    path("api/admin/dashboard/", get_admin_dashboard_data, name="admin_dashboard_data"),

    # ✅ User Management APIs
    path("api/admin/users/", get_users_list, name="get_users_list"),
    path("api/admin/students/", get_students, name="get_students"),
    path("api/admin/trainers/", get_trainers, name="get_trainers"),

    # ✅ User Actions
    path("api/admin/assign-trainer/", assign_trainer_to_student, name="assign_trainer"),
    path("api/admin/delete-user/<int:user_id>/", delete_user, name="delete_user"),
    path("api/admin/add-user/", add_user, name="add-user"),
    path("api/trainer/assign-student/", assign_student_to_trainer, name="assign_student"),
    path("api/admin/reviews/", get_reviews, name="get_reviews"),
    path("api/admin/all-plans/", get_all_workouts_and_mealplans, name="get_all_plans"),
    path('api/admin/add-workout/', add_workout, name="add_workout"),
    path('api/admin/add-meal-plan/', add_meal_plan, name="add_meal_plan"),

    path('admin-dashboard/workouts/', views.view_all_workouts, name='view_all_workouts'),
    path('admin-dashboard/trainers/', views.view_all_trainers, name='view_all_trainers'),
    path('admin-dashboard/students/', views.view_all_students, name='view_all_students'),
    path('admin-dashboard/users/', view_all_users, name='view_all_users'),



]