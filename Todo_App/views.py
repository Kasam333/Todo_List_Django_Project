from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Todo_App.models import UserProfile, Task

# Create your views here.
def save_profile_image(profile_image, user_profile):
    if profile_image:
        fs = FileSystemStorage()
        filename = fs.save(f'profile_image/{profile_image.name}', profile_image)
        user_profile.profile_image = fs.url(filename)
        user_profile.save()

def user_profile(request):
    if request.method == 'POST' and request.FILES.get('profile_image'):
        profile_image = request.FILES['profile_image']
        user_profile = UserProfile.objects.get_or_create(user=request.user)
        save_profile_image(profile_image, user_profile)
        messages.success(request, 'Profile image updated successfully')
    return render(request, 'index.html', {'user': request.user.userprofile})

def RegisterView(request):
    if request.method != 'POST':
        return render(request, 'register.html')
    user_name = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    profile_image = request.FILES.get('profile_image')

    # Check if username exists
    if User.objects.filter(username=user_name).exists():
        messages.error(request, "Username is already taken")
        return redirect('/register/')

    # Create user and profile
    user = User.objects.create_user(
        username = user_name,
        email = email,
        password = password
    )
    user_profile = UserProfile.objects.create(user=user)

    # Handle profile image
    if profile_image:
        save_profile_image(profile_image, user_profile)

    messages.success(request, "Account created successfully")
    return redirect('/')

def LoginView(request):
    if request.method != 'POST':
        return render(request, 'login.html')
    user_name = request.POST['username']
    password = request.POST['password']

    if user := authenticate(username=user_name, password=password):
        login(request, user)
        return redirect('/home/')
    else:
        messages.error(request, "Invalid credentials")
        return redirect('/')
    
   
@login_required(login_url='/')
def HomeView(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        task_date = request.POST['task_date']

        task = Task.objects.create(
            user = request.user,
            title = title,
            description = description,
            task_date = task_date,
        )

        messages.success(request, "Task added successfully")
        return redirect('/home/')


    task = Task.objects.filter(user=request.user)
    return render(request, 'index.html',{'task':task})

@login_required(login_url='/')
def delet_task(request, id):
    task = get_object_or_404(Task, id=id)
    task.delete()
    messages.success(request, 'Task deleted successfully.')
    return redirect('/home/')