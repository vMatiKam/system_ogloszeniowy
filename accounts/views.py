import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

# <--- Ddodany import modelu UserProfile
from .models import UserProfile
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Użytkownik nieaktywny
            user.save()

            # Wygenerowanie unikalnego tokena UUID i zapisanie go w profilu
            token = str(uuid.uuid4())
            user.profile.activation_token = token
            user.profile.save()

            activation_link = f"http://{request.get_host()}/accounts/activate/{token}/"

            print(f"\n==========================================")
            print(f"LINK AKTYWACYJNY DLA {user.username}:")
            print(activation_link)
            print(f"==========================================\n")

            mail_subject = 'Aktywacja konta w serwisie ogłoszeniowym'
            message = f"Cześć {user.username}!\n\nKliknij poniższy link, aby aktywować konto:\n{activation_link}"
            
            send_mail(
                mail_subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, 'Konto zostało utworzone! Wysłyłaliśmy link aktywacyjny na Twój adres e-mail. Sprawdź skrzynkę (oraz folder SPAM), aby aktywować konto.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def activate_account(request, token):
    try:
        # Szukamy profilu na podstawie aktywacyjnego tokena UUID
        profile = UserProfile.objects.get(activation_token=token)
        user = profile.user
        
        user.is_active = True
        user.save()
        
        # Kasujemy token po pomyślnej aktywacji
        profile.activation_token = None
        profile.save()

        messages.success(request, 'Twoje konto zostało pomyślnie aktywowane! Możesz się teraz zalogować.')
        return redirect('login')
        
    except UserProfile.DoesNotExist:
        messages.error(request, 'Link aktywacyjny jest nieprawidłowy lub został już wykorzystany.')
        return redirect('register')


@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Twój profil został zaktualizowany!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/profile.html', {'u_form': u_form, 'p_form': p_form})