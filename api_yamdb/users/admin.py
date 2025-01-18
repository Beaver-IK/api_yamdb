from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username',
                    'email',
                    'first_name',
                    'last_name',
                    'is_staff',
                    'role',
                    'is_active',
                    )
    list_filter = ('is_staff', 'is_active', 'role')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name',
                                                'last_name',
                                                'email',
                                                'bio',
                                                'role',
                                                )
                                     }
         ),
        ('Доступы', {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)