from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import Contact, Unit, Lease
from .serializers import (
    ContactSerializer, ContactListSerializer,
    UnitSerializer, UnitListSerializer,
    LeaseCreateUpdateSerializer, LeaseDetailSerializer, LeaseListSerializer
)


class ContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing contacts (landlords and tenants)
    """
    queryset = Contact.objects.all().order_by('name')
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['contact_type']
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ContactListSerializer
        return ContactSerializer
    
    @action(detail=False, methods=['get'])
    def landlords(self, request):
        """Get all landlords"""
        landlords = self.queryset.filter(contact_type=Contact.ContactType.LANDLORD) 
        page = self.paginate_queryset(landlords)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(landlords, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def tenants(self, request):
        """Get all tenants"""
        tenants = self.queryset.filter(contact_type=Contact.ContactType.TENANT)  
        page = self.paginate_queryset(tenants)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tenants, many=True)
        return Response(serializer.data)


class UnitViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing property units
    """
    queryset = Unit.objects.all().order_by('unit_number')
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'type', 'owner']
    search_fields = ['unit_number', 'location']
    ordering_fields = ['unit_number', 'value', 'created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return UnitListSerializer
        return UnitSerializer
    
    @action(detail=False, methods=['get'])
    def vacant(self, request):
        """Get all vacant units"""
        vacant_units = self.queryset.filter(status=Unit.UnitStatus.VACANT)
        page = self.paginate_queryset(vacant_units)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(vacant_units, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def occupied(self, request):
        """Get all occupied units"""
        occupied_units = self.queryset.filter(status=Unit.UnitStatus.OCCUPIED)
        page = self.paginate_queryset(occupied_units)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(occupied_units, many=True)
        return Response(serializer.data)


class LeaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing lease agreements
    """
    queryset = Lease.objects.all().order_by('-start_date')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['unit', 'tenant', 'landlord', 'payment_frequency']
    search_fields = ['unit__unit_number', 'tenant__name', 'landlord__name']
    ordering_fields = ['start_date', 'rent_amount', 'duration']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return LeaseCreateUpdateSerializer
        elif self.action == 'list':
            return LeaseListSerializer
        return LeaseDetailSerializer


class DashboardView(viewsets.ViewSet):
    """
    Dashboard endpoint providing summary information
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """
        Provide dashboard data:
        - Total units by status
        - Landlords with unit counts
        - Rent income summary
        - Latest lease information
        """
        # Get unit status summary
        unit_counts = Unit.objects.values('status').annotate(count=Count('id'))
        unit_status = {
            unit['status']: unit['count'] for unit in unit_counts
        }
        
        total_units = Unit.objects.count()
        vacant_units = unit_status.get(Unit.UnitStatus.VACANT, 0)
        occupied_units = unit_status.get(Unit.UnitStatus.OCCUPIED, 0)
        maintenance_units = unit_status.get(Unit.UnitStatus.MAINTENANCE, 0)
        
        # Get landlord summary
        landlords = Contact.objects.filter(
            type=Contact.ContactType.LANDLORD
        ).annotate(
            units_count=Count('owned_units')
        ).values('id', 'name', 'units_count')
        
        # Get rent income summary
        total_rent = Lease.objects.aggregate(
            total=Sum('rent_amount')
        )['total'] or 0
        
        monthly_leases = Lease.objects.filter(
            payment_frequency=Lease.PaymentFrequency.MONTHLY
        ).aggregate(
            total=Sum('rent_amount')
        )['total'] or 0
        
        quarterly_leases = Lease.objects.filter(
            payment_frequency=Lease.PaymentFrequency.QUARTERLY
        ).aggregate(
            total=Sum('rent_amount')
        )['total'] or 0
        
        # Get latest lease
        latest_lease = None
        if Lease.objects.exists():
            latest_lease_obj = Lease.objects.latest('created_at')
            latest_lease = LeaseDetailSerializer(latest_lease_obj).data
        
        return Response({
            'units_summary': {
                'total': total_units,
                'vacant': vacant_units,
                'occupied': occupied_units,
                'maintenance': maintenance_units,
                'occupancy_rate': f"{(occupied_units / total_units * 100) if total_units else 0:.2f}%"
            },
            'landlords_summary': list(landlords),
            'rent_income_summary': {
                'total_monthly_rent': monthly_leases,
                'total_quarterly_rent': quarterly_leases,
                'total_rent': total_rent,
                'average_rent': f"{(total_rent / occupied_units) if occupied_units else 0:.2f}"
            },
            'latest_lease': latest_lease
        })


class SummaryView(viewsets.ViewSet):
    """
    Summary endpoint providing information about test data
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """
        Provide summary data showing the relationships between:
        - Test landlord
        - Test tenant
        - Test unit
        - Test lease
        """
        # Get test data
        # Assuming the first entries are our test data
        test_landlord = None
        landlords = Contact.objects.filter(contact_type=Contact.ContactType.LANDLORD)
        if landlords.exists():
            test_landlord = ContactSerializer(landlords.first()).data
        
        test_tenant = None
        tenants = Contact.objects.filter(contact_type=Contact.ContactType.TENANT)
        if tenants.exists():
            test_tenant = ContactSerializer(tenants.first()).data
        
        test_unit = None
        units = Unit.objects.all()
        if units.exists():
            test_unit = UnitSerializer(units.first()).data
        
        test_lease = None
        leases = Lease.objects.all()
        if leases.exists():
            test_lease = LeaseDetailSerializer(leases.first()).data
        
        # Build relationships
        relationships = []
        
        if test_landlord and test_unit:
            relationships.append({
                'type': 'Landlord owns Unit',
                'from': f"Landlord: {test_landlord['name']}",
                'to': f"Unit: {test_unit['unit_number']}"
            })
        
        if test_tenant and test_lease and test_unit:
            relationships.append({
                'type': 'Tenant leases Unit',
                'from': f"Tenant: {test_tenant['name']}",
                'to': f"Unit: {test_unit['unit_number']}"
            })
        
        if test_landlord and test_lease and test_tenant:
            relationships.append({
                'type': 'Landlord leases to Tenant',
                'from': f"Landlord: {test_landlord['name']}",
                'to': f"Tenant: {test_tenant['name']}"
            })
        
        return Response({
            'test_data': {
                'landlord': test_landlord,
                'tenant': test_tenant,
                'unit': test_unit,
                'lease': test_lease
            },
            'relationships': relationships
        })