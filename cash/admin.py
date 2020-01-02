from django.contrib import admin
from cash.models import Entry, EntryType, UserEntry


class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('detail',)}


class EntryTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class UserEntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('detail',)}


admin.site.register(Entry, EntryAdmin)
admin.site.register(EntryType, EntryTypeAdmin)
admin.site.register(UserEntry, UserEntryAdmin)
