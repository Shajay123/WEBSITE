from django.urls import path 
from webapp import views

urlpatterns = [
     path('',views.home,name='home'),
     path('purchase/',views.purchase,name='purchase'),
     path('checkout/', views.checkout, name="Checkout"),
     path('handlerequest/', views.handlerequest, name="HandleRequest"),
     path('tracker', views.tracker, name="TrackingStatus"),
]
