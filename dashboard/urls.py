from django.urls import path
from .views import register 
from . import views 
 
urlpatterns = [ 
    path('', views.home, name='home'), 
    path('register/', register, name='register'),
    path('profile/', views.profile, name='profile'), 
    path('profile/edit/', views.profile_edit, name='profile_edit'), 
    path('materials/', views.material_list, name='material_list'), 
    path('material/<int:pk>/', views.material_detail, name='material_detail'), 
    path('material/upload/', views.material_upload, name='material_upload'), 
    path('material/<int:pk>/edit/', views.material_edit, name='material_edit'), 
    path('material/<int:pk>/delete/', views.material_delete, name='material_delete'), 
    path('material/<int:pk>/save/', views.save_material, name='save_material'), 
    path('material/<int:pk>/rate/', views.rate_material, name='rate_material'), 
    path('material/<int:pk>/comment/', views.add_comment, name='add_comment'), 
    path('saved/', views.saved_materials, name='saved_materials'), 
    path('posts/', views.post_list, name='post_list'), 
    path('post/<int:pk>/', views.post_detail, name='post_detail'), 
    path('post/create/', views.post_create, name='post_create'), 
    path('post/<int:pk>/comment/', views.add_post_comment, name='add_post_comment'), 
    path('study-groups/', views.study_group_list, name='study_group_list'), 
    path('study-group/<int:pk>/', views.study_group_detail, name='study_group_detail'), 
    path('study-group/create/', views.study_group_create, name='study_group_create'), 
    path('study-group/<int:pk>/join/', views.study_group_join, name='study_group_join'), 
    path('search/', views.search, name='search'), 
] 
