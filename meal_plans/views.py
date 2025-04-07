from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view

from users.models import User, MealPlanReminder, FitnessStats
from .models import MealPlan
from .serializers import MealPlanSerializer

@api_view(['GET'])
def get_meal_plans(request):
    """Retrieve all meal plans."""
    meal_plans = MealPlan.objects.all()
    serializer = MealPlanSerializer(meal_plans, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_meal_plan(request):
    """Create a new meal plan."""
    serializer = MealPlanSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


def view_all_meal_plans(request):
    meal_plans = MealPlan.objects.all()
    return render(request, 'admin/view_meal_plans.html', {'meal_plans': meal_plans})

@login_required
def meal_plans_assigned(request):
    user = request.user
    assigned_meals = MealPlan.objects.filter(assigned_to=user)
    return render(request, "assigned_meal_plans.html", {"meal_plans": assigned_meals})


@login_required
def assign_meal_plan_view(request):
    students = User.objects.filter(role='student')
    available_meal_plans = MealPlan.objects.filter(assigned_to__isnull=True)

    if request.method == 'POST':
        student_id = request.POST.get("student_id")
        meal_plan_id = request.POST.get("meal_plan_id")

        student = User.objects.get(id=student_id)  # Here you are fetching the student based on student_id
        meal_plan = MealPlan.objects.get(id=meal_plan_id)  # Fetch the meal plan based on meal_plan_id

        # Assign the meal plan to the student
        meal_plan.assigned_to = student
        meal_plan.save()

        return redirect('trainer_dashboard')  # Redirect after assignment

    context = {
        'students': students,
        'meal_plans': available_meal_plans,
    }

    return render(request, template_name="admin/assign_meal_plan.html", context=context)


@login_required
def mark_meal_done(request, meal_id):
    if request.method == 'POST':
        stats, _ = FitnessStats.objects.get_or_create(user=request.user)
        meal = MealPlan.objects.get(id=meal_id)
        total_calories = sum([m.calories for m in meal.meals.all()])
        stats.total_calories_burned += total_calories
        stats.save()
        return redirect(request.META.get('HTTP_REFERER', 'user_dashboard'))
