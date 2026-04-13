from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('games/', views.game_list, name='game_list'),
    path('games/<int:game_id>/', views.game_detail, name='game_detail'),
    path('games/<int:game_id>/add/', views.add_to_library, name='add_to_library'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]