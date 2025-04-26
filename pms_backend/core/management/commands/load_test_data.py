from django.core.management.base import BaseCommand
from datetime import date
from core.models import Contact, Unit, Lease


class Command(BaseCommand):
    help = 'Loads test data for the FIFTH Property Management System'

    def handle(self, *args, **kwargs):
        """
        Creates test data for the FIFTH Property Management System
        """
        self.stdout.write("Creating test data...")
        
        # Check if test data already exists
        if Contact.objects.filter(name='John Doe').exists():
            self.stdout.write(self.style.WARNING("Test data already exists. Skipping creation."))
            return
        
        # Create test landlord
        self.stdout.write("Creating test landlord...")
        test_landlord = Contact.objects.create(
            name='John Doe',
            contact_type=Contact.ContactType.LANDLORD,  # Updated from 'type'
            email='john.doe@example.com',
            phone='555-123-4567',
            address='123 Landlord St, Property City, PC 12345'
        )
        
        # Create test tenant
        self.stdout.write("Creating test tenant...")
        test_tenant = Contact.objects.create(
            name='Jane Smith',
            contact_type=Contact.ContactType.TENANT,  # Updated from 'type'
            email='jane.smith@example.com',
            phone='555-765-4321',
            address='456 Tenant Ave, Renter City, RC 54321'
        )
        
        # Create test unit
        self.stdout.write("Creating test unit...")
        test_unit = Unit.objects.create(
            unit_number='A1',
            type=Unit.UnitType.APARTMENT,
            location='789 Property Blvd, Rental City, RC 67890',
            value=250000.00,
            status=Unit.UnitStatus.VACANT,
            owner=test_landlord
        )
        
        # Create test lease
        self.stdout.write("Creating test lease...")
        Lease.objects.create(
            unit=test_unit,
            tenant=test_tenant,
            landlord=test_landlord,
            start_date=date(2025, 1, 1),
            duration=12,  # 12 months
            rent_amount=1500.00,
            payment_frequency=Lease.PaymentFrequency.MONTHLY
        )
        
        self.stdout.write(self.style.SUCCESS("Test data created successfully!"))