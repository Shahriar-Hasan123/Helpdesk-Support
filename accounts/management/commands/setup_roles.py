from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from tickets.models import Ticket, TicketComment, TicketAttachment, Department, AgentProfile
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Create default roles (Student, SupportAgent, Manager) and assign permissions."

    def handle(self, *args, **options):
        student_group, _ = Group.objects.get_or_create(name="Student")
        agent_group, _ = Group.objects.get_or_create(name="SupportAgent")
        manager_group, _ = Group.objects.get_or_create(name="Manager")

        # Ticket permissions
        ticket_ct = ContentType.objects.get_for_model(Ticket)
        comment_ct = ContentType.objects.get_for_model(TicketComment)
        attach_ct = ContentType.objects.get_for_model(TicketAttachment)
        dept_ct = ContentType.objects.get_for_model(Department)
        agent_ct = ContentType.objects.get_for_model(AgentProfile)

        def perms(ct):
            return Permission.objects.filter(content_type=ct)

        # Student: can add ticket, add comment, add attachment, view own via code (not perms)
        student_group.permissions.set(
            list(Permission.objects.filter(codename__in=[
                "add_ticket", "add_ticketcomment", "add_ticketattachment",
                "view_ticket", "view_ticketcomment", "view_ticketattachment"
            ]))
        )

        # Agent: view/change tickets + comments/attachments (access limited by code)
        agent_group.permissions.set(
            list(Permission.objects.filter(codename__in=[
                "view_ticket", "change_ticket",
                "view_ticketcomment", "add_ticketcomment",
                "view_ticketattachment", "add_ticketattachment"
            ]))
        )

        # Manager: full control of ticket system (+ user changes)
        manager_group.permissions.set(
            list(Permission.objects.filter(codename__in=[
                "add_ticket", "view_ticket", "change_ticket", "delete_ticket",
                "add_ticketcomment", "view_ticketcomment", "change_ticketcomment", "delete_ticketcomment",
                "add_ticketattachment", "view_ticketattachment", "delete_ticketattachment",
                "add_department", "view_department", "change_department", "delete_department",
                "add_agentprofile", "view_agentprofile", "change_agentprofile", "delete_agentprofile",
                "change_user", "view_user"
            ]))
        )

        self.stdout.write(self.style.SUCCESS("Roles + permissions created/updated."))
