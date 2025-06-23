from pydantic import BaseModel


class CertificateInput(BaseModel):
    id: str
    recipient: str
    course: str

class RevokeInput(BaseModel):
    id: str