from django.db import models
from django.core.validators import MinValueValidator
import uuid


class Contact(models.Model):
    """Model representing a contact (either landlord or tenant)"""
    
    class ContactType(models.TextChoices):
        LANDLORD = 'LANDLORD', 'Landlord'
        TENANT = 'TENANT', 'Tenant'
    
    name = models.CharField(max_length=255)
    contact_type = models.CharField(  # Changed from 'type' to 'contact_type'
        max_length=10, 
        choices=ContactType.choices, 
        default=ContactType.TENANT
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_contact_type_display()})"  # Updated method
    
    @property
    def contact_info(self):
        """Return a dictionary of contact information"""
        return {
            'email': self.email,
            'phone': self.phone,
            'address': self.address
        }

class Unit(models.Model):
    """Model representing a property unit"""
    
    class UnitType(models.TextChoices):
        APARTMENT = 'APARTMENT', 'Apartment'
        HOUSE = 'HOUSE', 'House'
        CONDO = 'CONDO', 'Condominium'
        COMMERCIAL = 'COMMERCIAL', 'Commercial'
        OTHER = 'OTHER', 'Other'
    
    class UnitStatus(models.TextChoices):
        VACANT = 'VACANT', 'Vacant'
        OCCUPIED = 'OCCUPIED', 'Occupied'
        MAINTENANCE = 'MAINTENANCE', 'Under Maintenance'
    
    unit_number = models.CharField(max_length=50, unique=True)
    type = models.CharField(
        max_length=15, 
        choices=UnitType.choices, 
        default=UnitType.APARTMENT
    )
    location = models.CharField(max_length=255)
    value = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=15, 
        choices=UnitStatus.choices, 
        default=UnitStatus.VACANT
    )
    owner = models.ForeignKey(
        Contact, 
        on_delete=models.CASCADE, 
        related_name='owned_units',
        limit_choices_to={'contact_type': Contact.ContactType.LANDLORD}  # Changed from 'type' to 'contact_type'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.unit_number} ({self.get_type_display()} - {self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Override save to validate owner is a landlord"""
        if self.owner.contact_type != Contact.ContactType.LANDLORD:  # Updated from type to contact_type
            raise ValueError("Unit owner must be a landlord")
        super().save(*args, **kwargs)


class Lease(models.Model):
    """Model representing a lease agreement"""
    
    class PaymentFrequency(models.TextChoices):
        MONTHLY = 'MONTHLY', 'Monthly'
        QUARTERLY = 'QUARTERLY', 'Quarterly'
        SEMI_ANNUAL = 'SEMI_ANNUAL', 'Semi-Annual'
        ANNUAL = 'ANNUAL', 'Annual'
    
    unit = models.ForeignKey(
        Unit, 
        on_delete=models.CASCADE, 
        related_name='leases'
    )
    tenant = models.ForeignKey(
        Contact, 
        on_delete=models.CASCADE, 
        related_name='leases_as_tenant',
        limit_choices_to={'contact_type': Contact.ContactType.TENANT}  # Changed from 'type' to 'contact_type'
    )

    landlord = models.ForeignKey(
        Contact, 
        on_delete=models.CASCADE, 
        related_name='leases_as_landlord',
        limit_choices_to={'contact_type': Contact.ContactType.LANDLORD}  # Changed from 'type' to 'contact_type'
    )
    start_date = models.DateField()
    duration = models.IntegerField(
        help_text="Duration in months",
        validators=[MinValueValidator(1)]
    )
    rent_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    payment_frequency = models.CharField(
        max_length=15, 
        choices=PaymentFrequency.choices, 
        default=PaymentFrequency.MONTHLY
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Lease: {self.unit.unit_number} - {self.tenant.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure:
        1. Tenant is of type 'Tenant'
        2. Landlord is of type 'Landlord'
        3. Unit's status is set to 'Occupied'
        4. Landlord of the lease is the owner of the unit
        """
        if self.tenant.contact_type != Contact.ContactType.TENANT:  
            raise ValueError("Tenant must be of type 'Tenant'")
        
        if self.landlord.contact_type != Contact.ContactType.LANDLORD: 
            raise ValueError("Landlord must be of type 'Landlord'")
        
        if self.landlord != self.unit.owner:
            raise ValueError("Landlord of the lease must be the owner of the unit")
        
        # Set the unit status to occupied
        if self.unit.status != Unit.UnitStatus.OCCUPIED:
            self.unit.status = Unit.UnitStatus.OCCUPIED
            self.unit.save()
        
        super().save(*args, **kwargs)
    


class APIKey(models.Model):
    """Model for API Key authentication"""
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}: {self.key}"