from django.shortcuts import render
from FacultyView.models import Student, Branch, Year, Section
from attendance_state import present
import datetime

def dashboard_home(request):
    """Main dashboard view showing attendance statistics"""
    total_students = Student.objects.count()
    present_count = len(present)
    absent_count = total_students - present_count

    # Get attendance by branch
    branches = Branch.objects.all()
    branch_stats = []
    for branch in branches:
        branch_students = Student.objects.filter(s_branch=branch)
        branch_present = len([s for s in present if str(s) in [str(st.s_roll) for st in branch_students]])
        branch_stats.append({
            'name': branch.branch,
            'total': branch_students.count(),
            'present': branch_present,
            'absent': branch_students.count() - branch_present,
            'percentage': round((branch_present / branch_students.count() * 100), 1) if branch_students.count() > 0 else 0
        })

    context = {
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': round((present_count / total_students * 100), 1) if total_students > 0 else 0,
        'branch_stats': branch_stats,
        'present_students': list(present),
        'current_time': datetime.datetime.now(),
    }

    return render(request, 'Dashboard/dashboard.html', context)

def attendance_report(request):
    """Detailed attendance report"""
    students = Student.objects.all().order_by('s_branch', 's_year', 's_section', 's_roll')

    # Get attendance by branch
    branches = Branch.objects.all()
    branch_stats = []
    for branch in branches:
        branch_students = Student.objects.filter(s_branch=branch)
        branch_present = len([s for s in present if str(s) in [str(st.s_roll) for st in branch_students]])
        branch_stats.append({
            'name': branch.branch,
            'total': branch_students.count(),
            'present': branch_present,
            'absent': branch_students.count() - branch_present,
            'percentage': round((branch_present / branch_students.count() * 100), 1) if branch_students.count() > 0 else 0
        })

    total_students = Student.objects.count()
    present_count = len(present)
    absent_count = total_students - present_count

    context = {
        'all_students': students,
        'present_students': present,
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': round((present_count / total_students * 100), 1) if total_students > 0 else 0,
        'branch_stats': branch_stats,
        'current_time': datetime.datetime.now(),
    }

    return render(request, 'Dashboard/report.html', context)
