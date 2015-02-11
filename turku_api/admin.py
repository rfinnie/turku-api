from django.contrib import admin
from turku_api.models import Machine, Source, Auth, Storage


class AuthAdmin(admin.ModelAdmin):
    list_display = ('secret', 'secret_type', 'comment', 'active')


class MachineAdmin(admin.ModelAdmin):
    list_display = ('unit_name', 'uuid', 'environment_name', 'service_name', 'date_checked_in', 'active')


class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'machine', 'date_last_backed_up', 'frequency', 'date_next_backup', 'active')


class StorageAdmin(admin.ModelAdmin):
    list_display = ('name', 'ssh_ping_host', 'ssh_ping_user', 'active')


admin.site.register(Auth, AuthAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Storage, StorageAdmin)
