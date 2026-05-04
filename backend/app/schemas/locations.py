from pydantic import BaseModel, ConfigDict
from typing import List


class KecamatanResponse(BaseModel):
    id: int
    kecamatan_name: str
    model_config = ConfigDict(from_attributes=True)


class KotaResponse(BaseModel):
    id: int
    kota_name: str
    model_config = ConfigDict(from_attributes=True)


class ProvinsiResponse(BaseModel):
    id: int
    provinsi_name: str
    model_config = ConfigDict(from_attributes=True)
