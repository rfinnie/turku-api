from django.contrib import admin
from api.models import Machine, Source


class SourceInline(admin.StackedInline):
    model = Source


class MachineAdmin(admin.ModelAdmin):
    list_display = ('machine_uuid', 'unit_name', 'date_checked_in')
    inlines = [SourceInline]


class SourceAdmin(admin.ModelAdmin):
    pass


admin.site.register(Machine, MachineAdmin)
admin.site.register(Source, SourceAdmin)
