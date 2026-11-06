# A managed identity plus exactly the roles it is given.
#
# Generic on purpose: callers pass the role map, so envs/dev/main.tf shows the
# API's read-only set next to the job's write set. That contrast is the security
# story, so it belongs at the call site rather than buried here.

resource "azurerm_user_assigned_identity" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

resource "azurerm_role_assignment" "this" {
  for_each = var.role_assignments

  scope                = each.value.scope
  role_definition_name = each.value.role
  principal_id         = azurerm_user_assigned_identity.this.principal_id
}
