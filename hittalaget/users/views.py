from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, redirect_to_login
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    RedirectView,
    UpdateView,
)
from .forms import (
    UserCreateForm,
    UserUpdateForm,
    AuthenticationForm2,
    PasswordChangeForm2,
)   

User = get_user_model()


# ---------------------------------- #
# ------------- MIXINS ------------- #
# ---------------------------------- #


class RedirectIfLoggedInMixin:
    ''' Redirect to <user:detail> if user is already logged in. '''
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            return redirect(user.get_absolute_url())
        else:
            return super().dispatch(request, *args, **kwargs)


class GetObjectMixin:
    ''' Get the user object of the currently logged in user. '''
    def get_object(self, queryset=None):
        if not hasattr(self, 'object'):
            user = self.request.user
            self.object = user
        
        return self.object


class GetSuccessUrlMixin:
    ''' Return the user:detail page. '''
    def get_success_url(self):
        user = self.request.user
        return user.get_absolute_url()

 
# --------------------------------- #
# ------------- VIEWS ------------- #
# --------------------------------- #


class UserCreateView(RedirectIfLoggedInMixin, GetSuccessUrlMixin, CreateView):
    template_name = "registration/register.html"
    form_class = UserCreateForm

    def form_valid(self, form):
        """ Login user after account is created. """
        form.save()
        username = self.request.POST["username"]
        password = self.request.POST["password2"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "Välkommen till hittalaget.se!")
        return super().get_success_url()


class UserDetailView(DetailView):
    template_name = "users/detail.html"

    def dispatch(self, request, *args, **kwargs):
        user = self.get_object()
        """ Only show user profile if user is active. """
        if user.is_active:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404()

    def get_object(self, queryset=None):
        if not hasattr(self, "object"):
            username = self.kwargs["username"]
            user = get_object_or_404(User, username=username)
            self.object = user

        return self.object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['age'] = user.get_age()
        return context


class UserLoginView(RedirectIfLoggedInMixin, LoginView):
    template_name = "registration/login.html"
    form_class = AuthenticationForm2


class UserRedirectView(LoginRequiredMixin, RedirectView):
    """ LoginView redirects to settings.LOGIN_REDIRECT_URL which in turn
    will call this view. """
    def get_redirect_url(self):
        user = self.request.user
        return user.get_absolute_url()


class UserUpdateView(LoginRequiredMixin, GetObjectMixin, GetSuccessUrlMixin, UpdateView):
    template_name = "users/update.html"
    form_class = UserUpdateForm
    
    def get_success_url(self):
        messages.success(self.request, "Kontot har uppdaterats!")
        return super().get_success_url()


class UserDeleteView(LoginRequiredMixin, GetObjectMixin, DeleteView):
    template_name = "users/delete.html"
    
    def delete(self, request, *args, **kwargs):
        """ Soft deletion of user. """
        user = self.get_object()
        user.is_active = False
        user.save()
        logout(request)
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse("index")


class UserPasswordChangeView(LoginRequiredMixin, GetSuccessUrlMixin, PasswordChangeView):
    template_name = "registration/password_change_form.html"
    form_class = PasswordChangeForm2

    def get_success_url(self):
        messages.success(self.request, "Ditt lösenord har uppdaterats!")
        return super().get_success_url()




