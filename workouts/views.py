from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.generic import ListView
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render, redirect
from .models import Workout, UserWorkoutTracking, Reminder
from .serializers import WorkoutSerializer, UserWorkoutTrackingSerializer, TrainerSerializer
from django.contrib import messages
from users.models import User
from workouts.models import Trainer


# ✅ List all workouts or filter by category/difficulty
class WorkoutListView(generics.ListAPIView):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Workout.objects.all()
        category = self.request.GET.get("category")  # ✅ Use GET instead of query_params
        difficulty = self.request.GET.get("difficulty")

        if category:
            queryset = queryset.filter(category=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        return queryset


# ✅ Retrieve single workout with exercises
class WorkoutDetailView(generics.RetrieveAPIView):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.AllowAny]


# ✅ Track a user's workout completion
class UserWorkoutTrackingView(generics.CreateAPIView):
    queryset = UserWorkoutTracking.objects.all()
    serializer_class = UserWorkoutTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Assign current user automatically


# ✅ Trainer assigns workouts to users
class AssignWorkoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def post(self, request, *args, **kwargs):
        trainer = get_object_or_404(Trainer, user=request.user)
        user_id = request.data.get("user_id")
        workout_id = request.data.get("workout_id")

        user = get_object_or_404(User, id=user_id)
        workout = get_object_or_404(Workout, id=workout_id)

        UserWorkoutTracking.objects.create(
            user=user,
            workout=workout,
            duration_minutes=workout.duration_minutes,
            calories_burned=workout.calories_burned_estimate
        )

        return Response({"message": f"Workout '{workout.title}' assigned to {user.username}"}, status=201)

# ✅ List trainers
class TrainerListView(generics.ListAPIView):
    queryset = Trainer.objects.all()
    serializer_class = TrainerSerializer
    permission_classes = [permissions.AllowAny]

def workout_list(request):
    category = request.GET.get("category", "")
    workouts = Workout.objects.filter(category=category) if category else Workout.objects.all()
    return render(request, "workouts/workout_list.html", {"workouts": workouts})

def workout_detail(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id)
    return render(request, "workouts/workout_detail.html", {"workout": workout})


@login_required
def my_workouts(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated"}, status=401)

    # Fetch workouts linked to the user via UserWorkoutTracking
    user_workouts = UserWorkoutTracking.objects.filter(user=request.user)

    workout_list = [
        {
            "id": uwt.workout.id,
            "title": uwt.workout.title,
            "duration": uwt.workout.duration_minutes,
            "calories_burned": uwt.calories_burned,
            "category": uwt.workout.category,
            "date_completed": uwt.date_completed.strftime("%Y-%m-%d"),
        }
        for uwt in user_workouts
    ]

    return JsonResponse({"my_workouts": workout_list})


@login_required
def trainer_dashboard(request):
    try:
        trainer = request.user.trainer_profile  # Check if user has trainer profile
    except Trainer.DoesNotExist:
        return JsonResponse({"error": "Trainer profile not found. Please contact admin."}, status=404)

    clients = trainer.assigned_users.all()
    context = {"trainer": trainer, "clients": clients}

    return render(request, "workouts/trainer_dashboard.html", context)




@login_required
def get_trainer_clients(request):
    trainer = request.user.trainer_profile
    clients = trainer.assigned_users.values("id", "first_name", "email")
    return JsonResponse({"clients": list(clients)})


@login_required
def assign_workout(request, user_id):
    """Assign a workout to a client."""
    client = get_object_or_404(User, id=user_id)  # Get the client user
    workouts = Workout.objects.all()  # Fetch available workouts

    if request.method == "POST":
        workout_id = request.POST.get("workout_id")  # Get selected workout
        duration_minutes = request.POST.get("duration_minutes")
        calories_burned = request.POST.get("calories_burned")

        workout = get_object_or_404(Workout, id=workout_id)  # Get the workout object
        UserWorkoutTracking.objects.create(
            user=client,
            workout=workout,
            duration_minutes=duration_minutes,
            calories_burned=calories_burned
        )

        messages.success(request, f"Workout '{workout.title}' assigned to {client.first_name}!")
        return redirect("trainer_dashboard")  # Redirect back to the trainer dashboard

    return render(request, "workouts/assign_workout.html", {"client": client, "workouts": workouts})


@login_required
def assign_clients(request):
    """Assign students to a trainer & retrieve students assigned to the trainer."""
    trainer = request.user.trainer_profile  # Ensure the user has a trainer profile

    # Get only students (excluding trainers and admins)
    available_clients = User.objects.filter(role="student").exclude(id__in=trainer.assigned_users.all())

    # If it's a POST request, assign selected students
    if request.method == "POST":
        selected_clients = request.POST.getlist("clients")
        trainer.assigned_users.add(*selected_clients)
        trainer.save()
        return redirect("trainer_dashboard")  # Redirect back to trainer dashboard

    # If it's an API request (AJAX), return JSON response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        assigned_clients = trainer.assigned_users.filter(role="student").values("id", "first_name", "email",
                                                                                "fitness_goals")
        return JsonResponse({"assigned_clients": list(assigned_clients)})

    # Render the HTML template normally
    return render(request, "workouts/assign_clients.html", {"available_clients": available_clients})


class AssignWorkoutListView(ListView):
    model = Workout
    template_name = 'workouts/assign_workout_list.html'


@login_required
def user_dashboard(request):
    user = request.user
    progress = UserWorkoutTracking.get_weekly_progress(user)

    context = {
        "total_calories_burned": progress.get("total_calories", 0),
        "total_workout_duration": progress.get("total_duration", 0),
        "upcoming_workouts": Workout.objects.filter(category="Personalized")[:3]  # Placeholder for future reminders
    }

    return render(request, "dashboard/user_dashboard.html", context)

@login_required
def get_user_reminders(request):
    reminders = Reminder.objects.filter(user=request.user, date_time__gte=now(), is_read=False)
    return JsonResponse({"reminders": list(reminders.values("message", "date_time"))})
