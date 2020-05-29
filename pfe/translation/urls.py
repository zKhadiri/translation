from django.urls import path
from . import views

app_name = 'translation'
urlpatterns = [
    path('', views.index,name='index'),
    path('start-now/', views.play_video,name='startnow'),
]
