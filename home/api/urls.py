from django.urls import path, include
from .user import *
from rest_framework import routers

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
router = routers.DefaultRouter()
urlpatterns=[
    path('', include(router.urls)),
    path('register/', UserRegister.as_view(), name='user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

#AUTHOR  PATH  
    path('authors/', AuthorAPIView.as_view(), name='author-list-create'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author-list-create'),
    
#BOOK PATH
    path('books/', BookListAPIView.as_view(), name='books-list'),
    path('books/<int:pk>/', BookDetailAPIView.as_view(), name='book-detail'),
    path('books/<int:book_id>/reviews/', BookReviewListAPIView.as_view(), name='book-reviews'),

#REVIEWS PATH
    path('reviews/', ReviewListCreateAPIView.as_view(), name='book-detail'),
    path('reviews/<int:pk>/', ReviewDetailAPIView.as_view(), name='review-detail'),

]
