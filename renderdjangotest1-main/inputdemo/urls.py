from . import views
from django.urls import path

urlpatterns = [
    path('detail/<int:pk>',views.image_detail),
    path('list', views.images_list),
    path('process', views.image_receive_and_process),
    path('testmobile', views.test_mobile)
]
