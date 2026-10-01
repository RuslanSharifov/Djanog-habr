from functools import wraps

from django.contrib.auth.models import Group
from django.shortcuts import redirect


def is_super_admin(user):
    return (
        user.is_authenticated
        and user.is_superuser
    )


def is_admin(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name='Admin').exists()
        )
    )


def super_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_super_admin(request.user):
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_admin(request.user):
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return wrapper


def get_admin_group():
    group, _ = Group.objects.get_or_create(
        name='Admin'
    )

    return group