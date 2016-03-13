from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from guardian.shortcuts import assign_perm

DEFAULT_USER_GROUP_MODEL_PERMISSION = {
    "api.add_user", "api.change_user", "api.delete_user",
    "api.add_band", "api.change_band", "api.delete_band",
    "api.add_instrument", "api.change_instrument", "api.delete_instrument",
    "api.add_member", "api.change_member", "api.delete_member",
    "api.add_composition", "api.change_composition", "api.delete_composition",
    "api.add_track", "api.change_track", "api.delete_track",
}

GROUP_NAME_PERMISSION_NAMES_MAP = {
    settings.DEFAULT_USER_GROUP: DEFAULT_USER_GROUP_MODEL_PERMISSION
}


def create_groups():
    group_permission_names_map = dict()
    for group_name in GROUP_NAME_PERMISSION_NAMES_MAP:
        group, _ = Group.objects.get_or_create(name=group_name)
        group_permission_names_map[group] = GROUP_NAME_PERMISSION_NAMES_MAP[group_name]
    return group_permission_names_map


def add_permissions_to_groups(group_permission_names_map):
    for group in group_permission_names_map:
        permission_names = group_permission_names_map[group]
        for permission_name in permission_names:
            assign_perm(permission_name, group)


@transaction.atomic
def renovate_permissions():
    group_permission_names_map = create_groups()
    add_permissions_to_groups(group_permission_names_map)
