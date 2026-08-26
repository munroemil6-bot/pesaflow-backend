"""
Beneficiaries Models

Owner: Naomi
Responsibility: Beneficiary model and related database tables

Models to implement:
# TODO: Beneficiary model
#   - user (ForeignKey to User, cascade delete)
#   - name (CharField)
#   - phone (CharField)
#   - created_at (DateTimeField auto_now_add)
#   - updated_at (DateTimeField auto_now)
#   - Meta: unique_together on (user, phone) to prevent duplicates
#   - Methods: to_dict()
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError


User = get_user_model()


class Beneficiary(models.Model):
    """
    Model for storing beneficiary (saved recipient) information.
    Each beneficiary belongs to a user and stores their contact details.
    """
    
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='beneficiaries',
        verbose_name='User',
        help_text='The user who owns this beneficiary'
    )
    

    name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(2)],
        verbose_name='Full Name',
        help_text='Full name of the beneficiary'
    ) 
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+1234567890'. Up to 15 digits allowed."
            )
        ],
        verbose_name='Phone Number',
        help_text='Phone number with country code (e.g., +1234567890)'
    )
    
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At',
        help_text='Date and time when this beneficiary was created'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At',
        help_text='Date and time when this beneficiary was last updated'
    )
    
  
    class Meta:
        
        unique_together = [['user', 'phone']]
        
        
        ordering = ['-created_at']
        
        
        
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['phone']),
        ]
    
    def __str__(self):
        """String representation of the beneficiary"""
        return f"{self.name} ({self.phone})"
    
    def to_dict(self):
        """
        Convert the beneficiary instance to a dictionary.
        Returns a dictionary containing all relevant beneficiary data.
        """
        return {
            'id': self.id,
            'user_id': self.user.id,
            'user_email': self.user.email if hasattr(self.user, 'email') else None,
            'name': self.name,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def clean(self):
        """Custom validation for the model"""
        if self.phone:
            cleaned_phone = ''.join(c for c in self.phone if c.isdigit() or c == '+')
            if cleaned_phone != self.phone:
                raise ValidationError({
                    'phone': 'Phone number can only contain digits and an optional leading "+" sign.'
                })
    
    def save(self, *args, **kwargs):
        """Override save to run validation before saving"""
        self.full_clean()  
        super().save(*args, **kwargs)

# TODO: Create Beneficiary model linked to User
# TODO: Add validation for phone number format
