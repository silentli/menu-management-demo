"""
URL configuration for menu_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from menu_app.views import staff_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('menu/', include('menu_app.urls')),
    # Staff URLs
    path('staff/login/', staff_views.StaffLoginView.as_view(), name='staff_login'),
    path('staff/logout/', staff_views.StaffLogoutView.as_view(), name='staff_logout'),
    path('staff/dashboard/', staff_views.StaffDashboardView.as_view(), name='staff_dashboard'),
    path('staff/menu/', staff_views.StaffMenuListView.as_view(), name='staff_menu_list'),
    path('staff/menu/create/', staff_views.StaffMenuCreateView.as_view(), name='staff_menu_create'),
    path('staff/menu/<int:pk>/update/', staff_views.StaffMenuUpdateView.as_view(), name='staff_menu_update'),
    path('staff/menu/<int:pk>/delete/', staff_views.StaffMenuDeleteView.as_view(), name='staff_menu_delete'),
    path('staff/inventory/', staff_views.InventoryListView.as_view(), name='inventory_list'),
    path('staff/inventory/low-stock/', staff_views.LowStockListView.as_view(), name='low_stock_list'),
    path('staff/inventory/<int:menu_item_id>/update/', staff_views.InventoryUpdateView.as_view(), name='inventory_update'),
    path('staff/orders/', staff_views.StaffOrderListView.as_view(), name='staff_order_list'),
    path('staff/orders/<int:pk>/', staff_views.StaffOrderDetailView.as_view(), name='staff_order_detail'),
]
