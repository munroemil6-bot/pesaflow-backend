"""
Beneficiaries Views

Owner: Naomi
Responsibility: API endpoints for beneficiary operations

API Endpoints to implement:
# TODO: GET /api/beneficiaries/
#   - Returns: list of all beneficiaries for current user
#   - Pagination: supported
#   - Status: 200 OK

# TODO: POST /api/beneficiaries/
#   - Accepts: name, phone
#   - Returns: created beneficiary
#   - Status: 201 CREATED or 400 BAD REQUEST

# TODO: GET /api/beneficiaries/<id>/
#   - Returns: specific beneficiary details
#   - Status: 200 OK or 404 NOT FOUND

# TODO: PUT /api/beneficiaries/<id>/
#   - Accepts: name, phone
#   - Returns: updated beneficiary
#   - Status: 200 OK or 404 NOT FOUND or 400 BAD REQUEST

# TODO: DELETE /api/beneficiaries/<id>/
#   - Deletes beneficiary
#   - Status: 204 NO CONTENT or 404 NOT FOUND
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# TODO: @api_view(['GET', 'POST']) beneficiary_list view
# TODO: @api_view(['GET', 'PUT', 'DELETE']) beneficiary_detail view
