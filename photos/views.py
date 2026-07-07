from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Photo, Submission

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not email or not password1 or not password2:
            messages.error(request, 'All fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(username=email, email=email, password=password1)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')

    return render(request, 'photos/register.html')



@login_required
def submit(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        place_of_living = request.POST.get('place_of_living')
        country_of_origin = request.POST.get('country_of_origin')
        description = request.POST.get('description', '')
        photo_file = request.FILES.get('photo_file')

        if photo_file and name and age and gender and place_of_living and country_of_origin:
            import os
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile

            file_name = default_storage.save(f'photos/{photo_file.name}', ContentFile(photo_file.read()))
            file_url = default_storage.url(file_name)

            photo = Photo.objects.create(
                file_name=photo_file.name,
                storage_url=file_url,          
                mime_type=photo_file.content_type,
                size_bytes=photo_file.size,
            )
            submission = Submission.objects.create(
                user=request.user,
                photo=photo,
                name=name,
                age=age,
                gender=gender,
                place_of_living=place_of_living,
                country_of_origin=country_of_origin,
                description=description,
            )
            messages.success(request, 'Submission created!')
            return redirect('home')
        else:
            messages.error(request, 'Please fill all required fields.')
    return render(request, 'photos/submit.html')