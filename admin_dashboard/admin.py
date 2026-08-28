

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
