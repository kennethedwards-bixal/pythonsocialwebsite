from django.shortcuts import render
from common.decorators import ajax_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Contact
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from actions.utils import create_action
from actions.models import Action


@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, ' is following ', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse ({'status': 'error'})



# This is what the basic login view does: when the 
# user_login view is called with a GET request, you instantiate a new login form with 
# form = LoginForm() to display it in the template. 
# When the user submits the form via POST, you perform the following actions:
def user_login(request):
    if request.method == 'POST':
        # Instantiate the form with the submitted data with form = LoginForm(request.POST).
        form = LoginForm(request.POST)
        # Check whether the form is valid with form.is_valid().
        #  If it is not valid, you display the form errors in your
        #  template (for example, if the user didn't fill in one of the fields).
        if form.is_valid():
            # If the submitted data is valid, you authenticate 
            # the user against the database using the authenticate() method. 
            # This method takes the request object, the username, 
            # and the password parameters and returns the User object if 
            # the user has been successfully authenticated, or None otherwise. 
            # If the user has not been authenticated, you return a raw HttpResponse, displaying the Invalid login message.
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])

            if user is not None:
                # If the user was successfully authenticated, you 
                # check whether the user is active by accessing 
                # the is_active attribute. This is an attribute 
                # of Django's user model. If the user is not active, 
                # you return an HttpResponse that displays the Disabled account message.
                if user.is_active:
                    # If the user is active, you log the user into the website. 
                    # You set the user in the session by calling the login() method
                    #  and return the Authenticated successfully message.
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    
    return render(request, 'account/login.html', {'form': form})

# The login_required decorator checks whether 
# the current user is authenticated. If the 
# user is authenticated, it executes the decorated view; if the user is not authenticated,
# it redirects the user to the login URL with the originally requested URL as a GET parameter named next.
@login_required
def dashboard(request):
    # Display all actions by default - stream section #10
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id',flat=True)
    if following_ids:
        # If user is following others, retrieve only their actions
        actions = actions.filter(user_id__in=following_ids)
        # 11
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]
    return render(request, 'account/dashboard.html', {'section': 'dashboard', 'actions': actions})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
        # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            # For security reasons, instead of saving the raw password 
            # entered by the user, you use the set_password() method 
            # of the user model that handles hashing.
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            Profile.objects.create(user=new_user)
            create_action(new_user, 'has been created')
            return render(request, 'account/register_done.html',{'new_user': new_user}) 
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html',{'user_form': user_form})

# 3
@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data= request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated sucessfully')
        else: 
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user) 
        profile_form = ProfileEditForm(instance=request.user.profile)
    
    return render (request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})


# The user_list view gets all active users. The Django User model contains an is_active 
# flag to designate whether the user account is considered active. 
# You filter the query by is_active=True
# to return only active users. This view returns all results, 
# but you can improve it by adding pagination 
@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render (request, 'account/user/list.html', {'section': 'people', 'users': users})


# The user_detail view uses the get_object_or_404() 
# shortcut to retrieve the active user with the given username. 
# The view returns an HTTP 404 response if no active user with the given username is found
@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'account/user/detail.html', {'section': 'people', 'user': user})


