from django import forms
from django.contrib import admin
from turku_api.models import Machine, Source, Auth, Storage, BackupLog
from django.utils.html import format_html
from django.core.urlresolvers import reverse


def get_admin_change_link(obj, name=None):
    url = reverse(
        'admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name),
        args=(obj.id,)
    )
    if not name:
        name = obj
    return format_html(
        '<a href="%s">%s</a>' % (url, unicode(name))
    )


class ReadonlyTabularInline(admin.TabularInline):
    can_delete = False
    extra = 0
    editable_fields = []

    def __init__(self, *args, **kwargs):
        self.readonly_fields = self.fields
        super(ReadonlyTabularInline, self).__init__(*args, **kwargs)

    def has_add_permission(self, request):
        return False


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
    ordering = ('name',)


class MachineInline(ReadonlyTabularInline):
    def unit_name_link(self, obj):
        return get_admin_change_link(obj, obj.unit_name)

    unit_name_link.allow_tags = True
    unit_name_link.short_description = 'unit name'

    model = Machine
    fields = ('unit_name_link', 'uuid', 'environment_name', 'service_name', 'date_checked_in', 'healthy')


class SourceInline(ReadonlyTabularInline):
    def name_link(self, obj):
        return get_admin_change_link(obj, obj.name)

    name_link.allow_tags = True
    name_link.short_description = 'name'

    model = Source
    fields = ('name_link', 'path', 'date_last_backed_up', 'date_next_backup', 'healthy')


class BackupLogInline(ReadonlyTabularInline):
    def date_link(self, obj):
        return get_admin_change_link(obj, obj.date)

    date_link.allow_tags = True
    date_link.short_description = 'date'

    model = BackupLog
    fields = ('date_link', 'storage', 'success', 'date_begin', 'date_end')
    max_num = 5


class MachineAdmin(admin.ModelAdmin):
    def storage_link(self, obj):
        return get_admin_change_link(obj.storage)

    storage_link.allow_tags = True
    storage_link.admin_order_field = 'storage__name'
    storage_link.short_description = 'storage'

    form = MachineAdminForm
    inlines = (SourceInline,)
    list_display = ('unit_name', 'uuid', 'storage_link', 'environment_name', 'service_name', 'date_checked_in', 'healthy')
    list_display_links = ('unit_name',)
    list_filter = ('date_checked_in',)
    ordering = ('unit_name',)


class SourceAdmin(admin.ModelAdmin):
    def machine_link(self, obj):
        return get_admin_change_link(obj.machine)

    machine_link.allow_tags = True
    machine_link.admin_order_field = 'machine__unit_name'
    machine_link.short_description = 'machine'

    # max_num=5 isn't working for some reason, making this unweildy
    #inlines = (BackupLogInline,)
    list_display = ('name', 'machine_link', 'path', 'date_last_backed_up', 'date_next_backup', 'healthy')
    list_display_links = ('name',)
    list_filter = ('date_last_backed_up', 'date_next_backup')
    ordering = ('machine__unit_name', 'name')


class BackupLogAdmin(admin.ModelAdmin):
    def source_link(self, obj):
        return get_admin_change_link(obj.source)

    source_link.allow_tags = True
    source_link.admin_order_field = 'source__name'
    source_link.short_description = 'source'

    list_display = ('date', 'source_link', 'success', 'date_begin', 'date_end')
    list_display_links = ('date',)
    ordering = ('-date',)

class StorageAdmin(admin.ModelAdmin):
    form = StorageAdminForm
    inlines = (MachineInline,)
    list_display = ('name', 'ssh_ping_host', 'ssh_ping_user', 'date_checked_in', 'healthy')
    ordering = ('name',)


admin.site.register(Auth, AuthAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Storage, StorageAdmin)
admin.site.register(BackupLog, BackupLogAdmin)
