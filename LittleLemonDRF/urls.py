from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'menu-item', views.MenuItemViewset)
router.register(r'orders', views.ManageOrdersViewset)

urlpatterns =[
    path('groups/manager/users/', views.managerAdminView, name='manager-admin'),
    path('groups/manager/users/<str:username>', views.managerAdminDeleteView, name='manager-delete-admin'),
    path('groups/delivery-crew/users/', views.deliveryCrewAdminView, name='delivery-crew-admin'),
    path('groups/delivery-crew/users/<str:username>', views.deliveryCrewAdminDeleteView, name='delivery-crew-delete-admin'),
    path('cart/menu-items/', views.cartItemsView, name='cart-items')

]

urlpatterns += router.urls
