import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ccl_portal.settings')
django.setup()

from maintenance.models import CustomUser, Complaint, JobAllocation, Feedback

def seed():
    print("Seeding initial CCL demo data...")

    # 1. Create Superuser / Staff Officer
    if not CustomUser.objects.filter(username='admin').exists():
        admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@centralcoalfields.in',
            password='admin',
            eis_number='EIS-ADMIN01',
            role='STAFF_OFFICER',
            phone='9876543210',
            colony_name='GANDHINAGAR',
            quarter_no='Bungalow-01'
        )
        print("Created Superuser: admin / admin")

    # 2. Create Junior Engineers
    je_civil, created = CustomUser.objects.get_or_create(
        username='je_civil',
        defaults={
            'first_name': 'Ramesh',
            'last_name': 'Kumar',
            'email': 'je.civil@centralcoalfields.in',
            'eis_number': 'EIS-804512',
            'role': 'JE_CIVIL',
            'phone': '9876543211',
            'colony_name': 'GANDHINAGAR',
            'quarter_no': 'Type-IV/C-02'
        }
    )
    if created:
        je_civil.set_password('ccl123')
        je_civil.save()
        print("Created JE Civil: je_civil / ccl123")

    je_elec, created = CustomUser.objects.get_or_create(
        username='je_elec',
        defaults={
            'first_name': 'Anil',
            'last_name': 'Verma',
            'email': 'je.elec@centralcoalfields.in',
            'eis_number': 'EIS-804513',
            'role': 'JE_ELEC',
            'phone': '9876543212',
            'colony_name': 'JAWAHARNAGAR',
            'quarter_no': 'Type-IV/A-05'
        }
    )
    if created:
        je_elec.set_password('ccl123')
        je_elec.save()
        print("Created JE Electrical: je_elec / ccl123")

    # 3. Create Sample Resident
    resident, created = CustomUser.objects.get_or_create(
        username='resident1',
        defaults={
            'first_name': 'Suresh',
            'last_name': 'Prasad',
            'email': 'suresh.prasad@centralcoalfields.in',
            'eis_number': 'EIS-901234',
            'role': 'RESIDENT',
            'phone': '9876543213',
            'colony_name': 'GANDHINAGAR',
            'quarter_no': 'Qtr B-14, Type-III'
        }
    )
    if created:
        resident.set_password('ccl123')
        resident.save()
        print("Created Resident: resident1 / ccl123")

    # 4. Create Sample Complaints
    if Complaint.objects.count() == 0:
        # Complaint 1: In Progress with Materials
        c1 = Complaint.objects.create(
            resident=resident,
            department='CIVIL',
            issue_type='Roof seepage and peeling plaster in bedroom',
            description='Severe roof water seepage during rains. Moisture spreading along ceiling corner.',
            priority='NORMAL',
            status='IN_PROGRESS'
        )
        JobAllocation.objects.create(
            complaint=c1,
            assigned_by_je=je_civil,
            technician_name='Manoj Mistry (Contractor)',
            technician_phone='9431102938',
            target_completion_date=timezone.now().date() + timedelta(days=2),
            materials_issued='1 Bag Water-Proof Cement, 2L Waterproof Coating, 1 Brush',
            work_remarks='Surface scraping completed. Coating to be applied tomorrow.'
        )

        # Complaint 2: Resolved pending OTP
        c2 = Complaint.objects.create(
            resident=resident,
            department='ELECTRICAL',
            issue_type='Sparks from main switchboard and MCB trip',
            description='Main 32A MCB frequently trips when geyser is switched on.',
            priority='EMERGENCY',
            status='RESOLVED',
            resolved_at=timezone.now()
        )
        JobAllocation.objects.create(
            complaint=c2,
            assigned_by_je=je_elec,
            technician_name='Santosh Electrician',
            technician_phone='9431188221',
            target_completion_date=timezone.now().date(),
            materials_issued='1x 32A C-Curve MCB, 5m 4-sq-mm Copper Wire',
            work_remarks='Replaced overloaded MCB. Circuit testing verified.'
        )

        # Complaint 3: SLA Escalated (Created 9 days ago)
        c3 = Complaint.objects.create(
            resident=resident,
            department='WATER_SUPPLY',
            issue_type='Main overhead water tank inlet valve damaged',
            description='Continuous water overflow from overhead rooftop tank.',
            priority='NORMAL',
            status='SUBMITTED'
        )
        # Manually alter created_at to trigger escalation (> 7 days)
        Complaint.objects.filter(pk=c3.pk).update(created_at=timezone.now() - timedelta(days=9))

        print("Created 3 initial demonstration complaints (Normal, Emergency, and Escalated).")

    print("Seeding completed successfully!")

if __name__ == '__main__':
    seed()
