from .. import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship


class Port(BaseModel):
    __tablename__ = 'port'
    __repr_attrs__ = ['port_number']
    id = Column(Integer, primary_key=True)
    port_number = Column(Integer, unique=False)
    proto = Column(String, unique=False)
    status = Column(String, unique=False)
    services = relationship('Service',
                            backref='port')
    ip_address_id = Column(Integer, ForeignKey('ipaddress.id'))
    urls = relationship('Url', backref='port')