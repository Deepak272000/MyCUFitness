from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from meal_plans.models import MealPlan
from workouts.models import Trainer
from . import models
from .models import UserProfile, MealPlanReminder
from django.conf import settings

User= get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(post_save, sender=User)
def create_trainer_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'trainer':
        Trainer.objects.create(user=instance)


from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WorkoutProgress, FitnessStats

@receiver(post_save, sender=WorkoutProgress)
def update_fitness_stats(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        fitness_stats, created = FitnessStats.objects.get_or_create(user=user)
        fitness_stats.total_calories_burned += instance.calories_burned
        fitness_stats.workouts_completed += 1
        fitness_stats.save()


@receiver(post_save, sender=MealPlan)
def create_meal_plan_reminder(sender, instance, created, **kwargs):
    if created:
        reminder = MealPlanReminder.objects.create(
            user=instance.assigned_to,
            meal_name=instance.name,
            scheduled_time=instance.scheduled_time,
            date=instance.date
        )
        reminder.save()
