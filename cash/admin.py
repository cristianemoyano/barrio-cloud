from django.contrib import admin
from cash.models import Entry, EntryType


class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('detail',)}


class EntryTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Entry, EntryAdmin)
admin.site.register(EntryType, EntryTypeAdmin)
