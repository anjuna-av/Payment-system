from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Client
from .models import Project
from .models import Invoice

# Register your models here.


class ClientAdmin(UserAdmin):
    """ Overriding user adminto add additional fields"""
    readonly_fields = ('idencode',)
    ordering = ('-id',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'updated_email',
                       'dob', 'phone', 'address', 'type', 'idencode')
        }),
        (('Internal values'), {
            'fields': ('terms_accepted', 'email_verified'),
        }),
        (('Important dates'), {'fields': ('last_login',)}),
    )
    list_display = (
        'idencode', 'first_name', 'last_name', 'email', 'email_verified'
    )


admin.site.register(Client, ClientAdmin)
admin.site.register(Project)
admin.site.register(Invoice)
