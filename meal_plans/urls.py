from django.urls import path

from . import views
from .views import get_meal_plans, create_meal_plan, view_all_meal_plans, meal_plans_assigned, assign_meal_plan_view


urlpatterns = [
    path('meal-plans/', get_meal_plans, name='get_meal_plans'),
    path('create-meal-plan/', create_meal_plan, name='create_meal_plan'),
    # path("admin-dashboard/meal-plans/", views.view_meal_plans, name="view_meal_plans")
    path("assigned/", meal_plans_assigned, name="meal_plans_assigned"),
    path('view-all-meal-plans/', view_all_meal_plans, name='view_all_meal_plans'),
    path('assign-meal/', assign_meal_plan_view, name='assign_meal_plan'),
    path('mark-meal-done/<int:meal_id>/', views.mark_meal_done, name='mark_meal_done'),
]
