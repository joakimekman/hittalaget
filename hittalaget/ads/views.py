from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView,
)
from .models import Ad
from .forms import AdForm
from hittalaget.conversations.forms import AdMessageForm
from hittalaget.teams.models import Team


VALID_SPORTS = ["fotboll"]


class AdDetailView(DetailView):
    template_name = "ads/detail.html"

    def get_object(self, queryset=None):
        ''' Return ad if it exist else raise 404. '''
        if not hasattr(self, 'object'):
            ad_id = self.kwargs['ad_id']
            self.object = get_object_or_404(Ad.objects.select_related('team__user', 'position'), ad_id=ad_id) 
            
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AdMessageForm
        return context
    

class AdListView(ListView):
    template_name = "ads/list.html"

    def dispatch(self, request, *args, **kwargs):
        ''' Raise 404 if invalid sport. '''
        sport = kwargs['sport']
        if sport not in VALID_SPORTS:
            raise Http404()
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        sport = self.kwargs['sport']
        queryset = Ad.objects.filter(sport=sport)
        return queryset


class AdCreateView(CreateView):
    template_name = "ads/create.html"
    form_class = AdForm
    initial = {
        "max_age": "25",
        "min_height": "175",
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

        ''' Only users with a team for the sport in question can create an ad. '''
        team = self.get_team_object()

        if team is None:
            return redirect(reverse('ad:list', kwargs={"sport": sport}))
        else:
            return super().dispatch(request, *args, **kwargs)          
    
    def get_team_object(self):
        user = self.request.user
        sport = self.kwargs['sport']
        
        if not hasattr(self, 'team_object'):
            try:
                team = Team.objects.get(user=user, sport=sport)
            except Team.DoesNotExist:
                self.team_object = None
            else:
                self.team_object = team

        return self.team_object

    def get_form_kwargs(self):
        '''
        Pass sport to the form so that it can generate the right
        form choices.
        '''
        kwargs = super().get_form_kwargs()
        kwargs['sport'] = self.kwargs['sport']
        return kwargs

    def form_valid(self, form):
        '''
        Assign team, and sport to ad, and change status of team.
        '''
        f = form.save(commit=False)
        team = self.get_team_object()
        f.team = team
        f.sport = self.kwargs['sport']
        f.save()
        self.object = f

        if not team.is_looking:
            team.is_looking = True
            team.save()
        
        return HttpResponseRedirect(self.get_success_url())
        
    def get_success_url(self):
        messages.success(self.request, 'Annonsen skapades utan problem!')
        return self.object.get_absolute_url()


class AdDeleteView(DeleteView):
    template_name = "ads/delete.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Raise 403 if user is not owner of the ad. '''
        obj = self.get_object()

        if obj.team.user == user:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def get_object(self, queryset=None):
        if not hasattr(self, 'object'):
            ad_id = self.kwargs['ad_id']
            self.object = get_object_or_404(Ad, ad_id=ad_id)
        
        return self.object

    def get_success_url(self):
        sport = self.kwargs['sport']
        messages.success(self.request, 'Annonsen togs bort utan problem!')
        return reverse('ad:list', kwargs={"sport": sport})