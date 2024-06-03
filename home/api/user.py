from ..models import User, Author, Book, Review
# from .serializer import UserSerializer, AuthorSerializer, BookSerializer, ReviewSerializer
from .serializer import UserSerializer, AuthorSerializer,ReviewSerializer, BookSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.http import Http404
from .custom_permissions import IsSuperAdmin

class UserRegister(APIView):
    permission_classes = [AllowAny]
    def post(self, request):  
        password = request.data.get('password')
        email = request.data.get('email')
        username = request.data.get('username')
        
        if not (email and password):
            return JsonResponse({"error": "Email and password are required"}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({"message": "Email already exists"}, status=400)
        try:
            user = User.objects.create_user(email=email, password=password)   
            user.save()
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        return JsonResponse({"message": "Registered successfully"}, status=201)

#AUTHOR API

class AuthorAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthorDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)
    
#BOOK API
class BookListAPIView(APIView):
    def get(self, request, format=None):
        books = Book.objects.all()

        author_name = request.query_params.get('author_name')
        published_date = request.query_params.get('published_date')

        if author_name:
            books = books.filter(author__name__icontains=author_name)
        if published_date:
            books = books.filter(published_date=published_date)

        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
#Fetch Book with Id
class BookDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk, format=None):
        book = self.get_object(pk)
        serializer = BookSerializer(book)
        return Response(serializer.data)


class BookReviewListAPIView(APIView):
    def get(self, request, book_id, *args, **kwargs):
        reviews = Review.objects.filter(book_id=book_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


#REVIEWS API

class ReviewListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # print(f"Authorization Header: {request.headers.get('Authorization')}")
        book_id = request.query_params.get('book')
        user_id = request.query_params.get('user')
        reviews = Review.objects.all()

        if book_id:
            reviews = reviews.filter(book_id=book_id)
        if user_id:
            reviews = reviews.filter(user_id=user_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        serializer = ReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            review = serializer.save()
            return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#UPDATE AND DELETE REVIEW 
class ReviewDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            raise Http404

    def put(self, request, pk, *args, **kwargs):
        review = self.get_object(pk)
        if review.user != request.user:
            return Response({'error': 'You do not have permission to edit this review.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Review updated successfully', 'review': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        review = self.get_object(pk)
        if review.user != request.user:
            return Response({'error': 'You do not have permission to delete this review.'}, status=status.HTTP_403_FORBIDDEN)
        review.delete()
        return Response({'message': 'Review deleted successfully'}, status=status.HTTP_204_NO_CONTENT)




