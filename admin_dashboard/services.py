"""Query services powering administrator dashboard endpoints."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from transactions.models import Transaction
from wallet.models import Wallet

User = get_user_model()


def _zero(value):
    return value if value is not None else Decimal("0.00")


def _paginate(queryset, page=1, page_size=10):
    paginator = Paginator(queryset, min(max(int(page_size), 1), 100))
    result = paginator.get_page(page)
    return {"items": result.object_list, "page": result.number, "page_size": paginator.per_page,
            "total_pages": paginator.num_pages, "total_count": paginator.count}


def get_dashboard_summary():
    completed = Transaction.objects.filter(status=Transaction.Status.COMPLETED)
    today = timezone.now().date()
    return {
        "total_users": User.objects.count(), "total_transactions": Transaction.objects.count(),
        "total_transaction_volume": _zero(completed.aggregate(value=Sum("amount"))["value"]),
        "total_fees_collected": _zero(completed.aggregate(value=Sum("fee"))["value"]),
        "active_users_today": User.objects.filter(Q(sent_transactions__created_at__date=today) | Q(received_transactions__created_at__date=today)).distinct().count(),
    }


def get_user_list(filters=None, search=None, pagination=None):
    filters, pagination = filters or {}, pagination or {}
    users = User.objects.all().annotate(wallet_balance=Sum("wallet__balance"))
    if filters.get("is_active") is not None:
        users = users.filter(is_active=filters["is_active"])
    if filters.get("start_date"):
        users = users.filter(created_at__date__gte=filters["start_date"])
    if filters.get("end_date"):
        users = users.filter(created_at__date__lte=filters["end_date"])
    if search:
        users = users.filter(Q(email__icontains=search) | Q(phone__icontains=search) | Q(full_name__icontains=search))
    return _paginate(users.order_by("-created_at"), **pagination)


def get_user_detail(user_id):
    user = User.objects.select_related("wallet").get(pk=user_id)
    transfers = Transaction.objects.filter(Q(sender=user) | Q(recipient=user), status=Transaction.Status.COMPLETED)
    values = transfers.aggregate(total_sent=Sum("amount", filter=Q(sender=user)), total_received=Sum("amount", filter=Q(recipient=user)), transaction_count=Count("id"))
    return {"user": user, "wallet": getattr(user, "wallet", None), "transaction_count": values["transaction_count"],
            "total_sent": _zero(values["total_sent"]), "total_received": _zero(values["total_received"])}


def get_all_transactions(filters=None, pagination=None):
    filters, pagination = filters or {}, pagination or {}
    transfers = Transaction.objects.select_related("sender", "recipient")
    for key, lookup in (("status", "status"), ("start_date", "created_at__date__gte"), ("end_date", "created_at__date__lte"), ("min_amount", "amount__gte"), ("max_amount", "amount__lte")):
        if filters.get(key):
            transfers = transfers.filter(**{lookup: filters[key]})
    return _paginate(transfers.order_by("-created_at"), **pagination)


def get_all_wallets(sort="-balance", pagination=None):
    allowed_sort = sort if sort in {"balance", "-balance", "created_at", "-created_at"} else "-balance"
    return _paginate(Wallet.objects.select_related("user").order_by(allowed_sort), **(pagination or {}))


def get_analytics(period="daily"):
    periods = {"daily": 1, "weekly": 7, "monthly": 30}
    if period not in periods:
        raise ValueError("period must be daily, weekly, or monthly")
    start = timezone.now() - timedelta(days=periods[period])
    transfers = Transaction.objects.filter(created_at__gte=start)
    completed = transfers.filter(status=Transaction.Status.COMPLETED)
    aggregates = completed.aggregate(volume=Sum("amount"), average=Avg("amount"))
    total = transfers.count()
    timeline = list(completed.annotate(date=TruncDate("created_at")).values("date").annotate(transaction_count=Count("id"), volume=Sum("amount")).order_by("date"))
    return {"period": period, "transaction_count": total, "transaction_volume": _zero(aggregates["volume"]),
            "average_transaction_amount": _zero(aggregates["average"]), "user_growth": User.objects.filter(created_at__gte=start).count(),
            "success_rate": (Decimal(completed.count()) * 100 / total).quantize(Decimal("0.01")) if total else Decimal("0.00"), "timeline": timeline}


def get_revenue_report(start_date=None, end_date=None):
    transfers = Transaction.objects.filter(status=Transaction.Status.COMPLETED)
    if start_date:
        transfers = transfers.filter(created_at__date__gte=start_date)
    if end_date:
        transfers = transfers.filter(created_at__date__lte=end_date)
    breakdown = list(transfers.annotate(date=TruncDate("created_at")).values("date").annotate(fees=Sum("fee"), volume=Sum("amount")).order_by("date"))
    return {"total_fees_collected": _zero(transfers.aggregate(value=Sum("fee"))["value"]), "revenue_by_date": breakdown}


def get_top_users(limit=10):
    return User.objects.annotate(transaction_volume=Sum("sent_transactions__amount", filter=Q(sent_transactions__status=Transaction.Status.COMPLETED)), transaction_count=Count("sent_transactions", filter=Q(sent_transactions__status=Transaction.Status.COMPLETED))).order_by("-transaction_volume", "-transaction_count")[:min(max(int(limit), 1), 100)]


def get_payment_statistics():
    transfers = Transaction.objects.all()
    completed, failed, pending = (transfers.filter(status=value).count() for value in (Transaction.Status.COMPLETED, Transaction.Status.FAILED, Transaction.Status.PENDING))
    total = transfers.count()
    return {"completed": completed, "failed": failed, "pending": pending,
            "success_rate": (Decimal(completed) * 100 / total).quantize(Decimal("0.01")) if total else Decimal("0.00")}
