from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Blokujemy konto do czasu weryfikacji e-mail
            user.save()

            # Generowanie tokena i linku aktywacyjnego
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"http://{request.get_host()}/accounts/activate/{uid}/{token}/"

            # Treść wiadomości e-mail
            mail_subject = 'Aktywacja konta w serwisie ogłoszeniowym'
            message = f"Cześć {user.username}!\n\nDziękujemy za rejestrację. Kliknij poniższy link, aby aktywować swoje konto:\n{activation_link}\n\nJeśli to nie Ty rejestrowałeś konto, zignoruj tę wiadomość."
            
            send_mail(
                mail_subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.info(request, 'Konto zostało utworzone! Sprawdź swoją skrzynkę e-mail i kliknij link aktywacyjny.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Twoje konto zostało pomyślnie aktywowane! Możesz się teraz zalogować.')
        return redirect('login')
    else:
        messages.error(request, 'Link aktywacyjny jest nieprawidłowy lub wygasł.')
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

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/profile.html', context)