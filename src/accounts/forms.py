from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from accounts.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'company', 'brand')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'first_name': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'last_name': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'company': forms.TextInput(attrs={
                'class': 'shadow-sm bg-gray-200 focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'brand': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['company'].disabled = True
        self.fields['brand'].disabled = True


class UserAvatarForm(forms.ModelForm):
    avatar_form = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = User
        fields = ('avatar',)
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'onchange': 'submit();',
                                             'class': 'ml-5 bg-white py-2 px-3 border border-gray-300 rounded-md shadow-sm text-sm leading-4 font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'}),
        }

class FormChangePassword(PasswordChangeForm):


    class Meta:
        fields = ["old_password", "new_password1", "new_password2"]
        widgets = {
            'old_password': forms.PasswordInput(attrs={
                'class': 'shadow-sm focus:ring-blue-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'new_password1': forms.PasswordInput(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'}),
            'new_password2': forms.PasswordInput(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md'})
        }