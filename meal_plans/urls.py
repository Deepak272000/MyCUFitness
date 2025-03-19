from django.urls import path
from .views import get_meal_plans, create_meal_plan

urlpatterns = [
    path('meal-plans/', get_meal_plans, name='get_meal_plans'),
    path('create-meal-plan/', create_meal_plan, name='create_meal_plan'),
]