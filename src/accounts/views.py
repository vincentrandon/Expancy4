from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from accounts.forms import UserForm, UserAvatarForm, FormChangePassword
from accounts.models import User


def view_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    avatar_form = UserAvatarForm()

    initial_dict = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'company': user.company.name,
        'brand': user.brand,
    }
    if request.method == 'POST':
        print(request.POST)
        if 'avatar_form' in request.POST:
            avatar_form = UserAvatarForm(request.POST, request.FILES, instance=user)
            if avatar_form.is_valid():
                avatar_form.save()
                return redirect('tool:view-profile', pk=pk)

        else:
            form = UserForm(request.POST or None, request.FILES or None, instance=user)
            if form.is_valid():
                form.save()
                return redirect('tool:view-profile', pk=pk)
    else:
        form = UserForm(initial=initial_dict)

    return render(request, 'profile/profile.html', context={'form': form, 'avatar_form': avatar_form})


def change_password(request):
    if request.method == 'POST':
        form = FormChangePassword(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('tool:home')
        else:
            messages.error(request, 'Please correct the error below.')

    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'profile/change-password.html', {
        'form': form
    })
