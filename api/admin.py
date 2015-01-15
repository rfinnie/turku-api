from django.contrib import admin
from api.models import Machine, Source, Auth, Storage


class MachineAdmin(admin.ModelAdmin):
    list_display = ('id', 'unit_name', 'date_checked_in')


admin.site.register(Auth)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Source)
admin.site.register(Storage)
