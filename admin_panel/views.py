import json
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from users.models import Review, UserProfile  #
from meal_plans.models import MealPlan
from users.models import User
from workouts.models import WorkoutPlan, Trainer


# Create your views here.
def is_admin(user):
    return user.is_staff or user.is_superuser
    #return user.is_authenticated and user.role == "admin"

@csrf_exempt  # Allows DELETE request
@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    if request.method == "DELETE":
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({"message": "User deleted successfully!"}, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)
    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def add_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
        full_name, email = data.get("full_name"), data.get("email")

        # Validate required fields
        if not full_name or not email:
            return JsonResponse({"error": "Full Name and Email are required."}, status=400)

        first_name, last_name = (full_name.split(" ", 1) + [""])[:2]  # Splitting full name safely

        # Create user object
        user = User.objects.create(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email,
            phone_number=data.get("phone_number"),
            weight=data.get("weight"),
            height=data.get("height"),
            role=data.get("role"),
        )

        return JsonResponse({"message": "User added successfully!", "user_id": user.id}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ✅ Admin Dashboard View (renders the HTML page)
@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    return render(request, "admin/admin_dashboard.html")

# ✅ API: Fetch admin dashboard statistics
@login_required
@user_passes_test(is_admin)
def get_admin_dashboard_data(request):
    try:
        total_users = User.objects.count()
        total_trainers = User.objects.filter(role="trainer").count()
        total_students = User.objects.filter(role="student").count()
        active_workouts = WorkoutPlan.objects.filter(is_active=True).count()
        total_meal_plans = MealPlan.objects.count()

        data = {
            "total_users": total_users,
            "total_trainers": total_trainers,
            "total_students": total_students,
            "active_workouts": active_workouts,
            "total_meal_plans": total_meal_plans,
        }
        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ✅ API: Fetch all users list for admin panel
@login_required
@user_passes_test(is_admin)
def get_users_list(request):
    users = User.objects.all().values("id", "first_name", "last_name", "email", "role")
    users_list = list(users)

    print(users_list)
    return JsonResponse({"users": users_list})

# ✅ API: Assign a trainer to a student
@login_required
@user_passes_test(lambda u: u.role == "admin")
@csrf_exempt
def assign_trainer_to_student(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            student_id = data.get("student_id")
            trainer_id = data.get("trainer_id")

            student_user = get_object_or_404(User, id=student_id, role="student")
            trainer_user = get_object_or_404(User, id=trainer_id, role="trainer")

            student_profile = get_object_or_404(UserProfile, user=student_user)
            trainer = get_object_or_404(Trainer, user=trainer_user)

            student_profile.assigned_trainer = trainer
            student_profile.save()

            return JsonResponse({
                "message": f"{trainer_user.first_name} assigned to {student_user.first_name} successfully!"
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=405)
@login_required
def assign_student_to_trainer(request):
    if request.method == "POST":
        trainer = request.user  # Trainer must be logged in
        if trainer.role != "trainer":
            return JsonResponse({"error": "Only trainers can assign students."}, status=403)

        student_id = request.POST.get("student_id")
        try:
            student = User.objects.get(id=student_id, role="student")
            student.assigned_trainer = trainer
            student.save()
            return JsonResponse({"message": f"{student.first_name} assigned to {trainer.first_name} successfully!"})
        except User.DoesNotExist:
            return JsonResponse({"error": "Student not found."}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)


def add_workout(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        goal = request.POST.get('goal')
        duration = request.POST.get('duration')
        intensity = request.POST.get('intensity')

        try:
            WorkoutPlan.objects.create(
                name=name,
                description=description,
                goal=goal,
                duration_minutes=duration,
                intensity=intensity
            )
            messages.success(request, "Workout added successfully!")
        except Exception as e:
            print("Workout Add Error:", e)
            messages.error(request, "Error adding workout.")

    return redirect('admin_dashboard')


@csrf_exempt
@login_required
@user_passes_test(lambda u: u.role == "admin")
def add_meal_plan(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    return JsonResponse({"message": "Meal Plan added successfully! (Mock API)"}, status=201)


@login_required
@user_passes_test(lambda u: u.role == "admin")
def get_all_workouts_and_mealplans(request):
    workouts = WorkoutPlan.objects.all().values("id", "title", "description")
    meal_plans = MealPlan.objects.all().values("id", "name", "description")  # ✅ Change `title` to `name` if needed


    return JsonResponse({"workouts": list(workouts), "meal_plans": list(meal_plans)})
@login_required
@user_passes_test(lambda u: u.role == "admin")
def get_reviews(request):
    reviews = Review.objects.all().values("id", "reviewer__first_name", "reviewer__role", "rating", "comment")
    return JsonResponse({"reviews": list(reviews)})
def get_students(request):
    """Fetch all students"""
    students = User.objects.filter(role='student').values("id", "first_name", "last_name", "email")
    return JsonResponse({"students": list(students)})

def get_trainers(request):
    """Fetch all trainers"""
    trainers = User.objects.filter(role='trainer').values("id", "first_name", "last_name", "email")
    return JsonResponse({"trainers": list(trainers)})

@login_required
def view_all_workouts(request):
    workouts = WorkoutPlan.objects.all()
    return render(request, 'admin/view_workouts.html', {'workouts': workouts})

@login_required
def view_all_trainers(request):
    trainers = User.objects.filter(role='trainer')
    return render(request, 'admin/view_trainers.html', {'trainers': trainers})

@login_required
def view_all_students(request):
    students = User.objects.filter(role='student')
    return render(request, 'admin/view_students.html', {'students': students})

@login_required
def view_all_users(request):
    users = User.objects.all()
    return render(request, 'admin/view_users.html', {'users': users})