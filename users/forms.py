from django import forms
from django.apps import apps
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from users.models import User
UserProfile = apps.get_model("users", "UserProfile")

# User Registration Form
from django import forms
from users.models import User


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords must match!")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # Ensure password is hashed
        if commit:
            user.save()
        return user


# User Login Form
class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

# Password Reset Request Form
class PasswordResetRequestForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

# Password Reset Confirm Form
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

# Profile Update Form
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
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'activity_level', 'first_name', 'last_name', 'dob', 'phone_number', 'weight', 'height', 'bmi', 'fitness_goals', 'dietary_preferences', 'allergies', 'other_allergy']

# Custom Login Form with Remember Me Functionality
from allauth.account.forms import LoginForm
class CustomLoginForm(LoginForm):
    remember = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email or Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })

    def login(self, *args, **kwargs):
        remember = self.cleaned_data.get('remember')
        if not remember:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(1209600)
        return super(CustomLoginForm, self).login(*args, **kwargs)
