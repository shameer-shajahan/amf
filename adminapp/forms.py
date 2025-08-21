from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from adminapp.models import CustomUser  # adjust if CustomUser is elsewhere
from django.forms import inlineformset_factory
from django.utils.timezone import now
from .models import *


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
            'item': forms.Select(attrs={'class': 'form-control'}),
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

# Inline formset to attach items to a main entry
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





