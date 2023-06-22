from django.urls import path, re_path
from . import views

urlpatterns = [
    path('',views.login,name='login'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('dashboard/<int:sent>',views.dashboard,name='dashboard'),
    path('addcandidate',views.addCandidate,name='addCandidate'),
    path('addcsv/',views.addcsv, name="csv"),
    path('delete/<str:email>',views.delete_candidate,name='delete'),
    path('update/<str:pk>', views.update_candidate, name="update"),
    path('logout',views.logout,name='logout'),
]