from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from ribbit_app.forms import AuthenticateForm, UserCreateForm, bookPasserForm
from ribbit_app.models import bookPasser

from django.contrib.auth.decorators import login_required

from django.db.models import Count
from django.http import Http404

from django.core.exceptions import ObjectDoesNotExist

def index(request, auth_form=None, user_form=None):
    # User is logged in
    if request.user.is_authenticated():
        bookPasser_form = bookPasserForm()
        user = request.user
        bookPassers_self = bookPasser.objects.filter(user=user.id)
        bookPassers_buddies = bookPasser.objects.filter(user__userprofile__in=user.profile.follows.all)
        bookPassers = bookPassers_self | bookPassers_buddies
 
        return render(request,
                      'buddies.html',
                      {'bookPasser_form': bookPasser_form, 'user': user,
                       'bookPassers': bookPassers,
                       'next_url': '/', })
    else:
        # User is not logged in
        auth_form = auth_form or AuthenticateForm()
        user_form = user_form or UserCreateForm()
 
        return render(request,
                      'home.html',
                      {'auth_form': auth_form, 'user_form': user_form, })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticateForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Success
            return redirect('/')
        else:
            # Failure
            return index(request, auth_form=form)
    return redirect('/')
def logout_view(request):
    logout(request)
    return redirect('/')

def signup(request):
    user_form = UserCreateForm(data=request.POST)
    if request.method == 'POST':
        if user_form.is_valid():
            username = user_form.clean_username()
            password = user_form.clean_password2()
            user_form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        else:
            return index(request, user_form=user_form)
    return redirect('/')

@login_required
def submit(request):
    if request.method == "POST":
        bookPasser_form = bookPasserForm(data=request.POST)
        next_url = request.POST.get("next_url", "/")
        if bookPasser_form.is_valid():
            bookPasser = bookPasser_form.save(commit=False)
            bookPasser.user = request.user
            bookPasser.save()
            return redirect(next_url)
        else:
            return public(request, bookPasser_form)
    return redirect('/')

@login_required
def public(request, bookPasser_form=None):
    bookPasser_form = bookPasser_form or bookPasserForm()
    bookPassers = bookPasser.objects.reverse()[:10]
    return render(request,
                  'public.html',
                  {'bookPasser_form': bookPasser_form, 'next_url': '/bookPassers',
                   'bookPassers': bookPassers, 'username': request.user.username})



def get_latest(user):
    try:
        return user.bookPasser_set.order_by('-id')[0]
    except IndexError:
        return ""
@login_required
def users(request, username="", bookPasser_form=None):
    if username:
        # Show a profile
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        bookPassers = bookPasser.objects.filter(user=user.id)
        if username == request.user.username or request.user.profile.follows.filter(user__username=username):
            # Self Profile or buddies' profile
            return render(request, 'user.html', {'user': user, 'bookPassers': bookPassers, })
        return render(request, 'user.html', {'user': user, 'bookPassers': bookPassers, 'follow': True, })
    users = User.objects.all().annotate(bookPasser_count=Count('bookPasser'))
    bookPassers = map(get_latest, users)
    obj = zip(users, bookPassers)
    bookPasser_form = bookPasser_form or bookPasserForm()
    return render(request,
                  'profiles.html',
                  {'obj': obj, 'next_url': '/users/',
                   'bookPasser_form': bookPasser_form,
                   'username': request.user.username, })



@login_required
def follow(request):
    if request.method == "POST":
        follow_id = request.POST.get('follow', False)
        if follow_id:
            try:
                user = User.objects.get(id=follow_id)
                request.user.profile.follows.add(user.profile)
            except ObjectDoesNotExist:
                return redirect('/users/')
    return redirect('/users/')