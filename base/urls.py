from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('storage/', views.storage, name='storage'),
    path('roll/', views.roll, name='roll'),
]
