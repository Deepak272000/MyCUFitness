from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from meal_plans.models import Meal, MealPlan
from workouts.models import Workout
from chatbot.models import FitnessProgress
import matplotlib.pyplot as plt
import io
import base64
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view


from django.db.models import Q

user_context = {}

@api_view(['POST'])
def chatbot_response(request):
    user_id = request.user.id  # Identify user
    user_message = request.data.get("message", "").lower()

    # Initialize user session if not exists
    if user_id not in user_context:
        user_context[user_id] = {"step": "ask_goal"}

    # Step 1: Ask for fitness goal
    if user_context[user_id]["step"] == "ask_goal":
        user_context[user_id]["step"] = "waiting_for_goal"
        return Response({"response": "Hi! I can help you with meal and workout plans. What's your fitness goal? (e.g., weight loss, muscle gain, maintain fitness)"})

    # Step 2: Capture fitness goal and ask dietary preferences
    if user_context[user_id]["step"] == "waiting_for_goal":
        user_context[user_id]["goal"] = user_message
        user_context[user_id]["step"] = "waiting_for_diet"
        return Response({"response": "Got it! Do you have any dietary preferences? (e.g., vegetarian, keto, no preference)"})

    # Step 3: Capture dietary preference and provide meal plan
    if user_context[user_id]["step"] == "waiting_for_diet":
        user_context[user_id]["diet"] = user_message
        user_context[user_id]["step"] = "meal_suggestion"

        # Fetch meal plans based on user preference
        meal_plans = MealPlan.objects.filter(category=user_context[user_id]["diet"])
        if not meal_plans.exists():
            return Response({"response": "Sorry, no meal plans found for your preference."})

        meal_suggestions = "\n".join([f"- {meal.name}" for meal in meal_plans])
        return Response({"response": f"Thanks! Based on your goal and preference, here are some meal options:\n{meal_suggestions}"})

    return Response({"response": "How can I assist you with your fitness today?"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Only logged-in users can log progress
def log_fitness_progress(request):
    """Allows users to log daily fitness progress."""
    user = request.user
    weight = request.data.get("weight")
    calories_burned = request.data.get("calories_burned")
    workouts_completed = request.data.get("workouts_completed")

    progress = FitnessProgress.objects.create(
        user=user,
        weight=weight,
        calories_burned=calories_burned,
        workouts_completed=workouts_completed
    )

    adjustment = progress.adjust_fitness_plan()

    return Response({
        "message": "Progress logged successfully!",
        "adjustment": adjustment
    })



@login_required
def get_progress_chart(request):
    """Generates a progress chart for the user."""
    user = request.user
    progress_data = FitnessProgress.objects.filter(user=user).order_by("date")

    if not progress_data.exists():
        return Response({"error": "No progress data found."}, status=404)

    dates = [p.date for p in progress_data]
    weights = [p.weight for p in progress_data if p.weight is not None]
    calories = [p.calories_burned for p in progress_data if p.calories_burned is not None]
    workouts = [p.workouts_completed for p in progress_data if p.workouts_completed is not None]

    plt.figure(figsize=(8, 5))
    plt.plot(dates, weights, marker='o', label='Weight (kg)')
    plt.plot(dates, calories, marker='s', label='Calories Burned')
    plt.plot(dates, workouts, marker='^', label='Workouts Completed')
    plt.xlabel("Date")
    plt.ylabel("Progress")
    plt.legend()
    plt.title("Fitness Progress Over Time")
    plt.grid()

    # Convert plot to base64 image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    encoded_img = base64.b64encode(image_png).decode()

    return Response({"image": encoded_img})

