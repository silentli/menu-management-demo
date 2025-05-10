from django.urls import path

from menu_app.views import customer_views, staff_views

app_name = 'menu_app'

urlpatterns = [
    # Customer URLs
    path('', customer_views.MenuListView.as_view(), name='menu_list'),
    # Staff URLs
    path('staff/', staff_views.StaffRootRedirectView.as_view(), name='staff_root'),
    path('staff/login/', staff_views.StaffLoginView.as_view(), name='staff_login'),
    path('staff/logout/', staff_views.StaffLogoutView.as_view(), name='staff_logout'),
    path('staff/dashboard/', staff_views.StaffDashboardView.as_view(), name='staff_dashboard'),
    path('staff/menu/', staff_views.StaffMenuListView.as_view(), name='staff_menu_list'),
    path('staff/menu/create/', staff_views.StaffMenuCreateView.as_view(), name='staff_menu_create'),
    path(
        'staff/menu/<int:pk>/update/',
        staff_views.StaffMenuUpdateView.as_view(),
        name='staff_menu_update',
    ),
    path(
        'staff/menu/<int:pk>/delete/',
        staff_views.StaffMenuDeleteView.as_view(),
        name='staff_menu_delete',
    ),
    # Staff Inventory URLs
    path('staff/inventory/', staff_views.InventoryListView.as_view(), name='inventory_list'),
    path(
        'staff/inventory/low-stock/', staff_views.LowStockListView.as_view(), name='low_stock_list'
    ),
    path(
        'staff/inventory/<int:menu_item_id>/update/',
        staff_views.InventoryUpdateView.as_view(),
        name='inventory_update',
    ),
    # Staff Order URLs
    path('staff/orders/', staff_views.StaffOrderListView.as_view(), name='staff_order_list'),
    path(
        'staff/orders/<int:pk>/',
        staff_views.StaffOrderDetailView.as_view(),
        name='staff_order_detail',
    ),
]
