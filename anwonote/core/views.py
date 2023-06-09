from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q

from topic.models import Category, Topic
from .forms import SignupForm

from rest_framework import viewsets
from .serializers import CategorySerializer, TopicSerializer

# strona główna
def index(request):
    if request.user.is_authenticated:
        topics = Topic.objects.filter(
            Q(status='dla wszystkich') 
            | Q(created_by=request.user) 
            | Q(status='dla zalogowanych')
        )
    else:
        topics = Topic.objects.filter(status='dla wszystkich')
    categories = Category.objects.all()
    page = Paginator(topics, 9)
    page_list = request.GET.get('page', 1)
    page = page.get_page(page_list)
    context = {
        'categories':categories,
        'page':page,
    }
    return render(request, 'core/index.html', context)

# strona rejestracji
def signup(request):
    form = SignupForm()
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
        else:
            form = SignupForm()

    return render(request, 'core/signup.html',{
        'form' : form
    })
    

# !!! przesyłanie cookies podczas logowania !!!
class Logowanie(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        remember_me = self.request.POST.get('remember_me')
        if remember_me == 'true':
            response.set_cookie('remember_me', True, max_age=3600*24*7)
            response.set_cookie('username', form.cleaned_data['username'])
            response.set_cookie('login_status', True)
        return response
    
class Wylogowanie(LogoutView):
#   Funkcja usuwa pliki cookie po wylogowaniu 
    def dispatch(self, request):
        response = super().dispatch(request)
#   Usuwanie cookies po nazwie 
        response.delete_cookie('username')
        response.delete_cookie('login_status')
        response.delete_cookie('remember_me')
        return response