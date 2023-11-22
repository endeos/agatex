from typing import Annotated

from fastapi import APIRouter
from pydantic import BaseModel

from odoo import api, fields, models
from odoo.api import Environment

from odoo.addons.fastapi.dependencies import odoo_env

class FastapiEndpoint(models.Model):

    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("invoice", "Invoice Manager")], ondelete={"invoice": "cascade"}
    )

    def _get_fastapi_routers(self):
        if self.app == "invoice":
            return [invoice_api_router]
        return super()._get_fastapi_routers()


invoice_api_router = APIRouter()

class PartnerInfo(BaseModel):
    name: str
    email: str

@invoice_api_router.get("/agatex/partners", response_model=list[PartnerInfo])
def get_partners(env: Annotated[Environment, Depends(odoo_env)]) -> list[PartnerInfo]:
    return [
        PartnerInfo(name=partner.name, email=partner.email)
        for partner in env["res.partner"].search([])
    ]