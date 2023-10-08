
import datetime
from typing import List
from dataclasses import dataclass


@dataclass
class User:
	email:str
	name:str
	birthDate:datetime
	associatedAnimals:List[str]
	password:str
