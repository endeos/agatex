# -*- coding: utf-8 -*-

from odoo import _, api, models
import logging

_logger = logging.getLogger(__name__)



class ResGroups(models.Model):
    _inherit = "res.groups"

    def custom_group_add_user(self, user, group_external_id):
        group_id = self.env.ref(group_external_id)
        try:
            if group_id:
                group_id.write({"users": [(4, user.id)]})
        except:
            _logger.error(f"Could not set user {user.name} to group widh xml id {group_external_id}")

    @api.model
    def set_default_admin_custom_groups(self):
        """ search user with email odoo@endeos.com and set custom groups
        """
        user_id = self.env["res.users"].search(["|", ("email", "=", "odoo@endeos.com"), ("id", "=", 2)], limit=1)
        if not user_id:
            _logger.error(f"No user found with email odoo@endeos.com. Try to set permissions with SuperUser.")
            return False

        self.custom_group_add_user(user_id, "endeos_custom_groups_permissions.endeos_group_view_cost_price")
        self.custom_group_add_user(user_id, "endeos_custom_groups_permissions.endeos_group_inventory_settings_menu")
        self.custom_group_add_user(user_id, "endeos_custom_groups_permissions.endeos_group_general_settings_menu")
        self.custom_group_add_user(user_id, "endeos_custom_groups_permissions.endeos_group_apps_menu")

        return True