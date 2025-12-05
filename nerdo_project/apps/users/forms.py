from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    ajira_id = forms.CharField(max_length=20, required=True, help_text="Enter your Ajira ID (e.g. AJ-12345) for verification.")

    class Meta:
        model = User
        fields = ['username', 'email', 'ajira_id']

    def clean_ajira_id(self):
        """
        Simulated GOK Validation API
        In a real world, we would do: requests.get('api.ajira.go.ke/verify/...')
        Here, we validate the format.
        """
        ajira_id = self.cleaned_data.get('ajira_id')
        if not ajira_id.upper().startswith('AJ-'):
            raise forms.ValidationError("Invalid Ajira ID format. Must start with 'AJ-'")
        return ajira_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Update the auto-created profile
            user.profile.ajira_id = self.cleaned_data['ajira_id']
            # Grant verification badge if ID format is correct (Simulated)
            user.profile.is_verified = True 
            user.profile.save()
        return user