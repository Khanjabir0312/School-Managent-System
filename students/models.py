from django.db import models
from schools.models import School

class Student(models.Model):
    """
    Student model for billing purposes with complete information for receipts
    """
    # Basic Information (English)
    student_id = models.CharField(max_length=20, unique=True, verbose_name="Student ID")
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    
    # Arabic Names (for bilingual receipts)
    first_name_arabic = models.CharField(max_length=100, blank=True, verbose_name="First Name (Arabic)")
    last_name_arabic = models.CharField(max_length=100, blank=True, verbose_name="Last Name (Arabic)")
    
    # National ID / Iqama
    national_id = models.CharField(max_length=20, blank=True, verbose_name="Student National ID / Iqama")
    
    # Student File Number (Internal tracking)
    file_number = models.CharField(max_length=50, blank=True, verbose_name="Student File Number")
    
    # Contact Information
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone Number")
    mobile = models.CharField(max_length=20, blank=True, verbose_name="Mobile Number")
    
    # Father/Guardian Information
    father_name = models.CharField(max_length=200, blank=True, verbose_name="Father Name")
    father_name_arabic = models.CharField(max_length=200, blank=True, verbose_name="Father Name (Arabic)")
    father_national_id = models.CharField(max_length=20, blank=True, verbose_name="Father National ID / Iqama")
    father_phone = models.CharField(max_length=20, blank=True, verbose_name="Father Phone")
    father_email = models.EmailField(blank=True, null=True, verbose_name="Father Email")
    father_occupation = models.CharField(max_length=100, blank=True, verbose_name="Father Occupation")
    
    # Mother Information (Optional)
    mother_name = models.CharField(max_length=200, blank=True, verbose_name="Mother Name")
    mother_name_arabic = models.CharField(max_length=200, blank=True, verbose_name="Mother Name (Arabic)")
    mother_phone = models.CharField(max_length=20, blank=True, verbose_name="Mother Phone")
    
    # Academic Information
    grade_level = models.CharField(max_length=100, blank=True, verbose_name="Grade/Class")
    grade_level_arabic = models.CharField(max_length=100, blank=True, verbose_name="Grade/Class (Arabic)")
    academic_year = models.CharField(max_length=20, blank=True, verbose_name="Academic Year")
    admission_date = models.DateField(null=True, blank=True, verbose_name="Admission Date")
    
    # School Association
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students', null=True, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True, verbose_name="Emergency Contact Name")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Emergency Contact Phone")
    emergency_contact_relation = models.CharField(max_length=50, blank=True, verbose_name="Emergency Contact Relation")
    
    # Address
    address = models.TextField(blank=True, verbose_name="Address")
    city = models.CharField(max_length=100, blank=True, verbose_name="City")
    district = models.CharField(max_length=100, blank=True, verbose_name="District")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    # Notes
    notes = models.TextField(blank=True, verbose_name="Internal Notes")

    # ── Saudi Arabia Required Documents (all optional) ──────────────────────
    # Student photo
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True, verbose_name="Student Photo")

    # Iqama / National ID details
    iqama_expiry_date = models.DateField(blank=True, null=True, verbose_name="Iqama / National ID Expiry Date")

    # Passport
    passport_number = models.CharField(max_length=30, blank=True, verbose_name="Passport Number")
    passport_expiry_date = models.DateField(blank=True, null=True, verbose_name="Passport Expiry Date")

    # Birth Certificate
    birth_certificate_number = models.CharField(max_length=50, blank=True, verbose_name="Birth Certificate Number")

    # Transfer Certificate (from previous school)
    transfer_certificate_number = models.CharField(max_length=50, blank=True, verbose_name="Transfer Certificate Number")
    previous_school_name = models.CharField(max_length=200, blank=True, verbose_name="Previous School Name")

    # Vaccination
    vaccination_card_number = models.CharField(max_length=50, blank=True, verbose_name="Vaccination Card Number")
    is_vaccinated = models.BooleanField(default=False, verbose_name="Vaccination Record Provided")

    # Medical / Health Insurance
    medical_insurance_number = models.CharField(max_length=50, blank=True, verbose_name="Medical Insurance Number")
    medical_insurance_expiry = models.DateField(blank=True, null=True, verbose_name="Medical Insurance Expiry Date")
    # ────────────────────────────────────────────────────────────────────────

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['student_id']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
    
    def __str__(self):
        return f"{self.student_id} - {self.get_full_name()}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name_arabic(self):
        if self.first_name_arabic and self.last_name_arabic:
            return f"{self.first_name_arabic} {self.last_name_arabic}"
        return ""
