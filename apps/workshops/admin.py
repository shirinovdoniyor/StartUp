from django.contrib import admin

from .models import (
    LocationImage,
    LocationService,
    Workshop,
    WorkshopLocation,
    WorkingHour,
)


class LocationInline(admin.TabularInline):
    model = WorkshopLocation
    extra = 0
    show_change_link = True


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "is_verified", "premium", "created_at")
    list_filter = ("status", "is_verified", "premium")
    search_fields = ("name", "slug")
    inlines = [LocationInline]


@admin.register(WorkshopLocation)
class WorkshopLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "workshop", "is_main", "status", "rating", "review_count")
    list_filter = ("status", "is_main")
    search_fields = ("name", "address")


admin.site.register([WorkingHour, LocationImage, LocationService])
