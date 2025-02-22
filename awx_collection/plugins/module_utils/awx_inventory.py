#!/usr/bin/python

from tokenize import group

from .awx_organization import get_resource_access_list
from .export_tools import parse_extra_vars_to_json
from .awx_request import get_awx_resources

def get_inventory_hosts(inventory, awx_auth):
    hosts = get_awx_resources('/api/v2/hosts/?inventory='+str(inventory['id']), previousPageResults=[], awx_auth=awx_auth)
    for host_index, host_item in enumerate(hosts):
        hosts[host_index]['variables'] = parse_extra_vars_to_json(host_item['variables'])
    return hosts

def get_hosts_by_group_id(group_id, awx_auth):
    hosts = get_awx_resources('/api/v2/hosts/?group='+str(group_id), previousPageResults=[], awx_auth=awx_auth)
    hosts_in_group = []
    for host in hosts:
        host_in_group = dict(
            name = host['name']
        )
        hosts_in_group.append(host_in_group)
    return hosts_in_group

def get_inventory_groups(inventory, awx_auth):
    groups = get_awx_resources('/api/v2/groups/?inventory='+str(inventory['id']), previousPageResults=[], awx_auth=awx_auth)
    for group_index, group_item in enumerate(groups):
        groups[group_index]['hosts'] = get_hosts_by_group_id(group_item['id'], awx_auth)
        groups[group_index]['variables'] = parse_extra_vars_to_json(group_item['variables'])
    return groups

def get_inventories_by_organization(organization, existing_members_set, awx_auth):
    exported_inventories=[]
    inventories = get_awx_resources(uri='/api/v2/inventories?organization=' + str(organization['id']), previousPageResults=[], awx_auth=awx_auth)
    for inventory in inventories:
        if inventory['has_inventory_sources']:
            inventory['inventory_sources'] = get_awx_resources('/api/v2/inventory_sources/?inventory='+str(inventory['id']), previousPageResults=[], awx_auth=awx_auth)
            for inventory_source_index, inventory_source in enumerate(inventory['inventory_sources']):
                inventory['inventory_sources'][inventory_source_index]['source_vars'] = parse_extra_vars_to_json(inventory_source['source_vars'])
            inventory['hosts'] = []
            inventory['groups'] = []
        else:
            inventory['inventory_sources'] = []
            inventory['hosts'] = get_inventory_hosts(inventory, awx_auth)
            inventory['groups'] = get_inventory_groups(inventory, awx_auth)
        inventory['variables'] = parse_extra_vars_to_json(inventory['variables'])
        inventory['roles'], existing_members_set = get_resource_access_list('inventories', inventory['id'], existing_members_set, awx_auth)
        exported_inventories.append(inventory)
    return exported_inventories, existing_members_set

