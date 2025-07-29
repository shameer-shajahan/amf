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
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('owner','Owner')
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
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
    contact_number = models.CharField(max_length=15, blank=True)
    code=models.CharField(null=True,blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Store(BaseModel):
    name = models.CharField(max_length=150)
    address = models.TextField()
    contact_number = models.CharField(max_length=15, blank=True)
    code=models.CharField(null=True,blank=True)
    store_type = models.CharField(max_length=100, choices=[('Retail', 'Retail'), ('Warehouse', 'Warehouse')])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Shed(BaseModel):
    name = models.CharField(max_length=150)
    address = models.TextField()
    contact_number = models.CharField(max_length=15, blank=True)
    code=models.CharField(null=True,blank=True)    
    capacity_per_day_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

class PurchasingSpot(BaseModel):
    location_name = models.CharField(max_length=150)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    code = models.CharField(null=True,blank=True)

#  Personnel Masters

class PurchasingSupervisor(BaseModel):
    name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True)
    joining_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class PurchasingAgent(BaseModel):
    purchasingSpot = models.ForeignKey(PurchasingSpot, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=15, unique=True)
    code = models.CharField(null=True,blank=True)

# Item & Product Masters

class ItemCategory(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    code = models.CharField(null=True,blank=True)

    def __str__(self):
        return self.name

class Item(BaseModel):
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=50, unique=True)
    is_peeling = models.BooleanField(default=False)
    peeling_method = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class ItemGrade(BaseModel):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    grade = models.CharField(max_length=100)

class FreezingCategory(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(null=True,blank=True)
    tariff = models.PositiveIntegerField(null=True, blank=True)
    def __str__(self):
        return self.name

class PackingUnit(BaseModel):

    unit_code = models.CharField(max_length=50, unique=True)  # e.g., '10X0.350GRAM'
    basic_unit = models.CharField(max_length=20, choices=[
        ('KG', 'Kilogram'),
        ('GRAM', 'Gram'),
        ('LTR', 'Liter'),
        # Add more as needed
    ], default='KG')
    precision = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., 10.00
    factor = models.DecimalField(max_digits=10, decimal_places=5)     # e.g., 0.35
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.unit_code} ({self.description})"

class GlazePercentage(BaseModel):
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

class ItemBrand(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

#  Financial & Expense Masters

class Tenant(BaseModel):
    company_name = models.CharField(max_length=150)
    address = models.TextField(blank= True, null=True)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField(blank= True, null=True)
    phone = models.CharField(max_length=15,blank= True, null=True)
    freezing_tariff = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.company_name

class PeelingChargeManager(models.Manager):
    def peeling_items_only(self):
        return self.get_queryset().filter(item__is_peeling=True)

class PeelingCharge(BaseModel):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='peeling_for_item')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='kg')

    objects = PeelingChargeManager()

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
