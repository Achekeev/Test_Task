from django.urls import path
from .views import RegisterView, ArticleDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('article/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),

]