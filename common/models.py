import datetime
from typing import List
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    email: str
    name: str
    birthDate: datetime
    associatedAnimals: List[str]
    password: str


@dataclass
class Tenancy:
    checkInDate: datetime
    checkOutDate: datetime


@dataclass
class Critter:
    petName: str
    ownerEmail: str
    species: str
    birthDate: datetime
    breed: str = ""
    neutered: bool = False
    vaccines: dict[str, bool] = field(default_factory=lambda: {})
    tenancy: Tenancy = None
    pastTenancy: List[Tenancy] = field(default_factory=lambda: [])


@dataclass
class BillingProduct:
    petName:str
    tenancy:List[Tenancy]

@dataclass
class BillingDescriptor:
    total:float
    taxesIncluded:List[float]

@dataclass
class BillingStatement:
    userEmail:str
    billingId:int
    billed:List[BillingProduct]
    descriptor:BillingDescriptor
