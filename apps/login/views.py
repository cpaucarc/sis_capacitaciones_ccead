from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, RedirectView
from django.views.generic.base import ContextMixin, TemplateView

from apps.common.constants import TIPO_PERSONA_CONSEJO_FACULTAD
from apps.login.forms import LoginForm, UsuarioPasswordChangePassword
from django.conf import settings
from django.contrib import auth, messages


class LoginView(FormView):
    template_name = "login/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(self.request, user)
            if user.username != 'admin':
                self.request.session['tipo_persona_desc'] = user.persona.get_tipo_persona_display()
                self.request.session['tipo_persona'] = user.persona.tipo_persona
                self.request.session['fullname'] = user.persona.nombre_completo
                if self.request.session.get('tipo_persona') == TIPO_PERSONA_CONSEJO_FACULTAD:
                    self.request.session['facultad'] = user.persona.facultad.nombre
            else:
                self.request.session['tipo_persona_desc'] = ''
                self.request.session['tipo_persona'] = ''
                self.request.session['fullname'] = ''
                self.request.session['facultad'] = ''
            self.request.session['username'] = user.username
            return super().form_valid(form)
        else:
            messages.error(self.request, "El usuario o la contraseña son incorrectas")
            return self.form_invalid(form)

    def get_success_url(self):
        next = self.request.GET.get("next")
        if next is not None:
            return next
        return '/'


class LogoutView(RedirectView):
    def get_redirect_url(self, **kwargs):
        auth.logout(self.request)
        self.request.session['tipo_persona'] = None
        self.request.session['tipo_persona_desc'] = None
        self.request.session['username'] = None
        self.request.session['fullname'] = None
        self.request.session['facultad'] = None
        return settings.LOGIN_URL


class BaseLogin(ContextMixin, View):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'tipo_persona': self.request.session.get('tipo_persona'),
            'tipo_persona_desc': self.request.session.get('tipo_persona_desc'),
            'username': self.request.session.get('username'),
            'fullname': self.request.session.get('fullname'),
            'facultad': self.request.session.get('facultad')
        })
        return context


class InicioView(LoginRequiredMixin, BaseLogin, TemplateView):
    template_name = 'login/inicio.html'


class Error403View(LoginRequiredMixin, TemplateView):
    template_name = "403.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['msg_403'] = 'Ud. no tiene permisos para acceder a este sitio'
        return context_data


class UsuarioChangePasswordView(PasswordChangeView):
    template_name = 'login/password_change.html'
    form_class = UsuarioPasswordChangePassword
    success_url = reverse_lazy('login:logout')
