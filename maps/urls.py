from django.urls import path
from .views.fuelRouting import OptimizeFuelRoute

urlpatterns = [
    path('optimize-fuel-route/', OptimizeFuelRoute.as_view(), name='optimize_fuel_route'),
]
