from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, UnitViewSet, LeaseViewSet, DashboardView, SummaryView

router = DefaultRouter()
router.register(r'contacts', ContactViewSet)
router.register(r'units', UnitViewSet)
router.register(r'leases', LeaseViewSet)
router.register(r'dashboard', DashboardView, basename='dashboard')
router.register(r'summary', SummaryView, basename='summary')

urlpatterns = [
    path('', include(router.urls)),
]