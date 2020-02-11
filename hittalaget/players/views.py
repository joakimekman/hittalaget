from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
)
from .models import Player, History
from .forms import PlayerForm, HistoryForm

VALID_SPORTS = ["fotboll"]


# ---------------------------------- #
# ------------- MIXINS ------------- #
# ---------------------------------- #


class PlayerCheckMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        sport = kwargs['sport']

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))
        
        ''' Redirect if invalid sport. '''
        if sport not in VALID_SPORTS:
            raise Http404()

        ''' Redirect to <player:list> if user does not have the player profile. '''
        player = self.get_object()

        if player is None:
            return redirect(reverse("player:list", kwargs={"sport": sport}))
        else:
            return super().dispatch(request, *args, **kwargs)


class GetObjectMixin:
    def get_object(self, queryset=None):
        ''' Return player if it exist else return None. '''
        if not hasattr(self, 'object'):
            user = self.request.user
            sport = self.kwargs['sport']
            try:
                self.object = Player.objects.get(user=user, sport=sport)
            except Player.DoesNotExist:
                self.object = None
            
        return self.object


# --------------------------------- #
# ---------- PLAYER VIEWS --------- #
# --------------------------------- #


class PlayerListView(ListView):
    template_name = "players/list.html"

    def dispatch(self, request, *args, **kwargs):
        ''' Return 404 if sport is not supported. '''
        sport = kwargs['sport']
        if sport in VALID_SPORTS:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404()

    def get_queryset(self):
        ''' Return a list of available players for the sport in question. '''
        sport = self.kwargs['sport']
        q = Player.objects.filter(sport=sport, is_available=True)
        return q


class PlayerDetailView(DetailView):
    template_name = "players/detail.html"

    def get_object(self, queryset=None):
        ''' Return player if it exist else return 404. '''
        if not hasattr(self, 'object'):
            sport = self.kwargs['sport']
            username = self.kwargs['username']
            obj = get_object_or_404(Player.objects.select_related('user'), sport=sport, username=username)
            self.object = obj

        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sport = self.kwargs['sport']
        player = self.get_object()

        sides = {
            "fotboll": "bästa fot:",
        }
        
        try:
            context['side'] = sides[sport]
        except KeyError:
            context['side'] = "n/a:"    

        if player.is_available:
            context['status'] = "söker klubb"
        else:
            context['status'] = "upptagen"
        return context

    
class PlayerCreateView(CreateView):
    template_name = "players/create.html"
    form_class = PlayerForm

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        sport = kwargs['sport']

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Redirect if invalid sport. '''
        if sport not in VALID_SPORTS:
            raise Http404()

        ''' Redirect if user already has a player profile for
        the sport in question. '''
        try:
            player = Player.objects.get(user=user, sport=sport)
        except Player.DoesNotExist:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(player.get_absolute_url())
            
    def get_form_kwargs(self):
        '''
        Pass sport to the form so that it can generate form choices
        dynamically depending on the sport.
        '''
        kwargs = super().get_form_kwargs()
        kwargs['sport'] = self.kwargs['sport']
        return kwargs
    
    def form_valid(self, form):
        ''' Assign user, and sport to player object. '''
        player = form.save(commit=False)
        player.user = self.request.user
        player.sport = self.kwargs['sport']
        player.save()
        ''' Save positions that belongs to the player object. '''
        form.save_m2m()
        self.object = player
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "Spelarprofilen skapades utan problem!")
        return self.object.get_absolute_url()
    

class PlayerUpdateView(PlayerCheckMixin, GetObjectMixin, UpdateView):
    template_name = "players/update.html"
    form_class = PlayerForm
    
    def get_form_kwargs(self):
        '''
        Pass sport to the form so that it can generate form choices
        dynamically depending on the sport.
        '''
        kwargs = super().get_form_kwargs()
        kwargs['sport'] = self.kwargs['sport']
        return kwargs  
            
    def get_success_url(self):
        messages.success(self.request, "Spelarprofilen har uppdaterats!")
        return self.get_object().get_absolute_url()
        

class PlayerDeleteView(PlayerCheckMixin, GetObjectMixin, DeleteView):
    template_name = "players/delete.html"

    def get_success_url(self):
        messages.success(self.request, "Spelarprofilen har tagits bort!")
        user = self.request.user
        return user.get_absolute_url()


class PlayerUpdateStatusView(PlayerCheckMixin, GetObjectMixin, View):
    
    def post(self, request, *args, **kwargs):
        ''' Toggles the is_available attribute of a Player object. '''
        player = self.get_object()
        if player.is_available:
            player.is_available = False
        else:
            player.is_available = True
        player.save()
        messages.success(self.request, "Statusen har uppdaterats!")
        return redirect(player.get_absolute_url())
    


# --------------------------------- #
# --------- HISTORY VIEWS --------- #
# --------------------------------- #


class HistoryCreateView(CreateView):
    template_name = "players/create_history.html"
    form_class = HistoryForm
    initial = {
        "start_year": "2000",
        "end_year": "2000",
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

        ''' Redirect to <player:list> if user does not have a player to
        add the historic entry to. '''
        player = self.get_player_object()

        if player is None:
            return redirect(reverse("player:list", kwargs={"sport": sport}))
        else:
            return super().dispatch(request, *args, **kwargs)


    def get_player_object(self):
        ''' Custom get_object method to return player object if it
        exist else return None. Used by dispatch method to determine
        whether player exist. '''
        if not hasattr(self, 'player_object'):
            user = self.request.user
            sport = self.kwargs['sport']
            try:
                self.player_object = Player.objects.get(user=user, sport=sport)
            except Player.DoesNotExist:
                self.player_object = None

        return self.player_object
   
    def form_valid(self, form):
        ''' Assign player to the history object. '''
        f = form.save(commit=False)
        player = self.get_player_object()
        f.player = player
        f.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "Historiken skapades utan problem!")
        return self.get_player_object().get_absolute_url()


class HistoryDeleteView(DeleteView):
    template_name = "players/delete_history.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        sport = kwargs['sport']

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))
        
        ''' Redirect if invalid sport. '''
        if sport not in VALID_SPORTS:
            raise Http404()

        ''' Raise 403 if user does not have permission to delete history entry. '''
        obj = self.get_object()

        if obj.player.user == user:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def get_object(self, queryset=None):
        ''' Return history entry if it exist else return 404. '''
        if not hasattr(self, 'object'):
            history_id = self.kwargs['id']
            self.object = get_object_or_404(History, id=history_id)
        
        return self.object

    def get_success_url(self):
        user = self.request.user
        sport = self.kwargs['sport']
        return reverse("player:detail", kwargs={"sport": sport, "username": user.username})






