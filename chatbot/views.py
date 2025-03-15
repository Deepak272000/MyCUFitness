import nltk
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from nltk.tokenize import word_tokenize
from meal_plans.models import MealPlan
from workouts.models import Workout
import logging

nltk.download('punkt')

logger = logging.getLogger(__name__)

# **Expanded General Responses for More Natural Chat**
general_responses = {
    "hello": "Hello! How are you today?",
    "hi": "Hi there! What can I help you with?",
    "how are you": "I'm great! Here to help with fitness. How about you?",
    "bye": "Goodbye! Stay strong and keep working towards your goals!",
    "thank you": "You're welcome! Keep pushing forward!",
    "who are you": "I'm your fitness assistant! I can help with workouts, diet, and motivation.",
    "what can you do": "I can provide workout suggestions, meal plans, and fitness advice!",
}

# **Fitness-related Keywords**
workout_keywords = {"workout", "gym", "exercise", "training", "fitness", "lifting", "cardio"}
meal_keywords = {"meal", "diet", "nutrition", "food", "calories", "eating", "protein", "healthy"}

# **Memory to Maintain Conversation Flow (User Context)**
conversation_state = {}  # {user_id: {"topic": "meal" or "workout", "detail": None}}

@login_required
def chatbot_response(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input", "").strip().lower()
        user_id = request.user.id  # Unique identifier for tracking conversation state
        logger.info(f"User input: {user_input}")

        # **Tokenize input**
        tokens = set(word_tokenize(user_input))

        # **Step 1: Handle Basic Greetings & Responses**
        for phrase, reply in general_responses.items():
            if phrase in user_input:
                return JsonResponse({"response": reply})

        # **Step 2: Context Awareness - Follow Up on Previous Conversation**
        if user_id in conversation_state:
            last_topic = conversation_state[user_id]["topic"]

            # If the user asked about workouts last, fetch workout plans
            if last_topic == "workout":
                return fetch_workouts(request)

            # If the user asked about meals last, fetch meal plans
            elif last_topic == "meal":
                return fetch_meal_plans(request)

        # **Step 3: Identify if the User Wants a Workout or Meal Plan**
        if tokens.intersection(workout_keywords):
            conversation_state[user_id] = {"topic": "workout", "detail": None}
            return JsonResponse({"response": "Are you looking for a strength or cardio workout?"})

        elif tokens.intersection(meal_keywords):
            conversation_state[user_id] = {"topic": "meal", "detail": None}
            return JsonResponse({"response": "Do you prefer a high-protein or a low-carb diet?"})

        # **Step 4: Default fallback response (More Engaging)**
        return JsonResponse({"response": "That's interesting! Tell me more about your fitness goals."})

    return JsonResponse({"response": "Invalid request."})


def fetch_workouts(request):
    workouts = Workout.objects.filter(user=request.user).values("name", "description")[:3]
    response = (
        "Here are some workout recommendations:\n" +
        "\n".join([f"💪 {w['name']}: {w['description']}" for w in workouts])
        if workouts else "I don't see any workouts yet. Would you like me to suggest a routine?"
    )
    return JsonResponse({"response": response})


def fetch_meal_plans(request):
    meals = MealPlan.objects.filter(user=request.user).values("name", "description")[:3]
    response = (
        "Here are some meal plan ideas:\n" +
        "\n".join([f"🍽 {m['name']}: {m['description']}" for m in meals])
        if meals else "I don't have meal plans yet. Would you like a high-protein or balanced diet?"
    )
    return JsonResponse({"response": response})
