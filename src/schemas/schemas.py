from pydantic import BaseModel
from typing import List, Optional


class Campaign(BaseModel):
    __tablename__ = 'campaigns'
    id : Optional[int] = None
    name : str
    message : str
    schedule :bool = False
    date : Optional[str] = ''
    hour : Optional[str] = ''
    base_id : int 
    status : str = '0'
    disparos_de : int = 0
    disparos_ate : int = 0
    clicks : int = 0
    public_token_id : Optional[str] = 15
    user_id : int 
    disparos_efetuados : Optional[int] = 0

    class Config:
        from_attributes = True



class Links(BaseModel):
    id:Optional[int] = None
    url_original:str
    url_encurtada:str
    id_campaign: int 

    class Config:
        from_attributes = True



