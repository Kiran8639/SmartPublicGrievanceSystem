
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from .forms import CitizenRegistrationForm
from .complaint_forms import ComplaintForm
from .models import Complaint, Department, User, ComplaintStatusHistory, Notification



def register(request):
    form = CitizenRegistrationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('login')

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')

    return render(request, 'accounts/login.html', {'form': form})



@login_required
def dashboard(request):
    if request.user.role == User.Role.DEPARTMENT_STAFF:
      return redirect('staff_dashboard')
    if request.user.role == User.Role.ADMIN:
         return redirect('admin_dashboard')

    unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

    return render(
            request,
            'accounts/dashboard.html',
            {'unread_count': unread_count}
        )




@login_required
def admin_dashboard(request):
 if request.user.role != User.Role.ADMIN:
    messages.error(request, 'Access denied. Admins only.')
    return redirect('dashboard')

 departments = Department.objects.all().order_by('name')

 department_performance = []

 for department in departments:
        total = Complaint.objects.filter(
            department=department
        ).count()

        resolved = Complaint.objects.filter(
            department=department,
            status=Complaint.Status.RESOLVED
        ).count()

        if total > 0:
            resolution_percentage = round((resolved / total) * 100)
        else:
            resolution_percentage = 0

        department_performance.append({
            'department': department,
            'total': total,
            'resolved': resolved,
            'resolution_percentage': resolution_percentage,
        })

 context = {
        'total_complaints': Complaint.objects.count(),

        'new_complaints': Complaint.objects.filter(
            status=Complaint.Status.NEW
        ).count(),

        'in_progress_complaints': Complaint.objects.filter(
            status=Complaint.Status.IN_PROGRESS
        ).count(),

        'resolved_complaints': Complaint.objects.filter(
            status=Complaint.Status.RESOLVED
        ).count(),

        'total_departments': Department.objects.count(),

        'total_citizens': User.objects.filter(
            role=User.Role.USER
        ).count(),

        'low_priority': Complaint.objects.filter(
            priority=Complaint.Priority.LOW
        ).count(),

        'medium_priority': Complaint.objects.filter(
            priority=Complaint.Priority.MEDIUM
        ).count(),

        'high_priority': Complaint.objects.filter(
            priority=Complaint.Priority.HIGH
        ).count(),

        'critical_priority': Complaint.objects.filter(
            priority=Complaint.Priority.CRITICAL
        ).count(),

        'department_performance': department_performance,

        'recent_complaints': Complaint.objects.select_related(
            'citizen', 'department'
        ).order_by('-created_at')[:5],
    }

 return render(
        request,
        'accounts/admin_dashboard.html',
        context
    )



@login_required
def submit_complaint(request):
        if request.user.role != User.Role.USER:
            return redirect('dashboard')

        form = ComplaintForm(request.POST or None, request.FILES or None)

        if request.method == 'POST' and form.is_valid():
            complaint = form.save(commit=False)
            complaint.citizen = request.user
            complaint.save()
            return redirect('my_complaints')

        return render(request, 'accounts/submit_complaint.html', {'form': form})



@login_required
def my_complaints(request):
        complaints = Complaint.objects.filter(
            citizen=request.user
        ).prefetch_related('status_history').order_by('-created_at')

        return render(
            request,
            'accounts/my_complaints.html',
            {'complaints': complaints}
        )




def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def department_information(request):
    departments = Department.objects.all()

    return render(request, 'accounts/departments.html', {
        'departments': departments
    })


@login_required
def staff_dashboard(request):
    if request.user.role != User.Role.DEPARTMENT_STAFF:
        return redirect('dashboard')

    if not request.user.department:
        return render(request, 'accounts/staff_dashboard.html', {
            'complaints': Complaint.objects.none(),
            'department': None,
            'error': 'No department has been assigned to your account.'
        })

    complaints = Complaint.objects.filter(
        department=request.user.department
    ).select_related('citizen', 'department').order_by('-created_at')

    return render(request, 'accounts/staff_dashboard.html', {
        'complaints': complaints,
        'department': request.user.department
    })



@login_required
@require_POST
def update_complaint_status(request, complaint_id):
        if request.user.role != User.Role.DEPARTMENT_STAFF:
         return redirect('dashboard')


        complaint = get_object_or_404(
            Complaint,
            id=complaint_id,
            department=request.user.department
        )

        new_status = request.POST.get('status')

        allowed_statuses = [
            Complaint.Status.IN_PROGRESS,
            Complaint.Status.RESOLVED
        ]

        if new_status in allowed_statuses:
            old_status = complaint.status

            if old_status != new_status:
                complaint.status = new_status
                complaint.save()

                ComplaintStatusHistory.objects.create(
                    complaint=complaint,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=request.user
                )

                status_messages = {
                    Complaint.Status.IN_PROGRESS:
                        'Work has started on your complaint.',
                    Complaint.Status.RESOLVED:
                        'Your complaint has been resolved.'
                }

                Notification.objects.create(
                    user=complaint.citizen,
                    complaint=complaint,
                    message=(
                        f'Complaint "{complaint.title}": '
                        f'{status_messages[new_status]}'
                    )
                )

            messages.success(
                request,
                'Complaint status updated successfully.'
            )
        else:
            messages.error(
                request,
                'Invalid complaint status.'
            )

        return redirect('dashboard')



@login_required
@require_POST
def delete_complaint(request, complaint_id):
    if request.user.role != User.Role.USER:
        return redirect('dashboard')

    complaint = get_object_or_404(
        Complaint,
        id=complaint_id,
        citizen=request.user
    )

    if complaint.status != Complaint.Status.NEW:
        messages.error(
            request,
            'Only new complaints can be deleted.'
        )
        return redirect('my_complaints')

    complaint.delete()

    messages.success(
        request,
        'Complaint deleted successfully.'
    )

    return redirect('my_complaints')

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(
    user=request.user
    )
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return render(
        request,
        'accounts/notifications.html',
        {'notifications': notifications}
    )





