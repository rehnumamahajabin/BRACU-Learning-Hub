from django.contrib import admin 
from django.urls import path, include 
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views 
from dashboard.views import home 
 
urlpatterns = [ 
    path('admin/', admin.site.urls), 
    path('', home, name='home'), 
    path('dashboard/', include('dashboard.urls')), 
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'), 
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'), 
] 
 
if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
