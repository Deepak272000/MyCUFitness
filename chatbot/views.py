from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from meal_plans.models import MealPlan
from workouts.models import WorkoutPlan
from chatbot.models import FitnessProgress
import matplotlib.pyplot as plt
import io
import base64
import random

# User context to store temporary chat state
user_context = {}

# Expected input options
EXPECTED_GOALS = [
    "weight_loss", "muscle_gain", "core_strength", "endurance",
    "flexibility", "athletic_performance", "balanced_fitness", "custom_wellness"
]

EXPECTED_DIETARY_PREFERENCES = [
    "vegetarian", "vegan", "keto", "gluten_free", "non_vegetarian", "none"
]

FALLBACK_RESPONSES = [
    "I'm not sure I understand. Can you rephrase that?",
    "Could you clarify? I'm here to help with fitness and nutrition!",
    "I didn't get that. Can you try again?",
    "I'm designed to help with fitness goals. Can you tell me your goal?",
]

@api_view(['POST'])
def chatbot_response(request):
    user_id = request.user.id
    user_message = request.data.get("message", "").strip().lower()

    if user_id not in user_context:
        user_context[user_id] = {"step": "ask_goal"}

    if user_context[user_id]["step"] == "ask_goal":
        user_context[user_id]["step"] = "waiting_for_goal"
        return Response({
            "response": "Hi! I can help with meal and workout plans. What's your fitness goal? (e.g., weight_loss, muscle_gain, core_strength)"
        })

    if user_context[user_id]["step"] == "waiting_for_goal":
        if user_message in EXPECTED_GOALS:
            user_context[user_id]["goal"] = user_message
            user_context[user_id]["step"] = "waiting_for_diet"
            return Response({
                "response": "Got it! Do you have any dietary preferences? (e.g., vegetarian, keto, vegan, none)"
            })
        else:
            return Response({"response": random.choice(FALLBACK_RESPONSES)})

    if user_context[user_id]["step"] == "waiting_for_diet":
        if user_message in EXPECTED_DIETARY_PREFERENCES:
            user_context[user_id]["diet"] = user_message
            user_context[user_id]["step"] = "show_workout"

            meal_plans = MealPlan.objects.filter(diet_type__iexact=user_message)
            if not meal_plans.exists():
                meal_text = "No meal plans found for your preference."
            else:
                meal_text = "\n".join([f"- {meal.name}" for meal in meal_plans])

            return Response({
                "response": f"Here are some meal plans based on your preference:\n{meal_text}\n\nWould you like workout recommendations as well? (yes/no)"
            })
        else:
            return Response({"response": random.choice(FALLBACK_RESPONSES)})

    if user_context[user_id]["step"] == "show_workout":
        if "yes" in user_message:
            goal = user_context[user_id]["goal"]
            workouts = WorkoutPlan.objects.filter(goal__iexact=goal)
            if not workouts.exists():
                workout_text = "No workout plans found for your goal."
            else:
                workout_text = "\n".join([f"- {w.name}" for w in workouts])

            user_context[user_id]["step"] = "done"
            return Response({
                "response": f"Here are some recommended workout plans:\n{workout_text}\n\nLet me know if you'd like to log your progress or need anything else!"
            })
        else:
            user_context[user_id]["step"] = "done"
            return Response({"response": "Alright! Let me know if you want to log progress or need anything else."})

    return Response({"response": "How can I assist you with your fitness today?"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
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

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    encoded_img = base64.b64encode(image_png).decode()

    return Response({"image": encoded_img})
