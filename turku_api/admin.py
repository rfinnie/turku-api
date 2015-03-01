from django import forms
from django.contrib import admin
from turku_api.models import Machine, Source, Auth, Storage


class MachineAdminForm(forms.ModelForm):
    class Meta:
        model = Machine

    def __init__(self, *args, **kwargs):
        super(MachineAdminForm, self).__init__(*args, **kwargs)
        self.fields['auth'].queryset = Auth.objects.filter(secret_type='machine_reg')


class StorageAdminForm(forms.ModelForm):
    class Meta:
        model = Storage

    def __init__(self, *args, **kwargs):
        super(StorageAdminForm, self).__init__(*args, **kwargs)
        self.fields['auth'].queryset = Auth.objects.filter(secret_type='storage_reg')


class AuthAdmin(admin.ModelAdmin):
    list_display = ('name', 'secret', 'secret_type', 'active')


class MachineAdmin(admin.ModelAdmin):
    form = MachineAdminForm
    list_display = ('unit_name', 'uuid', 'storage', 'environment_name', 'service_name', 'date_checked_in', 'active')
    list_display_links = ('unit_name', 'uuid')
    list_filter = ('date_checked_in',)


class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'machine', 'date_last_backed_up', 'date_next_backup', 'published', 'active')
    list_display_links = ('name', 'path')
    list_filter = ('date_last_backed_up', 'date_next_backup')


class StorageAdmin(admin.ModelAdmin):
    form = StorageAdminForm
    list_display = ('name', 'ssh_ping_host', 'ssh_ping_user', 'date_checked_in', 'active')


admin.site.register(Auth, AuthAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Storage, StorageAdmin)
