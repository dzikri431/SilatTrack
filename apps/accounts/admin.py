from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from apps.members.models import AnggotaProfile, PelatihProfile


class AnggotaProfileInline(admin.StackedInline):
    model = AnggotaProfile
    can_delete = False
    verbose_name = "Profil Anggota / Pesilat"
    verbose_name_plural = "Profil Anggota / Pesilat"
    fk_name = 'user'
    extra = 0


class PelatihProfileInline(admin.StackedInline):
    model = PelatihProfile
    can_delete = False
    verbose_name = "Profil Pelatih"
    verbose_name_plural = "Profil Pelatih"
    fk_name = 'user'
    extra = 0


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('username',)
    inlines = [AnggotaProfileInline, PelatihProfileInline]
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informasi Tambahan Eskul', {
            'fields': ('role', 'phone_number', 'avatar'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informasi Tambahan Eskul', {
            'fields': ('role', 'phone_number', 'avatar'),
        }),
    )

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        if obj.role == User.Role.ANGGOTA:
            return [AnggotaProfileInline]
        elif obj.role == User.Role.PELATIH:
            return [PelatihProfileInline]
        return [AnggotaProfileInline, PelatihProfileInline]
