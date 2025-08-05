from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from adminapp.models import CustomUser  # adjust if CustomUser is elsewhere
from django.forms import inlineformset_factory
from .models import *


class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'mobile', 'email', 'address', 'profile_picture', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    
# Operational & Location
class ProcessingCenterForm(forms.ModelForm):
    class Meta:
        model = ProcessingCenter
        fields = '__all__'

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = '__all__'

class ShedForm(forms.ModelForm):
    class Meta:
        model = Shed
        fields = ['name', 'code', 'address', 'contact_number', 'capacity_per_day_kg']

class ShedItemForm(forms.ModelForm):
    class Meta:
        model = ShedItem
        fields = ['item', 'item_type', 'amount', 'unit']

ShedItemFormSet = inlineformset_factory(
    parent_model=Shed,
    model=ShedItem,
    form=ShedItemForm,
    extra=1,
    can_delete=True
)

class PurchasingSpotForm(forms.ModelForm):
    class Meta:
        model = PurchasingSpot
        fields = '__all__'

# Personnel
class PurchasingSupervisorForm(forms.ModelForm):
    class Meta:
        model = PurchasingSupervisor
        fields = '__all__'

class PurchasingAgentForm(forms.ModelForm):
    class Meta:
        model = PurchasingAgent
        fields = '__all__'

# Item & Product
class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        fields = '__all__'

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'

class ItemGradeForm(forms.ModelForm):
    class Meta:
        model = ItemGrade
        fields = '__all__'

class FreezingCategoryForm(forms.ModelForm):
    class Meta:
        model = FreezingCategory
        fields = '__all__'

class PackingUnitForm(forms.ModelForm):
    class Meta:
        model = PackingUnit
        fields = '__all__'

class GlazePercentageForm(forms.ModelForm):
    class Meta:
        model = GlazePercentage
        fields = '__all__'

class ItemBrandForm(forms.ModelForm):
    class Meta:
        model = ItemBrand
        fields = '__all__'

class ItemTypeForm(forms.ModelForm):
    class Meta:
        model = ItemType
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['item'].queryset = Item.objects.filter(is_peeling=True)

# Financial & Expense
class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = '__all__'

from django import forms
from .models import  Item, ItemType

class PurchaseOverheadForm(forms.ModelForm):
    class Meta:
        model = PurchaseOverhead
        fields = '__all__'

class PeelingOverheadForm(forms.ModelForm):
    class Meta:
        model = PeelingOverhead
        fields = '__all__'

class ProcessingOverheadForm(forms.ModelForm):
    class Meta:
        model = ProcessingOverhead
        fields = '__all__'

class ShipmentOverheadForm(forms.ModelForm):
    class Meta:
        model = ShipmentOverhead
        fields = '__all__'

# forms for create a Purchase Entry 

from django import forms
from django.forms import inlineformset_factory
from .models import SpotPurchase, SpotPurchaseItem, SpotPurchaseExpense

class SpotPurchaseForm(forms.ModelForm):
    class Meta:
        model = SpotPurchase
        fields = ['date', 'voucher_number', 'spot', 'supervisor', 'agent']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'voucher_number': forms.TextInput(attrs={'class': 'form-control'}),
            'spot': forms.Select(attrs={'class': 'form-control'}),
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
            'agent': forms.Select(attrs={'class': 'form-control'}),
        }

class SpotPurchaseItemForm(forms.ModelForm):
    class Meta:
        model = SpotPurchaseItem
        fields = ['item', 'quantity', 'rate', 'boxes']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'boxes': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

SpotPurchaseItemFormSet = inlineformset_factory(
    SpotPurchase,
    SpotPurchaseItem,
    form=SpotPurchaseItemForm,
    extra=1,
    can_delete=True
)

class SpotPurchaseExpenseForm(forms.ModelForm):
    class Meta:
        model = SpotPurchaseExpense
        fields = [
            'ice_expense',
            'vehicle_rent',
            'loading_and_unloading',
            'peeling_charge',
            'other_expense'
        ]
        widgets = {
            'ice_expense': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vehicle_rent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'loading_and_unloading': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'peeling_charge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_expense': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

# local purchase forms

class LocalPurchaseForm(forms.ModelForm):
    class Meta:
        model = LocalPurchase
        fields = ['date', 'voucher_number', 'party_name']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'voucher_number': forms.TextInput(attrs={'class': 'form-control'}),
            'party_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LocalPurchaseItemForm(forms.ModelForm):
    class Meta:
        model = LocalPurchaseItem
        exclude = ['purchase', 'amount']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': '0.01'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control rate-input', 'step': '0.01'}),
        }

LocalPurchaseItemFormSet = inlineformset_factory(
    LocalPurchase,
    LocalPurchaseItem,
    form=LocalPurchaseItemForm,
    extra=1,
    can_delete=True
)


# Peeling Shed Supply Form

# forms.py

from django import forms
from .models import PeelingShedSupply
from django.forms import inlineformset_factory
from django import forms
from .models import PeelingShedSupply

class PeelingShedSupplyForm(forms.ModelForm):
    class Meta:
        model = PeelingShedSupply
        fields = [
            'date',
            'voucher_number',
            'shed',
            'vehicle_number',
            'spot_purchase_date',
            'spot_purchase',
            'spot_purchase_item',
            'SpotPurchase_total_boxes',
            'SpotPurchase_quantity',
            'SpotPurchase_average_box_weight',
            'boxes_received_shed',
            'quantity_received_shed',
            'peeling_type',
            'amount',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'spot_purchase_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'ajax-date',  # ✅ Add class here
                'id': 'id_spot_purchase_date'  # Make sure this matches the JS selector
            }),
        }



