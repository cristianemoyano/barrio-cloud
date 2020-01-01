from django.contrib import admin
from cash.models import Entry


class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('detail',)}


admin.site.register(Entry, EntryAdmin)
