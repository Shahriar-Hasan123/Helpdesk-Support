from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, Permission, User
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        return render(request, "accounts/login.html", {"error": "Invalid credentials"})
    return render(request, "accounts/login.html")

@login_required
def user_logout(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    # Simple role-based redirect/summary
    if request.user.groups.filter(name="Manager").exists():
        return redirect("manager_ticket_list")
    if request.user.groups.filter(name="SupportAgent").exists():
        return redirect("agent_ticket_list")
    # default: Student
    return redirect("student_ticket_list")


@login_required
@permission_required("auth.change_user", raise_exception=True)
def access_rights(request):
    if not request.user.groups.filter(name="Manager").exists():
        return HttpResponseForbidden("Managers only.")

    # Only these roles are managed here (simple)
    role_names = ["Student", "SupportAgent", "Manager"]
    roles = Group.objects.filter(name__in=role_names).order_by("name")
    users = User.objects.all().order_by("username")

    # Helper: get a user's current role (first match)
    def get_user_role(u):
        user_roles = u.groups.filter(name__in=role_names).values_list("name", flat=True)
        return list(user_roles)

    selected_user = None
    selected_user_roles = []

    # If user chosen by GET (so page can show current role)
    selected_user_id = request.GET.get("user_id")
    if selected_user_id:
        selected_user = User.objects.filter(id=selected_user_id).first()
        if selected_user:
            selected_user_roles = get_user_role(selected_user)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        role_name = request.POST.get("role_name")  # new field name

        u = User.objects.get(id=user_id)
        new_role = Group.objects.get(name=role_name)

        # ✅ Remove all old roles first (so user has ONLY ONE role)
        u.groups.remove(*roles)

        # ✅ Add new role
        u.groups.add(new_role)

        messages.success(request, f"Role updated: {u.username} → {new_role.name}")
        return redirect(f"/access-rights/?user_id={u.id}")

    return render(request, "accounts/access_rights.html", {
        "users": users,
        "roles": roles,
        "selected_user": selected_user,
        "selected_user_roles": selected_user_roles,
    })