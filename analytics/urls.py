from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_view, name='analytics'),
    path('upload/', views.upload_data_view, name='upload_data'),
    path('analyze/', views.analyze_dataset_view, name='analyze_dataset'),
]
