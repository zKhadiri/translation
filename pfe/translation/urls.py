from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'translation'
urlpatterns = [
    path('', views.index,name='index'),
    path('start-now/', views.play_video,name='startnow'),
]
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
