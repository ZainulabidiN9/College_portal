from django.shortcuts import render,redirect,get_object_or_404
from academics.models import course
from .form import CourseForm
from django.http import HttpResponseForbidden
# Create your views here.


def can_manage_courses(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name='teacher').exists()
        )
    )



def courses(request):
    all_courses = course.objects.all()

    return render(
        request,
        'accounts/courses.html',
        {
            'courses': all_courses,
            'can_manage_courses': can_manage_courses(request.user),
        }
    )


def add_course(request):

    if not can_manage_courses(request.user):
        return HttpResponseForbidden("Permission denied")

    if request.method == 'POST':
        form = CourseForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('courses')
    else:
        form = CourseForm()

    return render(
        request,
        'academics/add_course.html',
        {'form': form}
    )


def edit_course(request, id):
    if not can_manage_courses(request.user):
        return HttpResponseForbidden("Permission denied")

    selected_course = get_object_or_404(course, id=id)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=selected_course)

        if form.is_valid():
            form.save()
            return redirect('courses')
    else:
        form = CourseForm(instance=selected_course)

    context = {'form': form, 'course': selected_course}

    return render(request, 'academics/edit_course.html', context)


def delete_course(request, id):
    if not can_manage_courses(request.user):
        return HttpResponseForbidden("Permission denied")

    selected_course = get_object_or_404(course, id=id)

    if request.method == 'POST':
        selected_course.delete()

    return redirect('courses')