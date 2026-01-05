from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Ticket, TicketAttachment, TicketComment, AgentProfile
from .forms import TicketCreateForm, TicketUpdateManagerForm, TicketUpdateAgentForm, CommentForm

def is_manager(user): return user.groups.filter(name="Manager").exists()
def is_agent(user): return user.groups.filter(name="SupportAgent").exists()
def is_student(user): return user.groups.filter(name="Student").exists() or (not is_manager(user) and not is_agent(user))

@login_required
def student_ticket_list(request):
    tickets = Ticket.objects.filter(student=request.user).order_by("-created_at")
    return render(request, "tickets/student_ticket_list.html", {"tickets": tickets})

@login_required
def ticket_create(request):
    if request.method == "POST":
        form = TicketCreateForm(request.POST)
        files = request.FILES.getlist("attachments")
        if form.is_valid():
            # Validate attachments server-side
            allowed = {"application/pdf", "image/png", "image/jpeg", "image/jpg", "image/webp"}
            max_size = 10 * 1024 * 1024
            attachments_error = None
            for f in files:
                if getattr(f, "content_type", None) not in allowed:
                    attachments_error = "Only PDF and image files are allowed."
                    break
                if f.size > max_size:
                    attachments_error = "Each file must be <= 10MB."
                    break

            if attachments_error:
                return render(request, "tickets/ticket_create.html", {"form": form, "attachments_error": attachments_error})

            ticket = form.save(commit=False)
            ticket.student = request.user
            ticket.save()

            for f in files:
                TicketAttachment.objects.create(ticket=ticket, file=f, uploaded_by=request.user)

            return redirect("ticket_detail", pk=ticket.pk)
    else:
        form = TicketCreateForm()
    return render(request, "tickets/ticket_create.html", {"form": form})

@login_required
def manager_ticket_list(request):
    if not is_manager(request.user):
        return HttpResponseForbidden("Managers only.")
    tickets = Ticket.objects.all().order_by("-created_at")
    return render(request, "tickets/manager_ticket_list.html", {"tickets": tickets})

@login_required
def agent_ticket_list(request):
    if not is_agent(request.user):
        return HttpResponseForbidden("Support agents only.")
    tickets = Ticket.objects.filter(assigned_agent=request.user).order_by("-created_at")
    return render(request, "tickets/agent_ticket_list.html", {"tickets": tickets})

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)

    # Access control:
    if is_manager(request.user):
        pass
    elif is_agent(request.user):
        if ticket.assigned_agent != request.user:
            return HttpResponseForbidden("You can only view your assigned tickets.")
    else:
        # student
        if ticket.student != request.user:
            return HttpResponseForbidden("You can only view your own tickets.")

    # Update forms (manager vs agent)
    manager_form = None
    agent_form = None

    if is_manager(request.user):
        if request.method == "POST" and request.POST.get("form_type") == "manager_update":
            manager_form = TicketUpdateManagerForm(request.POST, instance=ticket)
            if manager_form.is_valid():
                manager_form.save()
                return redirect("ticket_detail", pk=ticket.pk)
        else:
            manager_form = TicketUpdateManagerForm(instance=ticket)

        # For assignment: show only agents of same department (optional)
        # If you want strict department-wise assignment, filter here:
        agents = User.objects.filter(groups__name="SupportAgent")
        manager_form.fields["assigned_agent"].queryset = agents

    elif is_agent(request.user):
        if request.method == "POST" and request.POST.get("form_type") == "agent_update":
            agent_form = TicketUpdateAgentForm(request.POST, instance=ticket)
            if agent_form.is_valid():
                agent_form.save()
                return redirect("ticket_detail", pk=ticket.pk)
        else:
            agent_form = TicketUpdateAgentForm(instance=ticket)

    return render(request, "tickets/ticket_detail.html", {
        "ticket": ticket,
        "manager_form": manager_form,
        "agent_form": agent_form,
    })

@login_required
def ticket_add_comment(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)

    # Access control same as detail
    if is_manager(request.user):
        pass
    elif is_agent(request.user):
        if ticket.assigned_agent != request.user:
            return HttpResponseForbidden("Not your ticket.")
    else:
        if ticket.student != request.user:
            return HttpResponseForbidden("Not your ticket.")

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.ticket = ticket
            c.author = request.user

            # Students cannot create internal comments
            if is_student(request.user):
                c.is_internal = False

            c.save()
    return redirect("ticket_detail", pk=ticket.pk)

@login_required
def manager_ticket_assign(request, pk):
    if not is_manager(request.user):
        return HttpResponseForbidden("Managers only.")

    ticket = get_object_or_404(Ticket, pk=pk)

    if request.method == "POST":
        agent_id = request.POST.get("agent_id")
        agent = User.objects.get(id=agent_id)
        ticket.assigned_agent = agent
        ticket.status = Ticket.Status.IN_PROGRESS
        ticket.save()
        return redirect("ticket_detail", pk=ticket.pk)

    agents = User.objects.filter(groups__name="SupportAgent")
    return render(request, "tickets/manager_assign.html", {"ticket": ticket, "agents": agents})

@login_required
def manager_ticket_duplicate(request, pk):
    if not is_manager(request.user):
        return HttpResponseForbidden("Managers only.")

    ticket = get_object_or_404(Ticket, pk=pk)
    new_ticket = Ticket.objects.create(
        student=ticket.student,
        department=ticket.department,
        subject=f"[Duplicate] {ticket.subject}",
        description=ticket.description,
        status=Ticket.Status.NEW,
    )
    # copy attachments (file copy is not performed, just references - for real copy, you’d need file duplication)
    for att in ticket.attachments.all():
        TicketAttachment.objects.create(ticket=new_ticket, file=att.file, uploaded_by=request.user)

    TicketComment.objects.create(
        ticket=new_ticket,
        author=request.user,
        message=f"Duplicated from {ticket.ticket_id}.",
        is_internal=True
    )

    return redirect("ticket_detail", pk=new_ticket.pk)
