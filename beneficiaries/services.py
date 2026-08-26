"""
Beneficiaries Services

Owner: Naomi
Responsibility: Business logic for beneficiary management

Service functions to implement:
# TODO: create_beneficiary(user, name, phone)
#   - Validate phone format
#   - Check for duplicates
#   - Create beneficiary record
#   - Return beneficiary object

# TODO: get_user_beneficiaries(user)
#   - Get all beneficiaries for user
#   - Return list of beneficiaries

# TODO: get_beneficiary(user, beneficiary_id)
#   - Get specific beneficiary
#   - Verify ownership
#   - Return beneficiary or raise PermissionDenied

# TODO: update_beneficiary(user, beneficiary_id, data)
#   - Update beneficiary fields
#   - Validate uniqueness
#   - Return updated beneficiary

# TODO: delete_beneficiary(user, beneficiary_id)
#   - Delete beneficiary
#   - Verify ownership
#   - Return success message
"""

# TODO: Create beneficiary service functions
# TODO: Handle validation and business rules
# services.py
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
import re

from .models import Beneficiary

User = get_user_model()


def validate_phone_number(phone):
    """
    Validate phone number format.
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValidationError: If phone number format is invalid
    """

    cleaned_phone = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, cleaned_phone):
        raise ValidationError(
            "Phone number must be in format: '+1234567890'. "
            "Up to 15 digits allowed."
        )
    
    
    digits_only = ''.join(c for c in cleaned_phone if c.isdigit())
    if len(digits_only) < 10:
        raise ValidationError(
            "Phone number must have at least 10 digits."
        )
    
    return True


def create_beneficiary(user, name, phone):
    """
    Create a new beneficiary for a user.
    
    Args:
        user (User): The user creating the beneficiary
        name (str): Full name of the beneficiary
        phone (str): Phone number of the beneficiary
        
    Returns:
        Beneficiary: The created beneficiary object
        
    Raises:
        ValidationError: If validation fails
        IntegrityError: If duplicate beneficiary exists
    """
    
    validate_phone_number(phone)
    
    
    if Beneficiary.objects.filter(user=user, phone=phone).exists():
        raise IntegrityError(
            f"A beneficiary with phone number '{phone}' already exists for this user."
        )
    
    
    if Beneficiary.objects.filter(user=user, name=name).exists():
        raise IntegrityError(
            f"A beneficiary with name '{name}' already exists for this user."
        )
    
    try:
        beneficiary = Beneficiary.objects.create(
            user=user,
            name=name.strip(),
            phone=phone.strip()
        )
        return beneficiary
    except Exception as e:
        raise ValidationError(f"Failed to create beneficiary: {str(e)}")


def get_user_beneficiaries(user, active_only=True):
    """
    Get all beneficiaries for a user.
    
    Args:
        user (User): The user whose beneficiaries to retrieve
        active_only (bool): If True, only return active beneficiaries
        
    Returns:
        QuerySet: List of beneficiary objects
    """
    if not user or not user.is_authenticated:
        return Beneficiary.objects.none()
    
    queryset = Beneficiary.objects.filter(user=user)
   
    return queryset.order_by('-created_at')


def get_beneficiary(user, beneficiary_id):
    """
    Get a specific beneficiary by ID and verify ownership.
    
    Args:
        user (User): The user requesting the beneficiary
        beneficiary_id (int): ID of the beneficiary
        
    Returns:
        Beneficiary: The beneficiary object
        
    Raises:
        Beneficiary.DoesNotExist: If beneficiary doesn't exist
        PermissionDenied: If user doesn't own the beneficiary
    """
    try:
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)
    except Beneficiary.DoesNotExist:
        raise Beneficiary.DoesNotExist(
            f"Beneficiary with ID '{beneficiary_id}' does not exist."
        )
    
    
    if beneficiary.user != user:
        raise PermissionDenied(
            "You do not have permission to access this beneficiary."
        )
    
    return beneficiary


def update_beneficiary(user, beneficiary_id, data):
    """
    Update beneficiary fields with validation.
    
    Args:
        user (User): The user performing the update
        beneficiary_id (int): ID of the beneficiary to update
        data (dict): Dictionary of fields to update
        
    Returns:
        Beneficiary: The updated beneficiary object
        
    Raises:
        Beneficiary.DoesNotExist: If beneficiary doesn't exist
        PermissionDenied: If user doesn't own the beneficiary
        ValidationError: If validation fails
        IntegrityError: If duplicate data conflicts
    """

    beneficiary = get_beneficiary(user, beneficiary_id)
    name = data.get('name')
    phone = data.get('phone')
    
    
    if phone is not None:
        phone = phone.strip()
        validate_phone_number(phone)
    
        if Beneficiary.objects.filter(
            user=user, 
            phone=phone
        ).exclude(id=beneficiary_id).exists():
            raise IntegrityError(
                f"A beneficiary with phone number '{phone}' already exists for this user."
            )
        beneficiary.phone = phone
    
    
    if name is not None:
        name = name.strip()
        
    
        if Beneficiary.objects.filter(
            user=user, 
            name=name
        ).exclude(id=beneficiary_id).exists():
            raise IntegrityError(
                f"A beneficiary with name '{name}' already exists for this user."
            )
        beneficiary.name = name
    
    try:
        beneficiary.save()
        return beneficiary
    except Exception as e:
        raise ValidationError(f"Failed to update beneficiary: {str(e)}")


def delete_beneficiary(user, beneficiary_id):
    """
    Delete a beneficiary by ID with ownership verification.
    
    Args:
        user (User): The user performing the deletion
        beneficiary_id (int): ID of the beneficiary to delete
        
    Returns:
        dict: Success message with deleted beneficiary info
        
    Raises:
        Beneficiary.DoesNotExist: If beneficiary doesn't exist
        PermissionDenied: If user doesn't own the beneficiary
    """
    
    beneficiary = get_beneficiary(user, beneficiary_id)
    
    
    beneficiary_info = {
        'id': beneficiary.id,
        'name': beneficiary.name,
        'phone': beneficiary.phone
    }
    
    try:
    
        beneficiary.delete()
        return {
            'success': True,
            'message': f"Beneficiary '{beneficiary_info['name']}' deleted successfully.",
            'deleted_beneficiary': beneficiary_info
        }
    except Exception as e:
        raise ValidationError(f"Failed to delete beneficiary: {str(e)}")




def get_beneficiary_by_phone(user, phone):
    """
    Get a beneficiary by phone number for a specific user.
    
    Args:
        user (User): The user
        phone (str): Phone number to search for
        
    Returns:
        Beneficiary: The beneficiary object
        
    Raises:
        Beneficiary.DoesNotExist: If beneficiary doesn't exist
    """
    return Beneficiary.objects.get(user=user, phone=phone)


def get_beneficiary_by_name(user, name):
    """
    Get a beneficiary by name for a specific user.
    
    Args:
        user (User): The user
        name (str): Name to search for
        
    Returns:
        Beneficiary: The beneficiary object
        
    Raises:
        Beneficiary.DoesNotExist: If beneficiary doesn't exist
    """
    return Beneficiary.objects.get(user=user, name=name)


def search_beneficiaries(user, search_term):
    """
    Search beneficiaries by name or phone.
    
    Args:
        user (User): The user
        search_term (str): Search term
        
    Returns:
        QuerySet: List of matching beneficiaries
    """
    from django.db.models import Q
    
    return Beneficiary.objects.filter(
        user=user
    ).filter(
        Q(name__icontains=search_term) |
        Q(phone__icontains=search_term)
    ).order_by('-created_at')


def count_user_beneficiaries(user):
    """
    Count total beneficiaries for a user.
    
    Args:
        user (User): The user
        
    Returns:
        int: Number of beneficiaries
    """
    return Beneficiary.objects.filter(user=user).count()


def check_beneficiary_exists(user, phone=None, name=None):
    """
    Check if a beneficiary exists for a user.
    
    Args:
        user (User): The user
        phone (str, optional): Phone number to check
        name (str, optional): Name to check
        
    Returns:
        bool: True if exists, False otherwise
    """
    queryset = Beneficiary.objects.filter(user=user)
    
    if phone:
        queryset = queryset.filter(phone=phone)
    
    if name:
        queryset = queryset.filter(name=name)
    
    return queryset.exists()


def get_or_create_beneficiary(user, name, phone):
    """
    Get an existing beneficiary or create a new one.
    
    Args:
        user (User): The user
        name (str): Name of the beneficiary
        phone (str): Phone number
        
    Returns:
        tuple: (beneficiary, created) where created is a boolean
    """
    try:
        beneficiary = Beneficiary.objects.get(user=user, phone=phone)
        return beneficiary, False
    except Beneficiary.DoesNotExist:
        beneficiary = create_beneficiary(user, name, phone)
        return beneficiary, True