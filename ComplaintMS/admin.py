from django.contrib import admin
from .models import Profile, Complaint, Grievance

class CAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'subject',
        'type_of_complaint',
        'description',
        'time','status'
    )

admin.site.register(Profile)
admin.site.register(Complaint, CAdmin)
admin.site.register(Grievance)
