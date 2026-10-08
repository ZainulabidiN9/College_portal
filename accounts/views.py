from django.shortcuts import render, redirect, get_object_or_404
from .form import SignupForm
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group ,User
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from academics.models import course
from academics.views import can_manage_courses
from attendance.models import Attendance
from results.models import Result
from academics.models import Timetable
from academics.form import TimetableForm
from attendance.form import AttendanceForm
from results.form import ResultForm
from .models import AuthActivity
# Create your views here.


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            student_group, created = Group.objects.get_or_create(name='student')
            user.groups.add(student_group)
            AuthActivity.objects.create(user=user, action=AuthActivity.SIGNUP)
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        AuthActivity.objects.create(user=user, action=AuthActivity.LOGIN)
        login(request, user)
        return redirect('dashboard')

    return render(
        request,
        'accounts/login.html',
        {'form': form}
    )


def user_logout(request):
    logout(request)

    return redirect('login')

@login_required
def dashboad(request):
    can_view_all_records = can_manage_courses(request.user)
    attendance_records = Attendance.objects.select_related('course')
    result_records = Result.objects.select_related('course')

    if not can_view_all_records:
        attendance_records = attendance_records.filter(student=request.user)
        result_records = result_records.filter(student=request.user)

    course_metrics = {}
    total_present = 0
    total_classes = 0
    total_obtained = 0
    total_marks = 0

    for record in attendance_records:
        metric = course_metrics.setdefault(
            record.course_id,
            {
                'name': record.course.name,
                'present': 0,
                'classes': 0,
                'obtained': 0,
                'marks': 0,
            },
        )
        metric['present'] += record.present_classes
        metric['classes'] += record.total_classes
        total_present += record.present_classes
        total_classes += record.total_classes

    for record in result_records:
        metric = course_metrics.setdefault(
            record.course_id,
            {
                'name': record.course.name,
                'present': 0,
                'classes': 0,
                'obtained': 0,
                'marks': 0,
            },
        )
        metric['obtained'] += record.obtained_marks
        metric['marks'] += record.total_marks
        total_obtained += record.obtained_marks
        total_marks += record.total_marks

    ordered_metrics = sorted(course_metrics.values(), key=lambda metric: metric['name'])
    chart_data = {
        'labels': [metric['name'] for metric in ordered_metrics],
        'attendance': [
            round(metric['present'] * 100 / metric['classes']) if metric['classes'] else 0
            for metric in ordered_metrics
        ],
        'scores': [
            round(metric['obtained'] * 100 / metric['marks']) if metric['marks'] else 0
            for metric in ordered_metrics
        ],
    }

    return render(
        request,
        'accounts/dashboard.html',
        {
            'course_count': course.objects.count() if can_view_all_records else len(course_metrics),
            'attendance_percentage': round(total_present * 100 / total_classes) if total_classes else 0,
            'average_score': round(total_obtained * 100 / total_marks) if total_marks else 0,
            'chart_data': chart_data,
            'can_manage_records': can_view_all_records,
            'is_teacher': request.user.groups.filter(name='teacher').exists(),
            'is_student': request.user.groups.filter(name='student').exists(),
            'student_count': (
                User.objects.filter(groups__name='student').distinct().count()
                if can_view_all_records else None
            ),
        },
    )


@login_required
def student_directory(request):
    if not can_manage_courses(request.user):
        return HttpResponseForbidden('Only teachers and administrators can view students.')

    students = User.objects.filter(groups__name='student').distinct()
    student_count = students.count()
    search_query = request.GET.get('q', '').strip()[:100]
    if search_query:
        students = students.filter(
            Q(username__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    page = Paginator(
        students.order_by('first_name', 'last_name', 'username'),
        25,
    ).get_page(request.GET.get('page'))
    page_students = list(page.object_list)
    student_ids = [student.id for student in page_students]

    attendance_summary = {
        record['student_id']: record
        for record in Attendance.objects.filter(student_id__in=student_ids)
        .values('student_id')
        .annotate(
            present=Sum('present_classes'),
            total=Sum('total_classes'),
            courses=Count('course', distinct=True),
        )
    }
    result_summary = {
        record['student_id']: record
        for record in Result.objects.filter(student_id__in=student_ids)
        .values('student_id')
        .annotate(obtained=Sum('obtained_marks'), total=Sum('total_marks'))
    }

    student_rows = []
    for student in page_students:
        attendance = attendance_summary.get(student.id, {})
        result = result_summary.get(student.id, {})
        student_rows.append(
            {
                'student': student,
                'course_count': max(attendance.get('courses', 0), 0),
                'attendance_percentage': (
                    round(attendance['present'] * 100 / attendance['total'])
                    if attendance.get('total') else None
                ),
                'average_score': (
                    round(result['obtained'] * 100 / result['total'])
                    if result.get('total') else None
                ),
            }
        )

    return render(
        request,
        'accounts/student_directory.html',
        {
            'students': student_rows,
            'student_count': student_count,
            'result_count': page.paginator.count,
            'search_query': search_query,
            'page_obj': page,
        },
    )



@login_required
def profile(request):
    attendance_records = Attendance.objects.filter(
        student=request.user if not can_manage_courses(request.user) else None
    ).select_related('course').order_by('-recorded_at')
    result_records = Result.objects.filter(
        student=request.user if not can_manage_courses(request.user) else None
    ).select_related('course').order_by('course__name')
    auth_activities = AuthActivity.objects.filter(user=request.user)[:20]

    return render(
        request,
        'accounts/profile.html',
        {
            'attendance_records': attendance_records,
            'result_records': result_records,
            'current_time': timezone.localtime(),
            'can_manage_records': can_manage_courses(request.user),
            'auth_activities': auth_activities,
        }
    )





@login_required
def teacher_dashboard(request):
    if request.user.groups.filter(name='teacher').exists():
        return render(request,'accounts/teacher_dashboard.html')

    return HttpResponse("You are not a teacher")

@login_required
def student_dashboard(request):
    if request.user.groups.filter(name='student').exists():
        return render(request,'accounts/student_dashboard.html')

    return HttpResponse("You are not a Students")


@login_required
def admin_dashboard(request):

    if not request.user.is_superuser:
        return HttpResponse("You are not an admin")

    return render(
        request,
        'accounts/admin_dashboard.html'
    )



@login_required
def create_teacher(request):

    if not request.user.is_superuser:
        return HttpResponse("Only admin can create teachers")

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        teacher = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        teacher_group, created = Group.objects.get_or_create(
            name='teacher'
        )

        teacher.groups.add(teacher_group)

        return redirect('admin_dashboard')

    return render(
        request,
        'accounts/create_teacher.html'
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

def attendance(request):
    records = Attendance.objects.select_related('student', 'course')
    if not can_manage_courses(request.user):
        records = records.filter(student=request.user)

    return render(
        request,
        'accounts/attendance.html',
        {
            'attendance_records': records,
            'can_manage_records': can_manage_courses(request.user),
        }
    )



def results(request):
    result_records = Result.objects.select_related('student', 'course')
    if not can_manage_courses(request.user):
        result_records = result_records.filter(student=request.user)

    return render(
        request,
        'accounts/results.html',
        {
            'results': result_records,
            'can_manage_records': can_manage_courses(request.user),
        }
    )



def timetable(request):

    schedule = Timetable.objects.all().order_by(
        'day',
        'start_time'
    )

    return render(
        request,
        'accounts/timetable.html',
        {
            'timetable': schedule,
            'can_manage_timetable': can_manage_courses(request.user),
        }
    )


@login_required
def add_attendance(request):
    if not can_manage_courses(request.user):
        return HttpResponseForbidden("Permission denied")

    form = AttendanceForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('attendance')

    return render_record_form(request, form, 'Add Attendance', 'Add Attendance', 'attendance')


@login_required
def edit_attendance(request, id):
    if not can_manage_courses(request.user):
        return HttpResponseForbidden("Permission denied")

    attendance_record = get_object_or_404(Attendance, id=id)
    form = AttendanceForm(request.POST or None, instance=attendance_record)
    if form.is_valid():
        form.save()
        return redirect('attendance')

    return render_record_form(request, form, 'Update Attendance', 'Save Changes', 'attendance')


@login_required
def delete_attendance(request, id):
    if not can_manage_courses(request.user):
        return HttpResponseForbidden("Permission denied")

    attendance_record = get_object_or_404(Attendance, id=id)
    if request.method == 'POST':
        attendance_record.delete()
    return redirect('attendance')


@login_required
def add_result(request):
    if not can_manage_courses(request.user):
        return HttpResponseForbidden("Permission denied")

    form = ResultForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('results')

    return render_record_form(request, form, 'Add Result', 'Add Result', 'results')


@login_required
def edit_result(request, id):
    if not can_manage_courses(request.user):
        return HttpResponseForbidden("Permission denied")

    result_record = get_object_or_404(Result, id=id)
    form = ResultForm(request.POST or None, instance=result_record)
    if form.is_valid():
        form.save()
        return redirect('results')

    return render_record_form(request, form, 'Update Result', 'Save Changes', 'results')


@login_required
def delete_result(request, id):
    if not can_manage_courses(request.user):
        return HttpResponseForbidden("Permission denied")

    result_record = get_object_or_404(Result, id=id)
    if request.method == 'POST':
        result_record.delete()
    return redirect('results')


@login_required
def add_timetable(request):
    if not can_manage_courses(request.user):
        return HttpResponseForbidden("Permission denied")

    form = TimetableForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('timetable')

    return render_record_form(request, form, 'Add Timetable Entry', 'Add Entry', 'timetable')


@login_required
def edit_timetable(request, id):
    if not can_manage_courses(request.user):
        return HttpResponseForbidden("Permission denied")

    timetable_entry = get_object_or_404(Timetable, id=id)
    form = TimetableForm(request.POST or None, instance=timetable_entry)
    if form.is_valid():
        form.save()
        return redirect('timetable')

    return render_record_form(request, form, 'Update Timetable Entry', 'Save Changes', 'timetable')


@login_required
def delete_timetable(request, id):
    if not can_manage_courses(request.user):
        return HttpResponseForbidden("Permission denied")

    timetable_entry = get_object_or_404(Timetable, id=id)
    if request.method == 'POST':
        timetable_entry.delete()
    return redirect('timetable')


def render_record_form(request, form, title, submit_label, back_url):
    return render(
        request,
        'accounts/manage_record.html',
        {
            'form': form,
            'title': title,
            'submit_label': submit_label,
            'back_url': back_url,
        }
    )