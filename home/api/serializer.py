
from rest_framework import serializers
from ..models import *
from django.contrib import auth
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError

        
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length = 5,max_length=50, write_only=True)
    username = serializers.CharField(max_length=150)
    class Meta:
        model = User
        fields = ('username', 'email','password')
    
    default_error_messages = {
        'username': 'Username only containe characters'}
    
    
    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():  
            raise serializers.ValidationError(
                self.default_error_messages)
        return attrs

    def create(self, validated_data):
        username = validated_data.pop('username') 
        return User.objects.create_user(username=username,**validated_data)

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio']


class SimpleBookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'published_date', 'isbn']
        
class SimpleReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']



class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    reviews = serializers.SerializerMethodField()
    # reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'published_date', 'isbn', 'reviews']

    def get_reviews(self, obj):
        reviews = Review.objects.filter(book=obj)
        return SimpleReviewSerializer(reviews, many=True).data

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = SimpleBookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True, source='book')

    class Meta:
        model = Review
        fields = ['id', 'user','book','book_id', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return Review.objects.create(user=user, **validated_data)

