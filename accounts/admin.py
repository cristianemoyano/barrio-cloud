from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile, Lote


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_email')
    list_select_related = ('profile', )

    def get_email(self, instance):
        return instance.profile.email
    get_email.short_description = 'Email'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class LoteAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Lote, LoteAdmin)
