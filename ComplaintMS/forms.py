from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from .models import Profile, Complaint


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ('subject', 'type_of_complaint', 'description')
        

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('company', 'phone', 'branch')
    

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
        
    def clean_email(self):
        """Check to see if any users already exist with this email as a username."""
        email = self.cleaned_data.get('email')
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            return email
        raise forms.ValidationError(_('This email address is already in use.'))


class UserUpdateForm(forms.ModelForm):
    email =forms.EmailField(widget = forms.TextInput(attrs={'readonly':'readonly'}))
    first_name=forms.CharField( max_length=30, required=True)
    last_name=forms.CharField( max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    
    def clean_email(self):
        """Check to see if any users already exist with this email as a username."""
        username = self.cleaned_data.get('email')
        try:
            match = User.objects.exclude(pk=self.instance.pk).get(username=username)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            return username
        raise forms.ValidationError(_('This email address is already in use.'))


class ProfileUpdateForm(forms.ModelForm):
    company=forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))
    branch=forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))

    class Meta:
        model = Profile
        fields = ('company', 'phone', 'branch')


class StatusUpdate(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ('status',)
        help_texts = {'status': None,}
