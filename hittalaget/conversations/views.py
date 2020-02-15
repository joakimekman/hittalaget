from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    View,
    ListView,
)
from .models import PmConversation, AdConversation, AdMessage
from .forms import PmMessageForm, AdMessageForm
from hittalaget.ads.models import Ad
from hittalaget.players.models import Player

User = get_user_model()


# --------------------------------- #
# ------- CONVERSATION VIEWS ------ #
# --------------------------------- #


class ConversationDetailView(DetailView):
    template_name = "conversations/detail_pm.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        username = kwargs['username']
        
        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Redirect if user try to access conversation with self. '''
        if username == user.username:
            return redirect("conversation:list")
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PmMessageForm
        return context

    def get_object(self, queryset=None):
        if not hasattr(self, 'object'):
            username = self.kwargs['username']
            user = self.request.user
            try:
                ''' Get conversation if one exist between users. '''
                obj = PmConversation.objects.prefetch_related('messages__author').get(users=user, users_arr__icontains=username)
                self.object = obj
            except PmConversation.DoesNotExist:
                raise Http404()
        
        return self.object


class ConversationCreateView(View):

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        username = kwargs['username']

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Redirect if users try to message self. ''' 
        if username == user.username:
            return redirect(reverse("conversation:list"))

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        username = kwargs['username']
        user = request.user

        try:
            ''' Get conversation if one exist between users. '''
            conversation = PmConversation.objects.filter(
                users_arr__icontains=user.username
            ).get(
                users_arr__icontains=username
            )
        except PmConversation.DoesNotExist:
            ''' Create conversation if one does not exist between users. '''
            conversation = PmConversation()
            conversation.users_arr = [user, username]
            conversation.save()

        ''' Re-add users in case someone left the conversation. '''
        receiver = get_object_or_404(User, username=username)
        conversation.users.add(user, receiver)                

        form = PmMessageForm(request.POST)

        if form.is_valid():
            ''' Add conversation, and author to the message. '''
            message = form.save(commit=False)
            message.conversation = conversation
            message.author = user
            message.save()

        return redirect(reverse('conversation:detail', kwargs={"username": username}))


class ConversationDeleteView(DeleteView):
    template_name = "conversations/delete.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        username = kwargs['username']

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Redirect if user try to delete conversation with self. '''
        if username == user.username:
            return redirect("conversation:list")
        
        ''' Redirect if conversation doesn't exist. '''
        if self.get_object() is not None:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(reverse("conversation:list"))

    def get_object(self, queryset=None):
        if not hasattr(self, 'object'):
            user = self.request.user
            username = self.kwargs['username']
            try:
                obj = PmConversation.objects.get(users=user, users_arr__icontains=username)
                self.object = obj
            except PmConversation.DoesNotExist:
                self.object = None

        return self.object
        
    def delete(self, request, *args, **kwargs):
        ''' Remove user from conversation. '''
        conversation = self.get_object()
        user = request.user
        conversation.users.remove(user)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "Konversationen är borttagen!")
        return reverse("conversation:list", kwargs={"label": "pm"})


class ConversationListView(ListView):
    template_name = "conversations/list.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        label = self.kwargs['label']
        user = self.request.user

        if label == "pm":
            q = PmConversation.objects.filter(users=user)
        elif label == "ad":
            q = AdConversation.objects.select_related('ad__team__user').filter(users=user)
        else:
            raise Http404()

        return q
    

# --------------------------------- #
# ----- AD CONVERSATION VIEWS ----- #
# --------------------------------- #


class AdConversationDetailView(DetailView):
    template_name = "conversations/detail_ad.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
    
        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))
        
        ''' Raise 404 if conversation does not exist, 403 if user is not part
        of the conversation, otherwise proceed as normal. '''
        if user not in self.get_object().users.all():
            raise PermissionDenied()
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AdMessageForm
        return context

    def get_object(self, queryset=None):
        conversation_id = self.kwargs['conversation_id']

        if not hasattr(self, 'object'):
            ''' Get conversation if it exist, oterwise raise a 404. '''
            obj = get_object_or_404(AdConversation.objects.prefetch_related(
                'messages__author'
            ).select_related(
                'ad__team__user'
            ), conversation_id=conversation_id)
            self.object = obj

        return self.object


class AdConversationCreateView(View):
    ''' Handles messages posted from the ad detail page. Conversation will be
    created if one does not exist, otherwise the message sent will be added
    to the existing conversation. '''

    def dispatch(self, request, *args, **kwargs):
        user = request.user
    
        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))

        ''' Redirect if user try to contact its own ad. Raise 404 if ad does not exist. '''
        ad = self.get_ad()
        if ad.team.user == user:
            # add message in future..
            return redirect(ad.get_absoulte_url())

        ''' Redirect if user does not have player profile. '''
        if not Player.objects.filter(user=user, sport=ad.sport).exists():
            # want to add message.. but not good idea to put message in dispatch..
            return redirect(ad.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)

    def get_ad(self):
        if not hasattr(self, 'ad'):
            ad_id = self.kwargs['ad_id']
            ad = get_object_or_404(Ad, ad_id=ad_id) # select_related('team')
            self.ad = ad

        return self.ad
        
    def post(self, request, *args, **kwargs):
        user = request.user
        ad = self.get_ad()

        ''' Get conversation if one exist, otherwise create a new one. '''
        try:
            conversation = AdConversation.objects.get(users=user, ad=ad, is_active=True) 
        except AdConversation.DoesNotExist:
            conversation = AdConversation()
            conversation.ad = ad
            conversation.users_arr = [user.username, ad.team.user.username]
            conversation.save()

        ''' Assign conversation, and author to the message, and then create it. '''
        form = AdMessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.author = user
            message.save()
            # add users
            conversation.users.add(user, ad.team.user)

        return redirect(conversation.get_absolute_url())


class AdConversationMessageView(View):
    ''' Handles messages posted with the form from the conversation:detail_ad page. '''
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))
        
        ''' Raise 404 if conversation does not exist, and a 403 if user
        is not part of the conversation. '''
        conversation = self.get_conversation()

        if user not in conversation.users.all():
            raise PermissionDenied()
        else:
            return super().dispatch(request, *args, **kwargs)
    
    def get_conversation(self):
        if not hasattr(self, 'conversation'):
            conversation_id = self.kwargs['conversation_id']
            self.conversation = get_object_or_404(AdConversation, conversation_id=conversation_id)
        
        return self.conversation

    def post(self, request, *args, **kwargs):
        user = request.user
        conversation = self.get_conversation()

        ''' Create message IF the conversation is_active. Else, return an
        error message. '''
        if conversation.is_active:
            form = AdMessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.author = user
                message.conversation = conversation
                message.save()
        else:
            messages.error(request, "Denna konversation är stängd.")
            
        return redirect(conversation.get_absolute_url())


class AdConversationDeleteView(DeleteView):
    template_name = "conversations/delete.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        
        ''' Redirect client to login page if unauthorized. '''
        if not user.is_authenticated:
            return redirect_to_login(request.path, reverse("user:login"))
        
        ''' Raise 404 if conversation does not exist, 403 if user is not part of
        conversation, otherwise proceed as normal. '''
        if user not in self.get_object().users.all():
            raise PermissionDenied()
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        conversation_id = self.kwargs['conversation_id']

        if not hasattr(self, 'object'):
            ''' Get conversation if it exist, oterwise raise a 404. '''
            ''' select related => users (used in dispatch, and delete..) '''
            obj = get_object_or_404(AdConversation, conversation_id=conversation_id)
            self.object = obj

        return self.object

    def delete(self, request, *args, **kwargs):
        conversation = self.get_object()
        user = request.user

        if len(conversation.users.all()) < 2:
            ''' Delete the conversation if there is only one user left. '''
            conversation.delete()
        else:
            ''' Remove the user from the conversation, and set is_active to False. '''
            conversation.users.remove(user)
            conversation.is_active = False
            conversation.save()
        
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "Konversationen är borttagen!")
        return reverse('conversation:list', kwargs={"label": "ad"})
