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
    code=models.CharField(null=True,blank=True,unique=True,max_length=15)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.code}"

class Store(BaseModel):
    name = models.CharField(max_length=150)
    address = models.TextField()
    contact_number = models.CharField(max_length=15, blank=True)
    code=models.CharField(null=True,blank=True,unique=True)
    store_type = models.CharField(max_length=100, choices=[('Retail', 'Retail'), ('Warehouse', 'Warehouse')])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.code}"



class PurchasingSpot(BaseModel):
    location_name = models.CharField(max_length=150)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    code = models.CharField(null=True,blank=True,unique=True)

    def __str__(self):
        return f"{self.location_name} - {self.code}"
    
#  Personnel Masters

class PurchasingSupervisor(BaseModel):
    name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True)
    joining_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.mobile}"

class PurchasingAgent(BaseModel):
    purchasingSpot = models.ForeignKey(PurchasingSpot, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=15, unique=True)
    code = models.CharField(null=True,blank=True,unique=True)

    def __str__(self):
        return f"{self.name} - {self.code}"

# Item & Product Masters

class ItemCategory(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    code = models.CharField(null=True,blank=True, unique=True)

    def __str__(self):
        return f"{self.name}"

class Item(BaseModel):
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    is_peeling = models.BooleanField(default=False)
    peeling_method = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name}  - {self.code}"

class Species(BaseModel):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.name}"

class ItemGrade(BaseModel):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    grade = models.CharField(max_length=100)
    date = models.DateField(auto_created=True, auto_now=True) 

    def __str__(self):
        return f"{self.species} - {self.grade}"
    
class FreezingCategory(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(null=True,blank=True,unique=True)
    tariff = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

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
        return f"{self.unit_code}"

class GlazePercentage(BaseModel):
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.percentage}%"

class ItemBrand(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

class ItemType(BaseModel):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


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


# settings
class Settings(BaseModel):
    dollar_rate_to_inr = models.DecimalField(max_digits=10, decimal_places=2)
    vehicle_rent_km = models.DecimalField(max_digits=10, decimal_places=2)

# shed creation

class Shed(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    capacity_per_day_kg = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class ShedItem(models.Model):
    shed = models.ForeignKey(Shed, on_delete=models.CASCADE, related_name='shed_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, limit_choices_to={'is_peeling': True})
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='kg')

    def __str__(self):
        return f'{self.shed.name} - {self.item_type}'

# Spot Purchase Models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SpotPurchase(BaseModel):
    date = models.DateField()
    voucher_number = models.CharField(max_length=20, unique=True)
    spot = models.ForeignKey('PurchasingSpot', on_delete=models.CASCADE)
    supervisor = models.ForeignKey('PurchasingSupervisor', on_delete=models.CASCADE)
    agent = models.ForeignKey('PurchasingAgent', on_delete=models.CASCADE)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Voucher {self.voucher_number} on {self.date} at {self.spot.location_name}"

    def update_totals(self):
        items = self.items.all()
        self.total_amount = sum(item.amount for item in items)
        self.total_quantity = sum(item.quantity for item in items)
        self.total_items = items.count()
        self.save()

class SpotPurchaseItem(BaseModel):
    purchase = models.ForeignKey(SpotPurchase, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    boxes = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}kg @ {self.rate}"

class SpotPurchaseExpense(BaseModel):
    purchase = models.OneToOneField(SpotPurchase, on_delete=models.CASCADE, related_name='expense')
    ice_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vehicle_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loading_and_unloading = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    peeling_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_expense = (
            self.ice_expense +
            self.vehicle_rent +
            self.loading_and_unloading +
            self.peeling_charge +
            self.other_expense
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Expense for {self.purchase.voucher_number} at {self.purchase.spot.location_name}"

# local purchase models

class LocalPurchase(BaseModel):
    date = models.DateField()
    voucher_number = models.CharField(max_length=20, unique=True)
    party_name = models.CharField(max_length=150)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Voucher {self.voucher_number} on {self.date} from {self.party_name}"
    
class LocalPurchaseItem(BaseModel):
    purchase = models.ForeignKey(LocalPurchase, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    grade = models.ForeignKey(ItemGrade, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}kg @ {self.rate}"
    

# Peeling Shead Supply Entry

class PeelingShedSupply(models.Model):
    date = models.DateField()
    voucher_number = models.CharField(max_length=50)
    shed = models.ForeignKey('shed', on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=50)
    spot_purchase_date = models.DateField(null=True, blank=True)
    spot_purchase = models.ForeignKey('SpotPurchase', on_delete=models.CASCADE)
    spot_purchase_item = models.ForeignKey('SpotPurchaseItem', on_delete=models.CASCADE)
    SpotPurchase_total_boxes = models.PositiveIntegerField()
    SpotPurchase_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    SpotPurchase_average_box_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    boxes_received_shed = models.PositiveIntegerField(default=0)
    quantity_received_shed = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def __str__(self):
        return f"{self.voucher_number} - {self.date}"

class PeelingShedPeelingType(models.Model):
    supply = models.ForeignKey(PeelingShedSupply, on_delete=models.CASCADE, related_name='peeling_types')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    item_type = models.ForeignKey(ItemType, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)


# freezing entry by spot purchase 

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class FreezingEntrySpot(BaseModel):
    freezing_date = models.DateField()
    voucher_number = models.CharField(max_length=50)

    spot_purchase_date = models.DateField(null=True, blank=True)
    spot = models.ForeignKey('SpotPurchase', on_delete=models.CASCADE, related_name='freezing_entries')
    spot_agent = models.ForeignKey('PurchasingAgent', on_delete=models.CASCADE, related_name='freezing_entries')
    spot_supervisor = models.ForeignKey('PurchasingSupervisor', on_delete=models.CASCADE, related_name='freezing_entries')
    total_yield_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    total_usd = models.DecimalField(max_digits=10, decimal_places=2)
    total_inr = models.DecimalField(max_digits=10, decimal_places=2)
    total_slab = models.DecimalField(max_digits=10, decimal_places=2)
    total_c_s = models.DecimalField(max_digits=10, decimal_places=2)
    total_kg = models.DecimalField(max_digits=10, decimal_places=2)

    FREEZING_STATUS_CHOICES = [
        ('complete', 'Complete'),
        ('incomplete', 'Incomplete'),
    ]
    freezing_status = models.CharField(max_length=50, choices=FREEZING_STATUS_CHOICES , default='incomplete')

    def __str__(self):
        return f"Freezing Entry - {self.freezing_date} - {self.spot}"

class FreezingEntrySpotItem(BaseModel):
    freezing_entry = models.ForeignKey(FreezingEntrySpot, on_delete=models.CASCADE, related_name='items')

    processing_center = models.ForeignKey('ProcessingCenter', on_delete=models.CASCADE, null=True)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, null=True )
    shed = models.ForeignKey('shed', on_delete=models.CASCADE, related_name='freezing_shed_items')
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='freezing_item_entries')
    unit = models.ForeignKey('PackingUnit', on_delete=models.CASCADE)
    glaze = models.ForeignKey('GlazePercentage', on_delete=models.CASCADE)
    freezing_category = models.ForeignKey('FreezingCategory', on_delete=models.CASCADE)
    brand = models.ForeignKey('ItemBrand', on_delete=models.CASCADE)
    species = models.ForeignKey('Species', on_delete=models.CASCADE)
    peeling_type = models.ForeignKey('ItemType', on_delete=models.CASCADE)
    grade = models.ForeignKey('ItemGrade', on_delete=models.CASCADE)
    slab_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    c_s_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    kg = models.DecimalField(max_digits=10, decimal_places=2)
    usd_rate_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    usd_rate_item = models.DecimalField(max_digits=10, decimal_places=2)
    usd_rate_item_to_inr = models.DecimalField(max_digits=10, decimal_places=2)
    yield_percentage = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item} - {self.kg} KG"



    def __str__(self):
        return f"{self.item} - {self.kg} KG"


from django.db import models

class FreezingEntryLocal(BaseModel):
    freezing_date = models.DateField()
    voucher_number = models.CharField(max_length=50)

    local_purchase_date = models.DateField(null=True, blank=True)
    party = models.ForeignKey('LocalPurchase', on_delete=models.CASCADE)
    total_yield_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_inr = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_slab = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_c_s = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    FREEZING_STATUS_CHOICES = [
        ('complete', 'Complete'),
        ('incomplete', 'Incomplete'),
    ]
    freezing_status = models.CharField(
        max_length=50,
        choices=FREEZING_STATUS_CHOICES,
        default='incomplete'
    )

    def __str__(self):
        return f"Freezing Entry Local - {self.freezing_date} - {self.voucher_number}"

class FreezingEntryLocalItem(BaseModel):
    freezing_entry = models.ForeignKey(
        FreezingEntryLocal,
        on_delete=models.CASCADE,
        related_name='items'
    )

    processing_center = models.ForeignKey('ProcessingCenter', on_delete=models.CASCADE, null=True, blank=True)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    unit = models.ForeignKey('PackingUnit', on_delete=models.CASCADE)
    glaze = models.ForeignKey('GlazePercentage', on_delete=models.CASCADE)
    freezing_category = models.ForeignKey('FreezingCategory', on_delete=models.CASCADE)
    brand = models.ForeignKey('ItemBrand', on_delete=models.CASCADE)
    species = models.ForeignKey('Species', on_delete=models.CASCADE)
    peeling_type = models.ForeignKey('ItemType', on_delete=models.CASCADE)
    grade = models.ForeignKey('ItemGrade', on_delete=models.CASCADE)

    slab_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    c_s_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usd_rate_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usd_rate_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usd_rate_item_to_inr = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    yield_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.item} - {self.kg} KG"


# PRE SHIPMENT WORK OUT model

from django.db import models

class PreShipmentWorkOut(BaseModel):
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    unit = models.ForeignKey('PackingUnit', on_delete=models.CASCADE)
    glaze = models.ForeignKey('GlazePercentage', on_delete=models.CASCADE)
    category = models.ForeignKey('FreezingCategory', on_delete=models.CASCADE)
    brand = models.ForeignKey('ItemBrand', on_delete=models.CASCADE)

    def __str__(self):
        return f"Workout for {self.item}"

class PreShipmentWorkOutItem(BaseModel):
    workout = models.ForeignKey(PreShipmentWorkOut, on_delete=models.CASCADE, related_name="items")
    species = models.ForeignKey('Species', on_delete=models.CASCADE)
    peeling_type = models.ForeignKey('ItemType', on_delete=models.CASCADE)
    grade = models.ForeignKey('ItemGrade', on_delete=models.CASCADE)
    cartons = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # we want rate
    usd_rate_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usd_rate_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usd_rate_item_to_inr = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # we get rate
    usd_rate_per_kg_get = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usd_rate_item_get = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usd_rate_item_to_inr_get = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    loss = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)

    @property
    def profit_amount(self):
        return max(self.usd_rate_item_get - self.usd_rate_item, 0)

    @property
    def loss_amount(self):
        return max(self.usd_rate_item - self.usd_rate_item_get, 0)

    def __str__(self):
        return f"{self.species} - {self.grade} ({self.cartons} cartons)"




