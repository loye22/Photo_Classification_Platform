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


from django.core.exceptions import PermissionDenied
from django.db.models import Q

@login_required
def admin_panel(request):
    if not getattr(request.user, 'is_admin', False):
        raise PermissionDenied("You do not have permission to access the Admin Panel.")

    if request.method == 'POST':
        action = request.POST.get('action')
        submission_id = request.POST.get('submission_id')
        if action == 'update_status' and submission_id:
            try:
                submission = Submission.objects.get(id=submission_id)
                new_status = request.POST.get('status')
                if new_status in Submission.StatusChoices.values:
                    submission.status = new_status
                    submission.save()
                    messages.success(request, f"Status of Submission {submission.id} updated to {submission.get_status_display()}.")
                else:
                    messages.error(request, "Invalid status choice.")
            except Submission.DoesNotExist:
                messages.error(request, "Submission not found.")
            return redirect('admin_panel')

    submissions = Submission.objects.select_related('user', 'photo').all()

    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        submissions = submissions.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(country_of_origin__icontains=search_query) |
            Q(place_of_living__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(status__icontains=search_query)
        )

    # Filter functionality
    gender_filter = request.GET.get('gender', '').strip()
    if gender_filter:
        submissions = submissions.filter(gender=gender_filter)

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        submissions = submissions.filter(status=status_filter)

    country_filter = request.GET.get('country', '').strip()
    if country_filter:
        submissions = submissions.filter(country_of_origin__iexact=country_filter)

    min_age = request.GET.get('min_age', '').strip()
    if min_age:
        try:
            submissions = submissions.filter(age__gte=int(min_age))
        except ValueError:
            pass

    max_age = request.GET.get('max_age', '').strip()
    if max_age:
        try:
            submissions = submissions.filter(age__lte=int(max_age))
        except ValueError:
            pass

    # Get unique countries for filter dropdown
    countries = Submission.objects.values_list('country_of_origin', flat=True).distinct().order_by('country_of_origin')
    countries = [c for c in countries if c]

    context = {
        'submissions': submissions,
        'countries': countries,
        'search_query': search_query,
        'selected_gender': gender_filter,
        'selected_status': status_filter,
        'selected_country': country_filter,
        'min_age': min_age,
        'max_age': max_age,
    }
    return render(request, 'photos/admin_panel.html', context)