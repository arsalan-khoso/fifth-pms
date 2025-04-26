from rest_framework import serializers
from .models import Contact, Unit, Lease


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for the Contact model"""
    
    class Meta:
        model = Contact
        fields = ['id', 'name', 'contact_type', 'email', 'phone', 'address', 'created_at', 'updated_at']


class ContactListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing contacts"""
    
    type_display = serializers.CharField(source='get_contact_type_display', read_only=True)
    
    class Meta:
        model = Contact
        fields = ['id', 'name', 'contact_type', 'type_display', 'email', 'phone']

class UnitOwnerSerializer(serializers.ModelSerializer):
    """Simplified serializer for unit owner (landlord)"""
    
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone']
        read_only_fields = fields


class UnitSerializer(serializers.ModelSerializer):
    """Serializer for the Unit model"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    owner_details = UnitOwnerSerializer(source='owner', read_only=True)
    
    class Meta:
        model = Unit
        fields = [
            'id', 'unit_number', 'type', 'type_display', 'location', 
            'value', 'status', 'status_display', 'owner', 'owner_details',
            'created_at', 'updated_at'
        ]


class UnitListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing units"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    
    class Meta:
        model = Unit
        fields = [
            'id', 'unit_number', 'type_display', 'location', 
            'value', 'status_display', 'owner_name'
        ]


class LeaseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating lease objects"""
    
    class Meta:
        model = Lease
        fields = [
            'id', 'unit', 'tenant', 'landlord', 'start_date', 
            'duration', 'rent_amount', 'payment_frequency'
        ]
    
    def validate(self, data):    
        # Check if unit is already leased (for creation)
        if self.instance is None and 'unit' in data:
            unit = data['unit']
            if unit.status == Unit.UnitStatus.OCCUPIED:
                raise serializers.ValidationError({
                    'unit': 'This unit is already occupied and cannot be leased.'
                })
        
        # Check that tenant is of type 'Tenant'
        if 'tenant' in data and data['tenant'].contact_type != Contact.ContactType.TENANT:  # Updated
            raise serializers.ValidationError({
                'tenant': 'Contact must be of type Tenant.'
            })
        
        # Check that landlord is of type 'Landlord'
        if 'landlord' in data and data['landlord'].contact_type != Contact.ContactType.LANDLORD:  # Updated
            raise serializers.ValidationError({
                'landlord': 'Contact must be of type Landlord.'
            })
        
        # Ensure landlord is the owner of the unit
        if ('landlord' in data and 'unit' in data and 
                data['landlord'] != data['unit'].owner):
            raise serializers.ValidationError({
                'landlord': 'Landlord must be the owner of the unit.'
            })
        
        return data

class LeaseDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed lease information"""
    
    unit_details = UnitSerializer(source='unit', read_only=True)
    tenant_details = ContactSerializer(source='tenant', read_only=True)
    landlord_details = ContactSerializer(source='landlord', read_only=True)
    payment_frequency_display = serializers.CharField(
        source='get_payment_frequency_display', 
        read_only=True
    )
    end_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Lease
        fields = [
            'id', 'unit', 'unit_details', 'tenant', 'tenant_details',
            'landlord', 'landlord_details', 'start_date', 'end_date',
            'duration', 'rent_amount', 'payment_frequency',
            'payment_frequency_display', 'created_at', 'updated_at'
        ]
    
    def get_end_date(self, obj):
        """Calculate the end date based on start date and duration"""
        from dateutil.relativedelta import relativedelta
        
        if obj.start_date:
            return obj.start_date + relativedelta(months=obj.duration)
        return None


class LeaseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing leases"""
    
    unit_number = serializers.CharField(source='unit.unit_number')
    tenant_name = serializers.CharField(source='tenant.name')
    landlord_name = serializers.CharField(source='landlord.name')
    payment_frequency_display = serializers.CharField(
        source='get_payment_frequency_display'
    )
    
    class Meta:
        model = Lease
        fields = [
            'id', 'unit_number', 'tenant_name', 'landlord_name',
            'start_date', 'duration', 'rent_amount', 'payment_frequency_display'
        ]