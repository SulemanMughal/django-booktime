from django.urls import path, include
from django.views.generic.detail import DetailView
from main import models
from . import views
from django.contrib.auth import views as auth_views
from main import forms
from django.views.generic import TemplateView
# from django.urls import path, include
from rest_framework import routers
from main import endpoints

router = routers.DefaultRouter()
router.register(r'orderlines', endpoints.PaidOrderLineViewSet)
router.register(r'orders', endpoints.PaidOrderViewSet)

urlpatterns = [
    path('', views.index, name="index"),
    path("about-us/", views.about_us, name="about_us"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("products/<slug:tag>/",views.ProductListView.as_view(),name="products",),
    path("product/<slug:slug>/",DetailView.as_view(model=models.Product),name="product",),
    # path("login/",auth_views.LoginView.as_view(template_name="main/login.html",form_class=forms.AuthenticationForm,),name="user-login",),
    path('login', views.UserLoginView, name="user-login"),
    path('logout', views.UserLogoutView, name="user-logout"),
    path("address/",views.AddressListView.as_view(),name="address_list",),
    path("address/create/",views.AddressCreateView.as_view(),name="address_create",),
    path("address/<int:pk>/",views.AddressUpdateView.as_view(),name="address_update",),
    path("address/<int:pk>/delete/",views.AddressDeleteView.as_view(),name="address_delete",),
    path("add_to_basket/",views.add_to_basket,name="add_to_basket",),
    path('basket/', views.manage_basket, name="basket"),
    path(
"order/done/",
TemplateView.as_view(template_name="order_done.html"),
name="checkout_done",
),
path(
"order/address_select/",
views.AddressSelectionView.as_view(),
name="address_select",
),
path(
"order-dashboard/",
views.OrderView.as_view(),
name="order_dashboard",
),
path('api/', include(router.urls)),
]