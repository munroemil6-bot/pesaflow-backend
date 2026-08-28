
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from .models import Beneficiary

User = get_user_model()


class BeneficiarySerializer(serializers.ModelSerializer):
    """
    Full beneficiary details serializer for output.
    Used for retrieving beneficiary information.
    """
    
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Beneficiary
        fields = [
            'id',
            'user',
            'user_email',
            'user_username',
            'name',
            'phone',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'user_email',
            'user_username',
            'created_at',
            'updated_at',
        ]
    
    def to_representation(self, instance):
        """
        Customize the output representation.
        """
        data = super().to_representation(instance)
       
        data['created_at_formatted'] = instance.created_at.strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at_formatted'] = instance.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        return data


class CreateBeneficiarySerializer(serializers.ModelSerializer):
    """
    Serializer for creating new beneficiaries with validation.
    """
    
   
    phone = serializers.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in format: '+1234567890'. Up to 15 digits allowed."
            )
        ],
        help_text="Phone number with country code (e.g., +1234567890)"
    )
    

  
    name = serializers.CharField(
        max_length=255,
        min_length=2,
        help_text="Full name of the beneficiary (minimum 2 characters)"
    )
    
    class Meta:
        model = Beneficiary
        fields = [
            'name',
            'phone',
        ]
    
    def validate(self, data):
        """
        Validate the entire data before creation.
        """
        
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("User must be provided in context")

        name = data.get('name')
        phone = data.get('phone')
        
        if Beneficiary.objects.filter(user=user, phone=phone).exists():
            raise serializers.ValidationError({
                'phone': 'A beneficiary with this phone number already exists for this user.'
            })
        
        if Beneficiary.objects.filter(user=user, name=name).exists():
            raise serializers.ValidationError({
                'name': 'A beneficiary with this name already exists for this user.'
            })
        
        return data
    
    def create(self, validated_data):
        """
        Create the beneficiary instance.
        """
        user = self.context.get('user')
        validated_data['user'] = user
        return Beneficiary.objects.create(**validated_data)


class UpdateBeneficiarySerializer(serializers.ModelSerializer):
    """
    Serializer for updating beneficiaries with validation.
    All fields are optional for partial updates.
    """
    
    
    name = serializers.CharField(
        max_length=255,
        min_length=2,
        required=False,
        help_text="Full name of the beneficiary (minimum 2 characters)"
    )
    
    phone = serializers.CharField(
        max_length=20,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be in format: '+1234567890'. Up to 15 digits allowed."
            )
        ],
        help_text="Phone number with country code (e.g., +1234567890)"
    )
    
    class Meta:
        model = Beneficiary
        fields = [
            'name',
            'phone',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validate the entire data before update.
        """
        
        instance = self.instance
        user = instance.user
        
        
        if 'phone' in data:
            phone = data['phone']
            if Beneficiary.objects.filter(user=user, phone=phone).exclude(id=instance.id).exists():
                raise serializers.ValidationError({
                    'phone': 'A beneficiary with this phone number already exists for this user.'
                })
        
        
        if 'name' in data:
            name = data['name']
            if Beneficiary.objects.filter(user=user, name=name).exclude(id=instance.id).exists():
                raise serializers.ValidationError({
                    'name': 'A beneficiary with this name already exists for this user.'
                })
        
        return data
    
    def update(self, instance, validated_data):
        """
        Update the beneficiary instance.
        """
       
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class BeneficiaryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer with all beneficiary information.
    Includes additional computed fields.
    """
    
    user_info = serializers.SerializerMethodField()
   
    created_at_formatted = serializers.SerializerMethodField()
    updated_at_formatted = serializers.SerializerMethodField()
    
    
    days_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Beneficiary
        fields = [
            'id',
            'user',
            'user_info',
            'name',
            'phone',
            'created_at',
            'created_at_formatted',
            'updated_at',
            'updated_at_formatted',
            'days_since_created',
        ]
        read_only_fields = fields  
    
    def get_user_info(self, obj):
        """
        Get user information.
        """
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'full_name': getattr(obj.user, 'get_full_name', lambda: '')()
        }
    
    def get_created_at_formatted(self, obj):
        """
        Format created_at timestamp.
        """
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_updated_at_formatted(self, obj):
        """
        Format updated_at timestamp.
        """
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_days_since_created(self, obj):
        """
        Calculate days since creation.
        """
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        return delta.days


class BeneficiaryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing beneficiaries.
    Used for list views where only essential fields are needed.
    """
    
    class Meta:
        model = Beneficiary
        fields = [
            'id',
            'name',
            'phone',
            'created_at',
        ]
        read_only_fields = fields


class BulkCreateBeneficiarySerializer(serializers.Serializer):
    """
    Serializer for creating multiple beneficiaries at once.
    """
    
    beneficiaries = CreateBeneficiarySerializer(many=True)
    
    def validate(self, data):
        """
        Validate the entire bulk data.
        """
        beneficiaries_data = data.get('beneficiaries', [])
        
        if not beneficiaries_data:
            raise serializers.ValidationError("At least one beneficiary must be provided")
        
        if len(beneficiaries_data) > 100:
            raise serializers.ValidationError("Cannot create more than 100 beneficiaries at once")
        
        return data
    
    def create(self, validated_data):
        """
        Create multiple beneficiaries.
        """
        user = self.context.get('user')
        created_beneficiaries = []
        errors = []
        
        for idx, beneficiary_data in enumerate(validated_data.get('beneficiaries', [])):
            try:
                
                serializer = CreateBeneficiarySerializer(
                    data=beneficiary_data,
                    context={'user': user}
                )
                if serializer.is_valid():
                    beneficiary = serializer.save()
                    created_beneficiaries.append(beneficiary)
                else:
                    errors.append({
                        'index': idx,
                        'errors': serializer.errors
                    })
            except Exception as e:
                errors.append({
                    'index': idx,
                    'error': str(e)
                })
        
        if errors:
            raise serializers.ValidationError({
                'partial_success': len(created_beneficiaries),
                'total_errors': len(errors),
                'errors': errors
            })
        
        return created_beneficiaries


class BeneficiarySearchSerializer(serializers.Serializer):
    """
    Serializer for search parameters.
    """
    
    query = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Search term for name or phone"
    )
    
    name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Filter by name"
    )
    
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Filter by phone number"
    )
    
    created_after = serializers.DateTimeField(
        required=False,
        help_text="Filter beneficiaries created after this date"
    )
    
    created_before = serializers.DateTimeField(
        required=False,
        help_text="Filter beneficiaries created before this date"
    )
    
    def validate(self, data):
        """
        Validate search parameters.
        """
        created_after = data.get('created_after')
        created_before = data.get('created_before')
        
        if created_after and created_before:
            if created_after > created_before:
                raise serializers.ValidationError({
                    'created_after': 'created_after must be before created_before'
                })
        
        return data

# TODO: BeneficiarySerializer implementation
# TODO: CreateBeneficiarySerializer implementation
# TODO: UpdateBeneficiarySerializer implementation
