from django.db import models

# Create your models here.

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, mobile, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, mobile, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, full_name, mobile, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'mobile']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    


import uuid
from django.db import models

# Shared abstract base model with UUID primary key
from django.db import models
from django.utils.crypto import get_random_string

def generate_short_id():
    import random, string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

class BaseModel(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=4,
        editable=False,
        unique=True,
        default=generate_short_id
    )

    class Meta:
        abstract = True




# Operational & Location Masters

class ProcessingCenter(BaseModel):
    name = models.CharField(max_length=150)
    address = models.TextField()
    manager_name = models.CharField(max_length=100, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)

class Store(BaseModel):
    name = models.CharField(max_length=150)
    address = models.TextField()
    store_type = models.CharField(max_length=100, choices=[('Retail', 'Retail'), ('Warehouse', 'Warehouse')])
    is_active = models.BooleanField(default=True)

class PeelingCenter(BaseModel):
    name = models.CharField(max_length=150)
    address = models.TextField()
    equipment_type = models.CharField(max_length=100, blank=True)
    capacity_per_day_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class PurchasingSpot(BaseModel):
    location_name = models.CharField(max_length=150)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    gps_coordinates = models.CharField(max_length=100, blank=True)

#  Personnel Masters

class PurchasingSupervisor(BaseModel):
    name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True)
    joining_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class PurchasingAgent(BaseModel):
    name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=15, unique=True)
    supervisor = models.ForeignKey(PurchasingSupervisor, on_delete=models.SET_NULL, null=True, blank=True)
    region = models.CharField(max_length=100, blank=True)

# Item & Product Masters

class ItemCategory(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

class Item(BaseModel):
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    unit = models.CharField(max_length=20, choices=[('Kg', 'Kg'), ('Gram', 'Gram'), ('Piece', 'Piece')])
    is_perishable = models.BooleanField(default=False)

class ItemGrade(BaseModel):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    method_name = models.CharField(max_length=100)
    logic_description = models.TextField()

class FreezingCategory(BaseModel):
    name = models.CharField(max_length=100)
    storage_space = models.DecimalField(max_digits=10, decimal_places=2)

class PackingUnit(BaseModel):
    unit = models.CharField(max_length=50)
    calculation_logic = models.TextField()

class GlazePercentage(BaseModel):
    method = models.TextField()
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)

class ItemBrand(BaseModel):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

#  Financial & Expense Masters

class Tenant(BaseModel):
    company_name = models.CharField(max_length=150)
    address = models.TextField()
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

class FreezingTariff(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    tariff_type = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    rate_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

class PeelingCharge(BaseModel):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='kg')

class PurchaseOverhead(BaseModel):
    category_name = models.CharField(max_length=100)
    other_expenses = models.DecimalField(max_digits=10, decimal_places=2)

class PeelingOverhead(BaseModel):
    category_name = models.CharField(max_length=100)
    other_expenses = models.DecimalField(max_digits=10, decimal_places=2)

class ProcessingOverhead(BaseModel):
    category_name = models.CharField(max_length=100)
    freezing_expense = models.DecimalField(max_digits=10, decimal_places=2)
    other_expense = models.DecimalField(max_digits=10, decimal_places=2)

class ShipmentOverhead(BaseModel):
    documentation_charges = models.DecimalField(max_digits=10, decimal_places=2)
    logistics_expense = models.DecimalField(max_digits=10, decimal_places=2)
    vehicle_rent = models.DecimalField(max_digits=10, decimal_places=2)
    buyers_agent_commission = models.DecimalField(max_digits=10, decimal_places=2)
    other_expense = models.DecimalField(max_digits=10, decimal_places=2)
