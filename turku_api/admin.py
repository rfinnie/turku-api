from django.contrib import admin
from turku_api.models import Machine, Source, Auth, Storage


class AuthAdmin(admin.ModelAdmin):
    list_display = ('name', 'secret', 'secret_type', 'active')


class MachineAdmin(admin.ModelAdmin):
    list_display = ('unit_name', 'uuid', 'storage', 'environment_name', 'service_name', 'date_checked_in', 'active')
    list_display_links = ('unit_name', 'uuid')
    list_filter = ('date_checked_in',)


class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'machine', 'date_last_backed_up', 'date_next_backup', 'active')
    list_display_links = ('name', 'path')
    list_filter = ('date_last_backed_up', 'date_next_backup')

class StorageAdmin(admin.ModelAdmin):
    list_display = ('name', 'ssh_ping_host', 'ssh_ping_user', 'active')


admin.site.register(Auth, AuthAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Storage, StorageAdmin)
