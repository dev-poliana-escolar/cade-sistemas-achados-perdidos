from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.conf import settings


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'index.html', {})



def logout_view(request):
    logout(request)
    return redirect('index')


def admin_login(request):
    """Allow administrators to log in using native username/email + password.

    Only users with is_staff or is_superuser are allowed to authenticate here.
    This view accepts either username or email as the identifier.
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '')

        username = identifier
        if '@' in identifier:
            user_qs = User.objects.filter(email__iexact=identifier)
            if user_qs.exists():
                username = user_qs.first().get_username()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active and (user.is_staff or user.is_superuser):
                login(request, user)
                messages.success(request, 'Bem vindo, acesso administrativo concedido.')
                return HttpResponseRedirect(reverse('items:admin_items'))
            else:
                messages.error(request, 'Usuario ou senha inválidos.')
        else:
            messages.error(request, 'Credenciais inválidas. Verifique e tente novamente.')

    return render(request, 'admin_login.html', {})