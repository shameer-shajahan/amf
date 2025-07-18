from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from adminapp.models import CustomUser  # adjust if CustomUser is elsewhere

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
    

from django import forms
from .models import *

# Operational & Location
class ProcessingCenterForm(forms.ModelForm):
    class Meta:
        model = ProcessingCenter
        fields = '__all__'

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = '__all__'

class PeelingCenterForm(forms.ModelForm):
    class Meta:
        model = PeelingCenter
        fields = '__all__'

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

# Financial & Expense
class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = '__all__'

class FreezingTariffForm(forms.ModelForm):
    class Meta:
        model = FreezingTariff
        fields = '__all__'

class PeelingChargeForm(forms.ModelForm):
    class Meta:
        model = PeelingCharge
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
