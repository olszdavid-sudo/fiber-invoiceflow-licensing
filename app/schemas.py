from pydantic import BaseModel, Field


class LicenseRequest(BaseModel):
    app_id: str = Field(min_length=1, max_length=120)
    app_version: str = Field(default="")
    machine_id: str = Field(min_length=16, max_length=128)
    hostname: str = Field(default="")
    license_key: str = Field(default="")


class DeactivateRequest(BaseModel):
    app_id: str = Field(min_length=1, max_length=120)
    machine_id: str = Field(min_length=16, max_length=128)
    license_key: str = Field(min_length=8, max_length=256)


class AdminGenerateRequest(BaseModel):
    admin_api_key: str = Field(min_length=8, max_length=256)
    app_id: str = Field(default="fiber_invoiceflow", min_length=1, max_length=120)
    max_devices: int = Field(default=1, ge=1, le=100)
    validity_days: int = Field(default=365, ge=1, le=3650)
