# gym_app/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register, name='register'),
    path('free-trial-register/', views.register, name='free_trial_register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('member/<int:id>/', views.member_detail, name='member_detail'),
    path('plans/', views.membership_plans, name='plans'),
    path('logout/', views.logout_view, name='logout'),
    path('diet/15-30/', views.diet_15_30, name='diet_15_30'),
    path('diet/30-50/', views.diet_30_50, name='diet_30_50'),
    path('diet/50-70/', views.diet_50_70, name='diet_50_70'),
    path('diet/', views.diet_selection, name='diet_selection'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('events/register/', views.event_register, name='event_register'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)