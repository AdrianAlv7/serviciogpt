from django.contrib.auth import views as auth_views
from django.urls import path
from . import views, views_generador_documentos

urlpatterns = [
    path('', views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('egresado/', views.egresado, name='egresado'),
    path('perfil/', views.perfil, name='perfil'),
    path('servicios_escolares/', views.servicios_escolares, name='servicios_escolares'),
    # path('etapa-identificacion/', views.etapa_identificacion, name='etapa_identificacion'),
    # path('etapa-revision/', views.etapa_revision, name='etapa_revision'),
    # path('etapa-segundo-revision/', views.etapa_segundo_revision, name='etapa_segundo_revision'),
    # path('etapa-revicion-recibos/', views.etapa_revicion_recibos, name='etapa_revicion_recibos'),
    # path('etapa-cni/', views.etapa_cni, name='etapa_cni'),
    
    path('generar_documento/', views_generador_documentos.generar_documento, name='generar_documento'),
    path('importar-egresados/', views.importar_egresados, name='importar_egresados'),
    
    
]