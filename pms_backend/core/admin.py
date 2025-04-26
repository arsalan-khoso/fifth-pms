from django.contrib import admin
from .models import Contact, Unit, Lease, APIKey
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_type', 'email', 'phone')  # Changed 'type' to 'contact_type'
    list_filter = ('contact_type',)  # Changed 'type' to 'contact_type'
    search_fields = ('name', 'email', 'phone')


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'type', 'location', 'value', 'status', 'owner')
    list_filter = ('status', 'type')
    search_fields = ('unit_number', 'location')


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'unit', 'tenant', 'landlord', 'start_date', 'duration', 'rent_amount')
    list_filter = ('payment_frequency',)
    search_fields = ('unit__unit_number', 'tenant__name', 'landlord__name')



@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'created_at', 'is_active')
    readonly_fields = ('key',)