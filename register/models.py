from django.db import models
from django.contrib.auth.models import User
from myApp import models as myApp_models

#from myApp.views import
# Create your models here.

class Address(models.Model):
    id = models.BigAutoField(primary_key=True)  #For expansion.
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    address_str = models.CharField(max_length=200, null=True)
    number = models.CharField(max_length=10, null=True)
    street = models.CharField(max_length=100, null=True)
    sub_district  = models.CharField(max_length=100, null=True)
    district   = models.CharField(max_length=100, null=True)
    province   = models.CharField(max_length=100, null=True)
    postal_code   = models.IntegerField(null=True)


    def __str__(self):
        return '{} {} {} {} {} {} {} {}'.format(self.user.username, self.address_str, self.number,
                                 self.street, self.sub_district, self.district,
                                 self.province, self.postal_code)

    def get_address_str(self):
        return 'Address : {}  Number:{} Street: {} Sub district : {} District : {} Province : {} Postal code :{}'.format(self.number, self.address_str,
                                 self.street, self.sub_district, self.district,
                                 self.province, self.postal_code)