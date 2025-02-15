from django.shortcuts import render
from rest_framework import viewsets
from .models import MealPlan
from .serializers import MealPlanSerializer


class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    serializer_class = MealPlanSerializer