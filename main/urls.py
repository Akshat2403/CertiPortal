from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index , name="index"),
    path('candidform', views.candidForm , name="candidForm"),
    path('candidlist', views.candidList , name="candidList"),
    path('candidlist/filter/<int:id>', views.candidListFilter , name="candidListFilter"),
    path('candidbulk', views.candidBulk , name="candidBulk"),
    path('accounts/logout/', views.logoutView , name="logoutView"),
    path('cnotfound', views.certificateNotFound , name="certificateNotFound"),
    path('mail_sent/<slug:alcher_id>/<str:certificate_url>', views.send_email , name="send_email"),
    path('delete_candidate/<str:certificate_url>', views.delete_candidate , name="delete_candidate"),
    path('candidupdate/<int:tpk>', views.candidUpdateForm , name="candidUpdateForm"),
    re_path(r'^certificate/(?P<cert_id>[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]/$', views.certificate , name="certificate"),
    path('massmail/<str:event_name>', views.massmail, name="massmail"),
    path('sendall', views.send_email_to_all, name="sendall"),
    path('deleteall', views.delete_all, name="deleteall"),
    path('calist', views.calist, name="calist"),
    path('massmailca/', views.massmailca, name="massmailca"),
    path('salist', views.salist, name="salist"),
    path('massmailsa/', views.massmailsa, name="massmailsa"),
]

