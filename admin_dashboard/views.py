"""Administrator-only monitoring and reporting endpoints."""

from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .serializers import AdminTransactionSerializer, AdminUserSerializer, AdminWalletSerializer, AnalyticsSerializer, DashboardSummarySerializer, RevenueSerializer
from . import services


def _pagination(request):
    return {"page": request.query_params.get("page", 1), "page_size": request.query_params.get("page_size", 10)}


def _paginated_response(result, serializer):
    return Response({"results": serializer(result["items"], many=True).data, **{key: value for key, value in result.items() if key != "items"}})


@api_view(["GET"])
@permission_classes([IsAdminUser])
def dashboard_summary(request):
    return Response(DashboardSummarySerializer(services.get_dashboard_summary()).data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def user_list(request):
    active = request.query_params.get("is_active")
    filters = {"is_active": {"true": True, "false": False}.get(active.lower()) if active else None,
               "start_date": request.query_params.get("start_date"), "end_date": request.query_params.get("end_date")}
    return _paginated_response(services.get_user_list(filters, request.query_params.get("search"), _pagination(request)), AdminUserSerializer)


@api_view(["GET", "PATCH"])
@permission_classes([IsAdminUser])
def user_detail(request, user_id):
    try:
        result = services.get_user_detail(user_id)
    except services.User.DoesNotExist:
        raise Http404

    if request.method == "PATCH":
        is_active = request.data.get("is_active")
        if is_active is None:
            return Response({"detail": "is_active is required."}, status=400)

        user = result["user"]
        user.is_active = bool(is_active)
        user.save(update_fields=["is_active", "updated_at"])
        return Response({"user": AdminUserSerializer(user).data, "wallet": AdminWalletSerializer(result["wallet"]).data if result["wallet"] else None,
                         "transaction_count": result["transaction_count"], "total_sent": result["total_sent"], "total_received": result["total_received"]})

    return Response({"user": AdminUserSerializer(result["user"]).data, "wallet": AdminWalletSerializer(result["wallet"]).data if result["wallet"] else None,
                     "transaction_count": result["transaction_count"], "total_sent": result["total_sent"], "total_received": result["total_received"]})


@api_view(["GET"])
@permission_classes([IsAdminUser])
def transaction_list(request):
    keys = ("status", "start_date", "end_date", "min_amount", "max_amount")
    return _paginated_response(services.get_all_transactions({key: request.query_params.get(key) for key in keys}, _pagination(request)), AdminTransactionSerializer)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def wallet_list(request):
    return _paginated_response(services.get_all_wallets(request.query_params.get("sort", "-balance"), _pagination(request)), AdminWalletSerializer)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def analytics(request):
    try:
        result = services.get_analytics(request.query_params.get("period", "daily"))
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=400)
    return Response(AnalyticsSerializer(result).data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def revenue_report(request):
    return Response(RevenueSerializer(services.get_revenue_report(request.query_params.get("start_date"), request.query_params.get("end_date"))).data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def top_users(request):
    try:
        users = services.get_top_users(request.query_params.get("limit", 10))
    except ValueError:
        return Response({"detail": "limit must be an integer."}, status=400)
    return Response(AdminUserSerializer(users, many=True).data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def payment_statistics(request):
    return Response(services.get_payment_statistics())
