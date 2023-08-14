from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, PostModel
from datetime import date
import re
from django.contrib.auth.forms import UserCreationForm


class SignupForm(forms.ModelForm):
    email = forms.EmailField(error_messages={'unique': 'Email already exists'})
    password = forms.CharField(widget=forms.PasswordInput)
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'max': date.today()}))
    phone = forms.CharField(max_length=10, widget=forms.NumberInput)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'image', 'bio', 'phone', 'dob', 'password']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        pattern = r'\d{10}'
        if not re.match(pattern, phone):
            raise forms.ValidationError("Please Enter Proper Phone Number!")
        return phone

    def clean_first_name(self):
        fname = self.cleaned_data['first_name']
        if fname.isdigit():
            raise forms.ValidationError("Please Enter Character")
        return fname

    def clean_last_name(self):
        lname = self.cleaned_data['last_name']
        if lname.isdigit():
            raise forms.ValidationError("Please Enter Character")
        return lname

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autofocus": True}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )


class EditForm(forms.ModelForm):
    email = forms.EmailField(error_messages={'unique': 'Email already exists'})
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'max': date.today()}))
    phone = forms.CharField(max_length=10, widget=forms.NumberInput)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'image', 'bio', 'phone', 'dob']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        pattern = r'\d{10}'
        if not re.match(pattern, phone):
            raise forms.ValidationError("Please Enter Proper Phone Number!")
        return phone

    def clean_first_name(self):
        fname = self.cleaned_data['first_name']
        if fname.isdigit():
            raise forms.ValidationError("Please Enter Character")
        return fname

    def clean_last_name(self):
        lname = self.cleaned_data['last_name']
        if lname.isdigit():
            raise forms.ValidationError("Please Enter Character")
        return lname


class AddPostForm(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['caption', 'post_image']
