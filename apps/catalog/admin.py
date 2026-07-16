from django.contrib import admin

from .models import Category, Service, ServiceAlias


class ServiceAliasInline(admin.TabularInline):
    model = ServiceAlias
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "slug")
    list_filter = ("category",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ServiceAliasInline]
