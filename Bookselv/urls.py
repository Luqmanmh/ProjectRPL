from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', views.blink, name='blink'),
    path('online/f/<int:file_root>', views.index, name='online'),
    path('login/', views.loginusr, name='loginusr'),
    path('admin_login/', views.loginadm, name='loginadm'),
    path('register/', views.register, name='register'),
    path('logoutusr/', views.logoutusr, name='logoutusr'),
    path('userpanel/', views.userpanel, name='userpanel'),
    path('manage/f/<int:file_root>', views.manage, name='manage'),
    path('uploadfile/<int:file_root>', views.fileup, name='fileupload'),
    path('createfolder/<int:file_root>', views.folderup, name='createfolder'),
    path('download/<int:pk>/', views.download_file, name='download'),
    path('deletefile/<int:pk>', views.delete_file, name='deletefile'),
    path('deletefold/<int:pk>', views.delete_folder_and_contents, name='deletefold'),
    path('move/<str:type>/<int:pk>/', views.move, name='move'),
    path('manage/s/', views.search_file, name='search'),
    path('online/s', views.search_fileu, name='searchon'),
    path('pdf/<int:file_id>/', views.view_pdf, name='view_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += staticfiles_urlpatterns()
