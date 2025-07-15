from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from adminapp.models import CustomUser  # adjust if CustomUser is elsewhere

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'mobile', 'email', 'address', 'profile_picture', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    
