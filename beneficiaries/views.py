

from rest_framework import status, generics, permissions, pagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, NotFound
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import Beneficiary
from .serializers import (
    BeneficiarySerializer,
    CreateBeneficiarySerializer,
    UpdateBeneficiarySerializer,
    BeneficiaryListSerializer,
    BeneficiaryDetailSerializer
)
from .services import (
    create_beneficiary,
    get_user_beneficiaries,
    get_beneficiary,
    update_beneficiary,
    delete_beneficiary
)


class CustomPagination(pagination.PageNumberPagination):
    """
    Custom pagination for beneficiary list.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'


class BeneficiaryListCreateView(generics.ListCreateAPIView):
    """
    GET /api/beneficiaries/ - List all beneficiaries for current user
    POST /api/beneficiaries/ - Create a new beneficiary
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        """Return beneficiaries for the current user."""
        return get_user_beneficiaries(self.request.user)
    
    def get_serializer_class(self):
        """Use different serializers for GET and POST."""
        if self.request.method == 'POST':
            return CreateBeneficiarySerializer
        return BeneficiaryListSerializer
    
    def get_serializer_context(self):
        """Add user to serializer context for creation."""
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
    
    def perform_create(self, serializer):
        """Create a new beneficiary using the service layer."""
        try:
           
            name = serializer.validated_data.get('name')
            phone = serializer.validated_data.get('phone')
            
           
            beneficiary = create_beneficiary(
                user=self.request.user,
                name=name,
                phone=phone
            )
            
           
            serializer.instance = beneficiary
            
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        except IntegrityError as e:
            raise serializers.ValidationError(str(e))
    
    def list(self, request, *args, **kwargs):
        """Override list to add custom response structure."""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """Override create to use service layer."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            
            response_serializer = BeneficiarySerializer(serializer.instance)
            
            return Response(
                {
                    'message': 'Beneficiary created successfully.',
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )
            
        except serializers.ValidationError as e:
            return Response(
                {'error': e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )


class BeneficiaryDetailView(APIView):
    """
    GET /api/beneficiaries/<id> - Get specific beneficiary
    PUT /api/beneficiaries/<id> - Update specific beneficiary
    DELETE /api/beneficiaries/<id> - Delete specific beneficiary
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_beneficiary_object(self, id):
        """Helper method to get and verify beneficiary ownership."""
        try:
            return get_beneficiary(self.request.user, id)
        except Beneficiary.DoesNotExist:
            raise NotFound(detail="Beneficiary not found.")
        except PermissionDenied:
            raise PermissionDenied(detail="You do not have permission to access this beneficiary.")
    
    def get(self, request, id):
        """GET /api/beneficiaries/<id> - Retrieve a beneficiary."""
        try:
            beneficiary = self.get_beneficiary_object(id)
            serializer = BeneficiaryDetailSerializer(beneficiary)
            return Response({
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except NotFound as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
    
    def put(self, request, id):
        """PUT /api/beneficiaries/<id> - Update a beneficiary."""
        try:
           
            beneficiary = self.get_beneficiary_object(id)
            
            
            serializer = UpdateBeneficiarySerializer(
                instance=beneficiary,
                data=request.data,
                partial=False  
            )
            serializer.is_valid(raise_exception=True)
            
            
            update_data = {}
            if 'name' in serializer.validated_data:
                update_data['name'] = serializer.validated_data['name']
            if 'phone' in serializer.validated_data:
                update_data['phone'] = serializer.validated_data['phone']
            
            
            updated_beneficiary = update_beneficiary(
                user=request.user,
                beneficiary_id=id,
                data=update_data
            )
            
    
            response_serializer = BeneficiarySerializer(updated_beneficiary)
            return Response({
                'message': 'Beneficiary updated successfully.',
                'data': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except NotFound as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except (ValidationError, IntegrityError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except serializers.ValidationError as e:
            return Response(
                {'error': e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def patch(self, request, id):
        """PATCH /api/beneficiaries/<id> - Partially update a beneficiary."""
        try:
            
            beneficiary = self.get_beneficiary_object(id)
        
            serializer = UpdateBeneficiarySerializer(
                instance=beneficiary,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
    
            update_data = {}
            if 'name' in serializer.validated_data:
                update_data['name'] = serializer.validated_data['name']
            if 'phone' in serializer.validated_data:
                update_data['phone'] = serializer.validated_data['phone']
            
            if not update_data:
                return Response(
                    {'error': 'No fields to update provided.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use service to update
            updated_beneficiary = update_beneficiary(
                user=request.user,
                beneficiary_id=id,
                data=update_data
            )
            
            # Return response
            response_serializer = BeneficiarySerializer(updated_beneficiary)
            return Response({
                'message': 'Beneficiary updated successfully.',
                'data': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except NotFound as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except (ValidationError, IntegrityError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except serializers.ValidationError as e:
            return Response(
                {'error': e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request, id):
        """DELETE /api/beneficiaries/<id> - Delete a beneficiary."""
        try:
            
            result = delete_beneficiary(request.user, id)
            
            return Response(
                {
                    'message': result['message'],
                    'deleted_beneficiary': result['deleted_beneficiary']
                },
                status=status.HTTP_204_NO_CONTENT
            )
            
        except NotFound as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )