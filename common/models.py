import datetime
from typing import List
from dataclasses import dataclass, field
import uuid
from decimal import Decimal

from util import dictWithoutKey

# todo: find a framework way of doing data validation, don't forget type annotations are not binding

@dataclass
class Tenancy:
    checkInDate: datetime
    checkOutDate: datetime

@dataclass
class CritterTenancy(Tenancy):
    petName:str
    email:str

@dataclass
class Critter:
    petName: str
    email: str
    species: str
    birthDate: datetime
    breed: str = ""
    neutered: bool = False
    vaccines: dict[str, bool] = field(default_factory=lambda: {})
    tenancy: Tenancy = None
    pastTenancy: List[Tenancy] = field(default_factory=lambda: [])


@dataclass
class User:
    email: str
    name: str
    birthDate: datetime
    associatedAnimals: List[str]
    password: str


class ClientUser(User):
    associatedAnimals: List[Critter]


@dataclass
class BillingProduct:
    petName: str
    tenancy: Tenancy


def isNumber(source: str):
    withoutDot = source.replace(".", "", 1)
    withoutMinus = withoutDot.replace("-", "", 1)
    return withoutMinus.isnumeric()


@dataclass
class BillingDescriptor:
    total: Decimal
    valuePerDay: Decimal
    taxesIncluded: List[Decimal]

    def __post_init__(self):
        errors: List[str] = []
        if not isNumber(self.total):
            errors.append("BillingDescriptor.total: is not a numeric value")
        if not isNumber(self.valuePerDay):
            errors.append("BillingDescriptor.valuePerDay: is not a numeric value")
        if any(not isNumber(tax) for tax in self.taxesIncluded):
            errors.append(
                "BillingDescriptor.taxesIncluded: one or more items is not a numeric value"
            )
        if any(errors):
            raise Exception(";\n".join(errors))


@dataclass
class BillingStatement:
    email: str
    billingId: str = field(init=False)
    timestamp: Decimal
    billed: List[BillingProduct]
    descriptor: BillingDescriptor

    @classmethod
    def fromDict(cls, d: dict):
        billedDictList = d.get("billed")
        billedProductList: List[BillingProduct] = []
        [
            billedProductList.append(BillingProduct(**billedDict))
            for billedDict in billedDictList
        ]
        descriptorDict = d.get("descriptor")
        descriptor: BillingDescriptor = (
            BillingDescriptor(**descriptorDict) if descriptorDict is not None else None
        )
        sanitizedSourceDict = dictWithoutKey(d, "descriptor", "billed")
        return BillingStatement(
            **sanitizedSourceDict, billed=billedProductList, descriptor=descriptor
        )

    def __post_init__(self):
        self.billingId = str(uuid.uuid4())

    # def toDict(self):
    #     tbd