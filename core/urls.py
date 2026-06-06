from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('learn/', views.home, name='home'),
    path('learn/chart/', views.chart, name='chart'),
    path('learn/practice/', views.practice, name='practice'),
    path('learn/wordmode/', views.word_mode, name='word_mode'),
    path('profile/', views.profile, name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('api/progress/', views.save_progress, name='save_progress'),
    path('logout/', views.logout_view, name='logout'),
]
