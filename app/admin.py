from django.contrib import admin
from app import models


@admin.register(models.Server)
class ServerAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Peer)
class PeerAdmin(admin.ModelAdmin):
    readonly_fields = ("address",)
    change_form_template = "custom_admin/change_form.html"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "server":
            if db_field.blank:
                kwargs["queryset"] = models.Server.objects.filter(name="123")

            if db_field.model:
                print("ok")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
