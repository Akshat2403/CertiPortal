from django.urls import path, re_path
from . import views

urlpatterns = [
    path('',views.login,name='login'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('dashboard/<int:sent>',views.dashboard,name='dashboard'),
    path('addcandidate',views.addCandidate,name='addCandidate'),
    path('delete/<str:email>',views.delete_candidate,name='delete'),
    path('logout',views.logout,name='logout'),

]