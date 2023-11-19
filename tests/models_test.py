import unittest
from common import models
from datetime import datetime

class Models(unittest.TestCase):
    def test_critterTenancyAndTenancyAreCompatible(self):
        tenancy = models.Tenancy(datetime.now(), datetime.now())
        critterTenancy = models.CritterTenancy(petName="TestPet", **tenancy.__dict__)
        self.assertEqual(tenancy.tenancyId, critterTenancy.tenancyId)
        self.assertEqual(tenancy.checkInDate, critterTenancy.checkInDate)
        self.assertEqual(tenancy.checkOutDate, critterTenancy.checkOutDate)

if __name__ == "__main__":
    unittest.main()
