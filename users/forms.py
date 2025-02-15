from django import forms
from django.apps import apps
from rest_framework import serializers
from .models import User
UserProfile = apps.get_model("users", "UserProfile")

class ProfileUpdateForm(forms.ModelForm):
    fitness_goals = forms.ChoiceField(
        choices=[
            ("weight_loss", "Weight Loss & Fat Burn"),
            ("muscle_gain", "Muscle Gain & Strength Training"),
            ("endurance", "Endurance & Stamina Boost"),
            ("flexibility", "Flexibility & Mobility"),
            ("core_strength", "Core & Functional Strength"),
            ("balanced_fitness", "Balanced Fitness & Well-being"),
            ("athletic_performance", "Athletic Performance & Conditioning"),
            ("custom_wellness", "Customized & Holistic Wellness"),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    dietary_preferences = forms.ChoiceField(
        choices=[
            ("vegetarian", "Vegetarian"),
            ("non-vegetarian", "Non-Vegetarian"),
            ("vegan", "Vegan"),
            ("keto", "Keto"),
            ("gluten-free", "Gluten-Free"),
            ("none", "No Preference"),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    allergies = forms.ChoiceField(
        choices=[
            ("no allergies", "No Allergies"),
            ("nuts", "Nuts"),
            ("gluten", "Gluten"),
            ("dairy", "Dairy"),
            ("seafood", "Seafood"),
            ("other", "Other (Please specify below)"),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'allergy-select'}),
        required=False
    )

    other_allergy = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specify other allergy', 'id': 'other-allergy-input', 'style': 'display: none;'})
    )

    class Meta:
        model = UserProfile
        fields = ['profile_picture','activity_level','first_name','last_name','dob','phone_number','weight','height','bmi', 'fitness_goals', 'dietary_preferences', 'allergies', 'other_allergy']

        profile_picture = forms.ImageField(required=False)


