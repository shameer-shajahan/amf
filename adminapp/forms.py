from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from adminapp.models import CustomUser  # adjust if CustomUser is elsewhere
from django.forms import inlineformset_factory
from django.utils.timezone import now
from .models import *




# nammude client paranjhu name chage cheyyan athu too risk anu athukondu html name mathre matittullu
# item category ennu parayunne elam item quality anu  model name itemQuality
# item group ennu parayunne elam item category anu model name itemCategory


class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = [ 'role','full_name', 'mobile', 'email', 'address', 'profile_picture', 'password']

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
    joining_date = forms.DateField(
        input_formats=['%d/%m/%Y'],   # accepts DD/MM/YYYY
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'placeholder': 'DD/MM/YYYY'})
    )
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

class ItemQualityForm(forms.ModelForm):
    class Meta:
        model = ItemQuality
        fields = '__all__'

# forms.py
class SpeciesForm(forms.ModelForm):
    class Meta:
        model = Species
        fields = ['item', 'name', 'code']

class ItemGradeForm(forms.ModelForm):
    class Meta:
        model = ItemGrade
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        item_id = None

        # Try getting item from bound form data (POST)
        if 'item' in self.data:
            item_id = self.data.get('item')

        # Or from initial data (GET with initial value)
        elif 'item' in self.initial:
            item_id = self.initial.get('item')

        # Or from instance (if editing existing object)
        elif self.instance and self.instance.pk:
            item_id = self.instance.item_id

        if item_id:
            self.fields['species'].queryset = Species.objects.filter(item_id=item_id)
        else:
            self.fields['species'].queryset = Species.objects.none()

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

class TenantFreezingTariffForm(forms.ModelForm):
    class Meta:
        model = TenantFreezingTariff
        fields = ['category', 'tariff']

TenantFreezingTariffFormSet = inlineformset_factory(
    Tenant,
    TenantFreezingTariff,
    form=TenantFreezingTariffForm,
    extra=1,
    can_delete=True
)



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

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['dollar_rate_to_inr', 'vehicle_rent_km']

# forms for create a Purchase Entry 
class SpotPurchaseForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.TextInput(attrs={
            'class': 'form-control datepicker',
            'placeholder': 'dd/mm/yyyy'
        }),
        input_formats=['%d/%m/%Y'],  # ✅ Accept dd/mm/yyyy
        initial=now
    )

    class Meta:
        model = SpotPurchase
        fields = ['date', 'voucher_number', 'spot', 'supervisor', 'agent']
        widgets = {
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
    date = forms.DateField(
        widget=forms.TextInput(attrs={
            'class': 'form-control datepicker',
            'placeholder': 'dd/mm/yyyy'
        }),
        input_formats=['%d/%m/%Y'],  # ✅ Accept dd/mm/yyyy
        initial=now
    )

    class Meta:
        model = LocalPurchase
        fields = ['date', 'voucher_number', 'party_name']
        widgets = {
            'voucher_number': forms.TextInput(attrs={'class': 'form-control'}),
            'party_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LocalPurchaseItemForm(forms.ModelForm):
    class Meta:
        model = LocalPurchaseItem
        exclude = ['purchase', 'amount']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'item_quality': forms.Select(attrs={'class': 'form-control', 'id': 'id_item_quality'}),
            'species': forms.Select(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-control'}),
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
class PeelingShedSupplyForm(forms.ModelForm):
    class Meta:
        model = PeelingShedSupply
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'spot_purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }

PeelingShedPeelingTypeFormSet = inlineformset_factory(
    PeelingShedSupply,
    PeelingShedPeelingType,
    fields=('item', 'item_type', 'amount', 'unit'),
    extra=0,
    can_delete=False
)



# Freezing Entry Spot Form


class FreezingEntrySpotForm(forms.ModelForm):
    class Meta:
        model = FreezingEntrySpot
        fields = '__all__'
        widgets = {
            'freezing_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'voucher_number': forms.TextInput(attrs={'class': 'form-control'}),

            'spot_purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'spot': forms.Select(attrs={'class': 'form-control'}),
            'spot_agent': forms.Select(attrs={'class': 'form-control'}),
            'spot_supervisor': forms.Select(attrs={'class': 'form-control'}),
            'total_usd': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_inr': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_slab': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_c_s': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_kg': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_yield_percentage': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),

            'freezing_status': forms.Select(attrs={'class': 'form-control'}),
        }

class FreezingEntrySpotItemForm(forms.ModelForm):
    class Meta:
        model = FreezingEntrySpotItem
        fields = '__all__'
        widgets = {
            'processing_center': forms.Select(attrs={'class': 'form-control'}),
            'store': forms.Select(attrs={'class': 'form-control'}),
            'shed': forms.Select(attrs={'class': 'form-control'}),

            # 🔹 Add "item-select" for AJAX binding
            'item': forms.Select(attrs={'class': 'form-control item-select'}),
            'item_quality': forms.Select(attrs={'class': 'form-control'}),

            'unit': forms.Select(attrs={'class': 'form-control unit-select', 'data-units': '{}'}),
            'glaze': forms.Select(attrs={'class': 'form-control'}),
            'freezing_category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),

            # 🔹 Add "species-select" + "peeling-select" for AJAX population
            'species': forms.Select(attrs={'class': 'form-control species-select'}),
            'peeling_type': forms.Select(attrs={'class': 'form-control peeling-select'}),

            'grade': forms.Select(attrs={'class': 'form-control'}),

            'slab_quantity': forms.NumberInput(attrs={'class': 'form-control slab-quantity'}),
            'c_s_quantity': forms.NumberInput(attrs={'class': 'form-control cs-quantity'}),
            'kg': forms.NumberInput(attrs={'class': 'form-control kg'}),

            'usd_rate_per_kg': forms.NumberInput(attrs={'class': 'form-control usd-rate-per-kg'}),
            'usd_rate_item': forms.NumberInput(attrs={'class': 'form-control usd-rate-item'}),
            'usd_rate_item_to_inr': forms.NumberInput(attrs={'class': 'form-control usd-rate-item-inr'}),
            'yield_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

FreezingEntrySpotItemFormSet = inlineformset_factory(
    FreezingEntrySpot,
    FreezingEntrySpotItem,
    form=FreezingEntrySpotItemForm,
    extra=1,
    can_delete=True
)



# Freezing Entry local Form
class FreezingEntryLocalForm(forms.ModelForm):
    class Meta:
        model = FreezingEntryLocal
        fields = "__all__" 
        widgets = {
            'freezing_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'local_purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'voucher_number': forms.TextInput(attrs={'class': 'form-control'}),
            'party': forms.Select(attrs={'class': 'form-control'}),
            'total_usd': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_inr': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_slab': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_c_s': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_kg': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),

            'freezing_status': forms.Select(attrs={'class': 'form-control'}),
        }

class FreezingEntryLocalItemForm(forms.ModelForm):
    class Meta:
        model = FreezingEntryLocalItem
        fields = '__all__'
        widgets = {

            'processing_center': forms.Select(attrs={'class': 'form-control'}),
            'store': forms.Select(attrs={'class': 'form-control'}),
            "item": forms.Select(attrs={"class": "form-control item-select"}),
            "item_quality": forms.Select(attrs={"class": "form-control quality-select"}),
            'unit': forms.Select(attrs={'class': 'form-control unit-select', 'data-units': '{}'}),
            'glaze': forms.Select(attrs={'class': 'form-control'}),
            'freezing_category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'species': forms.Select(attrs={'class': 'form-control'}),
            'peeling_type': forms.Select(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),

            'slab_quantity': forms.NumberInput(attrs={'class': 'form-control slab-quantity'}),
            'c_s_quantity': forms.NumberInput(attrs={'class': 'form-control cs-quantity'}),
            'kg': forms.NumberInput(attrs={'class': 'form-control kg'}),

            'usd_rate_per_kg': forms.NumberInput(attrs={'class': 'form-control usd-rate-per-kg'}),
            'usd_rate_item': forms.NumberInput(attrs={'class': 'form-control usd-rate-item'}),
            'usd_rate_item_to_inr': forms.NumberInput(attrs={'class': 'form-control usd-rate-item-inr'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure item_quality shows qualities, not item names
        self.fields['item_quality'].queryset = ItemQuality.objects.all().select_related('item')
        self.fields['item_quality'].label_from_instance = lambda obj: f"{obj.quality} ({obj.item.name})"

FreezingEntryLocalItemFormSet = inlineformset_factory(
    FreezingEntryLocal,
    FreezingEntryLocalItem,
    form=FreezingEntryLocalItemForm,
    extra=1,
    can_delete=True
)





# Main form for PreShipmentWorkOut
class PreShipmentWorkOutForm(forms.ModelForm):
    class Meta:
        model = PreShipmentWorkOut
        fields = "__all__"
        exclude = ['remark']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'glaze': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
        }

# Inline form for PreShipmentWorkOutItem
class PreShipmentWorkOutItemForm(forms.ModelForm):
    class Meta:
        model = PreShipmentWorkOutItem
        fields = "__all__"
        exclude = ['remark']  # Exclude remark field
        widgets = {
            'item_quality': forms.Select(attrs={'class': 'form-control quality'}),
            'species': forms.Select(attrs={'class': 'form-control species'}),            
            'peeling_type': forms.Select(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),

            'cartons': forms.NumberInput(attrs={'class': 'form-control cartons'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity'}),

            # "We want rate" fields
            'usd_rate_per_kg': forms.NumberInput(attrs={'class': 'form-control usd-rate-per-kg'}),
            'usd_rate_item': forms.NumberInput(attrs={'class': 'form-control usd-rate-item'}),
            'usd_rate_item_to_inr': forms.NumberInput(attrs={'class': 'form-control usd-rate-item-inr'}),

            # "We get rate" fields
            'usd_rate_per_kg_get': forms.NumberInput(attrs={'class': 'form-control usd-rate-per-kg-get'}),
            'usd_rate_item_get': forms.NumberInput(attrs={'class': 'form-control usd-rate-item-get'}),
            'usd_rate_item_to_inr_get': forms.NumberInput(attrs={'class': 'form-control usd-rate-item-inr-get'}),

            'profit': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control profit'}),
            'loss': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control loss'}),
        }

    def __init__(self, *args, **kwargs):
        item_id = kwargs.pop('item_id', None)
        super().__init__(*args, **kwargs)
        if item_id:
            self.fields['species'].queryset = Species.objects.filter(item_id=item_id)
        else:
            self.fields['species'].queryset = Species.objects.none()
            
# Inline formset to attach PreShipmentWorkOutItem to PreShipmentWorkOut
PreShipmentWorkOutItemFormSet = inlineformset_factory(
    PreShipmentWorkOut,
    PreShipmentWorkOutItem,
    form=PreShipmentWorkOutItemForm,
    extra=1,
    can_delete=True
)





# Freezing Entry Tenant Form

class FreezingEntryTenantForm(forms.ModelForm):

    class Meta:
        model = FreezingEntryTenant
        fields = "__all__"
        exclude = ['total_amount']  
        widgets = {
            'freezing_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'voucher_number': forms.TextInput(attrs={'class': 'form-control'}),
            'tenant_company_name': forms.Select(attrs={'class': 'form-control'}),

            'total_slab': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_c_s': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_kg': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),

            'freezing_status': forms.Select(attrs={'class': 'form-control'}),
        }

class FreezingEntryTenantItemForm(forms.ModelForm):
    class Meta:
        model = FreezingEntryTenantItem
        fields = "__all__"
        widgets = {
            'processing_center': forms.Select(attrs={'class': 'form-control'}),
            'store': forms.Select(attrs={'class': 'form-control'}),

            # 🔹 For AJAX population
            'item': forms.Select(attrs={'class': 'form-control item-select'}),
            'item_quality': forms.Select(attrs={'class': 'form-control'}),

            'unit': forms.Select(attrs={'class': 'form-control unit-select'}),
            'glaze': forms.Select(attrs={'class': 'form-control'}),
            'freezing_category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),

            # 🔹 Add "species-select" for dependent dropdowns
            'species': forms.Select(attrs={'class': 'form-control species-select'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),

            'slab_quantity': forms.NumberInput(attrs={'class': 'form-control slab-quantity'}),
            'c_s_quantity': forms.NumberInput(attrs={'class': 'form-control cs-quantity'}),
            'kg': forms.NumberInput(attrs={'class': 'form-control kg'}),
        }

FreezingEntryTenantItemFormSet = inlineformset_factory(
    FreezingEntryTenant,
    FreezingEntryTenantItem,
    form=FreezingEntryTenantItemForm,
    extra=1,
    can_delete=True
)


# return to Tenant Forms


class ReturnTenantForm(forms.ModelForm):
    class Meta:
        model = ReturnTenant
        fields = "__all__"
        exclude = ['total_amount']  # Exclude if calculated automatically
        widgets = {
            'return_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),  # Fixed field name
            'voucher_number': forms.TextInput(attrs={'class': 'form-control'}),
            'tenant_company_name': forms.Select(attrs={'class': 'form-control'}),

            'total_slab': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_c_s': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'total_kg': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),

            'return_status': forms.Select(attrs={'class': 'form-control'}),  # Fixed field name
        }

class ReturnTenantItemForm(forms.ModelForm):
    class Meta:
        model = ReturnTenantItem
        fields = "__all__"
        widgets = {
            'original_item': forms.Select(attrs={'class': 'form-control original-item-select'}),  # Added for traceability
            'processing_center': forms.Select(attrs={'class': 'form-control'}),
            'store': forms.Select(attrs={'class': 'form-control'}),

            # 🔹 For AJAX population
            'item': forms.Select(attrs={'class': 'form-control item-select'}),
            'item_quality': forms.Select(attrs={'class': 'form-control'}),

            'unit': forms.Select(attrs={'class': 'form-control unit-select'}),
            'glaze': forms.Select(attrs={'class': 'form-control'}),
            'freezing_category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),

            # 🔹 Add "species-select" for dependent dropdowns
            'species': forms.Select(attrs={'class': 'form-control species-select'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),

            'slab_quantity': forms.NumberInput(attrs={'class': 'form-control slab-quantity'}),
            'c_s_quantity': forms.NumberInput(attrs={'class': 'form-control cs-quantity'}),
            'kg': forms.NumberInput(attrs={'class': 'form-control kg'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter original_item to show only items from the same tenant
        if 'tenant_company_name' in self.initial:
            tenant = self.initial['tenant_company_name']
            self.fields['original_item'].queryset = FreezingEntryTenantItem.objects.filter(
                freezing_entry__tenant_company_name=tenant
            ).select_related('item', 'freezing_entry')
        
        # Make original_item optional but helpful
        self.fields['original_item'].required = False
        self.fields['original_item'].help_text = "Link to original stock lot (optional)"

ReturnTenantItemFormSet = inlineformset_factory(
    ReturnTenant,
    ReturnTenantItem,
    form=ReturnTenantItemForm,
    extra=1,
    can_delete=True
)





# forms.py

from django import forms
from django.forms import modelformset_factory

class TenantBillingConfigurationForm(forms.ModelForm):
    class Meta:
        model = TenantBillingConfiguration
        fields = ['tenant', 'billing_start_date', 'billing_frequency_days', 'is_active']
        widgets = {
            'billing_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'billing_frequency_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'tenant': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['billing_frequency_days'].help_text = "Enter number of days (e.g., 2 for every 2 days, 7 for weekly)"

class BillGenerationForm(forms.Form):
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Tenant"
    )
    from_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    to_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

class TenantBillForm(forms.ModelForm):
    class Meta:
        model = TenantBill
        fields = ['tenant', 'from_date', 'to_date', 'status']
        widgets = {
            'tenant': forms.Select(attrs={'class': 'form-control'}),
            'from_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'to_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }






# forms.py - Updated forms with better validation

from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import StoreTransfer, StoreTransferItem, Stock
from collections import defaultdict
from decimal import Decimal


class StoreTransferForm(forms.ModelForm):
    class Meta:
        model = StoreTransfer
        fields = ["voucher_no", "date", "from_store", "to_store"]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'voucher_no': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'from_store': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'to_store': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        from_store = cleaned_data.get('from_store')
        to_store = cleaned_data.get('to_store')
        
        if from_store and to_store and from_store == to_store:
            raise ValidationError("From store and To store cannot be the same.")
        
        return cleaned_data


class StoreTransferItemForm(forms.ModelForm):
    class Meta:
        model = StoreTransferItem
        exclude = ['plus_qty','minus_qty']
        fields = ["stock", "item_grade", "cs_quantity", "kg_quantity"]
        widgets = {
            'stock': forms.Select(attrs={'class': 'form-control stock-select'}),
            'item_grade': forms.TextInput(attrs={'class': 'form-control'}),
            'cs_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'kg_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        from_store = kwargs.pop('from_store', None)
        super().__init__(*args, **kwargs)
        
        if from_store:
            self.fields['stock'].queryset = Stock.objects.filter(
                store=from_store
            ).select_related('item', 'brand', 'category')
        else:
            self.fields['stock'].queryset = Stock.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        stock = cleaned_data.get('stock')
        cs_quantity = cleaned_data.get('cs_quantity', 0)
        kg_quantity = cleaned_data.get('kg_quantity', 0)
        
        if not stock:
            return cleaned_data
        
        # Validate that transfer quantities don't exceed available stock
        if cs_quantity and cs_quantity > stock.cs_quantity:
            raise ValidationError({
                'cs_quantity': f'CS quantity ({cs_quantity}) exceeds available stock ({stock.cs_quantity})'
            })
        
        if kg_quantity and kg_quantity > stock.kg_quantity:
            raise ValidationError({
                'kg_quantity': f'KG quantity ({kg_quantity}) exceeds available stock ({stock.kg_quantity})'
            })
        
        # Ensure at least one quantity is provided
        if not cs_quantity and not kg_quantity:
            raise ValidationError("Either CS quantity or KG quantity must be provided.")
        
        return cleaned_data


# Custom formset with validation for duplicate handling
class StoreTransferItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        """
        Custom validation to check for duplicate stocks and validate total quantities
        """
        if any(self.errors):
            return
        
        if not self.forms:
            raise ValidationError("At least one item must be added to the transfer.")
        
        # Track stock quantities for validation
        stock_quantities = defaultdict(lambda: {'cs': Decimal('0'), 'kg': Decimal('0')})
        
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue
            
            stock = form.cleaned_data.get('stock')
            item_grade = form.cleaned_data.get('item_grade', '')
            cs_quantity = form.cleaned_data.get('cs_quantity', Decimal('0'))
            kg_quantity = form.cleaned_data.get('kg_quantity', Decimal('0'))
            
            if not stock:
                continue
            
            # Create key for tracking (stock + grade combination)
            key = (stock.id, item_grade or '')
            stock_quantities[key]['cs'] += cs_quantity
            stock_quantities[key]['kg'] += kg_quantity
        
        # Validate against available stock quantities
        for (stock_id, item_grade), quantities in stock_quantities.items():
            try:
                stock = Stock.objects.get(id=stock_id)
                
                if quantities['cs'] > stock.cs_quantity:
                    raise ValidationError(
                        f"Total CS quantity for {stock.item.name} ({quantities['cs']}) "
                        f"exceeds available stock ({stock.cs_quantity})"
                    )
                
                if quantities['kg'] > stock.kg_quantity:
                    raise ValidationError(
                        f"Total KG quantity for {stock.item.name} ({quantities['kg']}) "
                        f"exceeds available stock ({stock.kg_quantity})"
                    )
            except Stock.DoesNotExist:
                raise ValidationError(f"Stock with ID {stock_id} not found")


# Create the formset with custom validation
StoreTransferItemFormSet = inlineformset_factory(
    StoreTransfer,
    StoreTransferItem,
    form=StoreTransferItemForm,
    formset=StoreTransferItemFormSet,
    fields=["stock", "item_grade", "plus_qty", "minus_qty", "cs_quantity", "kg_quantity"],
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

