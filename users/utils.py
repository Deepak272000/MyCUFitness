from django.core.mail import send_mail
from django.conf import settings
import math

def calculate_bmi(weight, height):
    """ Calculate BMI from weight (kg) and height (cm) """
    if weight and height:
        return round(weight / ((height / 100) ** 2), 2)
    return None

def send_welcome_email(user_email):
    """ Send Welcome Email to New Users """
    subject = "Welcome to MyCUFitness!"
    message = "Thank you for signing up. Start your fitness journey today!"
    sender = settings.EMAIL_HOST_USER
    send_mail(subject, message, sender, [user_email])