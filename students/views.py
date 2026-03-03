from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Student
from schools.models import School

@login_required
def student_list(request):
    """List all students with search and filter"""
    students = Student.objects.select_related('school').all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(father_name__icontains=search_query) |
            Q(national_id__icontains=search_query)
        )
    
    # Filter by school
    school_id = request.GET.get('school', '')
    if school_id:
        students = students.filter(school_id=school_id)
    
    # Filter by grade
    grade = request.GET.get('grade', '')
    if grade:
        students = students.filter(grade_level__icontains=grade)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        students = students.filter(is_active=True)
    elif status == 'inactive':
        students = students.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    schools = School.objects.all()
    
    context = {
        'students': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'schools': schools,
        'selected_school': school_id,
        'selected_grade': grade,
        'selected_status': status,
    }
    
    return render(request, 'students/student_list.html', context)


@login_required
def student_create(request):
    """Create a new student"""
    if request.method == 'POST':
        try:
            student = Student.objects.create(
                student_id=request.POST.get('student_id'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                first_name_arabic=request.POST.get('first_name_arabic', ''),
                last_name_arabic=request.POST.get('last_name_arabic', ''),
                national_id=request.POST.get('national_id', ''),
                file_number=request.POST.get('file_number', ''),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
                mobile=request.POST.get('mobile', ''),
                father_name=request.POST.get('father_name', ''),
                father_name_arabic=request.POST.get('father_name_arabic', ''),
                father_national_id=request.POST.get('father_national_id', ''),
                father_phone=request.POST.get('father_phone', ''),
                father_email=request.POST.get('father_email', ''),
                father_occupation=request.POST.get('father_occupation', ''),
                mother_name=request.POST.get('mother_name', ''),
                mother_name_arabic=request.POST.get('mother_name_arabic', ''),
                mother_phone=request.POST.get('mother_phone', ''),
                grade_level=request.POST.get('grade_level', ''),
                grade_level_arabic=request.POST.get('grade_level_arabic', ''),
                academic_year=request.POST.get('academic_year', ''),
                admission_date=request.POST.get('admission_date') or None,
                school_id=request.POST.get('school') or None,
                emergency_contact_name=request.POST.get('emergency_contact_name', ''),
                emergency_contact_phone=request.POST.get('emergency_contact_phone', ''),
                emergency_contact_relation=request.POST.get('emergency_contact_relation', ''),
                address=request.POST.get('address', ''),
                city=request.POST.get('city', ''),
                district=request.POST.get('district', ''),
                is_active=request.POST.get('is_active') == 'on',
                notes=request.POST.get('notes', ''),
                # Saudi Documents
                iqama_expiry_date=request.POST.get('iqama_expiry_date') or None,
                passport_number=request.POST.get('passport_number', ''),
                passport_expiry_date=request.POST.get('passport_expiry_date') or None,
                birth_certificate_number=request.POST.get('birth_certificate_number', ''),
                transfer_certificate_number=request.POST.get('transfer_certificate_number', ''),
                previous_school_name=request.POST.get('previous_school_name', ''),
                vaccination_card_number=request.POST.get('vaccination_card_number', ''),
                is_vaccinated=request.POST.get('is_vaccinated') == 'on',
                medical_insurance_number=request.POST.get('medical_insurance_number', ''),
                medical_insurance_expiry=request.POST.get('medical_insurance_expiry') or None,
            )
            if request.FILES.get('photo'):
                student.photo = request.FILES['photo']
                student.save()
            messages.success(request, f'Student {student.get_full_name()} created successfully!')
            return redirect('students:student_detail', pk=student.pk)
        except Exception as e:
            messages.error(request, f'Error creating student: {str(e)}')
    
    schools = School.objects.all()
    context = {
        'schools': schools,
    }
    return render(request, 'students/student_form.html', context)


@login_required
def student_detail(request, pk):
    """View student details"""
    student = get_object_or_404(Student, pk=pk)
    
    context = {
        'student': student,
    }
    return render(request, 'students/student_detail.html', context)


@login_required
def student_update(request, pk):
    """Update student information"""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        try:
            student.student_id = request.POST.get('student_id')
            student.first_name = request.POST.get('first_name')
            student.last_name = request.POST.get('last_name')
            student.first_name_arabic = request.POST.get('first_name_arabic', '')
            student.last_name_arabic = request.POST.get('last_name_arabic', '')
            student.national_id = request.POST.get('national_id', '')
            student.file_number = request.POST.get('file_number', '')
            student.email = request.POST.get('email', '')
            student.phone = request.POST.get('phone', '')
            student.mobile = request.POST.get('mobile', '')
            student.father_name = request.POST.get('father_name', '')
            student.father_name_arabic = request.POST.get('father_name_arabic', '')
            student.father_national_id = request.POST.get('father_national_id', '')
            student.father_phone = request.POST.get('father_phone', '')
            student.father_email = request.POST.get('father_email', '')
            student.father_occupation = request.POST.get('father_occupation', '')
            student.mother_name = request.POST.get('mother_name', '')
            student.mother_name_arabic = request.POST.get('mother_name_arabic', '')
            student.mother_phone = request.POST.get('mother_phone', '')
            student.grade_level = request.POST.get('grade_level', '')
            student.grade_level_arabic = request.POST.get('grade_level_arabic', '')
            student.academic_year = request.POST.get('academic_year', '')
            student.admission_date = request.POST.get('admission_date') or None
            student.school_id = request.POST.get('school') or None
            student.emergency_contact_name = request.POST.get('emergency_contact_name', '')
            student.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
            student.emergency_contact_relation = request.POST.get('emergency_contact_relation', '')
            student.address = request.POST.get('address', '')
            student.city = request.POST.get('city', '')
            student.district = request.POST.get('district', '')
            student.is_active = request.POST.get('is_active') == 'on'
            student.notes = request.POST.get('notes', '')
            # Saudi Documents
            student.iqama_expiry_date = request.POST.get('iqama_expiry_date') or None
            student.passport_number = request.POST.get('passport_number', '')
            student.passport_expiry_date = request.POST.get('passport_expiry_date') or None
            student.birth_certificate_number = request.POST.get('birth_certificate_number', '')
            student.transfer_certificate_number = request.POST.get('transfer_certificate_number', '')
            student.previous_school_name = request.POST.get('previous_school_name', '')
            student.vaccination_card_number = request.POST.get('vaccination_card_number', '')
            student.is_vaccinated = request.POST.get('is_vaccinated') == 'on'
            student.medical_insurance_number = request.POST.get('medical_insurance_number', '')
            student.medical_insurance_expiry = request.POST.get('medical_insurance_expiry') or None
            if request.FILES.get('photo'):
                student.photo = request.FILES['photo']
            student.save()
            
            messages.success(request, f'Student {student.get_full_name()} updated successfully!')
            return redirect('students:student_detail', pk=student.pk)
        except Exception as e:
            messages.error(request, f'Error updating student: {str(e)}')
    
    schools = School.objects.all()
    context = {
        'student': student,
        'schools': schools,
    }
    return render(request, 'students/student_form.html', context)


@login_required
def student_delete(request, pk):
    """Delete a student"""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        student_name = student.get_full_name()
        student.delete()
        messages.success(request, f'Student {student_name} deleted successfully!')
        return redirect('students:student_list')
    
    context = {
        'student': student,
    }
    return render(request, 'students/student_confirm_delete.html', context)

