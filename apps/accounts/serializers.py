from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, CustomerProfile, ModeratorProfile, WarehouseManagerProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 
                 'last_name', 'phone_number', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # Create profile based on role
        if user.role == 'customer':
            CustomerProfile.objects.create(user=user)
        elif user.role == 'moderator':
            ModeratorProfile.objects.create(user=user)
        elif user.role == 'warehouse_manager':
            WarehouseManagerProfile.objects.create(user=user)
            
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'role', 'address', 'city', 'state', 
                 'postal_code', 'country', 'profile_picture', 'is_verified',
                 'date_joined', 'last_login')
        read_only_fields = ('id', 'username', 'role', 'is_verified', 
                           'date_joined', 'last_login')


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = '__all__'


class ModeratorProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = ModeratorProfile
        fields = '__all__'


class WarehouseManagerProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = WarehouseManagerProfile
        fields = '__all__'