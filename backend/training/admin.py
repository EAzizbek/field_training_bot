from io import BytesIO

import openpyxl
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse

# Register your models here.

from .models import User,DailySession,TrackingLocation

admin.site.register(User)
class TrackingLocationInline(admin.TabularInline):
    model = TrackingLocation
    extra = 0

@admin.register(DailySession)
class DailySessionAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "is_started", "is_finished", "map_link")
    actions = ["export_as_excel"]

    def map_link(self, obj):
        if obj.map_file:
            return format_html(f'<a href="{obj.map_file.url}" target="_blank">🗺 Xarita</a>')
        return "❌"
    map_link.short_description = "Xarita"

    def export_as_excel(self, request, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Hisobot"

        ws.append(["Ism Familiya", "Boshlanish", "Selfie URL", "Xarita URL", "Yakunlangan"])

        for s in queryset.order_by("date", "user__full_name"):
            ws.append([
                s.user.full_name,
                s.started_at.strftime("%Y-%m-%d %H:%M") if s.started_at else "",
                request.build_absolute_uri(s.selfie.url) if s.selfie else "",
                request.build_absolute_uri(s.map_file.url) if s.map_file else "",
                s.finished_at.strftime("%Y-%m-%d %H:%M") if s.finished_at else ""
            ])

        # ❗ YANGI — save_virtual_workbook o‘rniga
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = 'attachment; filename="daily_sessions.xlsx"'
        return response

    export_as_excel.short_description = "⬇️ Excel'ga yuklab olish"

@admin.register(TrackingLocation)
class TrackingLocationAdmin(admin.ModelAdmin):
    list_display = ("session", "lat", "lon", "timestamp")