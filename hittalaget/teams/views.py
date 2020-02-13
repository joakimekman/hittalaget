from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from .forms import TeamForm, TeamCreateForm
from .models import Team


VALID_SPORTS = ["fotboll"]


# ---------------------------------- #
# ------------- MIXINS ------------- #
# ---------------------------------- #


class TeamCheckMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        sport = kwargs['sport']

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Redirect if invalid sport. '''
        if sport not in VALID_SPORTS:
            raise Http404()

        
        ''' Redirect to team:create if player does not have a team to
        update. '''
        team = self.get_object()

        if team is None:
            return redirect(reverse("team:create", kwargs={"sport": sport}))
        else:
            return super().dispatch(request, *args, **kwargs)


class GetObjectMixin:
    ''' Get team if it exist else return None. '''
    def get_object(self, queryset=None):
        if not hasattr(self, 'object'):
            user = self.request.user
            sport = self.kwargs['sport']
            try:
                team = Team.objects.get(user=user, sport=sport)
            except Team.DoesNotExist:
                self.object = None
            else:
                self.object = team
        
        return self.object


class GetFormKwargsMixin:
    ''' Send sport to the form, so form choices can be rendered
        dynamically. '''
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        sport = self.kwargs['sport']
        kwargs['sport'] = sport
        return kwargs


# --------------------------------- #
# ---------- TEAMS VIEWS ---------- #
# --------------------------------- #



class TeamListView(ListView):
    template_name = "teams/list.html"

    def dispatch(self, request, *args, **kwargs):
        ''' Return 404 if sport is not supported. '''
        sport = kwargs['sport']
        if sport in VALID_SPORTS:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404()

    def get_queryset(self):
        sport = self.kwargs['sport']
        q = Team.objects.filter(sport=sport)
        return q


class TeamDetailView(DetailView):
    template_name = "teams/detail.html"

    def get_object(self, queryset=None):
        ''' Return team if it exist else raise 404. '''
        if not hasattr(self, 'object'):
            team_id = self.kwargs['team_id']
            self.object = get_object_or_404(Team, team_id=team_id)
        
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.get_object()
        if team.is_looking:
            context['is_looking'] = "Ja"
        else:
            context['is_looking'] = "Nej"
        
        return context


class TeamCreateView(GetFormKwargsMixin, CreateView):
    template_name = "teams/create.html"
    form_class = TeamCreateForm
    initial = {
        "founded": "2000",
    }

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        sport = kwargs['sport']

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Redirect if invalid sport. '''
        if sport not in VALID_SPORTS:
            raise Http404()

        ''' Redirect if user already has a team for the sport in 
        question. '''
        try:
            team = Team.objects.get(sport=sport, user=user)
        except Team.DoesNotExist:
            return super().dispatch(request, *args, **kwargs)
        else:  
            return redirect(team.get_absolute_url())

    def form_valid(self, form):
        ''' Add user, and sport to the team object. '''
        f = form.save(commit=False)
        f.user = self.request.user
        f.sport = self.kwargs['sport']
        f.save()
        self.object = f
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "Laget skapades utan problem!")
        return self.object.get_absolute_url()


class TeamUpdateView(TeamCheckMixin, GetFormKwargsMixin, GetObjectMixin, UpdateView):
    template_name = "teams/update.html"
    form_class = TeamForm

    def get_success_url(self):
        messages.success(self.request, "Laget har uppdaterats!")
        return self.get_object().get_absolute_url()


class TeamDeleteView(TeamCheckMixin, GetObjectMixin, DeleteView):
    template_name = "teams/delete.html"

    def get_success_url(self):
        user = self.request.user
        messages.success(self.request, "Laget har tagits bort!")
        return user.get_absolute_url()


class TeamUpdateStatusView(TeamCheckMixin, GetObjectMixin, View):

    def post(self, request, *args, **kwargs):
        ''' Toggle the is_looking attribute of the team object. '''
        team = self.get_object()
        if team.is_looking:
            team.is_looking = False
        else:
            team.is_looking = True
        team.save()
        messages.success(request, "Status har uppdaterats!")
        return redirect(team.get_absolute_url())

