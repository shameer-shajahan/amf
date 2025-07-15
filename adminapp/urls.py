from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'adminapp'

urlpatterns = [
    path('create-user/', views.create_user_view, name='create_user'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
