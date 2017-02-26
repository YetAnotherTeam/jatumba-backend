from django.conf import settings
from django.contrib.auth.models import Group
from django.db import transaction

from guardian.shortcuts import assign_perm

from api.models import Composition, Member

DEFAULT_USER_GROUP_MODEL_PERMISSION = {
    'api.add_user', 'api.change_user', 'api.delete_user',
    'api.add_band', 'api.change_band', 'api.delete_band',
    'api.add_instrument', 'api.change_instrument', 'api.delete_instrument',
    'api.add_member', 'api.change_member', 'api.delete_member',
    'api.add_composition', 'api.change_composition', 'api.delete_composition',
    'api.add_track', 'api.change_track', 'api.delete_track',
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


def renovate_band_composition_permissions():
    for composition in Composition.objects.select_related('band__group'):
        for perm in ('api.change_composition', 'api.delete_composition'):
            assign_perm(perm, composition.band.group, composition)


def renovate_user_groups():
    for member in Member.objects.select_related('band__group', 'user'):
        member.band.group.user_set.add(member.user)


@transaction.atomic
def renovate_permissions():
    group_permission_names_map = create_groups()
    add_permissions_to_groups(group_permission_names_map)
    renovate_band_composition_permissions()
    renovate_user_groups()
