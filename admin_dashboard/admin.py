"""
Admin Dashboard Admin

Owner: Nasra
Responsibility: Django admin interface for dashboard (if needed)

Admin configuration to implement (optional):
# TODO: Create custom admin actions for bulk operations
# TODO: Custom admin views if needed
"""

from django.contrib import admin
from .models import DashboardLog, DashboardSnapshot

@admin.register(DashboardSnapshot)
class DashboardSnapshotAdmin(admin.ModelAdmin):
    list_display = ('key', 'generated_at')
    readonly_fields = ('generated_at',)


@admin.register(DashboardLog)
class DashboardLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'admin', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('action', 'admin__email')
    readonly_fields = ('created_at',)
