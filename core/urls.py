from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('learn/', views.dashboard, name='dashboard'),
    path('learn/<str:script>/select/', views.select_characters, name='select_characters'),
    path('learn/<str:script>/study/', views.study, name='study'),
    path('learn/<str:script>/timer/', views.timer_mode, name='timer_mode'),
    path('api/progress/', views.save_progress, name='save_progress'),
    path('api/spaced/', views.get_spaced_chars, name='get_spaced_chars'),
    path('profile/', views.profile, name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('logout/', views.logout_view, name='logout'),
]