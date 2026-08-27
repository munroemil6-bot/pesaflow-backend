"""Optional persisted dashboard snapshots and administrator audit events."""

from django.conf import settings
from django.db import models


class DashboardSnapshot(models.Model):
    key = models.CharField(max_length=100, unique=True)
    data = models.JSONField()
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-generated_at",)

    def __str__(self):
        return self.key


class DashboardLog(models.Model):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="dashboard_logs")
    action = models.CharField(max_length=100)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("action", "created_at"))]

    def __str__(self):
        return f"{self.action} at {self.created_at:%Y-%m-%d %H:%M}"
