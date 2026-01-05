from django.contrib import admin
from .models import Department, StudentProfile, AgentProfile, Ticket, TicketAttachment, TicketComment

admin.site.register(Department)
admin.site.register(StudentProfile)
admin.site.register(AgentProfile)
admin.site.register(Ticket)
admin.site.register(TicketAttachment)
admin.site.register(TicketComment)
