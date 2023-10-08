
import datetime
from typing import List
from dataclasses import dataclass


@dataclass
class User:
	id:str
	name:str
	accoundName:str
	birthDate:datetime
	associatedAnimals:List[str]
	password:str
