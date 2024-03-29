# SPDX-PackageSummary: Turku backups - API server
# SPDX-FileCopyrightText: Copyright (C) 2015-2020 Canonical Ltd.
# SPDX-FileCopyrightText: Copyright (C) 2015-2021 Ryan Finnie <ryan@finnie.org>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from django import forms
from django.contrib import admin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone
from django.utils.html import format_html

try:
    from django.urls import reverse  # 1.10+
except ImportError:
    from django.core.urlresolvers import reverse  # pre-1.10

from turku_api.models import Auth, BackupLog, FilterSet, Machine, Source, Storage


def get_admin_change_link(obj, name=None):
    url = reverse(
        "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
        args=(obj.id,),
    )
    if not name:
        name = obj
    return format_html('<a href="{}">{}</a>'.format(url, name))


def human_si(v, begin=0):
    p = ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi")
    i = begin
    while v >= 1024.0:
        v = int(v / 10.24) / 100.0
        i += 1
    return "%g %sB" % (v, p[i])


def human_time(t):
    if t is None:
        return None
    if abs(timezone.localtime() - t) >= datetime.timedelta(days=1):
        return t
    else:
        return naturaltime(t)


class CustomModelAdmin(admin.ModelAdmin):
    change_form_template = "admin/custom_change_form.html"

    def render_change_form(self, request, context, *args, **kwargs):
        # Build a list of related children objects and their counts
        # so they may be linked to in the admin interface
        related_links = []
        if "object_id" in context and hasattr(self.model._meta, "get_fields"):
            related_objs = [
                f
                for f in self.model._meta.get_fields()
                if (f.one_to_many or f.one_to_one) and f.auto_created and not f.concrete
            ]
            for obj in related_objs:
                count = obj.related_model.objects.filter(
                    **{obj.field.name: context["object_id"]}
                ).count()
                if count > 0:
                    related_links.append((obj, obj.related_model._meta, count))
        context.update({"related_links": related_links})

        return super(CustomModelAdmin, self).render_change_form(
            request, context, *args, **kwargs
        )


class MachineAdminForm(forms.ModelForm):
    secret_hash = ReadOnlyPasswordHashField()

    class Meta:
        model = Machine
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(MachineAdminForm, self).__init__(*args, **kwargs)
        self.fields["auth"].queryset = Auth.objects.filter(secret_type="machine_reg")


class StorageAdminForm(forms.ModelForm):
    secret_hash = ReadOnlyPasswordHashField()

    class Meta:
        model = Storage
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(StorageAdminForm, self).__init__(*args, **kwargs)
        self.fields["auth"].queryset = Auth.objects.filter(secret_type="storage_reg")


class AuthAdminForm(forms.ModelForm):
    secret_hash = ReadOnlyPasswordHashField()

    class Meta:
        model = Auth
        fields = "__all__"


class AuthAdmin(CustomModelAdmin):
    form = AuthAdminForm
    list_display = ("name", "secret_type", "date_added", "active")
    ordering = ("name",)
    search_fields = ("name", "comment")


class ExcludeListFilter(admin.SimpleListFilter):
    def __init__(self, *args, **kwargs):
        if not self.title:
            self.title = self.parameter_name
        self.parameter_name += "__exclude"
        super(ExcludeListFilter, self).__init__(*args, **kwargs)

    def has_output(self):
        if self.value():
            return True
        return super(ExcludeListFilter, self).has_output()

    def lookups(self, request, model_admin):
        return

    def queryset(self, request, queryset):
        return queryset.exclude(**{self.parameter_name[:-9]: self.value()})


class NameExcludeListFilter(ExcludeListFilter):
    parameter_name = "name"


class MachineAdmin(CustomModelAdmin):
    def storage_link(self, obj):
        return get_admin_change_link(obj.storage)

    storage_link.allow_tags = True
    storage_link.admin_order_field = "storage__name"
    storage_link.short_description = "storage"

    def date_checked_in_human(self, obj):
        return human_time(obj.date_checked_in)

    date_checked_in_human.admin_order_field = "date_checked_in"
    date_checked_in_human.short_description = "date checked in"

    form = MachineAdminForm
    list_display = (
        "unit_name",
        "uuid",
        "storage_link",
        "environment_name",
        "service_name",
        "date_checked_in_human",
        "published",
        "active",
        "healthy",
    )
    list_display_links = ("unit_name",)
    list_filter = ("date_checked_in", "storage", "active", "published")
    ordering = ("unit_name",)
    search_fields = ("unit_name", "uuid", "environment_name", "service_name", "comment")


class SourceAdmin(CustomModelAdmin):
    def date_last_backed_up_human(self, obj):
        return human_time(obj.date_last_backed_up)

    date_last_backed_up_human.admin_order_field = "date_last_backed_up"
    date_last_backed_up_human.short_description = "date last backed up"

    def date_next_backup_human(self, obj):
        return human_time(obj.date_next_backup)

    date_next_backup_human.admin_order_field = "date_next_backup"
    date_next_backup_human.short_description = "date next backup"

    def machine_link(self, obj):
        return get_admin_change_link(obj.machine)

    machine_link.allow_tags = True
    machine_link.admin_order_field = "machine__unit_name"
    machine_link.short_description = "machine"

    list_display = (
        "name",
        "machine_link",
        "path",
        "date_last_backed_up_human",
        "date_next_backup_human",
        "published",
        "active",
        "healthy",
    )
    list_display_links = ("name",)
    list_filter = (
        "date_last_backed_up",
        "date_next_backup",
        "active",
        "published",
        NameExcludeListFilter,
    )
    ordering = ("machine__unit_name", "name")
    search_fields = ("name", "comment", "path")


class BackupLogAdmin(CustomModelAdmin):
    def source_link(self, obj):
        return get_admin_change_link(obj.source)

    source_link.allow_tags = True
    source_link.admin_order_field = "source__name"
    source_link.short_description = "source"

    def duration(self, obj):
        if not (obj.date_end and obj.date_begin):
            return None
        d = obj.date_end - obj.date_begin
        return d - datetime.timedelta(microseconds=d.microseconds)

    duration.admin_order_field = "date_end"
    duration.short_description = "duration"

    def storage_link(self, obj):
        if not obj.storage:
            return None
        return get_admin_change_link(obj.storage)

    storage_link.allow_tags = True
    storage_link.admin_order_field = "storage__name"
    storage_link.short_description = "storage"

    def date_human(self, obj):
        return human_time(obj.date)

    date_human.admin_order_field = "date"
    date_human.short_description = "date"

    list_display = (
        "date_human",
        "source_link",
        "success",
        "snapshot",
        "storage_link",
        "duration",
    )
    list_display_links = ("date_human",)
    list_filter = ("date", "success")
    ordering = ("-date",)


class FilterSetAdmin(CustomModelAdmin):
    list_display = ("name", "date_added", "active")
    ordering = ("name",)
    search_fields = ("name", "comment")


class StorageAdmin(CustomModelAdmin):
    def space_total_human(self, obj):
        return human_si(obj.space_total, 2)

    space_total_human.admin_order_field = "space_total"
    space_total_human.short_description = "space total"

    def space_available_human(self, obj):
        return human_si(obj.space_available, 2)

    space_available_human.admin_order_field = "space_available"
    space_available_human.short_description = "space available"

    def date_checked_in_human(self, obj):
        return human_time(obj.date_checked_in)

    date_checked_in_human.admin_order_field = "date_checked_in"
    date_checked_in_human.short_description = "date checked in"

    form = StorageAdminForm
    list_display = (
        "name",
        "ssh_ping_host",
        "ssh_ping_user",
        "date_checked_in_human",
        "space_total_human",
        "space_available_human",
        "published",
        "active",
        "healthy",
    )
    ordering = ("name",)
    search_fields = ("name", "comment", "ssh_ping_host")


admin.site.register(Auth, AuthAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Storage, StorageAdmin)
admin.site.register(BackupLog, BackupLogAdmin)
admin.site.register(FilterSet, FilterSetAdmin)
