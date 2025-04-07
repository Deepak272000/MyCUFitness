import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from users.models import UserProfile, WorkoutProgress, User, FitnessStats
from workouts.models import WorkoutPlan, Trainer
from django.contrib import messages
from django.db.models import Sum, Count
@login_required
def workout_dashboard(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:

        profile = None

    plans = WorkoutPlan.objects.all()

    if profile and profile.fitness_goals:
        filtered = plans.filter(goal=profile.fitness_goals.lower())
        plans = filtered if filtered.exists() else plans

    curr_plan = getattr(request.user.userprofile, "workout_plan", None)

    # Add workout progress calculation
    total_calories = WorkoutProgress.objects.filter(user=request.user).aggregate(Sum("calories_burned"))["calories_burned__sum"] or 0
    workouts_done = WorkoutProgress.objects.filter(user=request.user).count()

    context = {
        "profile": profile,
        "plans": plans,
        "curr_plan": curr_plan,
        "total_calories": total_calories,
        "workouts_done": workouts_done,
    }

    return render(request, "workouts/my_workouts.html", context)


@login_required
def workout_plan_view(request):
    if request.method == "POST":
        selected_plan_id = request.POST.get("selected_plan")
        if selected_plan_id:
            try:
                selected_plan = WorkoutPlan.objects.get(id=selected_plan_id)
                request.user.userprofile.workout_plan = selected_plan
                request.user.userprofile.save()
                messages.success(request, f"You have successfully chosen the {selected_plan.name} plan!")
                return redirect("dashboard")
            except WorkoutPlan.DoesNotExist:

                messages.error(request, "Invalid Workout Plan Selected.")
        else:
            messages.error(request, "Please select a workout plan.")
    return redirect("workout_dashboard")


@login_required
def my_plan_view(request):
    curr_plan = request.user.userprofile.workout_plan
    context = {
        "curr_plan": curr_plan
    }
    return render(request, "workouts/my_workouts.html", context)



@login_required
def calc_calories(request):
    if request.method == "POST":
        duration_minutes = request.POST.get("duration_minutes")
        calories_burned = request.POST.get("calories_burned")
        try:
            duration_minutes = int(duration_minutes)
            calories_burned = int(calories_burned)
        except (TypeError, ValueError):
            return JsonResponse({"error": "Invalid numeric values."}, status=400)

        progress = WorkoutProgress.objects.create(
            user=request.user,
            workout_type=request.user.userprofile.fitness_goals.lower(),
            duration_minutes=duration_minutes,
            calories_burned=calories_burned,
        )
        return JsonResponse({"status": "success", "progress_id": progress.id})

    return JsonResponse({"error": "POST request required."}, status=405)

@login_required
def assign_workout_view(request, client_id):
    if not hasattr(request.user, 'trainer'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        client = UserProfile.objects.get(id=client_id, assigned_trainer=request.user.trainer)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': "Client not found or not assigned to you."}, status=404)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            workout_id = data.get("workout_id")
            workout = WorkoutPlan.objects.get(id=workout_id)

            client.workout_plan = workout
            client.save()
            return JsonResponse({'message': f"{client.user.first_name} assigned to {workout.name}."})
        except WorkoutPlan.DoesNotExist:
            return JsonResponse({'error': 'WorkoutPlan matching query does not exist.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@login_required
def trainer_dashboard_view(request):
    trainer = getattr(request.user, "trainer", None)

    if trainer is None:
        messages.error(request, "You are not registered as a trainer.")
        return redirect("dashboard")

    assigned_clients = UserProfile.objects.select_related('user').filter(
        assigned_trainer=trainer
    ).values(
    "user__id",  # this is the correct ID for the user
    "user__first_name",
    "user__last_name",
    "user__email",
    "fitness_goals",
)


    workout_plans = WorkoutPlan.objects.all()

    return render(request, "workouts/trainer_dashboard.html", {
        "clients": assigned_clients,
        "workouts": workout_plans,
    })


# @login_required
# def select_student_for_assignment(request):
#     if not hasattr(request.user, 'trainer'):
#         return redirect('dashboard')
#
#     students = UserProfile.objects.filter(assigned_trainer=request.user.trainer)
#     return render(request, 'workouts/select_student.html', {'students': students})
#
from .forms import WorkoutPlanForm

@login_required
def create_workout_plan(request):
    if not request.user.is_staff and not hasattr(request.user, 'trainer'):
        return redirect("dashboard")  # Only admin/trainer allowed

    if request.method == "POST":
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Workout Plan added successfully!")
            return redirect("workout_dashboard")
    else:
        form = WorkoutPlanForm()

    return render(request, "workouts/create_workout_plan.html", {"form": form})

@login_required
def get_all_workouts(request):
    try:
        # First, get the Trainer object linked to the user
        trainer = Trainer.objects.get(user=request.user)
        workouts = WorkoutPlan.objects.filter(trainer=trainer).values("id", "name")
        return JsonResponse({"workouts": list(workouts)}, safe=True)
    except Trainer.DoesNotExist:
        return JsonResponse({"error": "Trainer profile not found."}, status=404)
    except Exception as e:
        print("Workout API error:", e)
        return JsonResponse({"error": str(e)}, status=500)



@login_required
def get_assigned_clients(request):
    trainer = getattr(request.user, "trainer", None)
    if not trainer:
        return JsonResponse({"error": "You are not registered as a trainer."}, status=403)

    clients = UserProfile.objects.filter(assigned_trainer=trainer).select_related("user").values(
        "id",
        "user__first_name",
        "user__last_name",
        "user__email",
        "fitness_goals"
    )
    return JsonResponse({"assigned_clients": list(clients)}, safe=True)


from users.models import UserProfile  # ✅ Make sure this is at the top if not already

def get_filtered_workouts(request, user_id):
    try:
        user_profile = UserProfile.objects.select_related("user").get(id=user_id)
        user = user_profile.user

        fitness_goal = user_profile.fitness_goals
        intensity = user_profile.activity_level

        # filtered_workouts = WorkoutPlan.objects.filter(goal=fitness_goal, intensity=intensity)
        filters = {'goal': fitness_goal}
        if intensity:  # Only filter by intensity if it is set
            filters['intensity'] = intensity

        filtered_workouts = WorkoutPlan.objects.filter(**filters)
        data = [
            {
                'id': workout.id,
                'name': workout.name,
                'goal': workout.goal,
                'intensity': workout.intensity,
                'duration_minutes': workout.duration_minutes,
            }
            for workout in filtered_workouts
        ]

        return JsonResponse({'filtered_workouts': data}, safe=False)

    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User profile not found'}, status=404)

    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def workout_goals_view(request):
    # Get distinct fitness goals from your plans
    fitness_goals = WorkoutPlan.objects.values_list('goal', flat=True).distinct()
    return render(request, "workouts/workout_plans.html", {"fitness_goals": fitness_goals})

@login_required
def goal_workout_plans(request, goal_name):
    plans = WorkoutPlan.objects.filter(goal=goal_name)
    return render(request, "workouts/goal_plans.html", {"plans": plans, "goal": goal_name})

from datetime import date, timedelta
@login_required
def students_progress_view(request):
    user = request.user

    # Student view – see own progress
    if user.role == 'student':
        try:
            profile = UserProfile.objects.get(user=user)
            stats = FitnessStats.objects.get(user=user)
        except (UserProfile.DoesNotExist, FitnessStats.DoesNotExist):
            profile = None
            stats = None

        # Calculate weekly calories burned
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())  # Monday

        weekly_qs = WorkoutProgress.objects.filter(
            user=user,
            date__range=(start_of_week, today)
        )

        # Initialize dict for 7 days
        weekly_calories = {
            (start_of_week + timedelta(days=i)).strftime('%A'): 0
            for i in range(7)
        }

        for entry in weekly_qs:
            weekday = entry.date.strftime('%A')
            weekly_calories[weekday] += entry.calories_burned

        # 🏅 Gamification – Badge Logic
        badges = []
        if stats:
            if stats.total_calories_burned >= 2000:
                badges.append("🔥 Calorie Crusher")
            if stats.workouts_completed >= 5:
                badges.append("🏋️ Workout Warrior")
            if stats.workouts_completed >= stats.weekly_workout_goal:
                badges.append("✅ Goal Smasher")

        context = {
            'is_trainer': False,
            'student': user,
            'profile': profile,
            'stats': stats,
            'badges': badges,
            'weekly_goals': {
                'calories_goal': stats.weekly_calorie_goal if stats else 0,
                'workouts_goal': stats.weekly_workout_goal if stats else 0,
            },
            'weekly_days': list(weekly_calories.keys()),
            'weekly_calories_data': list(weekly_calories.values()),
        }
        return render(request, 'workouts/students_progress.html', context)

    # Trainer view – see assigned students' progress
    elif user.role == 'trainer':
        try:
            trainer_obj = Trainer.objects.get(user=user)
        except Trainer.DoesNotExist:
            return redirect('dashboard')

        students = User.objects.filter(role='student', userprofile__assigned_trainer=trainer_obj)
        progress_data = []

        for student in students:
            try:
                profile = UserProfile.objects.get(user=student)
                stats = FitnessStats.objects.get(user=student)
            except (UserProfile.DoesNotExist, FitnessStats.DoesNotExist):
                continue

            progress_data.append({
                'student': student,
                'profile': profile,
                'stats': stats,
            })

        context = {
            'is_trainer': True,
            'students_progress': progress_data,
        }
        return render(request, 'workouts/students_progress.html', context)

    return redirect('dashboard')


from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import FitnessStats
from .models import WorkoutPlan


@login_required
def mark_workout_done(request, workout_id):
    if request.method == 'POST':
        # Get or create user's fitness stats
        stats, _ = FitnessStats.objects.get_or_create(user=request.user)

        # Get the workout plan
        workout = get_object_or_404(WorkoutPlan, id=workout_id)

        # Update stats
        stats.total_calories_burned += workout.total_calories
        stats.workouts_completed += 1

        # Save the stats
        stats.save()

    # Redirect back to dashboard or previous page
    return redirect(request.META.get('HTTP_REFERER', 'user_dashboard'))

