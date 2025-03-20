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
    from_email = settings.EMAIL_HOST_USER  # ✅ Correct sender email
    recipient_list = [user_email]  # ✅ Ensure it's a list

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
