"""
Beneficiaries Tests

Owner: Naomi
Responsibility: Unit tests for beneficiary endpoints

Tests to implement:
# TODO: TestBeneficiaryList
#   - test_list_beneficiaries
#   - test_list_empty_beneficiaries
#   - test_list_beneficiaries_pagination

# TODO: TestCreateBeneficiary
#   - test_create_beneficiary_success
#   - test_create_invalid_phone
#   - test_create_duplicate_beneficiary
#   - test_create_unauthenticated

# TODO: TestUpdateBeneficiary
#   - test_update_beneficiary_success
#   - test_update_nonexistent_beneficiary
#   - test_update_another_users_beneficiary

# TODO: TestDeleteBeneficiary
#   - test_delete_beneficiary_success
#   - test_delete_nonexistent_beneficiary
#   - test_delete_another_users_beneficiary
"""


import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.exceptions import ValidationError

from beneficiaries.models import Beneficiary
from beneficiaries.serializers import BeneficiarySerializer

User = get_user_model()


@pytest.mark.django_db
class TestBeneficiaryList:
    """Test suite for listing beneficiaries"""
    
    def setup_method(self):
        """Set up test data before each test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('beneficiaries:list-create')
        
        
        self.beneficiary1 = Beneficiary.objects.create(
            user=self.user,
            name='John Doe',
            phone='+1234567890'
        )
        self.beneficiary2 = Beneficiary.objects.create(
            user=self.user,
            name='Jane Smith',
            phone='+1987654321'
        )
        self.other_beneficiary = Beneficiary.objects.create(
            user=self.other_user,
            name='Other User',
            phone='+1122334455'
        )
    
    def test_list_beneficiaries(self):
        """Test listing all beneficiaries for authenticated user"""
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert len(response.data['results']) == 2
        
        
        names = [item['name'] for item in response.data['results']]
        assert 'John Doe' in names
        assert 'Jane Smith' in names
        assert 'Other User' not in names
    
    def test_list_empty_beneficiaries(self):
        """Test listing beneficiaries when user has none"""
       
        new_user = User.objects.create_user(
            username='emptyuser',
            password='emptypass123'
        )
        self.client.force_authenticate(user=new_user)
        
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0
    
    def test_list_beneficiaries_pagination(self):
        """Test pagination of beneficiary list"""
        
        for i in range(25):
            Beneficiary.objects.create(
                user=self.user,
                name=f'Test User {i}',
                phone=f'+123456789{i}'
            )
        
        
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 27  
        assert len(response.data['results']) == 20
        
        
        response = self.client.get(f"{self.url}?page=2")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 7
        
        
        response = self.client.get(f"{self.url}?page_size=5")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
        
        
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
    
    def test_list_beneficiaries_unauthenticated(self):
        """Test listing beneficiaries without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_beneficiaries_with_search(self):
        """Test searching beneficiaries by name or phone"""
        
        response = self.client.get(f"{self.url}?search=John")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'John Doe'
        
        
        response = self.client.get(f"{self.url}?search=987654321")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Jane Smith'


@pytest.mark.django_db
class TestCreateBeneficiary:
    """Test suite for creating beneficiaries"""
    
    def setup_method(self):
        """Set up test data before each test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('beneficiaries:list-create')
        
        
        self.existing_beneficiary = Beneficiary.objects.create(
            user=self.user,
            name='Existing User',
            phone='+1234567890'
        )
    
    def test_create_beneficiary_success(self):
        """Test successful beneficiary creation"""
        data = {
            'name': 'New Beneficiary',
            'phone': '+1987654321'
        }
        response = self.client.post(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Beneficiary created successfully.'
        assert response.data['data']['name'] == 'New Beneficiary'
        assert response.data['data']['phone'] == '+1987654321'
        
    
        assert Beneficiary.objects.count() == 2
        new_beneficiary = Beneficiary.objects.get(phone='+1987654321')
        assert new_beneficiary.user == self.user
        assert new_beneficiary.name == 'New Beneficiary'
    
    def test_create_beneficiary_invalid_phone(self):
        """Test creating beneficiary with invalid phone number"""
        test_cases = [
            {'phone': 'invalid', 'name': 'Invalid Phone'},
            {'phone': '123', 'name': 'Too Short'},
            {'phone': '1234567890123456789', 'name': 'Too Long'},
            {'phone': 'abc123def456', 'name': 'Alpha Numeric'},
        ]
        
        for test_case in test_cases:
            response = self.client.post(self.url, test_case, format='json')
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert 'error' in response.data
    
    def test_create_beneficiary_duplicate_phone(self):
        """Test creating beneficiary with duplicate phone number"""
        data = {
            'name': 'Duplicate User',
            'phone': '+1234567890'  
        }
        response = self.client.post(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert 'already exists' in str(response.data['error'])
        
        
        assert Beneficiary.objects.count() == 1
    
    def test_create_beneficiary_duplicate_name(self):
        """Test creating beneficiary with duplicate name"""
        data = {
            'name': 'Existing User',  
            'phone': '+1999999999'
        }
        response = self.client.post(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        
        
        assert Beneficiary.objects.count() == 1
    
    def test_create_beneficiary_unauthenticated(self):
        """Test creating beneficiary without authentication"""
        self.client.force_authenticate(user=None)
        data = {
            'name': 'Unauthenticated User',
            'phone': '+1234567890'
        }
        response = self.client.post(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Beneficiary.objects.count() == 1
    
    def test_create_beneficiary_missing_fields(self):
        """Test creating beneficiary with missing required fields"""
        
        data = {'phone': '+1234567890'}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        
        data = {'name': 'Missing Phone'}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
        response = self.client.post(self.url, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUpdateBeneficiary:
    """Test suite for updating beneficiaries"""
    
    def setup_method(self):
        """Set up test data before each test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        
        self.beneficiary = Beneficiary.objects.create(
            user=self.user,
            name='John Doe',
            phone='+1234567890'
        )
        self.other_beneficiary = Beneficiary.objects.create(
            user=self.other_user,
            name='Other Beneficiary',
            phone='+1987654321'
        )
        self.url = reverse('beneficiaries:detail', kwargs={'id': self.beneficiary.id})
        self.other_url = reverse('beneficiaries:detail', kwargs={'id': self.other_beneficiary.id})
    
    def test_update_beneficiary_success(self):
        """Test successful beneficiary update"""
        data = {
            'name': 'John Updated',
            'phone': '+1111111111'
        }
        response = self.client.put(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Beneficiary updated successfully.'
        assert response.data['data']['name'] == 'John Updated'
        assert response.data['data']['phone'] == '+1111111111'
        
    
        self.beneficiary.refresh_from_db()
        assert self.beneficiary.name == 'John Updated'
        assert self.beneficiary.phone == '+1111111111'
    
    def test_update_beneficiary_partial_success(self):
        """Test successful partial beneficiary update"""
        
        data = {'name': 'John Partially Updated'}
        response = self.client.patch(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['name'] == 'John Partially Updated'

        assert response.data['data']['phone'] == '+1234567890'
        
    
        data = {'phone': '+1999999999'}
        response = self.client.patch(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['phone'] == '+1999999999'
        
        assert response.data['data']['name'] == 'John Partially Updated'
    
    def test_update_beneficiary_nonexistent(self):
        """Test updating a non-existent beneficiary"""
        non_existent_url = reverse('beneficiaries:detail', kwargs={'id': 999})
        data = {'name': 'Non Existent'}
        response = self.client.put(non_existent_url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data
    
    def test_update_another_users_beneficiary(self):
        """Test updating another user's beneficiary"""
        data = {
            'name': 'Hacked Name',
            'phone': '+1999999999'
        }
        response = self.client.put(self.other_url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data
        
        
        self.other_beneficiary.refresh_from_db()
        assert self.other_beneficiary.name == 'Other Beneficiary'
        assert self.other_beneficiary.phone == '+1987654321'
    
    def test_update_beneficiary_duplicate_phone(self):
        """Test updating beneficiary with duplicate phone"""
        
        another_beneficiary = Beneficiary.objects.create(
            user=self.user,
            name='Another User',
            phone='+1555555555'
        )
        

        data = {'phone': '+1555555555'}
        response = self.client.patch(
            reverse('beneficiaries:detail', kwargs={'id': self.beneficiary.id}),
            data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_update_beneficiary_invalid_phone(self):
        """Test updating beneficiary with invalid phone"""
        data = {'phone': 'invalid'}
        response = self.client.patch(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_update_beneficiary_unauthenticated(self):
        """Test updating beneficiary without authentication"""
        self.client.force_authenticate(user=None)
        data = {'name': 'Unauthenticated'}
        response = self.client.put(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDeleteBeneficiary:
    """Test suite for deleting beneficiaries"""
    
    def setup_method(self):
        """Set up test data before each test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        
        self.beneficiary = Beneficiary.objects.create(
            user=self.user,
            name='John Doe',
            phone='+1234567890'
        )
        self.other_beneficiary = Beneficiary.objects.create(
            user=self.other_user,
            name='Other Beneficiary',
            phone='+1987654321'
        )
        self.url = reverse('beneficiaries:detail', kwargs={'id': self.beneficiary.id})
        self.other_url = reverse('beneficiaries:detail', kwargs={'id': self.other_beneficiary.id})
    
    def test_delete_beneficiary_success(self):
        """Test successful beneficiary deletion"""
        response = self.client.delete(self.url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data is None or response.data == {}
        
        
        assert Beneficiary.objects.count() == 1  
        assert not Beneficiary.objects.filter(id=self.beneficiary.id).exists()
    
    def test_delete_beneficiary_nonexistent(self):
        """Test deleting a non-existent beneficiary"""
        non_existent_url = reverse('beneficiaries:detail', kwargs={'id': 999})
        response = self.client.delete(non_existent_url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data
    
    def test_delete_another_users_beneficiary(self):
        """Test deleting another user's beneficiary"""
        response = self.client.delete(self.other_url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.data
        
        # Verify beneficiary wasn't deleted
        assert Beneficiary.objects.filter(id=self.other_beneficiary.id).exists()
        assert Beneficiary.objects.count() == 2
    
    def test_delete_beneficiary_unauthenticated(self):
        """Test deleting beneficiary without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        # Verify beneficiary wasn't deleted
        assert Beneficiary.objects.filter(id=self.beneficiary.id).exists()
    
    def test_delete_beneficiary_verify_owner(self):
        """Test that deleted beneficiary belongs to the correct user"""
        beneficiary_id = self.beneficiary.id
        response = self.client.delete(self.url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Try to access the deleted beneficiary
        get_response = self.client.get(self.url)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify other user's beneficiary still exists
        assert Beneficiary.objects.filter(id=self.other_beneficiary.id).exists()


@pytest.mark.django_db
class TestBeneficiaryPermissions:
    """Test suite for permission checks"""
    
    def setup_method(self):
        """Set up test data before each test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('beneficiaries:list-create')
    
    def test_authenticated_user_can_access(self):
        """Test that authenticated user can access endpoints"""
        # Test GET
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        
        # Test POST
        data = {'name': 'Test User', 'phone': '+1234567890'}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
    
    def test_unauthenticated_user_cannot_access(self):
        """Test that unauthenticated user cannot access endpoints"""
        self.client.force_authenticate(user=None)
        
        # Test GET
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test POST
        data = {'name': 'Test User', 'phone': '+1234567890'}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestBeneficiaryEdgeCases:
    """Test suite for edge cases"""
    
    def setup_method(self):
        """Set up test data before each test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('beneficiaries:list-create')
    
    def test_create_beneficiary_with_whitespace(self):
        """Test creating beneficiary with leading/trailing whitespace"""
        data = {
            'name': '  John Doe  ',
            'phone': '  +1234567890  '
        }
        response = self.client.post(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        # Name should be stripped
        assert response.data['data']['name'] == 'John Doe'
        assert response.data['data']['phone'] == '+1234567890'
    
    def test_create_beneficiary_with_special_characters_in_name(self):
        """Test creating beneficiary with special characters in name"""
        data = {
            'name': 'John-Paul O\'Connor Jr.',
            'phone': '+1234567890'
        }
        response = self.client.post(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['name'] == "John-Paul O'Connor Jr."
    
    def test_create_beneficiary_max_length_name(self):
        """Test creating beneficiary with maximum length name"""
        long_name = 'A' * 255
        data = {
            'name': long_name,
            'phone': '+1234567890'
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_create_beneficiary_min_length_name(self):
        """Test creating beneficiary with minimum length name"""
        data = {
            'name': 'Jo',
            'phone': '+1234567890'
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestBeneficiaryModel:
    """Test suite for beneficiary model"""
    
    def setup_method(self):
        """Set up test data before each test"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_beneficiary(self):
        """Test creating a beneficiary object"""
        beneficiary = Beneficiary.objects.create(
            user=self.user,
            name='John Doe',
            phone='+1234567890'
        )
        
        assert beneficiary.user == self.user
        assert beneficiary.name == 'John Doe'
        assert beneficiary.phone == '+1234567890'
        assert beneficiary.created_at is not None
        assert beneficiary.updated_at is not None
    
    def test_beneficiary_str_method(self):
        """Test the __str__ method of Beneficiary"""
        beneficiary = Beneficiary.objects.create(
            user=self.user,
            name='John Doe',
            phone='+1234567890'
        )
        
        expected_str = f"{beneficiary.name} ({beneficiary.phone})"
        assert str(beneficiary) == expected_str
    
    def test_beneficiary_unique_together_constraint(self):
        """Test unique_together constraint on (user, phone)"""
        Beneficiary.objects.create(
            user=self.user,
            name='John Doe',
            phone='+1234567890'
        )
        
        # Try to create duplicate
        with pytest.raises(Exception):  # IntegrityError
            Beneficiary.objects.create(
                user=self.user,
                name='Jane Doe',
                phone='+1234567890'  # Same phone
            )
    
    def test_beneficiary_to_dict_method(self):
        """Test the to_dict method"""
        beneficiary = Beneficiary.objects.create(
            user=self.user,
            name='John Doe',
            phone='+1234567890'
        )
        
        beneficiary_dict = beneficiary.to_dict()
        
        assert beneficiary_dict['id'] == beneficiary.id
        assert beneficiary_dict['user_id'] == self.user.id
        assert beneficiary_dict['name'] == 'John Doe'
        assert beneficiary_dict['phone'] == '+1234567890'
        assert 'created_at' in beneficiary_dict
        assert 'updated_at' in beneficiary_dict


