# Create your views here.
from .models import *
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView 
from django.views.generic import DetailView, ListView
from decimal import Decimal
from django.views import View
from django.db.models import Sum, Count, Avg, DecimalField, Value as V
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta, datetime
import xlsxwriter
from django.db.models import Sum, F, FloatField
from django.http import HttpResponse
from datetime import datetime, timedelta
import csv
import io
from django.db.models import Sum, Avg, F, Value, CharField, DecimalField, FloatField
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import ItemQuality
from django.db import transaction
from django.urls import reverse
import io
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Import your models and forms - change names/paths if different in your project
from adminapp.models import (
    TenantBill, TenantBillItem, TenantBillingConfiguration,
    TenantFreezingTariff, FreezingEntryTenant
)
from adminapp.forms import TenantBillingConfigurationForm, BillGenerationForm

from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


# nammude client paranjhu name chage cheyyan athu too risk anu athukondu html name mathre matittullu
# item category ennu parayunne elam item quality anu  model name itemQuality
# item group ennu parayunne elam item category anu model name itemCategory


# Check if user is an admin
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

# Admin login view
def admin_login(request):
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('adminapp:admin_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None and is_admin(user):
            login(request, user)
            return redirect('adminapp:admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials.')

    return render(request, 'adminapp/login.html')

# Admin logout view
def admin_logout(request):
    logout(request)
    return redirect('adminapp:admin_login')

@login_required
@user_passes_test(is_admin)
def create_user_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('adminapp:create_user')  # Redirect to form again or elsewhere
        else:
            messages.error(request, 'Error creating user.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'adminapp/create_user.html', {'form': form})


def users_list_view(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
    }
    
    return render(request, 'adminapp/list/users_list.html', context)


class UserDeleteView(DeleteView):
    model = CustomUser
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:users_list')

    
# Dashboard View
def admin_dashboard(request):
    return render(request, 'adminapp/dashboard.html')

def master(request):
    return render(request, 'adminapp/master.html')
# -------------------------------
# Operational & Location Masters
# -------------------------------

class ProcessingCenterCreateView(CreateView):
    model = ProcessingCenter
    form_class = ProcessingCenterForm
    template_name = 'adminapp/forms/processingcenter_form.html'
    success_url = reverse_lazy('adminapp:processing_center_create')

class ProcessingCenterListView(ListView):
    model = ProcessingCenter
    template_name = 'adminapp/list/processingcenter_list.html'
    context_object_name = 'processing_centers'

class ProcessingCenterUpdateView(UpdateView):
    model = ProcessingCenter
    form_class = ProcessingCenterForm
    template_name = 'adminapp/forms/processingcenter_form.html'
    success_url = reverse_lazy('adminapp:processing_center_list')

class ProcessingCenterDeleteView(DeleteView):
    model = ProcessingCenter
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:processing_center_list')

class StoreCreateView(CreateView):
    model = Store
    form_class = StoreForm
    template_name = 'adminapp/forms/store_form.html'
    success_url = reverse_lazy('adminapp:store_create')

class StoreListView(ListView):
    model = Store
    template_name = 'adminapp/list/store_list.html'
    context_object_name = 'stores'

class StoreUpdateView(UpdateView):
    model = Store
    form_class = StoreForm
    template_name = 'adminapp/forms/store_form.html'
    success_url = reverse_lazy('adminapp:store_list')

class StoreDeleteView(DeleteView):
    model = Store
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:store_list')

def create_shed(request):
    if request.method == 'POST':
        form = ShedForm(request.POST)
        formset = ShedItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            shed = form.save()
            items = formset.save(commit=False)

            for item in items:
                item.shed = shed
                item.save()

            for deleted_item in formset.deleted_objects:
                deleted_item.delete()

            return redirect('adminapp:peeling_center_list')
    else:
        form = ShedForm()
        formset = ShedItemFormSet()

    return render(request, 'adminapp/forms/create_shed.html', {
        'form': form,
        'formset': formset,
    })

def get_item_types(request):
    item_id = request.GET.get('item_id')
    item_types = ItemType.objects.filter(item_id=item_id).values('id', 'name')
    return JsonResponse(list(item_types), safe=False)

class ShedListView(ListView):
    model = Shed
    template_name = 'adminapp/list/shed_list.html'
    context_object_name = 'peeling_centers'

def update_shed(request, pk):
    shed = get_object_or_404(Shed, pk=pk)

    if request.method == 'POST':
        form = ShedForm(request.POST, instance=shed)
        formset = ShedItemFormSet(request.POST, instance=shed)

        if form.is_valid() and formset.is_valid():
            shed = form.save()
            items = formset.save(commit=False)

            for item in items:
                item.shed = shed
                item.save()

            # Delete any items marked for deletion
            for deleted_item in formset.deleted_objects:
                deleted_item.delete()

            return redirect('adminapp:peeling_center_list')
    else:
        form = ShedForm(instance=shed)
        formset = ShedItemFormSet(instance=shed)

    return render(request, 'adminapp/forms/update_shed.html', {
        'form': form,
        'formset': formset,
        'shed': shed
    })

class ShedDeleteView(DeleteView):
    model = Shed
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:peeling_center_list')

class PurchasingSpotCreateView(CreateView):
    model = PurchasingSpot
    form_class = PurchasingSpotForm
    template_name = 'adminapp/forms/purchasingspot_form.html'
    success_url = reverse_lazy('adminapp:purchasing_spot_create')

class PurchasingSpotListView(ListView):
    model = PurchasingSpot
    template_name = 'adminapp/list/purchasingspot_list.html'
    context_object_name = 'purchasing_spots'

class PurchasingSpotUpdateView(UpdateView):
    model = PurchasingSpot
    form_class = PurchasingSpotForm
    template_name = 'adminapp/forms/purchasingspot_form.html'
    success_url = reverse_lazy('adminapp:purchasing_spot_list')

class PurchasingSpotDeleteView(DeleteView):
    model = PurchasingSpot
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:purchasing_spot_list')

# -------------------
# Personnel Masters
# -------------------

class PurchasingSupervisorCreateView(CreateView):
    model = PurchasingSupervisor
    form_class = PurchasingSupervisorForm
    template_name = 'adminapp/forms/purchasingsupervisor_form.html'
    success_url = reverse_lazy('adminapp:purchasing_supervisor_create')

class PurchasingSupervisorListView(ListView):
    model = PurchasingSupervisor
    template_name = 'adminapp/list/purchasingsupervisor_list.html'
    context_object_name = 'purchasing_supervisors'

class PurchasingSupervisorUpdateView(UpdateView):
    model = PurchasingSupervisor
    form_class = PurchasingSupervisorForm
    template_name = 'adminapp/forms/purchasingsupervisor_form.html'
    success_url = reverse_lazy('adminapp:purchasing_supervisor_list')

class PurchasingSupervisorDeleteView(DeleteView):
    model = PurchasingSupervisor
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:purchasing_supervisor_list')

class PurchasingAgentCreateView(CreateView):
    model = PurchasingAgent
    form_class = PurchasingAgentForm
    template_name = 'adminapp/forms/purchasingagent_form.html'
    success_url = reverse_lazy('adminapp:purchasing_agent_create')

class PurchasingAgentListView(ListView):
    model = PurchasingAgent
    template_name = 'adminapp/list/purchasingagent_list.html'
    context_object_name = 'purchasing_agents'

class PurchasingAgentUpdateView(UpdateView):
    model = PurchasingAgent
    form_class = PurchasingAgentForm
    template_name = 'adminapp/forms/purchasingagent_form.html'
    success_url = reverse_lazy('adminapp:purchasing_agent_list')

class PurchasingAgentDeleteView(DeleteView):
    model = PurchasingAgent
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:purchasing_agent_list')

# ----------------------
# Item & Product Masters
# ----------------------

class ItemCategoryCreateView(CreateView):
    model = ItemCategory
    form_class = ItemCategoryForm
    template_name = 'adminapp/forms/itemcategory_form.html'
    success_url = reverse_lazy('adminapp:item_category_create')

class ItemCategoryListView(ListView):
    model = ItemCategory
    template_name = 'adminapp/list/itemcategory_list.html'
    context_object_name = 'item_categories'

class ItemCategoryUpdateView(UpdateView):
    model = ItemCategory
    form_class = ItemCategoryForm
    template_name = 'adminapp/forms/itemcategory_form.html'
    success_url = reverse_lazy('adminapp:item_category_list')

class ItemCategoryDeleteView(DeleteView):
    model = ItemCategory
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:item_category_list')

class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'adminapp/forms/item_form.html'
    success_url = reverse_lazy('adminapp:item_create')

class ItemListView(ListView):
    model = Item
    template_name = 'adminapp/list/item_list.html'
    context_object_name = 'items'

class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'adminapp/forms/item_form.html'
    success_url = reverse_lazy('adminapp:item_list')

class ItemDeleteView(DeleteView):
    model = Item
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:item_list')

class ItemQualityCreateView(CreateView):
    model = ItemQuality
    form_class = ItemQualityForm
    template_name = 'adminapp/forms/itemquality_form.html'
    success_url = reverse_lazy('adminapp:item_quality_create')

class ItemQualityListView(ListView):
    model = ItemQuality
    template_name = 'adminapp/list/itemquality_list.html'
    context_object_name = 'item_qualities'

class ItemQualityUpdateView(UpdateView):
    model = ItemQuality
    form_class = ItemQualityForm
    template_name = 'adminapp/forms/itemquality_form.html'
    success_url = reverse_lazy('adminapp:item_quality_list')

class ItemQualityDeleteView(DeleteView):
    model = ItemQuality
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:item_quality_list')

class SpeciesListView(ListView):
    model = Species
    template_name = 'adminapp/list/species_list.html'
    context_object_name = 'species_list'

class SpeciesCreateView(CreateView):
    model = Species
    form_class = SpeciesForm
    template_name = 'adminapp/forms/species_form.html'
    success_url = reverse_lazy('adminapp:species_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context

class SpeciesUpdateView(UpdateView):
    model = Species
    form_class = SpeciesForm
    template_name = 'adminapp/forms/species_form.html'
    success_url = reverse_lazy('adminapp:species_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        return context

class SpeciesDeleteView(DeleteView):
    model = Species
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:species_list')

class ItemGradeCreateView(CreateView):
    model = ItemGrade
    form_class = ItemGradeForm
    template_name = 'adminapp/forms/itemgrade_form.html'
    success_url = reverse_lazy('adminapp:item_grade_list')

def load_species(request):
    item_id = request.GET.get('item_id')
    species = Species.objects.filter(item_id=item_id).values('id', 'name', 'code')
    data = list(species)
    return JsonResponse(data, safe=False)

class ItemGradeListView(ListView):
    model = ItemGrade
    template_name = 'adminapp/list/itemgrade_list.html'
    context_object_name = 'item_grades'

class ItemGradeUpdateView(UpdateView):
    model = ItemGrade
    form_class = ItemGradeForm
    template_name = 'adminapp/forms/itemgrade_form.html'
    success_url = reverse_lazy('adminapp:item_grade_list')

class ItemGradeDeleteView(DeleteView):
    model = ItemGrade
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:item_grade_list')

class FreezingCategoryCreateView(CreateView):
    model = FreezingCategory
    form_class = FreezingCategoryForm
    template_name = 'adminapp/forms/freezingcategory_form.html'
    success_url = reverse_lazy('adminapp:freezing_category_create')

class FreezingCategoryListView(ListView):
    model = FreezingCategory
    template_name = 'adminapp/list/freezingcategory_list.html'
    context_object_name = 'freezing_categories'

class FreezingCategoryUpdateView(UpdateView):
    model = FreezingCategory
    form_class = FreezingCategoryForm
    template_name = 'adminapp/forms/freezingcategory_form.html'
    success_url = reverse_lazy('adminapp:freezing_category_list')

class FreezingCategoryDeleteView(DeleteView):
    model = FreezingCategory
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:freezing_category_list')

class PackingUnitCreateView(CreateView):
    model = PackingUnit
    form_class = PackingUnitForm
    template_name = 'adminapp/forms/packingunit_form.html'
    success_url = reverse_lazy('adminapp:packing_unit_create')

class PackingUnitListView(ListView):
    model = PackingUnit
    template_name = 'adminapp/list/packingunit_list.html'
    context_object_name = 'packing_units'

class PackingUnitUpdateView(UpdateView):
    model = PackingUnit
    form_class = PackingUnitForm
    template_name = 'adminapp/forms/packingunit_form.html'
    success_url = reverse_lazy('adminapp:packing_unit_list')

class PackingUnitDeleteView(DeleteView):
    model = PackingUnit
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:packing_unit_list')

class GlazePercentageCreateView(CreateView):
    model = GlazePercentage
    form_class = GlazePercentageForm
    template_name = 'adminapp/forms/glazepercentage_form.html'
    success_url = reverse_lazy('adminapp:glaze_percentage_create')

class GlazePercentageListView(ListView):
    model = GlazePercentage
    template_name = 'adminapp/list/glazepercentage_list.html'
    context_object_name = 'glaze_percentages'

class GlazePercentageUpdateView(UpdateView):
    model = GlazePercentage
    form_class = GlazePercentageForm
    template_name = 'adminapp/forms/glazepercentage_form.html'
    success_url = reverse_lazy('adminapp:glaze_percentage_list')

class GlazePercentageDeleteView(DeleteView):
    model = GlazePercentage
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:glaze_percentage_list')

class ItemBrandCreateView(CreateView):
    model = ItemBrand
    form_class = ItemBrandForm
    template_name = 'adminapp/forms/itembrand_form.html'
    success_url = reverse_lazy('adminapp:item_brand_create')

class ItemBrandListView(ListView):
    model = ItemBrand
    template_name = 'adminapp/list/itembrand_list.html'
    context_object_name = 'item_brands'

class ItemBrandUpdateView(UpdateView):
    model = ItemBrand
    form_class = ItemBrandForm
    template_name = 'adminapp/forms/itembrand_form.html'
    success_url = reverse_lazy('adminapp:item_brand_list')

class ItemBrandDeleteView(DeleteView):
    model = ItemBrand
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:item_brand_list')

class ItemTypeCreateView(CreateView):
    model = ItemType
    form_class = ItemTypeForm
    template_name = 'adminapp/forms/itemtype_form.html'
    success_url = reverse_lazy('adminapp:item_type_create')

class ItemTypeListView(ListView):
    model = ItemType
    template_name = 'adminapp/list/itemtype_list.html'
    context_object_name = 'item_types'

class ItemTypeUpdateView(UpdateView):
    model = ItemType
    form_class = ItemTypeForm
    template_name = 'adminapp/forms/itemtype_form.html'
    success_url = reverse_lazy('adminapp:item_type_list')

class ItemTypeDeleteView(DeleteView):
    model = ItemType
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:item_type_list')

# ----------------------------
# Financial & Expense Masters
# ----------------------------



class TenantCreateView(CreateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'adminapp/forms/tenant_form.html'
    success_url = reverse_lazy('adminapp:tenant_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TenantFreezingTariffFormSet(self.request.POST)
        else:
            context['formset'] = TenantFreezingTariffFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            tenant = form.save()
            formset.instance = tenant
            formset.save()
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))


class TenantListView(ListView):
    model = Tenant
    template_name = 'adminapp/list/tenant_list.html'
    context_object_name = 'tenants'


class TenantUpdateView(UpdateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'adminapp/forms/tenant_form.html'
    success_url = reverse_lazy('adminapp:tenant_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TenantFreezingTariffFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = TenantFreezingTariffFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            tenant = form.save()
            formset.instance = tenant
            formset.save()
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))


class TenantDeleteView(DeleteView):
    model = Tenant
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:tenant_list')





class PurchaseOverheadCreateView(CreateView):
    model = PurchaseOverhead
    form_class = PurchaseOverheadForm
    template_name = 'adminapp/forms/purchaseoverhead_form.html'
    success_url = reverse_lazy('adminapp:purchase_overhead_create')

class PurchaseOverheadListView(ListView):
    model = PurchaseOverhead
    template_name = 'adminapp/list/purchaseoverhead_list.html'
    context_object_name = 'purchase_overheads'

class PurchaseOverheadUpdateView(UpdateView):
    model = PurchaseOverhead
    form_class = PurchaseOverheadForm
    template_name = 'adminapp/forms/purchaseoverhead_form.html'
    success_url = reverse_lazy('adminapp:purchase_overhead_list')

class PurchaseOverheadDeleteView(DeleteView):
    model = PurchaseOverhead
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:purchase_overhead_list')

class PeelingOverheadCreateView(CreateView):
    model = PeelingOverhead
    form_class = PeelingOverheadForm
    template_name = 'adminapp/forms/peelingoverhead_form.html'
    success_url = reverse_lazy('adminapp:peeling_overhead_create')

class PeelingOverheadListView(ListView):
    model = PeelingOverhead
    template_name = 'adminapp/list/peelingoverhead_list.html'
    context_object_name = 'peeling_overheads'

class PeelingOverheadUpdateView(UpdateView):
    model = PeelingOverhead
    form_class = PeelingOverheadForm
    template_name = 'adminapp/forms/peelingoverhead_form.html'
    success_url = reverse_lazy('adminapp:peeling_overhead_list')

class PeelingOverheadDeleteView(DeleteView):
    model = PeelingOverhead
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:peeling_overhead_list')

class ProcessingOverheadCreateView(CreateView):
    model = ProcessingOverhead
    form_class = ProcessingOverheadForm
    template_name = 'adminapp/forms/processingoverhead_form.html'
    success_url = reverse_lazy('adminapp:processing_overhead_create')

class ProcessingOverheadListView(ListView):
    model = ProcessingOverhead
    template_name = 'adminapp/list/processingoverhead_list.html'
    context_object_name = 'processing_overheads'

class ProcessingOverheadUpdateView(UpdateView):
    model = ProcessingOverhead
    form_class = ProcessingOverheadForm
    template_name = 'adminapp/forms/processingoverhead_form.html'
    success_url = reverse_lazy('adminapp:processing_overhead_list')

class ProcessingOverheadDeleteView(DeleteView):
    model = ProcessingOverhead
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:processing_overhead_list')

class ShipmentOverheadCreateView(CreateView):
    model = ShipmentOverhead
    form_class = ShipmentOverheadForm
    template_name = 'adminapp/forms/shipmentoverhead_form.html'
    success_url = reverse_lazy('adminapp:shipment_overhead_create')

class ShipmentOverheadListView(ListView):
    model = ShipmentOverhead
    template_name = 'adminapp/list/shipmentoverhead_list.html'
    context_object_name = 'shipment_overheads'

class ShipmentOverheadUpdateView(UpdateView):
    model = ShipmentOverhead
    form_class = ShipmentOverheadForm
    template_name = 'adminapp/forms/shipmentoverhead_form.html'
    success_url = reverse_lazy('adminapp:shipment_overhead_list')

class ShipmentOverheadDeleteView(DeleteView):
    model = ShipmentOverhead
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:shipment_overhead_list')

def settings_create(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            dollar_rate = form.cleaned_data['dollar_rate_to_inr']
            vehicle_rent = form.cleaned_data['vehicle_rent_km']

            # Only create if NO active settings exist with same values
            exists = Settings.objects.filter(
                dollar_rate_to_inr=dollar_rate,
                vehicle_rent_km=vehicle_rent,
                is_active=True
            ).exists()

            if not exists:
                # deactivate all old ones
                Settings.objects.filter(is_active=True).update(is_active=False)
                # create new one
                form.save()
            return redirect('adminapp:settings_list')
    else:
        form = SettingsForm()

    return render(request, 'adminapp/forms/settings_form.html', {'form': form})

def settings_update(request, pk):
    old_setting = get_object_or_404(Settings, pk=pk)

    if request.method == 'POST':
        # Don’t bind to old instance → we want a *new* row
        form = SettingsForm(request.POST)
        if form.is_valid():
            # Mark old setting inactive
            old_setting.is_active = False
            old_setting.save()

            # Create new setting
            new_setting = form.save(commit=False)
            new_setting.is_active = True
            new_setting.save()

            return redirect('adminapp:settings_list')
    else:
        # Prefill form with old values for editing
        form = SettingsForm(instance=old_setting)

    return render(request, 'adminapp/forms/settings_form.html', {'form': form})

def settings_delete(request, pk):
    setting = get_object_or_404(Settings, pk=pk)
    if request.method == 'POST':
        setting.is_active = False   # mark inactive instead of deleting
        setting.save()
        return redirect('adminapp:settings_list')

    return render(request, 'adminapp/confirm_delete.html', {'setting': setting})

def settings_list(request):
    settings = Settings.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'adminapp/list/settings_list.html', {'settings': settings})


# function for creating a Purchase Entry

def create_spot_purchase(request):
    if request.method == 'POST':
        purchase_form = SpotPurchaseForm(request.POST)
        item_formset = SpotPurchaseItemFormSet(request.POST)
        expense_form = SpotPurchaseExpenseForm(request.POST)

        if purchase_form.is_valid() and item_formset.is_valid() and expense_form.is_valid():
            purchase = purchase_form.save()

            items = item_formset.save(commit=False)
            for item in items:
                item.purchase = purchase
                item.amount = item.quantity * item.rate  # Ensure amount is calculated
                item.save()
            item_formset.save_m2m()

            expense = expense_form.save(commit=False)
            expense.purchase = purchase
            expense.save()

            purchase.update_totals()
            return redirect('adminapp:create_peeling_shed_supply')

    else:
        purchase_form = SpotPurchaseForm()
        item_formset = SpotPurchaseItemFormSet()
        expense_form = SpotPurchaseExpenseForm()

    # ✅ Always return something at the end
    return render(request, 'adminapp/purchases/spot_purchase_form.html', {
        'purchase_form': purchase_form,
        'item_formset': item_formset,
        'expense_form': expense_form,
    })

def edit_spot_purchase(request, pk):
    purchase = get_object_or_404(SpotPurchase, pk=pk)
    SpotPurchaseItemFormSet = inlineformset_factory(
    SpotPurchase,
    SpotPurchaseItem,
    form=SpotPurchaseItemForm,
    extra=0,
    can_delete=True
)

    # Get expense or set to None if it doesn't exist
    try:
        expense = purchase.expense
    except SpotPurchaseExpense.DoesNotExist:
        expense = None

    if request.method == 'POST':
        purchase_form = SpotPurchaseForm(request.POST, instance=purchase)
        item_formset = SpotPurchaseItemFormSet(request.POST, instance=purchase)
        expense_form = SpotPurchaseExpenseForm(request.POST, instance=expense)

        if purchase_form.is_valid() and item_formset.is_valid() and expense_form.is_valid():
            purchase = purchase_form.save()

            items = item_formset.save(commit=False)
            for item in items:
                item.purchase = purchase
                item.amount = item.quantity * item.rate  # Auto calculate amount
                item.save()
            item_formset.save_m2m()

            # Handle deleted items
            for obj in item_formset.deleted_objects:
                obj.delete()

            # Save expense (create if it doesn't exist)
            expense = expense_form.save(commit=False)
            expense.purchase = purchase
            expense.save()

            purchase.update_totals()
            return redirect('adminapp:spot_purchase_list')

        # 🐍 Debugging form errors
        print("Purchase Form Errors:", purchase_form.errors)
        print("Item Formset Errors:", item_formset.errors)
        print("Expense Form Errors:", expense_form.errors)

    else:
        purchase_form = SpotPurchaseForm(instance=purchase)
        item_formset = SpotPurchaseItemFormSet(instance=purchase)
        expense_form = SpotPurchaseExpenseForm(instance=expense)

    return render(request, 'adminapp/purchases/spot_purchase_edit.html', {
        'purchase_form': purchase_form,
        'item_formset': item_formset,
        'expense_form': expense_form,
    })

def spot_purchase_list(request):
    purchases = SpotPurchase.objects.all().order_by('-date')
    return render(request, 'adminapp/purchases/spot_purchase_list.html', {'purchases': purchases})

def spot_purchase_delete(request, pk):
    purchase = get_object_or_404(SpotPurchase, pk=pk)
    if request.method == 'POST':
        purchase.delete()
        return redirect('adminapp:spot_purchase_list')
    return render(request, 'adminapp/purchases/spot_purchase_confirm_delete.html', {'purchase': purchase})

def spot_purchase_detail(request, pk):
    purchase = get_object_or_404(
        SpotPurchase.objects.select_related('expense', 'spot', 'supervisor', 'agent')
                            .prefetch_related('items'),
        pk=pk
    )
    return render(request, 'adminapp/purchases/spot_purchase_detail.html', {
        'purchase': purchase
    })




def local_purchase_create(request):
    if request.method == 'POST':
        form = LocalPurchaseForm(request.POST)
        formset = LocalPurchaseItemFormSet(request.POST, prefix='form')  # ✅ Add prefix

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                purchase = form.save()
                total_amount = 0
                total_quantity = 0

                for item_form in formset:
                    item = item_form.save(commit=False)
                    item.purchase = purchase
                    item.amount = item.quantity * item.rate
                    item.save()
                    total_amount += item.amount
                    total_quantity += item.quantity

                purchase.total_amount = total_amount
                purchase.total_quantity = total_quantity
                purchase.total_items = formset.total_form_count()
                purchase.save()

                return redirect('adminapp:admin_dashboard')  # update as needed

    else:
        form = LocalPurchaseForm()
        formset = LocalPurchaseItemFormSet(prefix='form')  # ✅ Add prefix

    return render(request, 'adminapp/purchases/local_purchase_form.html', {
        'form': form,
        'formset': formset,
    })

# List View
def local_purchase_list(request):
    purchases = LocalPurchase.objects.all().order_by('-date')
    return render(request, 'adminapp/purchases/local_purchase_list.html', {'purchases': purchases})

# Update View
def local_purchase_update(request, pk):
    purchase = get_object_or_404(LocalPurchase, pk=pk)
    if request.method == 'POST':
        form = LocalPurchaseForm(request.POST, instance=purchase)
        formset = LocalPurchaseItemFormSet(request.POST, instance=purchase, prefix='form')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                purchase = form.save()
                total_amount = 0
                total_quantity = 0
                items = formset.save(commit=False)
                for item in items:
                    item.purchase = purchase
                    item.amount = item.quantity * item.rate
                    item.save()
                    total_amount += item.amount
                    total_quantity += item.quantity

                formset.save_m2m()
                purchase.total_amount = total_amount
                purchase.total_quantity = total_quantity
                purchase.total_items = formset.total_form_count()
                purchase.save()

                return redirect('adminapp:local_purchase_list')
    else:
        form = LocalPurchaseForm(instance=purchase)
        formset = LocalPurchaseItemFormSet(instance=purchase, prefix='form')

    return render(request, 'adminapp/purchases/local_purchase_edit.html', {
        'form': form,
        'formset': formset
    })

# Delete View
def local_purchase_delete(request, pk):
    purchase = get_object_or_404(LocalPurchase, pk=pk)
    if request.method == 'POST':
        purchase.delete()
        return redirect('adminapp:local_purchase_list')
    return render(request, 'adminapp/purchases/local_purchase_confirm_delete.html', {'purchase': purchase})

# Detail View
def local_purchase_detail(request, pk):
    purchase = get_object_or_404(LocalPurchase, pk=pk)
    items = purchase.items.all()  # using related_name='items' from the model
    return render(request, 'adminapp/purchases/local_purchase_detail.html', {
        'purchase': purchase,
        'items': items,
        'title': f"Local Purchase Details - Voucher #{purchase.voucher_number}"
    })

def spot_purchase_workout_summary(request):
    items = Item.objects.all()
    spots = PurchasingSpot.objects.all()
    agents = PurchasingAgent.objects.all()
    categories = ItemCategory.objects.all()

    queryset = SpotPurchaseItem.objects.select_related(
        "purchase", "item", "purchase__spot", "purchase__agent"
    )

    # ✅ Multi-select filters
    selected_items = request.GET.getlist("items")
    selected_spots = request.GET.getlist("spots")
    selected_agents = request.GET.getlist("agents")
    selected_categories = request.GET.getlist("categories")
    date_filter = request.GET.get("date_filter")

    # ✅ Date range filter
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if selected_items:
        queryset = queryset.filter(item__id__in=selected_items)
    if selected_spots:
        queryset = queryset.filter(purchase__spot__id__in=selected_spots)
    if selected_agents:
        queryset = queryset.filter(purchase__agent__id__in=selected_agents)
    if selected_categories:
        queryset = queryset.filter(item__category__id__in=selected_categories)

    # ✅ Quick date filter
    if date_filter == "week":
        queryset = queryset.filter(purchase__date__gte=now().date() - timedelta(days=7))
    elif date_filter == "month":
        queryset = queryset.filter(purchase__date__month=now().month)
    elif date_filter == "year":
        queryset = queryset.filter(purchase__date__year=now().year)

    # ✅ Custom date range
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            queryset = queryset.filter(purchase__date__range=[start, end])
        except:
            pass

    # ✅ Group & summary
    summary = (
        queryset.values(
            "item__name",
            "item__category__name",
            "purchase__spot__location_name",
            "purchase__agent__name",
            "purchase__date",
        )
        .annotate(
            total_quantity=Sum("quantity"),
            total_amount=Sum("amount"),
            avg_rate=Sum("amount") / Sum("quantity"),
        )
        .order_by("purchase__date")
    )

    return render(
        request,
        "adminapp/purchases/spot_purchase_workout_summary.html",
        {
            "summary": summary,
            "items": items,
            "spots": spots,
            "agents": agents,
            "categories": categories,
            "selected_items": selected_items,
            "selected_spots": selected_spots,
            "selected_agents": selected_agents,
            "selected_categories": selected_categories,
            "date_filter": date_filter,
            "start_date": start_date,
            "end_date": end_date,
        },
    )

def local_purchase_workout_summary(request):
    items = Item.objects.all()
    categories = ItemCategory.objects.all()
    species_list = Species.objects.all()
    parties = LocalPurchase.objects.values_list("party_name", flat=True).distinct()

    queryset = LocalPurchaseItem.objects.select_related(
        "purchase", "item", "item__category", "item__species"
    )

    # ✅ Multi-select filters
    selected_items = request.GET.getlist("items")
    selected_categories = request.GET.getlist("categories")
    selected_parties = request.GET.getlist("parties")
    selected_species = request.GET.getlist("species")

    # ✅ Date range filter
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # ✅ Quick filters (week, month, year)
    period = request.GET.get("period")

    if selected_items:
        queryset = queryset.filter(item__id__in=selected_items)

    if selected_categories:
        queryset = queryset.filter(item__category__id__in=selected_categories)

    if selected_parties:
        queryset = queryset.filter(purchase__party_name__in=selected_parties)

    if selected_species:
        queryset = queryset.filter(item__species__id__in=selected_species)

    # 📅 Date filters
    today = now().date()
    if start_date:
        queryset = queryset.filter(purchase__date__gte=start_date)
    if end_date:
        queryset = queryset.filter(purchase__date__lte=end_date)

    if period == "week":
        week_start = today - timedelta(days=today.weekday())  # Monday
        queryset = queryset.filter(purchase__date__gte=week_start)
    elif period == "month":
        queryset = queryset.filter(
            purchase__date__year=today.year, purchase__date__month=today.month
        )
    elif period == "year":
        queryset = queryset.filter(purchase__date__year=today.year)

    # ✅ Group & summary
    summary = (
        queryset.values(
            "purchase__date",
            "item__name",
            "item__category__name",
            "item__species__name",
            "purchase__party_name",
        )
        .annotate(
            total_qty=Sum("quantity"),
            total_amount=Sum("amount"),
            avg_rate=Sum("amount") / Sum("quantity"),
        )
        .order_by("purchase__date", "item__name")
    )

    return render(request, "adminapp/purchases/local_purchase_workout_summary.html", {
        "summary": summary,
        "items": items,
        "categories": categories,
        "species_list": species_list,
        "parties": parties,
        "selected_items": selected_items,
        "selected_categories": selected_categories,
        "selected_parties": selected_parties,
        "selected_species": selected_species,
        "start_date": start_date,
        "end_date": end_date,
        "period": period,
    })

# views.py
class PeelingShedSupplyListView(ListView):
    model = PeelingShedSupply
    template_name = 'adminapp/purchases/peeling_shed_supply_list.html'
    context_object_name = 'supplies'

class PeelingShedSupplyDeleteView(DeleteView):
    model = PeelingShedSupply
    template_name = 'adminapp/purchases/confirm_delete.html'
    success_url = reverse_lazy('adminapp:peeling_shed_supply_list')

def create_peeling_shed_supply(request):
    if request.method == 'POST':
        form = PeelingShedSupplyForm(request.POST)
        formset = PeelingShedPeelingTypeFormSet(request.POST, prefix='form')

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                supply = form.save()

                # Optional: calculate totals (if needed later)
                total_amount = 0

                for item_form in formset:
                    peeling_type = item_form.save(commit=False)
                    peeling_type.supply = supply
                    peeling_type.save()
                    total_amount += peeling_type.amount  # If total needed

                # Example: supply.total_amount = total_amount
                # supply.save()

                return redirect('adminapp:create_peeling_shed_supply')
        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.errors)
    else:
        form = PeelingShedSupplyForm()
        formset = PeelingShedPeelingTypeFormSet(prefix='form')

    return render(request, 'adminapp/purchases/peeling_shed_supply_form.html', {
        'form': form,
        'formset': formset,
    })

def get_spot_purchases_by_date(request):
    date = request.GET.get('date')
    spot_purchases = SpotPurchase.objects.filter(date=date)

    data = [
        {
            'id': purchase.id,
            'name': f"{purchase.voucher_number} - {purchase.spot.location_name}"
        }
        for purchase in spot_purchases
    ]
    return JsonResponse(data, safe=False)

def get_spot_purchase_items(request):
    spot_purchase_id = request.GET.get('spot_purchase_id')
    items = SpotPurchaseItem.objects.filter(purchase_id=spot_purchase_id)

    data = [
        {
            'id': item.id,
            'name': item.item.name,
            'quantity': float(item.quantity),          }
        for item in items
    ]
    return JsonResponse(data, safe=False)

def get_spot_purchase_item_details(request):
    item_id = request.GET.get('item_id')
    try:
        item = SpotPurchaseItem.objects.get(id=item_id)
        avg_weight = float(item.quantity) / float(item.boxes) if item.boxes else 0
        data = {
            'total_boxes': float(item.boxes or 0),
            'quantity': float(item.quantity),
            'average_weight': avg_weight
        }
    except SpotPurchaseItem.DoesNotExist:
        data = {
            'total_boxes': 0,
            'quantity': 0,
            'average_weight': 0
        }

    return JsonResponse(data)

def get_peeling_charge_by_shed(request):
    shed_id = request.GET.get('shed_id')
    data = []

    if shed_id:
        items = ShedItem.objects.filter(shed_id=shed_id)
        for i in items:
            data.append({
                'item_id': i.item.id,
                'item_name': i.item.name,
                'item_type_id': i.item_type.id if i.item_type else None,
                'item_type_name': i.item_type.name if i.item_type else '',
                'amount': float(i.amount),
                'unit': i.unit
            })
    return JsonResponse({'peeling_types': data})

class PeelingShedSupplyDetailView(DetailView):
    model = PeelingShedSupply
    template_name = 'adminapp/purchases/peeling_shed_supply_detail.html'
    context_object_name = 'supply'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['peeling_types'] = self.object.peeling_types.all()
        return context

def update_peeling_shed_supply(request, pk):
    supply = get_object_or_404(PeelingShedSupply, pk=pk)
    FreezingEntrySpotItemFormSet = inlineformset_factory(
    FreezingEntrySpot,
    FreezingEntrySpotItem,
    form=FreezingEntrySpotItemForm,
    extra=0,
    can_delete=True
)

    if request.method == 'POST':
        form = PeelingShedSupplyForm(request.POST, instance=supply)
        formset = PeelingShedPeelingTypeFormSet(request.POST, instance=supply, prefix='form')

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                supply = form.save()
                formset.save()  # saves peeling types linked to supply
            return redirect('adminapp:peeling_shed_supply_detail', pk=supply.pk)
        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.errors)
    else:
        form = PeelingShedSupplyForm(instance=supply)
        formset = PeelingShedPeelingTypeFormSet(instance=supply, prefix='form')

    return render(request, 'adminapp/purchases/update_peeling_shed_supply_form.html', {
        'form': form,
        'formset': formset,
        'is_update': True,
        'supply': supply,
    })


# create freezing entry spot
def create_freezing_entry_spot(request):
    if request.method == 'POST':
        form = FreezingEntrySpotForm(request.POST)
        formset = FreezingEntrySpotItemFormSet(request.POST, prefix='form')

        # Ensure shed queryset is set for each form in formset
        for f in formset.forms:
            f.fields['shed'].queryset = Shed.objects.all()

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                freezing_entry = form.save(commit=False)

                total_kg = Decimal(0)
                total_slab = Decimal(0)
                total_c_s = Decimal(0)
                total_usd = Decimal(0)
                total_inr = Decimal(0)
                yield_percentages = []

                for f in formset:
                    if f.cleaned_data and not f.cleaned_data.get('DELETE', False):
                        slab = f.cleaned_data.get('slab_quantity') or Decimal(0)
                        cs = f.cleaned_data.get('c_s_quantity') or Decimal(0)
                        kg = f.cleaned_data.get('kg') or Decimal(0)
                        usd = f.cleaned_data.get('usd_rate_item') or Decimal(0)
                        inr = f.cleaned_data.get('usd_rate_item_to_inr') or Decimal(0)
                        yield_percent = f.cleaned_data.get('yield_percentage')

                        total_slab += slab
                        total_c_s += cs
                        total_kg += kg
                        total_usd += usd
                        total_inr += inr
                        if yield_percent is not None:
                            yield_percentages.append(yield_percent)

                # Assign totals
                freezing_entry.total_slab = total_slab
                freezing_entry.total_c_s = total_c_s
                freezing_entry.total_kg = total_kg
                freezing_entry.total_usd = total_usd
                freezing_entry.total_inr = total_inr
                freezing_entry.total_yield_percentage = (
                    sum(yield_percentages) if yield_percentages else Decimal(0)
                )

                # Save main form and formset
                freezing_entry.save()
                formset.instance = freezing_entry
                formset.save()

            return redirect('adminapp:freezing_entry_spot_list')
        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.errors)
    else:
        form = FreezingEntrySpotForm()
        form.fields['spot_agent'].queryset = PurchasingAgent.objects.none()
        form.fields['spot_supervisor'].queryset = PurchasingSupervisor.objects.none()
        formset = FreezingEntrySpotItemFormSet(prefix='form')

    return render(request, 'adminapp/freezing/freezing_entry_spot_create.html', {
        'form': form,
        'formset': formset,
    })

def get_spots_by_date(request):
    date = request.GET.get('date')
    spots = SpotPurchase.objects.filter(date=date).values('id', 'spot__location_name' , 'voucher_number')
    return JsonResponse({'spots': list(spots)})

def get_spot_details(request):
    spot_id = request.GET.get('spot_id')

    try:
        spot = SpotPurchase.objects.select_related('agent', 'supervisor').get(id=spot_id)

        # ✅ Fetch all related items for this spot purchase
        items = SpotPurchaseItem.objects.filter(purchase=spot).select_related("item")

        items_data = [
            {
                "id": item.item.id,
                "name": item.item.name,
                "quantity": str(item.quantity),  # ensure JSON serializable
            }
            for item in items
        ]

        data = {
            "agent_id": spot.agent.id,
            "agent_name": str(spot.agent),  # e.g. "John - AG001"
            "supervisor_id": spot.supervisor.id,
            "supervisor_name": str(spot.supervisor),  # e.g. "Anita - 9876543210"
            "items": items_data,  # ✅ added items list
        }

        # Debug print for terminal
        print("Spot Purchase Details:", data)

        return JsonResponse(data)

    except SpotPurchase.DoesNotExist:
        return JsonResponse({"error": "SpotPurchase not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_sheds_by_date(request):
    date_str = request.GET.get('date')  # Spot Purchase Date
    if not date_str:
        return JsonResponse({'error': 'Missing date'}, status=400)

    # Convert string to Python date
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    # Fetch supplies for that spot purchase date
    supplies = PeelingShedSupply.objects.filter(
        spot_purchase__date=date_obj
    ).select_related('shed', 'spot_purchase_item__item')

    seen_pairs = set()
    result = []

    for supply in supplies:
        shed = supply.shed
        item = supply.spot_purchase_item.item
        key = (shed.id, item.id)

        if key not in seen_pairs:
            seen_pairs.add(key)

            # Yield calculation example
            try:
                total_qty = supply.spot_purchase_item.quantity  # adjust field name
                qty_received = supply.quantity_received_shed
                yield_percent = (qty_received / total_qty) * 100 if total_qty else 0
            except:
                yield_percent = 0

            result.append({
                'shed_id': shed.id,
                'shed_name': str(shed),
                'item_id': item.id,
                'item_name': str(item),
                'boxes_received_shed': supply.boxes_received_shed,
                'quantity_received_shed': str(supply.quantity_received_shed),
                'yield_percent': round(yield_percent, 2)
            })

    return JsonResponse({'sheds': result})

def get_unit_details(request):
    unit_id = request.GET.get('unit_id')
    try:
        unit = PackingUnit.objects.get(pk=unit_id)
        return JsonResponse({
            'precision': float(unit.precision),
            'factor': float(unit.factor)
        })
    except PackingUnit.DoesNotExist:
        return JsonResponse({'error': 'Unit not found'}, status=404)

def get_dollar_rate(request):
    settings_obj = Settings.objects.filter(is_active=True).order_by('-created_at').first()
    if settings_obj:
        return JsonResponse({
            'dollar_rate_to_inr': float(settings_obj.dollar_rate_to_inr)
        })
    return JsonResponse({'error': 'Settings not found'}, status=404)

def freezing_entry_spot_list(request):
    entries = FreezingEntrySpot.objects.all()
    return render(request, 'adminapp/freezing/freezing_entry_spot_list.html', {'entries': entries})

def get_spot_purchase_items_by_date(request):
    date = request.GET.get("date")
    if not date:
        return JsonResponse({"error": "Missing date"}, status=400)

    items = SpotPurchaseItem.objects.filter(
        purchase__date=date
    ).select_related("item")

    data = []
    for item in items:
        # ✅ print to terminal
        print(f"Item: {item.item.name}, Quantity: {item.quantity}")

        data.append({
            "id": item.id,
            "name": str(item.item),
            "quantity": str(item.quantity),
        })

    return JsonResponse({"items": data})

def delete_freezing_entry_spot(request, pk):
    entry = get_object_or_404(FreezingEntrySpot, pk=pk)
    if request.method == 'POST':
        entry.delete()
        return redirect('adminapp:freezing_entry_spot_list')
    return render(request, 'adminapp/confirm_delete.html', {'entry': entry})

class FreezingEntrySpotDetailView(View):
    template_name = "adminapp/freezing/freezing_entry_spot_detail.html"

    def get(self, request, pk):
        entry = get_object_or_404(FreezingEntrySpot, pk=pk)
        items = entry.items.select_related(
            "shed", "item", "unit", "glaze",
            "freezing_category", "brand", "species",
            "peeling_type", "grade"
        )

        context = {
            "entry": entry,
            "items": items,
        }
        return render(request, self.template_name, context)

def freezing_entry_spot_update(request, pk):
    freezing_entry = get_object_or_404(FreezingEntrySpot, pk=pk)

    if request.method == "POST":
        form = FreezingEntrySpotForm(request.POST, instance=freezing_entry)
        formset = FreezingEntrySpotItemFormSet(
            request.POST, instance=freezing_entry, prefix="form"
        )

        # Ensure shed queryset is set for each form in formset
        for f in formset.forms:
            f.fields["shed"].queryset = Shed.objects.all()

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                entry = form.save(commit=False)

                total_kg = Decimal(0)
                total_slab = Decimal(0)
                total_c_s = Decimal(0)
                total_usd = Decimal(0)
                total_inr = Decimal(0)
                yield_percentages = []

                for f in formset:
                    if f.cleaned_data and not f.cleaned_data.get("DELETE", False):
                        slab = f.cleaned_data.get("slab_quantity") or Decimal(0)
                        cs = f.cleaned_data.get("c_s_quantity") or Decimal(0)
                        kg = f.cleaned_data.get("kg") or Decimal(0)
                        usd = f.cleaned_data.get("usd_rate_item") or Decimal(0)
                        inr = f.cleaned_data.get("usd_rate_item_to_inr") or Decimal(0)
                        yield_percent = f.cleaned_data.get("yield_percentage")

                        total_slab += slab
                        total_c_s += cs
                        total_kg += kg
                        total_usd += usd
                        total_inr += inr
                        if yield_percent is not None:
                            yield_percentages.append(yield_percent)

                # Assign recalculated totals
                entry.total_slab = total_slab
                entry.total_c_s = total_c_s
                entry.total_kg = total_kg
                entry.total_usd = total_usd
                entry.total_inr = total_inr
                entry.total_yield_percentage = (
                    sum(yield_percentages) if yield_percentages else Decimal(0)
                )

                entry.save()
                formset.instance = entry
                formset.save()

            return redirect("adminapp:freezing_entry_spot_list")
        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.errors)

    else:
        form = FreezingEntrySpotForm(instance=freezing_entry)
        # preload dependent dropdowns
        form.fields["spot_agent"].queryset = PurchasingAgent.objects.all()
        form.fields["spot_supervisor"].queryset = PurchasingSupervisor.objects.all()
        formset = FreezingEntrySpotItemFormSet(
            instance=freezing_entry, prefix="form"
        )

    return render(
        request,
        "adminapp/freezing/freezing_entry_spot_update.html",
        {"form": form, "formset": formset, "entry": freezing_entry},
    )






# Create Freezing Entry Local
def create_freezing_entry_local(request):
    if request.method == 'POST':
        form = FreezingEntryLocalForm(request.POST)
        formset = FreezingEntryLocalItemFormSet(request.POST, prefix='form')

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                freezing_entry = form.save(commit=False)
                freezing_entry.created_by = request.user
                freezing_entry.save()

                dollar_rate_to_inr = Decimal(0)

                # Fetch Dollar Rate from Settings or latest table
                try:
                    from .models import DollarRate
                    dollar_obj = DollarRate.objects.latest("id")
                    dollar_rate_to_inr = dollar_obj.rate
                except:
                    pass

                for f in formset.forms:
                    if not f.cleaned_data or f.cleaned_data.get("DELETE"):
                        continue

                    item = f.save(commit=False)
                    item.freezing_entry = freezing_entry

                    # Auto-calc fields
                    kg = f.cleaned_data.get("kg") or Decimal(0)
                    usd_rate_per_kg = f.cleaned_data.get("usd_rate_per_kg") or Decimal(0)

                    usd_item = kg * usd_rate_per_kg
                    inr_item = usd_item * dollar_rate_to_inr

                    item.usd_rate_item = usd_item
                    item.usd_rate_item_to_inr = inr_item

                    item.save()

                messages.success(request, "Freezing Entry created successfully ✅")
                return redirect("adminapp:freezing_entry_local_list")

        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", [f.errors for f in formset.forms])
    else:
        form = FreezingEntryLocalForm()
        formset = FreezingEntryLocalItemFormSet(prefix='form')

    return render(request, "adminapp/freezing/freezing_entry_local_create.html", {
        "form": form,
        "formset": formset,
    })

def get_parties_by_date(request):
    date = request.GET.get('date')
    parties = LocalPurchase.objects.filter(date=date).values(
        'id', 'party_name', 'voucher_number'
    )
    return JsonResponse({'parties': list(parties)})

def get_party_details(request):
    party_id = request.GET.get('party_id')
    try:
        purchase = LocalPurchase.objects.get(id=party_id)

        # assuming LocalPurchaseItem has FK → ItemGrade as `grade`
        items = purchase.items.all().values(
            'id',
            'item__id',
            'item__name',
            'quantity',
            'rate',
            'amount',
            'grade__id',
            'grade__grade',             # grade text
            'grade__species__name',     # ✅ species name
            'item_quality__quality',   # ✅ correct field
            'item_quality__code',      
        )

        data = {
            'party_name': purchase.party_name,
            'voucher_number': purchase.voucher_number,
            'items': list(items),
        }
        return JsonResponse(data)

    except LocalPurchase.DoesNotExist:
        return JsonResponse({'error': 'LocalPurchase not found'}, status=404)

def get_unit_details_local(request):
    unit_id = request.GET.get('unit_id')
    try:
        unit = PackingUnit.objects.get(pk=unit_id)
        return JsonResponse({
            'precision': float(unit.precision),
            'factor': float(unit.factor)
        })
    except PackingUnit.DoesNotExist:
        return JsonResponse({'error': 'Unit not found'}, status=404)

def get_dollar_rate_local(request):
    settings_obj = Settings.objects.filter(is_active=True).order_by('-created_at').first()
    if settings_obj:
        return JsonResponse({
            'dollar_rate_to_inr': float(settings_obj.dollar_rate_to_inr)
        })
    return JsonResponse({'error': 'Settings not found'}, status=404)

def freezing_entry_local_list(request):
    entries = FreezingEntryLocal.objects.all()
    return render(request, 'adminapp/freezing/freezing_entry_local_list.html', {'entries': entries})

def delete_freezing_entry_local(request, pk):
    entry = get_object_or_404(FreezingEntryLocal, pk=pk)
    if request.method == 'POST':
        entry.delete()
        return redirect('adminapp:freezing_entry_local_list')
    return render(request, 'adminapp/freezing/freezing_entry_local_confirm_delete.html', {'entry': entry})

def freezing_entry_local_detail(request, pk):
    entry = get_object_or_404(FreezingEntryLocal, pk=pk)
    items = entry.items.all().select_related(
        'processing_center',
        'store',
        'item',
        'unit',
        'glaze',
        'freezing_category',
        'brand',
        'species',
        'peeling_type',
        'grade'
    )

    context = {
        'entry': entry,
        'items': items
    }
    return render(request, 'adminapp/freezing/freezing_entry_local_detail.html', context)

def freezing_entry_local_update(request, pk):
    freezing_entry = get_object_or_404(FreezingEntryLocal, pk=pk)
    FreezingEntryLocalItemFormSet = inlineformset_factory(
        FreezingEntryLocal,
        FreezingEntryLocalItem,
        form=FreezingEntryLocalItemForm,
        extra=0,
        can_delete=True  # This is crucial for deletion functionality
    )
    
    if request.method == "POST":
        form = FreezingEntryLocalForm(request.POST, instance=freezing_entry)
        formset = FreezingEntryLocalItemFormSet(
            request.POST, instance=freezing_entry, prefix="form"
        )
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Save the main form first
                freezing_entry = form.save(commit=False)
                freezing_entry.save()

                # Get dollar rate
                dollar_rate_to_inr = Decimal(0)
                try:
                    from .models import DollarRate
                    dollar_obj = DollarRate.objects.latest("id")
                    dollar_rate_to_inr = dollar_obj.rate
                except:
                    pass

                # Process each form manually to handle calculations before saving
                instances = formset.save(commit=False)
                
                # Handle deletions first
                for obj in formset.deleted_objects:
                    obj.delete()
                
                # Process remaining instances
                for instance in instances:
                    # Get the corresponding form to access cleaned_data
                    form_data = None
                    for form in formset.forms:
                        if hasattr(form, 'instance') and form.instance == instance:
                            form_data = form.cleaned_data
                            break
                    
                    if form_data:
                        # Auto-calculate fields from form data
                        slab_quantity = form_data.get('slab_quantity') or Decimal(0)
                        usd_rate_per_kg = form_data.get('usd_rate_per_kg') or Decimal(0)
                        
                        # Get unit details for calculations (you might need to adjust this)
                        unit = form_data.get('unit')
                        precision = Decimal(2)  # Default precision
                        factor = Decimal(0.25)  # Default factor
                        
                        if unit:
                            try:
                                # Fetch unit details if you have a Unit model
                                # unit_obj = Unit.objects.get(id=unit.id)
                                # precision = unit_obj.precision
                                # factor = unit_obj.factor
                                pass
                            except:
                                pass
                        
                        # Calculate dependent fields
                        if slab_quantity and precision:
                            instance.c_s_quantity = slab_quantity / precision
                        else:
                            instance.c_s_quantity = Decimal(0)
                            
                        if slab_quantity and factor:
                            instance.kg = slab_quantity * factor
                        else:
                            instance.kg = Decimal(0)
                        
                        # Calculate USD amounts
                        if instance.kg and usd_rate_per_kg:
                            instance.usd_rate_item = instance.kg * usd_rate_per_kg
                        else:
                            instance.usd_rate_item = Decimal(0)
                        
                        # Calculate INR amount
                        if instance.usd_rate_item and dollar_rate_to_inr:
                            instance.usd_rate_item_to_inr = instance.usd_rate_item * dollar_rate_to_inr
                        else:
                            instance.usd_rate_item_to_inr = Decimal(0)
                    
                    instance.freezing_entry = freezing_entry
                    instance.save()

                messages.success(request, "Freezing Entry updated successfully ✅")
                return redirect("adminapp:freezing_entry_local_list")
        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", [f.errors for f in formset.forms if f.errors])
            print("Formset Non Form Errors:", formset.non_form_errors())
    else:
        form = FreezingEntryLocalForm(instance=freezing_entry)
        formset = FreezingEntryLocalItemFormSet(
            instance=freezing_entry, prefix="form"
        )
        
    return render(
        request,
        "adminapp/freezing/freezing_entry_local_update.html",
        {"form": form, "formset": formset, "entry": freezing_entry},
    )

def get_items_by_local_date(request):
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'items': []})
    
    # Adjust this query based on your LocalPurchase model structure
    items = LocalPurchaseItem.objects.filter(
        local_purchase__purchase_date=date
    ).select_related('item').values(
        'item_id', 
        'item__name'
    ).annotate(
        item_name=F('item__name')
    ).distinct()
    
    return JsonResponse({'items': list(items)})

@require_http_methods(["GET"])
@csrf_exempt  # Remove this if CSRF protection is needed
def get_item_qualities(request):
    item_id = request.GET.get("item_id")
    
    # If item_id is missing, return empty JSON array
    if not item_id:
        return JsonResponse([], safe=False)
    
    # Validate item_id is not empty (allow alphanumeric IDs)
    item_id = item_id.strip()
    if not item_id:
        return JsonResponse({"error": "Invalid item_id"}, status=400)

    try:
        # Filter qualities for the given item
        qualities = ItemQuality.objects.filter(item_id=item_id).values("id", "quality")
        
        # Return as JSON
        return JsonResponse(list(qualities), safe=False)
    
    except Exception as e:
        # Handle any database errors
        return JsonResponse({"error": "Database error occurred"}, status=500)


class FreezingWorkOutView(View):
    template_name = "adminapp/freezing/freezing_workout.html"

    def get_summary(self, queryset, has_yield=True):
        """
        Build aggregated summary for a given queryset.
        `has_yield` flag is used because Spot has yield_percentage but Local does not.
        """
        qs = (
            queryset
            .select_related(
                'item', 'grade', 'species', 'peeling_type', 'brand',
                'glaze', 'unit', 'freezing_category'
            )
            .values(
                'item__name',
                'grade__grade',
                'species__name',
                'peeling_type__name',
                'brand__name',
                'glaze__percentage',
                'unit__unit_code',
                'freezing_category__name',
            )
        )

        annotations = {
            'total_slab': Coalesce(Sum('slab_quantity'), V(0), output_field=DecimalField()),
            'total_c_s': Coalesce(Sum('c_s_quantity'), V(0), output_field=DecimalField()),
            'total_kg': Coalesce(Sum('kg'), V(0), output_field=DecimalField()),
            'total_usd': Coalesce(Sum('usd_rate_item'), V(0), output_field=DecimalField()),
            'total_inr': Coalesce(Sum('usd_rate_item_to_inr'), V(0), output_field=DecimalField()),
        }

        if has_yield:
            annotations.update({
                'total_yield_sum': Coalesce(Sum('yield_percentage'), V(0), output_field=DecimalField()),
                'count_yield': Count('id'),
            })

        return qs.annotate(**annotations).order_by(
            'item__name', 'grade__grade', 'species__name',
            'peeling_type__name', 'brand__name'
        )

    def get(self, request):
        # Spot has yield, Local does not
        spot_summary = self.get_summary(FreezingEntrySpotItem.objects.all(), has_yield=True)
        local_summary = self.get_summary(FreezingEntryLocalItem.objects.all(), has_yield=False)

        # Merge spot + local summaries
        combined_data = {}
        for dataset, has_yield in [(spot_summary, True), (local_summary, False)]:
            for row in dataset:
                key = (
                    row['item__name'],
                    row['grade__grade'],
                    row['species__name'],
                    row['peeling_type__name'],
                    row['brand__name'],
                    str(row['glaze__percentage']),
                    row['unit__unit_code'],
                    row['freezing_category__name'],
                )

                if key not in combined_data:
                    combined_data[key] = {
                        'item_name': row['item__name'],
                        'grade_name': row['grade__grade'],
                        'species_name': row['species__name'],
                        'peeling_type_name': row['peeling_type__name'],
                        'brand_name': row['brand__name'],
                        'glaze_percentage': row['glaze__percentage'],
                        'unit_code': row['unit__unit_code'],
                        'freezing_category_name': row['freezing_category__name'],
                        'total_slab': Decimal(0),
                        'total_c_s': Decimal(0),
                        'total_kg': Decimal(0),
                        'total_usd': Decimal(0),
                        'total_inr': Decimal(0),
                        'total_yield_sum': Decimal(0),
                        'count_yield': 0,
                    }

                combined_data[key]['total_slab'] += row['total_slab']
                combined_data[key]['total_c_s'] += row['total_c_s']
                combined_data[key]['total_kg'] += row['total_kg']
                combined_data[key]['total_usd'] += row['total_usd']
                combined_data[key]['total_inr'] += row['total_inr']

                # Only Spot rows have yield
                if has_yield:
                    combined_data[key]['total_yield_sum'] += row['total_yield_sum']
                    combined_data[key]['count_yield'] += row['count_yield']

        # Compute avg yield %
        for val in combined_data.values():
            if val['count_yield'] > 0:
                val['avg_yield'] = val['total_yield_sum'] / val['count_yield']
            else:
                val['avg_yield'] = Decimal(0)

        context = {
            'spot_summary': spot_summary,
            'local_summary': local_summary,
            'combined_summary': list(combined_data.values()),
        }
        return render(request, self.template_name, context)


# PRE SHIPMENT WORK OUT 
class PreShipmentWorkOutCreateAndSummaryView(View):
    template_name = "adminapp/create_preshipment_workout.html"

    def get_summary(self, queryset):
        """Aggregate summary data for freezing items."""
        return (
            queryset
            .select_related(
                'item', 'grade', 'species', 'peeling_type', 'brand',
                'glaze', 'unit', 'freezing_category'
            )
            .values(
                'item__name',
                'grade__grade',
                'species__name',
                'peeling_type__name',
                'brand__name',
                'glaze__percentage',
                'unit__unit_code',
                'freezing_category__name',
            )
            .annotate(
                total_slab=Coalesce(Sum('slab_quantity'), V(0), output_field=DecimalField()),
                total_c_s=Coalesce(Sum('c_s_quantity'), V(0), output_field=DecimalField()),
                total_kg=Coalesce(Sum('kg'), V(0), output_field=DecimalField()),
                # Removed yield_percentage related calculations as the field doesn't exist
                count_records=Count('id'),
                total_usd=Coalesce(Sum('usd_rate_item'), V(0), output_field=DecimalField()),
                total_inr=Coalesce(Sum('usd_rate_item_to_inr'), V(0), output_field=DecimalField()),
                avg_usd_per_kg=Coalesce(Avg('usd_rate_per_kg'), V(0), output_field=DecimalField()),
            )
            .order_by('item__name', 'grade__grade', 'species__name')
        )

    def get_combined_summary(self, filters):
        """Combine spot and local summaries."""
        spot_summary = self.get_summary(FreezingEntrySpotItem.objects.filter(**filters))
        local_summary = self.get_summary(FreezingEntryLocalItem.objects.filter(**filters))

        combined_data = {}
        for dataset in [spot_summary, local_summary]:
            for row in dataset:
                key = (
                    row['item__name'],
                    row['grade__grade'],
                    row['species__name'],
                    row['peeling_type__name'],
                    row['brand__name'],
                    str(row['glaze__percentage']),
                    row['unit__unit_code'],
                    row['freezing_category__name'],
                )
                if key not in combined_data:
                    combined_data[key] = {
                        'item_name': row['item__name'],
                        'grade_name': row['grade__grade'],
                        'species_name': row['species__name'],
                        'peeling_type_name': row['peeling_type__name'],
                        'brand_name': row['brand__name'],
                        'glaze_percentage': row['glaze__percentage'],
                        'unit_code': row['unit__unit_code'],
                        'freezing_category_name': row['freezing_category__name'],
                        'total_slab': Decimal(0),
                        'total_c_s': Decimal(0),
                        'total_kg': Decimal(0),
                        'count_records': 0,
                        'total_usd': Decimal(0),
                        'total_inr': Decimal(0),
                        'avg_usd_per_kg_sum': Decimal(0),
                        'avg_usd_per_kg_count': 0,
                    }
                combined_data[key]['avg_usd_per_kg_sum'] += row['avg_usd_per_kg']
                combined_data[key]['avg_usd_per_kg_count'] += 1
                combined_data[key]['total_slab'] += row['total_slab']
                combined_data[key]['total_c_s'] += row['total_c_s']
                combined_data[key]['total_kg'] += row['total_kg']
                combined_data[key]['total_usd'] += row['total_usd']
                combined_data[key]['total_inr'] += row['total_inr']
                combined_data[key]['count_records'] += row['count_records']

        for val in combined_data.values():
            # Removed avg_yield calculation as yield_percentage field doesn't exist
            
            if val['avg_usd_per_kg_count'] > 0:
                val['avg_usd_per_kg'] = val['avg_usd_per_kg_sum'] / val['avg_usd_per_kg_count']
            else:
                val['avg_usd_per_kg'] = Decimal(0)

        return list(combined_data.values())
    
    def get(self, request):
        filters = {}
        if request.GET.get("item"):
            filters["item_id"] = request.GET["item"]
        if request.GET.get("unit"):
            filters["unit_id"] = request.GET["unit"]
        if request.GET.get("glaze"):
            filters["glaze_id"] = request.GET["glaze"]
        if request.GET.get("category"):
            filters["freezing_category_id"] = request.GET["category"]
        if request.GET.get("brand"):
            filters["brand_id"] = request.GET["brand"]

        workout_form = PreShipmentWorkOutForm()
        formset = PreShipmentWorkOutItemFormSet(prefix="items", instance=PreShipmentWorkOut())

        context = {
            "workout_form": workout_form,
            "formset": formset,
            "combined_summary": self.get_combined_summary(filters),
            "items": Item.objects.all(),
            "units": PackingUnit.objects.all(),
            "glazes": GlazePercentage.objects.all(),
            "categories": FreezingCategory.objects.all(),
            "brands": ItemBrand.objects.all(),
            "request": request
        }
        return render(request, self.template_name, context)

    def post(self, request):
        filters = {}
        if request.GET.get("item"):
            filters["item_id"] = request.GET["item"]
        if request.GET.get("unit"):
            filters["unit_id"] = request.GET["unit"]
        if request.GET.get("glaze"):
            filters["glaze_id"] = request.GET["glaze"]
        if request.GET.get("category"):
            filters["freezing_category_id"] = request.GET["category"]
        if request.GET.get("brand"):
            filters["brand_id"] = request.GET["brand"]

        workout_form = PreShipmentWorkOutForm(request.POST)

        if workout_form.is_valid():
            workout = workout_form.save(commit=False)
            formset = PreShipmentWorkOutItemFormSet(request.POST, prefix="items", instance=workout)

            # ✅ Dynamically adjust species & peeling_type choices for validation
            selected_item = workout_form.cleaned_data.get("item")
            if selected_item:
                for f in formset.forms:
                    f.fields["species"].queryset = Species.objects.filter(item=selected_item)
                    f.fields["peeling_type"].queryset = ItemType.objects.filter(item=selected_item)

            if formset.is_valid():
                try:
                    with transaction.atomic():
                        workout.save()
                        # ✅ Backend profit/loss calculation
                        for f in formset:
                            obj = f.save(commit=False)
                            buy_inr = obj.usd_rate_item_to_inr or Decimal(0)
                            sell_inr = obj.usd_rate_item_to_inr_get or Decimal(0)
                            diff = sell_inr - buy_inr
                            if diff >= 0:
                                obj.profit = diff
                                obj.loss = Decimal(0)
                            else:
                                obj.profit = Decimal(0)
                                obj.loss = abs(diff)
                            obj.save()
                    messages.success(request, "Pre-Shipment WorkOut created successfully.")
                    return redirect(request.path)
                except Exception as e:
                    messages.error(request, f"Error saving data: {e}")
            else:
                print("Formset errors:", formset.errors)  # DEBUG
                messages.error(request, "Please correct the item form errors below.")
        else:
            print("Workout form errors:", workout_form.errors)  # DEBUG
            formset = PreShipmentWorkOutItemFormSet(request.POST, prefix="items", instance=PreShipmentWorkOut())
            messages.error(request, "Please correct the workout form errors below.")

        context = {
            "workout_form": workout_form,
            "formset": formset,
            "combined_summary": self.get_combined_summary(filters),
            "items": Item.objects.all(),
            "units": PackingUnit.objects.all(),
            "glazes": GlazePercentage.objects.all(),
            "categories": FreezingCategory.objects.all(),
            "brands": ItemBrand.objects.all(),
            "request": request
        }
        return render(request, self.template_name, context)

def get_species_for_item(request):
    item_id = request.GET.get("item_id")
    species_list = []

    if item_id:
        species_qs = Species.objects.filter(item_id=item_id)
        species_list = list(species_qs.values("id", "name"))

    return JsonResponse({"species": species_list})

def get_peeling_for_item(request):
    item_id = request.GET.get("item_id")
    peeling_list = []

    if item_id:
        peeling_qs = ItemType.objects.filter(item_id=item_id)
        peeling_list = list(peeling_qs.values("id", "name"))

    return JsonResponse({"peeling_types": peeling_list})

def get_grade_for_species(request):
    species_id = request.GET.get("species_id")
    grade_list = []

    if species_id:
        grade_qs = ItemGrade.objects.filter(species_id=species_id)
        grade_list = list(grade_qs.values("id", "grade"))

    return JsonResponse({"grades": grade_list})

def get_dollar_rate_pre_workout(request):
    """Return the current dollar to INR rate for Pre-Shipment WorkOut."""
    settings_obj = Settings.objects.filter(is_active=True).order_by('-created_at').first()
    if settings_obj:
        return JsonResponse({
            'dollar_rate_to_inr': float(settings_obj.dollar_rate_to_inr)
        })
    return JsonResponse({'error': 'Settings not found'}, status=404)

class PreShipmentWorkOutListView(ListView):
    model = PreShipmentWorkOut
    template_name = "adminapp/preshipment_workout_list.html"
    context_object_name = "workouts"
    paginate_by = 20  # Optional: pagination

    def get_queryset(self):
        queryset = super().get_queryset().select_related()
        # Optional filtering
        if self.request.GET.get("item"):
            queryset = queryset.filter(item_id=self.request.GET["item"])
        return queryset.order_by("-id")  # Latest first

class PreShipmentWorkOutDeleteView(DeleteView):
    model = PreShipmentWorkOut
    template_name = "adminapp/confirm_delete.html"
    success_url = reverse_lazy("adminapp:preshipment_workout_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Pre-Shipment WorkOut '{obj}' deleted successfully.")
        return super().delete(request, *args, **kwargs)

class PreShipmentWorkOutDetailView(DetailView):
    model = PreShipmentWorkOut
    template_name = "adminapp/detail_preshipment_workout.html"
    context_object_name = "workout"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # All related items
        items_qs = PreShipmentWorkOutItem.objects.filter(workout=self.object)

        # Summary calculation
        summary = items_qs.aggregate(
            total_cartons=Coalesce(Sum("cartons"), Decimal(0), output_field=DecimalField()),
            total_quantity=Coalesce(Sum("quantity"), Decimal(0), output_field=DecimalField()),
            total_usd_rate_item=Coalesce(Sum("usd_rate_item"), Decimal(0), output_field=DecimalField()),
            total_usd_rate_item_get=Coalesce(Sum("usd_rate_item_get"), Decimal(0), output_field=DecimalField()),
            total_usd_inr=Coalesce(Sum("usd_rate_item_to_inr"), Decimal(0), output_field=DecimalField()),
            total_usd_inr_get=Coalesce(Sum("usd_rate_item_to_inr_get"), Decimal(0), output_field=DecimalField()),
            avg_usd_per_kg=Coalesce(Avg("usd_rate_per_kg"), Decimal(0), output_field=DecimalField()),
            avg_usd_per_kg_get=Coalesce(Avg("usd_rate_per_kg_get"), Decimal(0), output_field=DecimalField()),
            total_profit=Coalesce(Sum("profit"), Decimal(0), output_field=DecimalField()),
            total_loss=Coalesce(Sum("loss"), Decimal(0), output_field=DecimalField()),
            item_count=Count("id")
        )

        context.update({
            "items": items_qs,
            "summary": summary
        })
        return context


# purchase Report 
def spot_purchase_report(request):
    items = Item.objects.all()
    spots = PurchasingSpot.objects.all()
    agents = PurchasingAgent.objects.all()
    categories = ItemCategory.objects.all()

    queryset = SpotPurchaseItem.objects.select_related(
        "purchase", "item", "purchase__spot", "purchase__agent"
    )

    # ✅ Multi-select filters
    selected_items = request.GET.getlist("items")
    selected_spots = request.GET.getlist("spots")
    selected_agents = request.GET.getlist("agents")
    selected_categories = request.GET.getlist("categories")
    date_filter = request.GET.get("date_filter")

    # ✅ Date range filter
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if selected_items:
        queryset = queryset.filter(item__id__in=selected_items)
    if selected_spots:
        queryset = queryset.filter(purchase__spot__id__in=selected_spots)
    if selected_agents:
        queryset = queryset.filter(purchase__agent__id__in=selected_agents)
    if selected_categories:
        queryset = queryset.filter(item__category__id__in=selected_categories)

    # ✅ Quick date filter
    if date_filter == "week":
        queryset = queryset.filter(purchase__date__gte=now().date() - timedelta(days=7))
    elif date_filter == "month":
        queryset = queryset.filter(purchase__date__month=now().month)
    elif date_filter == "year":
        queryset = queryset.filter(purchase__date__year=now().year)

    # ✅ Custom date range
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            queryset = queryset.filter(purchase__date__range=[start, end])
        except:
            pass

    # ✅ Group & summary
    summary = (
        queryset.values(
            "item__name",
            "item__category__name",
            "purchase__spot__location_name",
            "purchase__agent__name",
            "purchase__date",
        )
        .annotate(
            total_quantity=Sum("quantity"),
            total_amount=Sum("amount"),
            avg_rate=Sum(F("amount"), output_field=FloatField()) / Sum(F("quantity"), output_field=FloatField()),
        )
        .order_by("purchase__date")
    )

    # ✅ Check if print/export requested
    action = request.GET.get("action")
    print_mode = request.GET.get("print")  # Check for print parameter

    # Handle print request
    if action == "print" or print_mode == "1":
        return render(
            request,
            "adminapp/report/spot_purchase_report_print.html",
            {"summary": summary, "start_date": start_date, "end_date": end_date},
        )

    if action == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="spot_purchase_report.csv"'
        writer = csv.writer(response)
        writer.writerow(["Date", "Item", "Category", "Spot", "Agent", "Quantity", "Amount", "Avg Rate"])
        for row in summary:
            writer.writerow([
                row["purchase__date"],
                row["item__name"],
                row["item__category__name"],
                row["purchase__spot__location_name"],
                row["purchase__agent__name"],
                row["total_quantity"],
                row["total_amount"],
                round(row["avg_rate"], 2) if row["avg_rate"] else 0,
            ])
        return response

    if action == "excel":
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Report")

        headers = ["Date", "Item", "Category", "Spot", "Agent", "Quantity", "Amount", "Avg Rate"]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        for row_idx, row in enumerate(summary, start=1):
            worksheet.write(row_idx, 0, str(row["purchase__date"]))
            worksheet.write(row_idx, 1, row["item__name"])
            worksheet.write(row_idx, 2, row["item__category__name"])
            worksheet.write(row_idx, 3, row["purchase__spot__location_name"])
            worksheet.write(row_idx, 4, row["purchase__agent__name"])
            worksheet.write(row_idx, 5, row["total_quantity"])
            worksheet.write(row_idx, 6, row["total_amount"])
            worksheet.write(row_idx, 7, round(row["avg_rate"], 2) if row["avg_rate"] else 0)

        workbook.close()
        output.seek(0)

        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="spot_purchase_report.xlsx"'
        return response

    return render(
        request,
        "adminapp/report/spot_purchase_report.html",
        {
            "summary": summary,
            "items": items,
            "spots": spots,
            "agents": agents,
            "categories": categories,
            "selected_items": selected_items,
            "selected_spots": selected_spots,
            "selected_agents": selected_agents,
            "selected_categories": selected_categories,
            "date_filter": date_filter,
            "start_date": start_date,
            "end_date": end_date,
        },
    )

def spot_purchase_report_print(request):
    """Separate view specifically for print format"""
    items = Item.objects.all()
    spots = PurchasingSpot.objects.all()
    agents = PurchasingAgent.objects.all()
    categories = ItemCategory.objects.all()

    queryset = SpotPurchaseItem.objects.select_related(
        "purchase", "item", "purchase__spot", "purchase__agent"
    )

    # Apply the same filters as main view
    selected_items = request.GET.getlist("items")
    selected_spots = request.GET.getlist("spots")
    selected_agents = request.GET.getlist("agents")
    selected_categories = request.GET.getlist("categories")
    date_filter = request.GET.get("date_filter")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if selected_items:
        queryset = queryset.filter(item__id__in=selected_items)
    if selected_spots:
        queryset = queryset.filter(purchase__spot__id__in=selected_spots)
    if selected_agents:
        queryset = queryset.filter(purchase__agent__id__in=selected_agents)
    if selected_categories:
        queryset = queryset.filter(item__category__id__in=selected_categories)

    if date_filter == "week":
        queryset = queryset.filter(purchase__date__gte=now().date() - timedelta(days=7))
    elif date_filter == "month":
        queryset = queryset.filter(purchase__date__month=now().month)
    elif date_filter == "year":
        queryset = queryset.filter(purchase__date__year=now().year)

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            queryset = queryset.filter(purchase__date__range=[start, end])
        except:
            pass

    summary = (
        queryset.values(
            "item__name",
            "item__category__name",
            "purchase__spot__location_name",
            "purchase__agent__name",
            "purchase__date",
        )
        .annotate(
            total_quantity=Sum("quantity"),
            total_amount=Sum("amount"),
            avg_rate=Sum(F("amount"), output_field=FloatField()) / Sum(F("quantity"), output_field=FloatField()),
        )
        .order_by("purchase__date")
    )

    return render(
        request,
        "adminapp/report/spot_purchase_report_print.html",
        {
            "summary": summary,
            "start_date": start_date,
            "end_date": end_date,
            "selected_items": selected_items,
            "selected_spots": selected_spots,
            "selected_agents": selected_agents,
            "selected_categories": selected_categories,
        },
    )


# LOCAL PURCHASE REPORT 
def local_purchase_report(request):
    items = Item.objects.all()
    grades = ItemGrade.objects.all()
    categories = ItemCategory.objects.all()
    # Add species filter
    species = Species.objects.all()

    queryset = LocalPurchaseItem.objects.select_related(
        "purchase", "item", "grade", "item__category", "item__species"
    )

    # ✅ Multi-select filters
    selected_items = request.GET.getlist("items")
    selected_grades = request.GET.getlist("grades")
    selected_categories = request.GET.getlist("categories")
    selected_parties = request.GET.getlist("parties")
    selected_species = request.GET.getlist("species")  # Add species filter
    date_filter = request.GET.get("date_filter")

    # ✅ Date range filter
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # ✅ Party name filter (text search)
    party_search = request.GET.get("party_search", "").strip()

    if selected_items:
        queryset = queryset.filter(item__id__in=selected_items)
    if selected_grades:
        queryset = queryset.filter(grade__id__in=selected_grades)
    if selected_categories:
        queryset = queryset.filter(item__category__id__in=selected_categories)
    if selected_species:
        queryset = queryset.filter(item__species__id__in=selected_species)
    if party_search:
        queryset = queryset.filter(purchase__party_name__icontains=party_search)

    # ✅ Quick date filter
    if date_filter == "week":
        queryset = queryset.filter(purchase__date__gte=now().date() - timedelta(days=7))
    elif date_filter == "month":
        queryset = queryset.filter(purchase__date__month=now().month)
    elif date_filter == "year":
        queryset = queryset.filter(purchase__date__year=now().year)

    # ✅ Custom date range
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            queryset = queryset.filter(purchase__date__range=[start, end])
        except:
            pass

    # ✅ Group & summary
    summary = (
        queryset.values(
            "item__name",
            "item__category__name",
            "item__species__name",  # Add species name
            "grade__grade",  # Changed from grade__name to grade__grade
            "purchase__party_name",
            "purchase__voucher_number",
            "purchase__date",
        )
        .annotate(
            total_quantity=Sum("quantity"),
            total_amount=Sum("amount"),
            avg_rate=Sum(F("amount"), output_field=FloatField()) / Sum(F("quantity"), output_field=FloatField()),
        )
        .order_by("purchase__date")
    )

    # Get unique parties for filter dropdown
    parties = LocalPurchase.objects.values_list('party_name', flat=True).distinct().order_by('party_name')

    # ✅ Check if print/export requested
    action = request.GET.get("action")
    print_mode = request.GET.get("print")  # Check for print parameter

    # Handle print request
    if action == "print" or print_mode == "1":
        return render(
            request,
            "adminapp/report/local_purchase_report_print.html",
            {
                "summary": summary, 
                "start_date": start_date, 
                "end_date": end_date
            },
        )

    if action == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="local_purchase_report.csv"'
        writer = csv.writer(response)
        writer.writerow(["Date", "Voucher No", "Party", "Item", "Grade", "Category", "Species", "Quantity", "Amount", "Avg Rate"])
        for row in summary:
            writer.writerow([
                row["purchase__date"],
                row["purchase__voucher_number"],
                row["purchase__party_name"],
                row["item__name"],
                row["grade__grade"] or "N/A",  # Changed from grade__name
                row["item__category__name"],
                row["item__species__name"] or "N/A",  # Add species
                row["total_quantity"],
                row["total_amount"],
                round(row["avg_rate"], 2) if row["avg_rate"] else 0,
            ])
        return response

    if action == "excel":
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Report")

        headers = ["Date", "Voucher No", "Party", "Item", "Grade", "Category", "Species", "Quantity", "Amount", "Avg Rate"]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        for row_idx, row in enumerate(summary, start=1):
            worksheet.write(row_idx, 0, str(row["purchase__date"]))
            worksheet.write(row_idx, 1, row["purchase__voucher_number"])
            worksheet.write(row_idx, 2, row["purchase__party_name"])
            worksheet.write(row_idx, 3, row["item__name"])
            worksheet.write(row_idx, 4, row["grade__grade"] or "N/A")  # Changed from grade__name
            worksheet.write(row_idx, 5, row["item__category__name"])
            worksheet.write(row_idx, 6, row["item__species__name"] or "N/A")  # Add species
            worksheet.write(row_idx, 7, row["total_quantity"])
            worksheet.write(row_idx, 8, row["total_amount"])
            worksheet.write(row_idx, 9, round(row["avg_rate"], 2) if row["avg_rate"] else 0)

        workbook.close()
        output.seek(0)

        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="local_purchase_report.xlsx"'
        return response

    return render(
        request,
        "adminapp/report/local_purchase_report.html",
        {
            "summary": summary,
            "items": items,
            "grades": grades,
            "categories": categories,
            "species": species,  # Add species to context
            "parties": parties,
            "selected_items": selected_items,
            "selected_grades": selected_grades,
            "selected_categories": selected_categories,
            "selected_species": selected_species,  # Add to context
            "date_filter": date_filter,
            "start_date": start_date,
            "end_date": end_date,
            "party_search": party_search,
        },
    )

def local_purchase_report_print(request):
    """Separate view specifically for print format"""
    items = Item.objects.all()
    grades = ItemGrade.objects.all()
    categories = ItemCategory.objects.all()
    species = Species.objects.all()

    queryset = LocalPurchaseItem.objects.select_related(
        "purchase", "item", "grade", "item__category", "item__species"
    )

    # Apply the same filters as main view
    selected_items = request.GET.getlist("items")
    selected_grades = request.GET.getlist("grades")
    selected_categories = request.GET.getlist("categories")
    selected_species = request.GET.getlist("species")
    date_filter = request.GET.get("date_filter")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    party_search = request.GET.get("party_search", "").strip()

    if selected_items:
        queryset = queryset.filter(item__id__in=selected_items)
    if selected_grades:
        queryset = queryset.filter(grade__id__in=selected_grades)
    if selected_categories:
        queryset = queryset.filter(item__category__id__in=selected_categories)
    if selected_species:
        queryset = queryset.filter(item__species__id__in=selected_species)
    if party_search:
        queryset = queryset.filter(purchase__party_name__icontains=party_search)

    if date_filter == "week":
        queryset = queryset.filter(purchase__date__gte=now().date() - timedelta(days=7))
    elif date_filter == "month":
        queryset = queryset.filter(purchase__date__month=now().month)
    elif date_filter == "year":
        queryset = queryset.filter(purchase__date__year=now().year)

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            queryset = queryset.filter(purchase__date__range=[start, end])
        except:
            pass

    summary = (
        queryset.values(
            "item__name",
            "item__category__name",
            "item__species__name",
            "grade__grade",  # Changed from grade__name to grade__grade
            "purchase__party_name",
            "purchase__voucher_number",
            "purchase__date",
        )
        .annotate(
            total_quantity=Sum("quantity"),
            total_amount=Sum("amount"),
            avg_rate=Sum(F("amount"), output_field=FloatField()) / Sum(F("quantity"), output_field=FloatField()),
        )
        .order_by("purchase__date")
    )

    return render(
        request,
        "adminapp/report/local_purchase_report_print.html",
        {
            "summary": summary,
            "start_date": start_date,
            "end_date": end_date,
            "selected_items": selected_items,
            "selected_grades": selected_grades,
            "selected_categories": selected_categories,
            "selected_species": selected_species,
            "party_search": party_search,
        },
    )



# PEELING SHED SUPPLY REPORT
def peeling_shed_supply_report(request):
    items = Item.objects.all()
    item_types = ItemType.objects.all()
    sheds = Shed.objects.all()
    spot_purchases = SpotPurchase.objects.all()

    queryset = PeelingShedSupply.objects.select_related(
        "shed", "spot_purchase", "spot_purchase_item", "spot_purchase_item__item"
    ).prefetch_related("peeling_types", "peeling_types__item", "peeling_types__item_type")

    # ✅ Multi-select filters
    selected_items = request.GET.getlist("items")
    selected_item_types = request.GET.getlist("item_types")
    selected_sheds = request.GET.getlist("sheds")
    selected_spot_purchases = request.GET.getlist("spot_purchases")
    date_filter = request.GET.get("date_filter")

    # ✅ Date range filter
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # ✅ Voucher number search
    voucher_search = request.GET.get("voucher_search", "").strip()

    # ✅ Vehicle number search
    vehicle_search = request.GET.get("vehicle_search", "").strip()

    # Apply filters
    if selected_items:
        queryset = queryset.filter(spot_purchase_item__item__id__in=selected_items)
    if selected_item_types:
        queryset = queryset.filter(peeling_types__item_type__id__in=selected_item_types)
    if selected_sheds:
        queryset = queryset.filter(shed__id__in=selected_sheds)
    if selected_spot_purchases:
        queryset = queryset.filter(spot_purchase__id__in=selected_spot_purchases)
    if voucher_search:
        queryset = queryset.filter(voucher_number__icontains=voucher_search)
    if vehicle_search:
        queryset = queryset.filter(vehicle_number__icontains=vehicle_search)

    # ✅ Quick date filter
    if date_filter == "week":
        queryset = queryset.filter(date__gte=now().date() - timedelta(days=7))
    elif date_filter == "month":
        queryset = queryset.filter(date__month=now().month)
    elif date_filter == "year":
        queryset = queryset.filter(date__year=now().year)

    # ✅ Custom date range
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__range=[start, end])
        except:
            pass

    # ✅ Group & summary
    summary = (
        queryset.values(
            "voucher_number",
            "date",
            "shed__name",
            "vehicle_number",
            "spot_purchase_date",
            "spot_purchase__voucher_number",
            "spot_purchase_item__item__name",
            "spot_purchase_item__item__category__name",
            "spot_purchase_item__item__species__name",
        )
        .annotate(
            total_boxes_purchase=Sum("SpotPurchase_total_boxes"),
            total_quantity_purchase=Sum("SpotPurchase_quantity"),
            avg_box_weight=Avg("SpotPurchase_average_box_weight"),
            boxes_received=Sum("boxes_received_shed"),
            quantity_received=Sum("quantity_received_shed"),
            total_peeling_amount=Sum("peeling_types__amount"),
        )
        .order_by("date")
    )

    # Get unique voucher numbers and vehicles for search suggestions
    vouchers = PeelingShedSupply.objects.values_list('voucher_number', flat=True).distinct().order_by('voucher_number')
    vehicles = PeelingShedSupply.objects.values_list('vehicle_number', flat=True).distinct().order_by('vehicle_number')

    # ✅ Check if print/export requested
    action = request.GET.get("action")
    print_mode = request.GET.get("print")  # Check for print parameter

    # Handle print request
    if action == "print" or print_mode == "1":
        return render(
            request,
            "adminapp/report/peeling_shed_supply_report_print.html",
            {
                "summary": summary, 
                "start_date": start_date, 
                "end_date": end_date
            },
        )

    if action == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="peeling_shed_supply_report.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "Date", "Voucher No", "Shed", "Vehicle", "Spot Purchase Date", 
            "Spot Voucher", "Item", "Category", "Species", "Purchase Boxes", 
            "Purchase Quantity", "Avg Box Weight", "Boxes Received", 
            "Quantity Received", "Total Peeling Amount"
        ])
        for row in summary:
            writer.writerow([
                row["date"],
                row["voucher_number"],
                row["shed__name"],
                row["vehicle_number"],
                row["spot_purchase_date"],
                row["spot_purchase__voucher_number"],
                row["spot_purchase_item__item__name"],
                row["spot_purchase_item__item__category__name"] or "N/A",
                row["spot_purchase_item__item__species__name"] or "N/A",
                row["total_boxes_purchase"],
                row["total_quantity_purchase"],
                round(row["avg_box_weight"], 2) if row["avg_box_weight"] else 0,
                row["boxes_received"],
                row["quantity_received"],
                row["total_peeling_amount"],
            ])
        return response

    if action == "excel":
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet("Report")

        headers = [
            "Date", "Voucher No", "Shed", "Vehicle", "Spot Purchase Date", 
            "Spot Voucher", "Item", "Category", "Species", "Purchase Boxes", 
            "Purchase Quantity", "Avg Box Weight", "Boxes Received", 
            "Quantity Received", "Total Peeling Amount"
        ]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        for row_idx, row in enumerate(summary, start=1):
            worksheet.write(row_idx, 0, str(row["date"]))
            worksheet.write(row_idx, 1, row["voucher_number"])
            worksheet.write(row_idx, 2, row["shed__name"])
            worksheet.write(row_idx, 3, row["vehicle_number"])
            worksheet.write(row_idx, 4, str(row["spot_purchase_date"]) if row["spot_purchase_date"] else "N/A")
            worksheet.write(row_idx, 5, row["spot_purchase__voucher_number"])
            worksheet.write(row_idx, 6, row["spot_purchase_item__item__name"])
            worksheet.write(row_idx, 7, row["spot_purchase_item__item__category__name"] or "N/A")
            worksheet.write(row_idx, 8, row["spot_purchase_item__item__species__name"] or "N/A")
            worksheet.write(row_idx, 9, row["total_boxes_purchase"])
            worksheet.write(row_idx, 10, row["total_quantity_purchase"])
            worksheet.write(row_idx, 11, round(row["avg_box_weight"], 2) if row["avg_box_weight"] else 0)
            worksheet.write(row_idx, 12, row["boxes_received"])
            worksheet.write(row_idx, 13, row["quantity_received"])
            worksheet.write(row_idx, 14, row["total_peeling_amount"])

        workbook.close()
        output.seek(0)

        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="peeling_shed_supply_report.xlsx"'
        return response

    return render(
        request,
        "adminapp/report/peeling_shed_supply_report.html",
        {
            "summary": summary,
            "items": items,
            "item_types": item_types,
            "sheds": sheds,
            "spot_purchases": spot_purchases,
            "vouchers": vouchers,
            "vehicles": vehicles,
            "selected_items": selected_items,
            "selected_item_types": selected_item_types,
            "selected_sheds": selected_sheds,
            "selected_spot_purchases": selected_spot_purchases,
            "date_filter": date_filter,
            "start_date": start_date,
            "end_date": end_date,
            "voucher_search": voucher_search,
            "vehicle_search": vehicle_search,
        },
    )

def peeling_shed_supply_report_print(request):
    """Separate view specifically for print format"""
    items = Item.objects.all()
    item_types = ItemType.objects.all()
    sheds = Shed.objects.all()
    spot_purchases = SpotPurchase.objects.all()

    queryset = PeelingShedSupply.objects.select_related(
        "shed", 
        "spot_purchase", 
        "spot_purchase_item", 
        "spot_purchase_item__item",
        "spot_purchase_item__item__species",
        "spot_purchase_item__item__itemgrade",  # Add ForeignKey relationship
        "spot_purchase_item__item__itemtype"    # Add ForeignKey relationship
    ).prefetch_related("peeling_types", "peeling_types__item", "peeling_types__item_type")

    # Apply the same filters as main view
    selected_items = request.GET.getlist("items")
    selected_item_types = request.GET.getlist("item_types")
    selected_sheds = request.GET.getlist("sheds")
    selected_spot_purchases = request.GET.getlist("spot_purchases")
    date_filter = request.GET.get("date_filter")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    voucher_search = request.GET.get("voucher_search", "").strip()
    vehicle_search = request.GET.get("vehicle_search", "").strip()

    # Apply filters
    if selected_items:
        queryset = queryset.filter(spot_purchase_item__item__id__in=selected_items)
    if selected_item_types:
        queryset = queryset.filter(peeling_types__item_type__id__in=selected_item_types)
    if selected_sheds:
        queryset = queryset.filter(shed__id__in=selected_sheds)
    if selected_spot_purchases:
        queryset = queryset.filter(spot_purchase__id__in=selected_spot_purchases)
    if voucher_search:
        queryset = queryset.filter(voucher_number__icontains=voucher_search)
    if vehicle_search:
        queryset = queryset.filter(vehicle_number__icontains=vehicle_search)

    # Date filters
    if date_filter == "week":
        queryset = queryset.filter(date__gte=now().date() - timedelta(days=7))
    elif date_filter == "month":
        queryset = queryset.filter(date__month=now().month)
    elif date_filter == "year":
        queryset = queryset.filter(date__year=now().year)

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            queryset = queryset.filter(date__range=[start, end])
        except ValueError:
            pass

    # Generate summary - Access ForeignKey relationships properly
    summary = (
        queryset.values(
            "voucher_number",
            "date",
            "shed__name",
            "vehicle_number",
            "spot_purchase_date",
            "spot_purchase__voucher_number",
            "spot_purchase_item__item__name",
            "spot_purchase_item__item__category__name",
            "spot_purchase_item__item__species__name",           # Species (ForeignKey -> name)
            "spot_purchase_item__item__itemgrade__grade",        # Grade (ForeignKey -> grade field)
            "spot_purchase_item__item__itemtype__name",          # ItemType (ForeignKey -> name field)
        )
        .annotate(
            total_boxes_purchase=Sum("SpotPurchase_total_boxes"),
            total_quantity_purchase=Sum("SpotPurchase_quantity"),
            avg_box_weight=Avg("SpotPurchase_average_box_weight"),
            boxes_received=Sum("boxes_received_shed"),
            quantity_received=Sum("quantity_received_shed"),
            total_peeling_amount=Sum("peeling_types__amount"),
        )
        .order_by("date", "voucher_number")
    )

    return render(
        request,
        "adminapp/report/peeling_shed_supply_report_print.html",
        {
            "summary": summary,
            "start_date": start_date,
            "end_date": end_date,
            "selected_items": selected_items,
            "selected_item_types": selected_item_types,
            "selected_sheds": selected_sheds,
            "selected_spot_purchases": selected_spot_purchases,
            "voucher_search": voucher_search,
            "vehicle_search": vehicle_search,
        },
    )








# DIAGNOSTIC VERSION - Check what fields actually exist
def freezing_report(request):
    # First, let's check what fields actually exist on the models
    from django.db import connection
    
    # Check FreezingEntrySpotItem fields
    try:
        spot_item_fields = [field.name for field in FreezingEntrySpotItem._meta.fields]
        print("FreezingEntrySpotItem fields:", spot_item_fields)
        
        local_item_fields = [field.name for field in FreezingEntryLocalItem._meta.fields]
        print("FreezingEntryLocalItem fields:", local_item_fields)
        
        # Check foreign key relationships
        spot_fk_fields = [field.name for field in FreezingEntrySpotItem._meta.fields if field.get_internal_type() == 'ForeignKey']
        print("FreezingEntrySpotItem FK fields:", spot_fk_fields)
        
        local_fk_fields = [field.name for field in FreezingEntryLocalItem._meta.fields if field.get_internal_type() == 'ForeignKey']
        print("FreezingEntryLocalItem FK fields:", local_fk_fields)
        
    except Exception as e:
        print("Error checking fields:", str(e))

    items = Item.objects.all()
    grades = ItemGrade.objects.all()
    categories = ItemCategory.objects.all()
    species = Species.objects.all()
    brands = ItemBrand.objects.all()
    freezing_categories = FreezingCategory.objects.all()
    processing_centers = ProcessingCenter.objects.all()
    stores = Store.objects.all()
    
    # Check if models exist and get units/glazes
    try:
        units = PackingUnit.objects.all()
    except NameError:
        units = []
    
    try:
        glazes = GlazePercentage.objects.all()
    except NameError:
        glazes = []

    # Get filter parameters
    selected_items = request.GET.getlist("items")
    selected_grades = request.GET.getlist("grades")
    selected_categories = request.GET.getlist("categories")
    selected_species = request.GET.getlist("species")
    selected_brands = request.GET.getlist("brands")
    selected_freezing_categories = request.GET.getlist("freezing_categories")
    selected_processing_centers = request.GET.getlist("processing_centers")
    selected_stores = request.GET.getlist("stores")
    selected_units = request.GET.getlist("units")
    selected_glazes = request.GET.getlist("glazes")
    
    date_filter = request.GET.get("date_filter")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    freezing_status = request.GET.get("freezing_status")
    voucher_search = request.GET.get("voucher_search", "").strip()
    entry_type = request.GET.get("entry_type", "all")  # all, spot, local
    section_by = request.GET.get("section_by", "category")

    # SAFE: Start with minimal select_related and build up
    spot_queryset = FreezingEntrySpotItem.objects.select_related("freezing_entry", "item", "item__category")
    local_queryset = FreezingEntryLocalItem.objects.select_related("freezing_entry", "item", "item__category")

    # Check what other relationships exist and add them safely
    try:
        # Test if grade field exists
        test_spot = FreezingEntrySpotItem.objects.first()
        if test_spot and hasattr(test_spot, 'grade'):
            spot_queryset = spot_queryset.select_related("grade")
            local_queryset = local_queryset.select_related("grade")
            print("Added grade to select_related")
    except:
        print("No grade field found")

    try:
        # Test if species field exists
        if test_spot and hasattr(test_spot, 'species'):
            spot_queryset = spot_queryset.select_related("species")
            local_queryset = local_queryset.select_related("species")
            print("Added species to select_related")
    except:
        print("No direct species field found")

    try:
        # Test if brand field exists
        if test_spot and hasattr(test_spot, 'brand'):
            spot_queryset = spot_queryset.select_related("brand")
            local_queryset = local_queryset.select_related("brand")
            print("Added brand to select_related")
    except:
        print("No brand field found")

    try:
        # Test if freezing_category field exists
        if test_spot and hasattr(test_spot, 'freezing_category'):
            spot_queryset = spot_queryset.select_related("freezing_category")
            local_queryset = local_queryset.select_related("freezing_category")
            print("Added freezing_category to select_related")
    except:
        print("No freezing_category field found")

    try:
        # Test if processing_center field exists
        if test_spot and hasattr(test_spot, 'processing_center'):
            spot_queryset = spot_queryset.select_related("processing_center")
            local_queryset = local_queryset.select_related("processing_center")
            print("Added processing_center to select_related")
    except:
        print("No processing_center field found")

    try:
        # Test if store field exists
        if test_spot and hasattr(test_spot, 'store'):
            spot_queryset = spot_queryset.select_related("store")
            local_queryset = local_queryset.select_related("store")
            print("Added store to select_related")
    except:
        print("No store field found")

    # Apply filters with safe field checks
    def apply_filters(queryset, is_spot=True):
        # Item filters
        if selected_items:
            queryset = queryset.filter(item__id__in=selected_items)
        
        # Check if grade field exists before filtering
        test_item = queryset.first()
        if test_item and hasattr(test_item, 'grade') and selected_grades:
            queryset = queryset.filter(grade__id__in=selected_grades)
        
        if selected_categories:
            queryset = queryset.filter(item__category__id__in=selected_categories)
        
        # Check if species field exists before filtering
        if test_item and hasattr(test_item, 'species') and selected_species:
            queryset = queryset.filter(species__id__in=selected_species)
        
        # Check other fields similarly
        if test_item and hasattr(test_item, 'brand') and selected_brands:
            queryset = queryset.filter(brand__id__in=selected_brands)
        if test_item and hasattr(test_item, 'freezing_category') and selected_freezing_categories:
            queryset = queryset.filter(freezing_category__id__in=selected_freezing_categories)
        if test_item and hasattr(test_item, 'processing_center') and selected_processing_centers:
            queryset = queryset.filter(processing_center__id__in=selected_processing_centers)
        if test_item and hasattr(test_item, 'store') and selected_stores:
            queryset = queryset.filter(store__id__in=selected_stores)
        if test_item and hasattr(test_item, 'unit') and selected_units:
            queryset = queryset.filter(unit__id__in=selected_units)
        if test_item and hasattr(test_item, 'glaze') and selected_glazes:
            queryset = queryset.filter(glaze__id__in=selected_glazes)
            
        # Status and voucher filters
        if freezing_status:
            queryset = queryset.filter(freezing_entry__freezing_status=freezing_status)
        if voucher_search:
            queryset = queryset.filter(freezing_entry__voucher_number__icontains=voucher_search)

        # Date filters
        today = now().date()
        if date_filter == "today":
            queryset = queryset.filter(freezing_entry__freezing_date=today)
        elif date_filter == "week":
            week_start = today - timedelta(days=today.weekday())
            queryset = queryset.filter(freezing_entry__freezing_date__gte=week_start)
        elif date_filter == "month":
            queryset = queryset.filter(
                freezing_entry__freezing_date__year=today.year,
                freezing_entry__freezing_date__month=today.month
            )
        elif date_filter == "quarter":
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            quarter_start = today.replace(month=quarter_start_month, day=1)
            queryset = queryset.filter(freezing_entry__freezing_date__gte=quarter_start)
        elif date_filter == "year":
            queryset = queryset.filter(freezing_entry__freezing_date__year=today.year)
        elif date_filter == "custom" and start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                queryset = queryset.filter(freezing_entry__freezing_date__range=[start, end])
            except ValueError:
                pass

        if start_date and end_date and not date_filter:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                queryset = queryset.filter(freezing_entry__freezing_date__range=[start, end])
            except ValueError:
                pass

        return queryset

    # Apply filters
    spot_queryset = apply_filters(spot_queryset, True)
    local_queryset = apply_filters(local_queryset, False)

    # Process data safely
    all_data = []

    if entry_type in ['all', 'spot']:
        for item in spot_queryset:
            data_row = {
                'id': item.id,
                'item__name': item.item.name if item.item else None,
                'item__category__name': item.item.category.name if item.item and item.item.category else None,
                'freezing_entry__voucher_number': item.freezing_entry.voucher_number if item.freezing_entry else None,
                'freezing_entry__freezing_date': item.freezing_entry.freezing_date if item.freezing_entry else None,
                'freezing_entry__freezing_status': item.freezing_entry.freezing_status if item.freezing_entry else None,
                'entry_type': 'spot',
                'item_count': 1
            }
            
            # Add optional fields safely
            if hasattr(item, 'species') and item.species:
                data_row['item__species__name'] = item.species.name
            else:
                data_row['item__species__name'] = None
                
            if hasattr(item, 'grade') and item.grade:
                data_row['grade__grade'] = item.grade.grade
            else:
                data_row['grade__grade'] = None
                
            if hasattr(item, 'brand') and item.brand:
                data_row['brand__name'] = item.brand.name
            else:
                data_row['brand__name'] = None
                
            if hasattr(item, 'freezing_category') and item.freezing_category:
                data_row['freezing_category__name'] = item.freezing_category.name
            else:
                data_row['freezing_category__name'] = None
                
            if hasattr(item, 'processing_center') and item.processing_center:
                data_row['processing_center__name'] = item.processing_center.name
            else:
                data_row['processing_center__name'] = None
                
            if hasattr(item, 'store') and item.store:
                data_row['store__name'] = item.store.name
            else:
                data_row['store__name'] = None

            # Add numeric fields
            data_row.update({
                'total_kg': float(getattr(item, 'kg', 0) or 0),
                'total_slab_quantity': float(getattr(item, 'slab_quantity', 0) or 0),
                'total_c_s_quantity': float(getattr(item, 'c_s_quantity', 0) or 0),
                'total_usd_amount': float(getattr(item, 'usd_rate_item', 0) or 0),
                'total_inr_amount': float(getattr(item, 'usd_rate_item_to_inr', 0) or 0),
                'avg_usd_rate_per_kg': float(getattr(item, 'usd_rate_per_kg', 0) or 0),
                'avg_yield_percentage': float(getattr(item, 'yield_percentage', 0) or 0),
            })
            
            # Add unit and glaze fields if they exist
            if hasattr(item, 'unit') and item.unit:
                data_row['unit__description'] = item.unit.description
                data_row['unit__unit_code'] = item.unit.unit_code
            else:
                data_row['unit__description'] = None
                data_row['unit__unit_code'] = None
                
            if hasattr(item, 'glaze') and item.glaze:
                data_row['glaze__percentage'] = item.glaze.percentage
            else:
                data_row['glaze__percentage'] = None
                
            all_data.append(data_row)

    if entry_type in ['all', 'local']:
        for item in local_queryset:
            data_row = {
                'id': item.id,
                'item__name': item.item.name if item.item else None,
                'item__category__name': item.item.category.name if item.item and item.item.category else None,
                'freezing_entry__voucher_number': item.freezing_entry.voucher_number if item.freezing_entry else None,
                'freezing_entry__freezing_date': item.freezing_entry.freezing_date if item.freezing_entry else None,
                'freezing_entry__freezing_status': item.freezing_entry.freezing_status if item.freezing_entry else None,
                'entry_type': 'local',
                'item_count': 1
            }
            
            # Add optional fields safely (same as spot)
            if hasattr(item, 'species') and item.species:
                data_row['item__species__name'] = item.species.name
            else:
                data_row['item__species__name'] = None
                
            if hasattr(item, 'grade') and item.grade:
                data_row['grade__grade'] = item.grade.grade
            else:
                data_row['grade__grade'] = None
                
            if hasattr(item, 'brand') and item.brand:
                data_row['brand__name'] = item.brand.name
            else:
                data_row['brand__name'] = None
                
            if hasattr(item, 'freezing_category') and item.freezing_category:
                data_row['freezing_category__name'] = item.freezing_category.name
            else:
                data_row['freezing_category__name'] = None
                
            if hasattr(item, 'processing_center') and item.processing_center:
                data_row['processing_center__name'] = item.processing_center.name
            else:
                data_row['processing_center__name'] = None
                
            if hasattr(item, 'store') and item.store:
                data_row['store__name'] = item.store.name
            else:
                data_row['store__name'] = None

            # Add numeric fields
            data_row.update({
                'total_kg': float(getattr(item, 'kg', 0) or 0),
                'total_slab_quantity': float(getattr(item, 'slab_quantity', 0) or 0),
                'total_c_s_quantity': float(getattr(item, 'c_s_quantity', 0) or 0),
                'total_usd_amount': float(getattr(item, 'usd_rate_item', 0) or 0),
                'total_inr_amount': float(getattr(item, 'usd_rate_item_to_inr', 0) or 0),
                'avg_usd_rate_per_kg': float(getattr(item, 'usd_rate_per_kg', 0) or 0),
                'avg_yield_percentage': None,  # Local entries don't have yield percentage
            })
            
            # Add unit and glaze fields if they exist
            if hasattr(item, 'unit') and item.unit:
                data_row['unit__description'] = item.unit.description
                data_row['unit__unit_code'] = item.unit.unit_code
            else:
                data_row['unit__description'] = None
                data_row['unit__unit_code'] = None
                
            if hasattr(item, 'glaze') and item.glaze:
                data_row['glaze__percentage'] = item.glaze.percentage
            else:
                data_row['glaze__percentage'] = None
                
            all_data.append(data_row)

    # Sectioning logic (rest of the original code remains the same)
    sectioned_data = {}
    
    for item in all_data:
        if section_by == "category":
            section_key = item.get("item__category__name") or "Uncategorized"
        elif section_by == "brand":
            section_key = item.get("brand__name") or "No Brand"
        elif section_by == "processing_center":
            section_key = item.get("processing_center__name") or "No Processing Center"
        elif section_by == "store":
            section_key = item.get("store__name") or "No Store"
        elif section_by == "month":
            date_obj = item.get("freezing_entry__freezing_date")
            if date_obj:
                section_key = f"{date_obj.strftime('%B %Y')}"
            else:
                section_key = "No Date"
        elif section_by == "species":
            section_key = item.get("item__species__name") or "No Species"
        elif section_by == "grade":
            section_key = item.get("grade__grade") or "No Grade"
        elif section_by == "item":
            section_key = item.get("item__name") or "No Item"
        elif section_by == "unit":
            section_key = item.get("unit__description") or "No Unit"
        elif section_by == "glaze":
            glaze_pct = item.get("glaze__percentage")
            section_key = f"{glaze_pct}%" if glaze_pct is not None else "No Glaze"
        elif section_by == "entry_type":
            section_key = item.get("entry_type", "Unknown").title()
        elif section_by == "status":
            section_key = item.get("freezing_entry__freezing_status", "Unknown").title()
        else:
            section_key = "All Items"
            
        if section_key not in sectioned_data:
            sectioned_data[section_key] = {
                'items': [],
                'totals': {
                    'total_kg': 0,
                    'total_slab_quantity': 0,
                    'total_c_s_quantity': 0,
                    'total_usd_amount': 0,
                    'total_inr_amount': 0,
                    'count': 0,
                    'item_count': 0
                }
            }
        
        sectioned_data[section_key]['items'].append(item)
        
        # Calculate section totals
        totals = sectioned_data[section_key]['totals']
        totals['total_kg'] += float(item.get('total_kg') or 0)
        totals['total_slab_quantity'] += float(item.get('total_slab_quantity') or 0)
        totals['total_c_s_quantity'] += float(item.get('total_c_s_quantity') or 0)
        totals['total_usd_amount'] += float(item.get('total_usd_amount') or 0)
        totals['total_inr_amount'] += float(item.get('total_inr_amount') or 0)
        totals['count'] += 1
        totals['item_count'] += int(item.get('item_count') or 0)

    sectioned_data = dict(sorted(sectioned_data.items()))

    # Calculate grand totals
    grand_totals = {
        'total_kg': 0,
        'total_slab_quantity': 0,
        'total_c_s_quantity': 0,
        'total_usd_amount': 0,
        'total_inr_amount': 0,
        'count': 0,
        'item_count': 0,
        'avg_kg_per_entry': 0,
        'avg_usd_per_kg': 0
    }
    
    for section in sectioned_data.values():
        for key in ['total_kg', 'total_slab_quantity', 'total_c_s_quantity', 
                   'total_usd_amount', 'total_inr_amount', 'count', 'item_count']:
            grand_totals[key] += section['totals'][key]

    if grand_totals['count'] > 0:
        grand_totals['avg_kg_per_entry'] = grand_totals['total_kg'] / grand_totals['count']
    if grand_totals['total_kg'] > 0:
        grand_totals['avg_usd_per_kg'] = grand_totals['total_usd_amount'] / grand_totals['total_kg']

    # Get unique vouchers
    try:
        spot_vouchers = list(FreezingEntrySpot.objects.values_list('voucher_number', flat=True).distinct())
        local_vouchers = list(FreezingEntryLocal.objects.values_list('voucher_number', flat=True).distinct())
        all_vouchers = sorted(set(spot_vouchers + local_vouchers))
    except Exception as e:
        all_vouchers = []

    return render(
        request,
        "adminapp/report/freezing_report.html",
        {
            "sectioned_data": sectioned_data,
            "grand_totals": grand_totals,
            "items": items,
            "grades": grades,
            "categories": categories,
            "species": species,
            "brands": brands,
            "freezing_categories": freezing_categories,
            "processing_centers": processing_centers,
            "stores": stores,
            "units": units,
            "glazes": glazes,
            "vouchers": all_vouchers,
            "selected_items": selected_items,
            "selected_grades": selected_grades,
            "selected_categories": selected_categories,
            "selected_species": selected_species,
            "selected_brands": selected_brands,
            "selected_freezing_categories": selected_freezing_categories,
            "selected_processing_centers": selected_processing_centers,
            "selected_stores": selected_stores,
            "selected_units": selected_units,
            "selected_glazes": selected_glazes,
            "date_filter": date_filter,
            "start_date": start_date,
            "end_date": end_date,
            "freezing_status": freezing_status,
            "voucher_search": voucher_search,
            "entry_type": entry_type,
            "section_by": section_by,
        },
    )

# Separate view for print format
def freezing_report_print(request):
    """Separate view specifically for print format"""
    items = Item.objects.all()
    grades = ItemGrade.objects.all()
    categories = ItemCategory.objects.all()
    species = Species.objects.all()
    brands = ItemBrand.objects.all()
    freezing_categories = FreezingCategory.objects.all()

    # Get filter parameters (same as main view)
    selected_items = request.GET.getlist("items")
    selected_grades = request.GET.getlist("grades")
    selected_categories = request.GET.getlist("categories")
    selected_species = request.GET.getlist("species")
    selected_brands = request.GET.getlist("brands")
    selected_freezing_categories = request.GET.getlist("freezing_categories")
    date_filter = request.GET.get("date_filter")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    freezing_status = request.GET.get("freezing_status")
    voucher_search = request.GET.get("voucher_search", "").strip()
    entry_type = request.GET.get("entry_type", "all")

    # Base querysets
    spot_queryset = FreezingEntrySpotItem.objects.select_related(
        "freezing_entry", "item", "grade", "item__category", "item__species",
        "brand", "freezing_category"
    )
    
    local_queryset = FreezingEntryLocalItem.objects.select_related(
        "freezing_entry", "item", "grade", "item__category", "item__species",
        "brand", "freezing_category"
    )

    # Apply same filters as main view
    def apply_filters(queryset):
        if selected_items:
            queryset = queryset.filter(item__id__in=selected_items)
        if selected_grades:
            queryset = queryset.filter(grade__id__in=selected_grades)
        if selected_categories:
            queryset = queryset.filter(item__category__id__in=selected_categories)
        if selected_species:
            queryset = queryset.filter(item__species__id__in=selected_species)
        if selected_brands:
            queryset = queryset.filter(brand__id__in=selected_brands)
        if selected_freezing_categories:
            queryset = queryset.filter(freezing_category__id__in=selected_freezing_categories)
        if freezing_status:
            queryset = queryset.filter(freezing_entry__freezing_status=freezing_status)
        if voucher_search:
            queryset = queryset.filter(freezing_entry__voucher_number__icontains=voucher_search)

        if date_filter == "week":
            queryset = queryset.filter(freezing_entry__freezing_date__gte=now().date() - timedelta(days=7))
        elif date_filter == "month":
            queryset = queryset.filter(freezing_entry__freezing_date__month=now().month)
        elif date_filter == "year":
            queryset = queryset.filter(freezing_entry__freezing_date__year=now().year)

        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                queryset = queryset.filter(freezing_entry__freezing_date__range=[start, end])
            except:
                pass

        return queryset

    # Apply filters
    spot_queryset = apply_filters(spot_queryset)
    local_queryset = apply_filters(local_queryset)

    summary_data = []

    # Process entries based on type filter
    if entry_type in ['all', 'spot']:
        spot_summary = (
            spot_queryset.values(
                "item__name",
                "item__category__name",
                "item__species__name",
                "grade__grade",
                "brand__name",
                "freezing_category__name",
                "freezing_entry__voucher_number",
                "freezing_entry__freezing_date",
                "freezing_entry__freezing_status",
            )
            .annotate(
                total_kg=Sum("kg"),
                total_slab_quantity=Sum("slab_quantity"),
                total_c_s_quantity=Sum("c_s_quantity"),
                total_usd_amount=Sum("usd_rate_item"),
                total_inr_amount=Sum("usd_rate_item_to_inr"),
                avg_usd_rate_per_kg=Avg("usd_rate_per_kg"),
                avg_yield_percentage=Avg("yield_percentage"),
                entry_type=Value('Spot', output_field=CharField()),
            )
            .order_by("freezing_entry__freezing_date")
        )
        summary_data.extend(list(spot_summary))

    if entry_type in ['all', 'local']:
        local_summary = (
            local_queryset.values(
                "item__name",
                "item__category__name",
                "item__species__name",
                "grade__grade",
                "brand__name",
                "freezing_category__name",
                "freezing_entry__voucher_number",
                "freezing_entry__freezing_date",
                "freezing_entry__freezing_status",
            )
            .annotate(
                total_kg=Sum("kg"),
                total_slab_quantity=Sum("slab_quantity"),
                total_c_s_quantity=Sum("c_s_quantity"),
                total_usd_amount=Sum("usd_rate_item"),
                total_inr_amount=Sum("usd_rate_item_to_inr"),
                avg_usd_rate_per_kg=Avg("usd_rate_per_kg"),
                avg_yield_percentage=Value(None, output_field=DecimalField()),
                entry_type=Value('Local', output_field=CharField()),
            )
            .order_by("freezing_entry__freezing_date")
        )
        summary_data.extend(list(local_summary))

    # Sort combined data by date
    summary_data = sorted(summary_data, key=lambda x: x['freezing_entry__freezing_date'])

    return render(
        request,
        "adminapp/report/freezing_report_print.html",
        {
            "summary": summary_data,
            "start_date": start_date,
            "end_date": end_date,
            "entry_type": entry_type,
            "selected_items": selected_items,
            "selected_grades": selected_grades,
            "selected_categories": selected_categories,
            "selected_species": selected_species,
            "selected_brands": selected_brands,
            "selected_freezing_categories": selected_freezing_categories,
            "freezing_status": freezing_status,
            "voucher_search": voucher_search,
        },
    )









# Tenant Freezing Entry Views
def tenant_freezing_list(request):
    entries = FreezingEntryTenant.objects.all().order_by('-freezing_date')
    return render(request, 'adminapp/tenant/list.html', {'entries': entries})

def tenant_freezing_detail(request, pk):
    entry = get_object_or_404(FreezingEntryTenant, pk=pk)
    return render(request, 'adminapp/tenant/detail.html', {'entry': entry})

@transaction.atomic
def tenant_freezing_create(request):
    if request.method == "POST":
        form = FreezingEntryTenantForm(request.POST)
        formset = FreezingEntryTenantItemFormSet(request.POST)
        
        print("=== DEBUG FORMSET DATA ===")
        print(f"POST data keys: {list(request.POST.keys())}")
        print(f"Formset is_valid: {formset.is_valid()}")
        print(f"Form is_valid: {form.is_valid()}")
        print(f"Formset total forms: {formset.total_form_count()}")
        print(f"Formset errors: {formset.errors}")
        print(f"Formset non_form_errors: {formset.non_form_errors()}")
        
        if form.is_valid() and formset.is_valid():
            # Save the main entry first
            entry = form.save()
            print(f"Main entry saved with ID: {entry.id}")
            
            # Set the instance and save the formset
            formset.instance = entry
            saved_items = formset.save()
            print(f"Saved {len(saved_items)} items from formset")
            
            # Debug: Check what was actually saved
            for i, item in enumerate(saved_items):
                print(f"Item {i+1}: {item.item} - Slab: {item.slab_quantity} - CS: {item.c_s_quantity} - KG: {item.kg}")

            # 🔹 Update totals
            totals = entry.items.aggregate(
                total_slab_sum=Sum('slab_quantity'),
                total_c_s_sum=Sum('c_s_quantity'),
                total_kg_sum=Sum('kg'),
            )
            entry.total_slab = totals['total_slab_sum'] or 0
            entry.total_c_s = totals['total_c_s_sum'] or 0
            entry.total_kg = totals['total_kg_sum'] or 0
            entry.total_amount = 0  # (If you have rate × qty, calculate here)
            entry.save()
            
            print(f"Updated totals - Slab: {entry.total_slab}, CS: {entry.total_c_s}, KG: {entry.total_kg}")

            return redirect(reverse('adminapp:list_freezing_entry_tenant'))
        else:
            # Debug form and formset errors
            print("=== VALIDATION ERRORS ===")
            if not form.is_valid():
                print(f"Form errors: {form.errors}")
            if not formset.is_valid():
                print(f"Formset errors: {formset.errors}")
                print(f"Formset non-form errors: {formset.non_form_errors()}")
                
                # Debug individual form errors
                for i, form_instance in enumerate(formset):
                    if form_instance.errors:
                        print(f"Form {i} errors: {form_instance.errors}")
                        print(f"Form {i} cleaned_data: {form_instance.cleaned_data if form_instance.is_valid() else 'Invalid'}")
                
    else:
        form = FreezingEntryTenantForm()
        formset = FreezingEntryTenantItemFormSet()
        
    return render(request, 'adminapp/tenant/create.html', {'form': form, 'formset': formset})

@transaction.atomic
def tenant_freezing_update(request, pk):
    entry = get_object_or_404(FreezingEntryTenant, pk=pk)
    if request.method == "POST":
        form = FreezingEntryTenantForm(request.POST, instance=entry)
        formset = FreezingEntryTenantItemFormSet(request.POST, instance=entry)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()

            totals = entry.items.aggregate(
                total_slab_sum=Sum('slab_quantity'),
                total_c_s_sum=Sum('c_s_quantity'),
                total_kg_sum=Sum('kg'),
            )
            entry.total_slab = totals['total_slab_sum'] or 0
            entry.total_c_s = totals['total_c_s_sum'] or 0
            entry.total_kg = totals['total_kg_sum'] or 0
            entry.total_amount = 0
            entry.save()

            return redirect(reverse('adminapp:list_freezing_entry_tenant'))
    else:
        form = FreezingEntryTenantForm(instance=entry)
        formset = FreezingEntryTenantItemFormSet(instance=entry)
    return render(request, 'adminapp/tenant/update.html', {'form': form, 'formset': formset})

def tenant_freezing_delete(request, pk):
    entry = get_object_or_404(FreezingEntryTenant, pk=pk)
    if request.method == "POST":
        entry.delete()
        return redirect('adminapp:list_freezing_entry_tenant')
    return render(request, 'adminapp/confirm_delete.html', {'entry': entry})

def tenant_freezing_detail_pdf(request, pk):
    """
    Generate PDF for FreezingEntryTenant detail view
    """
    # Get the FreezingEntryTenant object
    entry = get_object_or_404(FreezingEntryTenant, pk=pk)
    
    # Get the PDF template
    template = get_template('adminapp/tenant/detail_pdf.html')
    
    # Context data for the template
    context = {
        'entry': entry,
        'items': entry.items.all(),
        'company_name': 'Your Company Name',  # Add your company name
        'company_address': 'Your Company Address',  # Add your company address
        'phone': 'Your Phone Number',  # Add your phone number
        'email': 'your-email@company.com',  # Add your email
    }
    
    # Render the template with context
    html = template.render(context)
    
    # Create a BytesIO buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Generate PDF
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), buffer)
    
    if not pdf.err:
        # PDF generation successful
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="freezing_entry_{entry.voucher_number}.pdf"'
        buffer.close()
        return response
    else:
        # PDF generation failed
        return HttpResponse("Error generating PDF", status=500)












# return_tenant views
@transaction.atomic
def return_tenant_create(request):
    if request.method == "POST":
        form = ReturnTenantForm(request.POST)
        formset = ReturnTenantItemFormSet(request.POST)
        
        print("=== DEBUG FORMSET DATA ===")
        print(f"POST data keys: {list(request.POST.keys())}")
        print(f"Formset is_valid: {formset.is_valid()}")
        print(f"Form is_valid: {form.is_valid()}")
        print(f"Formset total forms: {formset.total_form_count()}")
        print(f"Formset errors: {formset.errors}")
        print(f"Formset non_form_errors: {formset.non_form_errors()}")
        
        if form.is_valid() and formset.is_valid():
            # Save the main entry first
            entry = form.save()
            print(f"Main entry saved with ID: {entry.id}")
            
            # Set the instance and save the formset
            formset.instance = entry
            saved_items = formset.save()
            print(f"Saved {len(saved_items)} items from formset")
            
            # Debug: Check what was actually saved
            for i, item in enumerate(saved_items):
                print(f"Item {i+1}: {item.item} - Slab: {item.slab_quantity} - CS: {item.c_s_quantity} - KG: {item.kg}")

            total_amount = Decimal("0.00")

            # Process each saved item for additional logic
            for item in saved_items:
                # Auto-link to stock lot if not already linked
                if not item.original_item:
                    original = FreezingEntryTenantItem.objects.filter(
                        item=item.item,
                        store=item.store,
                        freezing_entry__tenant_company_name=entry.tenant_company_name,
                        species=item.species,
                        grade=item.grade
                    ).order_by('-freezing_entry__freezing_date', '-id').first()
                    if original:
                        item.original_item = original
                        item.save()

                # Calculate amount based on tariff
                try:
                    tariff_obj = TenantFreezingTariff.objects.get(
                        tenant=entry.tenant_company_name,
                        category=item.freezing_category
                    )
                    tariff = Decimal(str(tariff_obj.tariff or 0))
                except TenantFreezingTariff.DoesNotExist:
                    tariff = Decimal("0.00")

                if item.kg:
                    total_amount += Decimal(str(item.kg)) * tariff

            # Update totals
            totals = entry.items.aggregate(
                total_slab_sum=Sum('slab_quantity'),
                total_c_s_sum=Sum('c_s_quantity'),
                total_kg_sum=Sum('kg'),
            )
            entry.total_slab = totals['total_slab_sum'] or 0
            entry.total_c_s = totals['total_c_s_sum'] or 0
            entry.total_kg = totals['total_kg_sum'] or 0
            entry.total_amount = total_amount
            entry.save()
            
            print(f"Updated totals - Slab: {entry.total_slab}, CS: {entry.total_c_s}, KG: {entry.total_kg}")

            messages.success(request, f'Return entry {entry.voucher_number} created successfully with {len(saved_items)} items!')
            return redirect(reverse('adminapp:list_return_tenant'))
        else:
            # Debug form and formset errors
            print("=== VALIDATION ERRORS ===")
            if not form.is_valid():
                print(f"Form errors: {form.errors}")
                messages.error(request, f'Form errors: {form.errors}')
            if not formset.is_valid():
                print(f"Formset errors: {formset.errors}")
                print(f"Formset non-form errors: {formset.non_form_errors()}")
                messages.error(request, f'Formset errors: {formset.errors}')
                
                # Debug individual form errors
                for i, form_instance in enumerate(formset):
                    if form_instance.errors:
                        print(f"Form {i} errors: {form_instance.errors}")
                        print(f"Form {i} cleaned_data: {form_instance.cleaned_data if form_instance.is_valid() else 'Invalid'}")
                
    else:
        form = ReturnTenantForm()
        formset = ReturnTenantItemFormSet()
        
    return render(request, 'adminapp/ReturnTenant/create.html', {
        'form': form,
        'formset': formset,
    })

def get_tenant_tariff(request):
    """
    Get tariff rate for a specific tenant and freezing category combination
    """
    tenant_id = request.GET.get('tenant_id')
    freezing_category_id = request.GET.get('freezing_category_id')
    
    if not tenant_id or not freezing_category_id:
        return JsonResponse({
            'success': False, 
            'error': 'Both tenant_id and freezing_category_id are required',
            'tariff': 0
        })
    
    try:
        tariff_obj = TenantFreezingTariff.objects.get(
            tenant_id=tenant_id,
            category_id=freezing_category_id
        )
        
        return JsonResponse({
            'success': True,
            'tariff': float(tariff_obj.tariff or 0),
            'tenant_name': str(tariff_obj.tenant),
            'category_name': str(tariff_obj.category)
        })
        
    except TenantFreezingTariff.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'No tariff found for this tenant and freezing category combination',
            'tariff': 0
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'tariff': 0
        })

def get_tenant_companies(request):
    """
    Fixed: Get tenant companies properly
    """
    try:
        # Get unique tenant companies from FreezingEntryTenant
        # Assuming FreezingEntryTenant has a foreign key to TenantCompany
        tenants = (
            FreezingEntryTenant.objects
            .values('tenant_company_name__id', 'tenant_company_name__company_name')
            .distinct()
            .order_by('tenant_company_name__company_name')
        )
        
        data = [{"id": t['tenant_company_name__id'], "name": t['tenant_company_name__company_name']} 
                for t in tenants if t['tenant_company_name__id'] is not None]
        
        return JsonResponse({"tenants": data})
    
    except Exception as e:
        print(f"Error in get_tenant_companies: {str(e)}")
        # Fallback: Get all tenant companies
        try:
            all_tenants = FreezingEntryTenant.objects.all().order_by('company_name')
            data = [{"id": t.id, "name": t.company_name} for t in all_tenants]
            return JsonResponse({"tenants": data})
        except Exception as e2:
            print(f"Fallback error in get_tenant_companies: {str(e2)}")
            return JsonResponse({"tenants": []})

def calculate_return_total_amount(request):
    """
    Calculate total amount based on current form data
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'})
    
    try:
        tenant_id = request.POST.get('tenant_id')
        items_data = []
        
        # Parse formset data
        form_count = int(request.POST.get('form-TOTAL_FORMS', 0))
        
        for i in range(form_count):
            # Skip deleted forms
            if request.POST.get(f'form-{i}-DELETE'):
                continue
                
            freezing_category_id = request.POST.get(f'form-{i}-freezing_category')
            kg_weight = request.POST.get(f'form-{i}-kg')
            
            if freezing_category_id and kg_weight:
                try:
                    kg_weight = Decimal(str(kg_weight))
                    if kg_weight > 0:
                        items_data.append({
                            'freezing_category_id': freezing_category_id,
                            'kg': kg_weight
                        })
                except (ValueError, TypeError):
                    continue
        
        if not tenant_id or not items_data:
            return JsonResponse({
                'success': True,
                'total_amount': 0.00,
                'item_amounts': []
            })
        
        total_amount = Decimal('0.00')
        item_amounts = []
        
        # Calculate amount for each item
        for item_data in items_data:
            try:
                tariff_obj = TenantFreezingTariff.objects.get(
                    tenant_id=tenant_id,
                    category_id=item_data['freezing_category_id']
                )
                tariff = Decimal(str(tariff_obj.tariff or 0))
                item_amount = item_data['kg'] * tariff
                total_amount += item_amount
                
                item_amounts.append({
                    'freezing_category_id': item_data['freezing_category_id'],
                    'kg': float(item_data['kg']),
                    'tariff': float(tariff),
                    'amount': float(item_amount)
                })
                
            except TenantFreezingTariff.DoesNotExist:
                # No tariff found - contribute 0 to total
                item_amounts.append({
                    'freezing_category_id': item_data['freezing_category_id'],
                    'kg': float(item_data['kg']),
                    'tariff': 0,
                    'amount': 0,
                    'error': 'No tariff found'
                })
        
        return JsonResponse({
            'success': True,
            'total_amount': float(total_amount),
            'item_amounts': item_amounts,
            'item_count': len(items_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'total_amount': 0
        })

def get_tenant_original_items(request):
    """
    AJAX view to get original items filtered by tenant company
    """
    tenant_id = request.GET.get('tenant_id')
    item_id = request.GET.get('item_id')  # For getting specific item details
    
    if not tenant_id and not item_id:
        return JsonResponse({'success': False, 'error': 'No tenant ID or item ID provided'})
    
    try:
        # If item_id is provided, return specific item details
        if item_id:
            try:
                item = FreezingEntryTenantItem.objects.select_related(
                    'item', 'species', 'grade', 'unit', 'freezing_category', 
                    'store', 'item_quality', 'glaze', 'brand', 'processing_center'
                ).get(id=item_id)
                
                return JsonResponse({
                    'success': True,
                    'item_name': str(item.item) if item.item else '',
                    'full_description': f"{item.item} - {item.species} - {item.grade}" if all([item.item, item.species, item.grade]) else str(item.item),
                    'item': item.item.id if item.item else None,
                    'store': item.store.id if item.store else None,
                    'item_quality': item.item_quality.id if item.item_quality else None,
                    'unit': item.unit.id if item.unit else None,
                    'species': item.species.id if item.species else None,
                    'grade': item.grade.id if item.grade else None,
                    'glaze': item.glaze.id if item.glaze else None,
                    'freezing_category': item.freezing_category.id if item.freezing_category else None,
                    'brand': item.brand.id if item.brand else None,
                    'processing_center': item.processing_center.id if item.processing_center else None,
                    'slab_quantity': float(item.slab_quantity) if item.slab_quantity else 0,
                    'kg': float(item.kg) if item.kg else 0,
                })
            except FreezingEntryTenantItem.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Item not found'})
        
        # Get tenant and filter original items
        try:
            # Get the tenant by ID
            from django.shortcuts import get_object_or_404
            tenant = get_object_or_404(Tenant, id=tenant_id)
        except:
            return JsonResponse({'success': False, 'error': 'Tenant not found'})
        
        # Filter original items by the selected tenant company
        original_items = FreezingEntryTenantItem.objects.filter(
            freezing_entry__tenant_company_name=tenant  # This filters by the tenant object
        ).select_related(
            'item', 'species', 'grade', 'unit', 'freezing_category',
            'freezing_entry'  # Added to access freezing_entry data
        ).order_by('-freezing_entry__freezing_date', '-id').distinct()
        
        items_data = []
        for item in original_items:
            # Create a descriptive display name for each item
            display_parts = []
            
            if item.item:
                display_parts.append(str(item.item))
            if item.species:
                display_parts.append(str(item.species))
            if item.grade:
                display_parts.append(str(item.grade))
            if item.unit:
                display_parts.append(f"({item.unit})")
            
            # Add quantities for reference
            quantities = []
            if item.slab_quantity:
                quantities.append(f"Slab: {item.slab_quantity}")
            if item.kg:
                quantities.append(f"KG: {item.kg}")
            
            if quantities:
                display_parts.append(f"[{', '.join(quantities)}]")
            
            # Add voucher number for better identification
            if item.freezing_entry and item.freezing_entry.voucher_number:
                display_parts.append(f"(Voucher: {item.freezing_entry.voucher_number})")
            
            display_name = " - ".join(display_parts) if display_parts else f"Item #{item.id}"
            
            items_data.append({
                'id': item.id,
                'display_name': display_name,
                'item_id': item.item.id if item.item else None,
                'item_name': str(item.item) if item.item else '',
                'species_name': str(item.species) if item.species else '',
                'grade_name': str(item.grade) if item.grade else '',
                'slab_quantity': float(item.slab_quantity) if item.slab_quantity else 0,
                'kg': float(item.kg) if item.kg else 0,
                'voucher_number': item.freezing_entry.voucher_number if item.freezing_entry else '',
            })
        
        return JsonResponse({
            'success': True,
            'items': items_data,
            'tenant_name': tenant.company_name,
            'count': len(items_data)
        })
        
    except Exception as e:
        print(f"Error in get_tenant_original_items: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@transaction.atomic
def return_tenant_update(request, pk):
    entry = get_object_or_404(ReturnTenant, pk=pk)
    if request.method == "POST":
        form = ReturnTenantForm(request.POST, instance=entry)
        formset = ReturnTenantItemFormSet(request.POST, instance=entry)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()

            totals = entry.items.aggregate(
                total_slab_sum=Sum('slab_quantity'),
                total_c_s_sum=Sum('c_s_quantity'),
                total_kg_sum=Sum('kg'),
            )
            entry.total_slab = totals['total_slab_sum'] or 0
            entry.total_c_s = totals['total_c_s_sum'] or 0
            entry.total_kg = totals['total_kg_sum'] or 0
            entry.total_amount = 0
            entry.save()

            return redirect(reverse('adminapp:list_return_tenant'))
    else:
        form = ReturnTenantForm(instance=entry)
        formset = ReturnTenantItemFormSet(instance=entry)
    return render(request, 'adminapp/ReturnTenant/update.html', {'form': form, 'formset': formset})

def return_tenant_delete(request, pk):
    entry = get_object_or_404(ReturnTenant, pk=pk)
    if request.method == "POST":
        entry.delete()
        return redirect('adminapp:list_return_tenant')
    return render(request, 'adminapp/confirm_delete.html', {'entry': entry})

def return_tenant_list(request):
    entries = ReturnTenant.objects.all().order_by('-return_date')
    return render(request, 'adminapp/ReturnTenant/list.html', {'entries': entries})

def generate_return_tenant_pdf(request, pk):
    """
    Generate PDF for ReturnTenant detail view
    """
    # Get the ReturnTenant object
    entry = get_object_or_404(ReturnTenant, pk=pk)
    
    # Get the PDF template
    template = get_template('adminapp/ReturnTenant/pdf_detail.html')
    
    # Context data for the template
    context = {
        'entry': entry,
        'items': entry.items.all(),
        'company_name': 'Your Company Name',  # Add your company name
        'company_address': 'Your Company Address',  # Add your company address
        'phone': 'Your Phone Number',  # Add your phone number
        'email': 'your-email@company.com',  # Add your email
    }
    
    # Render the template with context
    html = template.render(context)
    
    # Create a BytesIO buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Generate PDF
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), buffer)
    
    if not pdf.err:
        # PDF generation successful
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="return_tenant_{entry.voucher_number}.pdf"'
        buffer.close()
        return response
    else:
        # PDF generation failed
        return HttpResponse("Error generating PDF", status=500)

def return_tenant_detail(request, pk):
    """
    Updated detail view with PDF generation option
    """
    entry = get_object_or_404(ReturnTenant, pk=pk)
    
    # Check if PDF generation is requested
    if request.GET.get('format') == 'pdf':
        return generate_return_tenant_pdf(request, pk)
    
    return render(request, 'adminapp/ReturnTenant/detail.html', {'entry': entry})




# # Tenant Stock Balance Views
def tenant_stock_balance(request):
    """
    Calculate current stock balance for all tenants
    """
    from django.db.models import Sum
    from collections import defaultdict
    
    # Get all freezing entries (INBOUND stock)
    freezing_data = FreezingEntryTenantItem.objects.select_related(
        'freezing_entry__tenant_company_name', 'item', 'species', 'grade', 'store'
    ).values(
        'freezing_entry__tenant_company_name__company_name',
        'freezing_entry__tenant_company_name__id',
        'item__name',
        'species__name',
        'grade__grade',
        'store__name'
    ).annotate(
        total_slab_in=Sum('slab_quantity'),
        total_cs_in=Sum('c_s_quantity'),
        total_kg_in=Sum('kg')
    )
    
    # Get all return entries (OUTBOUND stock)
    return_data = ReturnTenantItem.objects.select_related(
        'return_entry__tenant_company_name', 'item', 'species', 'grade', 'store'
    ).values(
        'return_entry__tenant_company_name__company_name',
        'return_entry__tenant_company_name__id',
        'item__name',
        'species__name',
        'grade__grade',
        'store__name'
    ).annotate(
        total_slab_out=Sum('slab_quantity'),
        total_cs_out=Sum('c_s_quantity'),
        total_kg_out=Sum('kg')
    )
    
    # Calculate balance for each tenant-item combination
    balance_data = defaultdict(lambda: {
        'slab_in': 0, 'cs_in': 0, 'kg_in': 0,
        'slab_out': 0, 'cs_out': 0, 'kg_out': 0,
        'slab_balance': 0, 'cs_balance': 0, 'kg_balance': 0
    })
    
    # Process inbound data
    for entry in freezing_data:
        key = (
            entry['freezing_entry__tenant_company_name__id'],
            entry['freezing_entry__tenant_company_name__company_name'],
            entry['item__name'],
            entry['species__name'],
            entry['grade__grade'],
            entry['store__name']
        )
        balance_data[key]['slab_in'] = entry['total_slab_in'] or 0
        balance_data[key]['cs_in'] = entry['total_cs_in'] or 0
        balance_data[key]['kg_in'] = entry['total_kg_in'] or 0
    
    # Process outbound data
    for entry in return_data:
        key = (
            entry['return_entry__tenant_company_name__id'],
            entry['return_entry__tenant_company_name__company_name'],
            entry['item__name'],
            entry['species__name'],
            entry['grade__grade'],
            entry['store__name']
        )
        balance_data[key]['slab_out'] = entry['total_slab_out'] or 0
        balance_data[key]['cs_out'] = entry['total_cs_out'] or 0
        balance_data[key]['kg_out'] = entry['total_kg_out'] or 0
    
    # Calculate final balances
    stock_balance = []
    for key, data in balance_data.items():
        tenant_id, tenant_name, item_name, species, grade, store = key
        
        slab_balance = data['slab_in'] - data['slab_out']
        cs_balance = data['cs_in'] - data['cs_out']
        kg_balance = data['kg_in'] - data['kg_out']
        
        # Only show items with remaining stock
        if slab_balance > 0 or cs_balance > 0 or kg_balance > 0:
            stock_balance.append({
                'tenant_id': tenant_id,
                'tenant_name': tenant_name,
                'item_name': item_name,
                'species': species,
                'grade': grade,
                'store': store,
                'slab_in': data['slab_in'],
                'cs_in': data['cs_in'], 
                'kg_in': data['kg_in'],
                'slab_out': data['slab_out'],
                'cs_out': data['cs_out'],
                'kg_out': data['kg_out'],
                'slab_balance': slab_balance,
                'cs_balance': cs_balance,
                'kg_balance': kg_balance,
            })
    
    # Sort by tenant name, then item name
    stock_balance.sort(key=lambda x: (x['tenant_name'], x['item_name']))
    
    context = {
        'stock_balance': stock_balance,
        'total_items': len(stock_balance)
    }
    return render(request, 'adminapp/TenantStock/balance.html', context)

def tenant_stock_detail(request, tenant_id):
    """
    Detailed stock view for a specific tenant
    """
    try:
        # Get the actual Tenant object, not ReturnTenant
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        messages.error(request, 'Tenant not found.')
        return redirect('adminapp:tenant_stock_balance')
    
    # Get detailed freezing entries for this tenant
    freezing_entries = FreezingEntryTenantItem.objects.filter(
        freezing_entry__tenant_company_name=tenant
    ).select_related(
        'freezing_entry', 'item', 'species', 'grade', 'store', 'unit'
    ).order_by('-freezing_entry__freezing_date')
    
    # Get detailed return entries for this tenant
    return_entries = ReturnTenantItem.objects.filter(
        return_entry__tenant_company_name=tenant
    ).select_related(
        'return_entry', 'item', 'species', 'grade', 'store', 'unit'
    ).order_by('-return_entry__return_date')
    
    # Calculate totals
    freezing_totals = freezing_entries.aggregate(
        total_slab=Sum('slab_quantity'),
        total_cs=Sum('c_s_quantity'),
        total_kg=Sum('kg')
    )
    
    return_totals = return_entries.aggregate(
        total_slab=Sum('slab_quantity'),
        total_cs=Sum('c_s_quantity'), 
        total_kg=Sum('kg')
    )
    
    balance_totals = {
        'slab_balance': (freezing_totals['total_slab'] or 0) - (return_totals['total_slab'] or 0),
        'cs_balance': (freezing_totals['total_cs'] or 0) - (return_totals['total_cs'] or 0),
        'kg_balance': (freezing_totals['total_kg'] or 0) - (return_totals['total_kg'] or 0),
    }
    
    context = {
        'tenant': tenant,
        'freezing_entries': freezing_entries,
        'return_entries': return_entries,
        'freezing_totals': freezing_totals,
        'return_totals': return_totals,
        'balance_totals': balance_totals,
    }
    return render(request, 'adminapp/TenantStock/detail.html', context)

def tenant_stock_summary(request):
    """
    Summary view showing total stock per tenant
    """
    tenants = Tenant.objects.all()  # Get all tenants, not ReturnTenant objects
    tenant_summary = []
    
    for tenant in tenants:
        # Calculate totals for this tenant
        freezing_totals = FreezingEntryTenantItem.objects.filter(
            freezing_entry__tenant_company_name=tenant
        ).aggregate(
            total_slab=Sum('slab_quantity'),
            total_cs=Sum('c_s_quantity'),
            total_kg=Sum('kg')
        )
        
        return_totals = ReturnTenantItem.objects.filter(
            return_entry__tenant_company_name=tenant  # Fixed: return_entry instead of return_tenant
        ).aggregate(
            total_slab=Sum('slab_quantity'),
            total_cs=Sum('c_s_quantity'),
            total_kg=Sum('kg')
        )
        
        slab_balance = (freezing_totals['total_slab'] or 0) - (return_totals['total_slab'] or 0)
        cs_balance = (freezing_totals['total_cs'] or 0) - (return_totals['total_cs'] or 0)
        kg_balance = (freezing_totals['total_kg'] or 0) - (return_totals['total_kg'] or 0)
        
        # Count unique items
        item_count = FreezingEntryTenantItem.objects.filter(
            freezing_entry__tenant_company_name=tenant
        ).values('item', 'species', 'grade').distinct().count()
        
        tenant_summary.append({
            'tenant': tenant,
            'freezing_totals': freezing_totals,
            'return_totals': return_totals,
            'slab_balance': slab_balance,
            'cs_balance': cs_balance,
            'kg_balance': kg_balance,
            'item_count': item_count,
            'has_stock': slab_balance > 0 or cs_balance > 0 or kg_balance > 0
        })
    
    context = {
        'tenant_summary': tenant_summary,
    }
    return render(request, 'adminapp/TenantStock/summary.html', context)







def create_tenant_bill(tenant, from_date, to_date):
    """
    Create a TenantBill and items from freezing entries between from_date and to_date.
    Calculation is tariff × kg (not per-day).
    Returns the created or existing bill, or None if nothing to bill.
    """
    # avoid duplicates for exact period
    existing = TenantBill.objects.filter(
        tenant=tenant, from_date=from_date, to_date=to_date
    ).first()
    if existing:
        logger.info(f"Bill already exists for {tenant} {from_date} to {to_date}")
        return existing

    entries = FreezingEntryTenant.objects.filter(
        tenant_company_name=tenant,
        freezing_date__gte=from_date,
        freezing_date__lte=to_date,
        freezing_status="complete",
    ).prefetch_related("items")

    if not entries.exists():
        logger.info(f"No freezing entries for {tenant} between {from_date} and {to_date}")
        return None

    bill = TenantBill.objects.create(
        tenant=tenant,
        from_date=from_date,
        to_date=to_date,
    )

    totals = {"amount": Decimal("0.00"), "slabs": 0, "cs": 0, "kg": Decimal("0.00")}
    items_created = 0

    for entry in entries:
        for item in entry.items.all():
            try:
                tariff_obj = TenantFreezingTariff.objects.get(
                    tenant=tenant, category=item.freezing_category
                )
                tariff = Decimal(str(tariff_obj.tariff))
            except TenantFreezingTariff.DoesNotExist:
                logger.warning(f"No tariff for {tenant} - {item.freezing_category}; using 0.00")
                tariff = Decimal("0.00")

            # quantity
            kg_quantity = Decimal(str(getattr(item, "kg", 0)))

            # ✅ only tariff × kg
            line_total = tariff * kg_quantity

            TenantBillItem.objects.create(
                bill=bill,
                freezing_entry=entry,
                freezing_entry_item=item,
                slab_quantity=getattr(item, "slab_quantity", 0),
                c_s_quantity=getattr(item, "c_s_quantity", 0),
                kg_quantity=kg_quantity,
                days_stored=0,             # optional placeholder
                tariff_per_day=tariff,     # actually "tariff", no per-day calc
                line_total=line_total,
            )

            totals["amount"] += line_total
            totals["slabs"] += getattr(item, "slab_quantity", 0) or 0
            totals["cs"] += getattr(item, "c_s_quantity", 0) or 0
            totals["kg"] += kg_quantity
            items_created += 1

    # update totals on bill
    bill.total_amount = totals["amount"]
    bill.total_slabs = totals["slabs"]
    bill.total_c_s = totals["cs"]
    bill.total_kg = totals["kg"]
    bill.save()

    logger.info(f"Created bill {bill.pk} ({items_created} items) for tenant {tenant}")
    return bill

def auto_generate_bills():
    """
    Generate bills for all TenantBillingConfiguration entries that are due.
    Returns (generated_bills_list, errors_list)
    """
    today = timezone.now().date()
    configs_due = TenantBillingConfiguration.objects.filter(is_active=True, next_bill_date__lte=today)
    generated = []
    errors = []

    for config in configs_due:
        try:
            from_date = (config.last_bill_generated_date + timedelta(days=1)) if config.last_bill_generated_date else config.billing_start_date
            to_date = today

            if from_date > to_date:
                logger.warning(f"Skipping {config.tenant}: from_date {from_date} > to_date {to_date}")
                continue

            bill = create_tenant_bill(config.tenant, from_date, to_date)
            if bill:
                generated.append(bill)
                # update config
                config.last_bill_generated_date = to_date
                config.next_bill_date = to_date + timedelta(days=config.billing_frequency_days)
                config.save()
        except Exception as e:
            logger.exception(f"Auto billing error for {config.tenant}: {e}")
            errors.append(f"{config.tenant}: {str(e)}")

    return generated, errors

def generate_manual_bill(request):
    """Form to generate bill for chosen tenant and date range"""
    if request.method == 'POST':
        form = BillGenerationForm(request.POST)
        if form.is_valid():
            tenant = form.cleaned_data['tenant']
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']

            bill = create_tenant_bill(tenant, from_date, to_date)
            if bill:
                messages.success(request, f"Bill {getattr(bill, 'bill_number', bill.id)} created successfully.")
                return redirect('adminapp:view_bill', bill_id=bill.id)
            else:
                messages.warning(request, "No freezing entries found for selected period.")
    else:
        tenant_id = request.GET.get("tenant_id")
        initial = {}
        if tenant_id:
            from adminapp.models import TenantBill  # adjust if different app name
            try:
                last_bill = TenantBill.objects.filter(tenant_id=tenant_id).order_by('-to_date').first()
                if last_bill:
                    # Set next start date = last bill end date + 1 day
                    initial['from_date'] = last_bill.to_date + timedelta(days=1)
            except TenantBill.DoesNotExist:
                pass

        form = BillGenerationForm(initial=initial)

    return render(request, 'adminapp/billing/generate_manual_bill.html', {'form': form})

def run_auto_billing(request):
    """
    Trigger auto billing manually.
    If POST contains config_id -> generate only for that config.
    Otherwise generate for all due configs.
    """
    if request.method == 'POST':
        config_id = request.POST.get('config_id')
        if config_id:
            config = get_object_or_404(TenantBillingConfiguration, id=config_id)
            today = timezone.now().date()
            from_date = (config.last_bill_generated_date + timedelta(days=1)) if config.last_bill_generated_date else config.billing_start_date
            bill = create_tenant_bill(config.tenant, from_date, today)
            if bill:
                config.last_bill_generated_date = today
                config.next_bill_date = today + timedelta(days=config.billing_frequency_days)
                config.save()
                messages.success(request, f"Generated bill {getattr(bill, 'bill_number', bill.id)} for {config.tenant}")
            else:
                messages.warning(request, f"No freezing entries found for {config.tenant}")
        else:
            bills, errors = auto_generate_bills()
            if bills:
                messages.success(request, f"Generated {len(bills)} bills.")
            else:
                messages.info(request, "No bills generated. No due configurations found.")
            for e in errors:
                messages.error(request, e)
    return redirect('adminapp:billing_config_list')

def view_bill(request, bill_id):
    bill = get_object_or_404(TenantBill, id=bill_id)
    items = bill.items.select_related('freezing_entry', 'freezing_entry_item').all()
    return render(request, 'adminapp/billing/view_bill.html', {'bill': bill, 'items': items})

def bill_list(request):
    bills = TenantBill.objects.select_related('tenant').order_by('-created_at')
    return render(request, 'adminapp/billing/bill_list.html', {'bills': bills})

def update_bill_status(request, bill_id):
    if request.method == 'POST':
        bill = get_object_or_404(TenantBill, id=bill_id)
        new_status = request.POST.get('status')
        if new_status in dict(TenantBill.BILL_STATUS_CHOICES):
            bill.status = new_status
            bill.save()
            messages.success(request, f"Bill {bill.bill_number} status updated to {new_status}")
    return redirect('adminapp:view_bill', bill_id=bill_id)

def delete_bill(request, bill_id):
    bill = get_object_or_404(TenantBill, id=bill_id)
    if request.method == 'POST':
        if bill.status == 'paid':
            messages.error(request, 'Cannot delete a paid bill.')
            return redirect('adminapp:view_bill', bill_id=bill.id)
        bill_number = bill.bill_number
        bill.delete()
        messages.success(request, f'Bill {bill_number} deleted successfully.')
        return redirect('adminapp:bill_list')
    # GET -> confirmation page
    return render(request, 'adminapp/billing/confirm_delete.html', {'bill': bill, 'bill_items_count': bill.items.count()})

def delete_bill_ajax(request, bill_id):
    if request.method == 'POST':
        bill = get_object_or_404(TenantBill, id=bill_id)
        if bill.status == 'paid':
            return JsonResponse({'success': False, 'message': 'Cannot delete paid bill'}, status=400)
        bill.delete()
        return JsonResponse({'success': True, 'message': 'Bill deleted'})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=405)

def billing_config_list(request):
    configs = TenantBillingConfiguration.objects.select_related('tenant').all()
    today = timezone.now().date()
    return render(request, 'adminapp/billing/config_list.html', {'configs': configs, 'today': today})

def setup_billing_configuration(request):
    if request.method == 'POST':
        form = TenantBillingConfigurationForm(request.POST)
        if form.is_valid():
            config = form.save()
            messages.success(request, f'Billing configuration created for {config.tenant}')
            return redirect('adminapp:billing_config_list')
    else:
        form = TenantBillingConfigurationForm()
    return render(request, 'adminapp/billing/setup_config.html', {'form': form})

def debug_billing_status(request):
    today = timezone.now().date()
    all_configs = TenantBillingConfiguration.objects.select_related('tenant').all()
    configs_due = TenantBillingConfiguration.objects.filter(is_active=True, next_bill_date__lte=today)

    debug_data = {
        'system_status': {
            'current_date': str(today),
            'total_configs': all_configs.count(),
            'active_configs': all_configs.filter(is_active=True).count(),
            'configs_due': configs_due.count(),
        },
        'configurations': []
    }

    for config in all_configs:
        from_date = (config.last_bill_generated_date + timedelta(days=1)) if config.last_bill_generated_date else config.billing_start_date
        freezing_count = FreezingEntryTenant.objects.filter(
            tenant_company_name=config.tenant,
            freezing_date__range=(from_date, today),
            freezing_status='complete'
        ).count()
        debug_data['configurations'].append({
            'tenant': config.tenant.company_name,
            'is_active': config.is_active,
            'billing_start_date': str(config.billing_start_date),
            'billing_frequency_days': config.billing_frequency_days,
            'last_bill_generated_date': str(config.last_bill_generated_date) if config.last_bill_generated_date else None,
            'next_bill_date': str(config.next_bill_date),
            'is_due': config.is_active and config.next_bill_date <= today,
            'calculated_from_date': str(from_date),
            'freezing_entries_available': freezing_count,
        })

    if request.GET.get('format') == 'json':
        return JsonResponse(debug_data, indent=2)

    # simple HTML fallback
    html = ["<h2>Billing Debug Info</h2>"]
    html.append(f"<p>Today: {today}</p>")
    html.append(f"<p>Total Configs: {debug_data['system_status']['total_configs']}</p>")
    html.append(f"<p>Active Configs: {debug_data['system_status']['active_configs']}</p>")
    html.append(f"<p>Due Configs: {debug_data['system_status']['configs_due']}</p>")
    html.append("<hr><ul>")
    for c in debug_data['configurations']:
        html.append(f"<li>{c['tenant']} → Active: {c['is_active']}, Due: {c['is_due']}, Next: {c['next_bill_date']}, Entries: {c['freezing_entries_available']}</li>")
    html.append("</ul>")
    return HttpResponse(''.join(html))

def delete_billing_configuration(request, pk):
    config = get_object_or_404(TenantBillingConfiguration, pk=pk)
    if request.method == 'POST':
        tenant_name = config.tenant.company_name
        config.delete()
        messages.success(request, f'Billing configuration for {tenant_name} deleted successfully.')
        return redirect('adminapp:billing_config_list')
    return render(request, 'adminapp/billing/delete_confirm.html', {'config': config})

def get_last_bill_date(request):
    tenant_id = request.GET.get("tenant_id")
    if not tenant_id:
        return JsonResponse({"success": False, "error": "No tenant_id given"})

    last_bill = TenantBill.objects.filter(tenant_id=tenant_id).order_by('-to_date').first()
    if last_bill:
        next_from_date = last_bill.to_date + timedelta(days=1)
        return JsonResponse({
            "success": True,
            "last_to_date": last_bill.to_date,
            "next_from_date": next_from_date
        })
    return JsonResponse({"success": False, "error": "No bills found"})

def render_to_pdf(template_src, context_dict={}):
    """
    Utility function to render a template to PDF using xhtml2pdf.
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="bill.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

def bill_pdf(request, bill_id):
    """
    Generate PDF for a TenantBill with grouped categories and qualities.
    """
    bill = get_object_or_404(TenantBill, id=bill_id)

    # Use the correct related_name from your TenantBillItem model (likely "items")
    items = bill.items.select_related("freezing_entry_item").all()

    categories_dict = defaultdict(lambda: {
        "name": None,
        "number": 0,
        "qualities": defaultdict(lambda: {
            "kg_quantity": Decimal("0"),
            "line_total": Decimal("0"),
            "tariff_per_day": Decimal("0"),
            "count": 0,
        }),
        "total_kg": Decimal("0"),
        "total_amount": Decimal("0"),
    })

    for item in items:
        category_obj = item.freezing_entry_item.freezing_category
        category_name = str(category_obj) if category_obj else "Uncategorized"
        item_quality = item.freezing_entry_item.item_quality or "N/A"

        if not categories_dict[category_name]["name"]:
            categories_dict[category_name]["name"] = category_obj or category_name

        # Group by quality
        quality_data = categories_dict[category_name]["qualities"][item_quality]
        quality_data["kg_quantity"] += Decimal(str(item.kg_quantity))
        quality_data["line_total"] += Decimal(str(item.line_total))
        quality_data["count"] += 1

        # Weighted avg tariff
        if quality_data["tariff_per_day"] == Decimal("0"):
            quality_data["tariff_per_day"] = Decimal(str(item.tariff_per_day))
        else:
            total_tariff = (
                quality_data["tariff_per_day"] * (quality_data["count"] - 1)
                + Decimal(str(item.tariff_per_day))
            )
            quality_data["tariff_per_day"] = total_tariff / quality_data["count"]

        # Category totals
        categories_dict[category_name]["total_kg"] += Decimal(str(item.kg_quantity))
        categories_dict[category_name]["total_amount"] += Decimal(str(item.line_total))

    # Convert to structured list for template
    categories = []
    category_number = 1
    for category_name, category_data in categories_dict.items():
        merged_items = []
        for quality, quality_data in category_data["qualities"].items():
            merged_items.append({
                "freezing_entry_item": {
                    "item_quality": quality
                },
                "kg_quantity": quality_data["kg_quantity"],
                "tariff_per_day": quality_data["tariff_per_day"],
                "line_total": quality_data["line_total"],
            })

        categories.append({
            "number": category_number,
            "name": category_name,  # stringified category name
            "items": merged_items,
            "total_kg": category_data["total_kg"],
            "total_amount": category_data["total_amount"],
        })
        category_number += 1

    # Sort categories by their name (string)
    categories.sort(key=lambda x: str(x["name"]))

    context = {
        "bill": bill,
        "categories": categories,
        "items": items,  # keep original items for fallback rendering
    }

    return render_to_pdf("adminapp/billing/bill_pdf.html", context)

    # Get the bill object
    bill = get_object_or_404(TenantBill, id=bill_id)
    
    # Get all items for this bill - adjust the relationship name based on your model
    # Common relationship names: tenantbillitem_set, bill_items, items, etc.
    items = bill.tenantbillitem_set.all().select_related('freezing_entry_item')
    
    # Group items by category and then by item quality
    categories_dict = defaultdict(lambda: {
        'name': '',
        'number': 0,
        'qualities': defaultdict(lambda: {
            'kg_quantity': Decimal('0'),
            'line_total': Decimal('0'),
            'tariff_per_day': Decimal('0'),
            'count': 0
        }),
        'total_kg': Decimal('0'),
        'total_amount': Decimal('0')
    })
    
    # Process each item
    for item in items:
        category_name = item.freezing_entry_item.freezing_category
        item_quality = item.freezing_entry_item.item_quality or "N/A"
        
        # Initialize category info if first time
        if not categories_dict[category_name]['name']:
            categories_dict[category_name]['name'] = category_name
        
        # Group by item quality within category
        quality_data = categories_dict[category_name]['qualities'][item_quality]
        quality_data['kg_quantity'] += Decimal(str(item.kg_quantity))
        quality_data['line_total'] += Decimal(str(item.line_total))
        quality_data['count'] += 1
        
        # For tariff_per_day, we'll take the average or you can modify this logic
        if quality_data['tariff_per_day'] == Decimal('0'):
            quality_data['tariff_per_day'] = Decimal(str(item.tariff_per_day))
        else:
            # Calculate weighted average of tariff_per_day
            total_tariff = quality_data['tariff_per_day'] * (quality_data['count'] - 1) + Decimal(str(item.tariff_per_day))
            quality_data['tariff_per_day'] = total_tariff / quality_data['count']
        
        # Update category totals
        categories_dict[category_name]['total_kg'] += Decimal(str(item.kg_quantity))
        categories_dict[category_name]['total_amount'] += Decimal(str(item.line_total))
    
    # Convert to structured format for template
    categories = []
    category_number = 1
    
    for category_name, category_data in categories_dict.items():
        merged_items = []
        
        for quality, quality_data in category_data['qualities'].items():
            merged_items.append({
                'freezing_entry_item': {
                    'item_quality': quality
                },
                'kg_quantity': quality_data['kg_quantity'],
                'tariff_per_day': quality_data['tariff_per_day'],
                'line_total': quality_data['line_total']
            })
        
        categories.append({
            'number': category_number,
            'name': category_name,
            'items': merged_items,
            'total_kg': category_data['total_kg'],
            'total_amount': category_data['total_amount']
        })
        category_number += 1
    
    # Sort categories by name for consistent output
    categories.sort(key=lambda x: x['name'])
    
    context = {
        'bill': bill,
        'categories': categories,
        'items': items,  # Keep original items for fallback
    }
    
    return render_to_pdf('bill_template.html', context)





def bill_list_by_status(request, status):
    """Generic view to list bills by status."""
    bills = TenantBill.objects.filter(status=status).select_related("tenant").order_by("-created_at")
    return render(request, f"adminapp/billing/bill_list_{status}.html", {
        "bills": bills,
        "status": status,
    })


def bill_list_draft(request):
    return bill_list_by_status(request, "draft")


def bill_list_finalized(request):
    return bill_list_by_status(request, "finalized")


def bill_list_sent(request):
    return bill_list_by_status(request, "sent")


def bill_list_paid(request):
    return bill_list_by_status(request, "paid")


def bill_list_cancelled(request):
    return bill_list_by_status(request, "cancelled")






# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import StoreTransfer, StoreTransferItem, Stock, Store
from .forms import StoreTransferForm, StoreTransferItemFormSet
import json
from decimal import Decimal
from collections import defaultdict



@transaction.atomic
def create_store_transfer(request):
    if request.method == "POST":
        form = StoreTransferForm(request.POST)
        formset = StoreTransferItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            transfer = form.save()
            
            # Process and merge duplicate items before saving
            merged_items = merge_duplicate_transfer_items(formset.cleaned_data)
            
            # Clear the original formset and create new items with merged data
            for item_data in merged_items:
                if item_data and not item_data.get('DELETE', False):
                    StoreTransferItem.objects.create(
                        transfer=transfer,
                        stock=item_data['stock'],
                        item_grade=item_data['item_grade'],
                        plus_qty=item_data['plus_qty'],
                        minus_qty=item_data['minus_qty'],
                        cs_quantity=item_data['cs_quantity'],
                        kg_quantity=item_data['kg_quantity']
                    )
            
            messages.success(request, f'Store transfer {transfer.voucher_no} created successfully!')
            return redirect("adminapp:store_transfer_list")
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StoreTransferForm()
        formset = StoreTransferItemFormSet()
    
    # Get available stocks for the from_store
    stocks = Stock.objects.none()
    if request.GET.get('from_store'):
        stocks = Stock.objects.filter(
            store_id=request.GET.get('from_store')
        ).select_related('item', 'brand', 'category')
    
    context = {
        "form": form, 
        "formset": formset,
        "stocks": stocks,
        "stores": Store.objects.all()
    }
    return render(request, "adminapp/store_transfer_form.html", context)

def merge_duplicate_transfer_items(formset_data):
    """
    Merge duplicate stock items in transfer by summing their quantities
    """
    merged_items = defaultdict(lambda: {
        'cs_quantity': Decimal('0'),
        'kg_quantity': Decimal('0'),
        'plus_qty': Decimal('0'),
        'minus_qty': Decimal('0'),
        'stock': None,
        'item_grade': None
    })
    
    for item_data in formset_data:
        if not item_data or item_data.get('DELETE', False):
            continue
            
        stock = item_data.get('stock')
        item_grade = item_data.get('item_grade', '')
        
        if not stock:
            continue
            
        # Create a unique key for grouping duplicates
        # Include item_grade in the key to handle different grades separately
        key = (stock.id, item_grade or '')
        
        # Sum up the quantities
        merged_items[key]['cs_quantity'] += item_data.get('cs_quantity', Decimal('0'))
        merged_items[key]['kg_quantity'] += item_data.get('kg_quantity', Decimal('0'))
        merged_items[key]['plus_qty'] += item_data.get('plus_qty', Decimal('0'))
        merged_items[key]['minus_qty'] += item_data.get('minus_qty', Decimal('0'))
        merged_items[key]['stock'] = stock
        merged_items[key]['item_grade'] = item_grade
    
    return list(merged_items.values())

@transaction.atomic
def edit_store_transfer(request, transfer_id):
    transfer = get_object_or_404(StoreTransfer, id=transfer_id)
    
    if request.method == "POST":
        form = StoreTransferForm(request.POST, instance=transfer)
        formset = StoreTransferItemFormSet(request.POST, instance=transfer)
        
        if form.is_valid() and formset.is_valid():
            # Reverse the original transfer effects on stock
            reverse_transfer_stock_effects(transfer)
            
            # Update the transfer
            transfer = form.save()
            
            # Clear existing items
            transfer.items.all().delete()
            
            # Process and merge duplicate items
            merged_items = merge_duplicate_transfer_items(formset.cleaned_data)
            
            # Create new items with merged data
            for item_data in merged_items:
                if item_data and not item_data.get('DELETE', False):
                    StoreTransferItem.objects.create(
                        transfer=transfer,
                        stock=item_data['stock'],
                        item_grade=item_data['item_grade'],
                        plus_qty=item_data['plus_qty'],
                        minus_qty=item_data['minus_qty'],
                        cs_quantity=item_data['cs_quantity'],
                        kg_quantity=item_data['kg_quantity']
                    )
            
            messages.success(request, f'Store transfer {transfer.voucher_no} updated successfully!')
            return redirect("adminapp:store_transfer_list")
    else:
        form = StoreTransferForm(instance=transfer)
        formset = StoreTransferItemFormSet(instance=transfer)
    
    stocks = Stock.objects.filter(
        store=transfer.from_store
    ).select_related('item', 'brand', 'category')
    
    context = {
        "form": form, 
        "formset": formset,
        "transfer": transfer,
        "stocks": stocks,
        "stores": Store.objects.all()
    }
    return render(request, "adminapp/store_transfer_form.html", context)

def reverse_transfer_stock_effects(transfer):
    """
    Reverse the stock effects of a transfer (for editing/deleting)
    """
    for item in transfer.items.all():
        # Add back to from_store
        from_stock = item.stock
        from_stock.cs_quantity += item.cs_quantity
        from_stock.kg_quantity += item.kg_quantity
        from_stock.save()
        
        # Remove from to_store
        try:
            to_stock = Stock.objects.get(
                store=transfer.to_store,
                category=from_stock.category,
                brand=from_stock.brand,
                unit=from_stock.unit,
                glaze=from_stock.glaze,
                item=from_stock.item,
                species=from_stock.species,
                selling_type=from_stock.selling_type,
                item_grade=item.item_grade or from_stock.item_grade,
            )
            to_stock.cs_quantity -= item.cs_quantity
            to_stock.kg_quantity -= item.kg_quantity
            
            # Delete the stock record if quantities become zero
            if to_stock.cs_quantity <= 0 and to_stock.kg_quantity <= 0:
                to_stock.delete()
            else:
                to_stock.save()
                
        except Stock.DoesNotExist:
            pass  # Stock might have been manually deleted

@transaction.atomic
def delete_store_transfer(request, transfer_id):
    transfer = get_object_or_404(StoreTransfer, id=transfer_id)
    
    if request.method == "POST":
        # Reverse the stock effects
        reverse_transfer_stock_effects(transfer)
        
        voucher_no = transfer.voucher_no
        transfer.delete()
        
        messages.success(request, f'Store transfer {voucher_no} deleted successfully!')
        return redirect("adminapp:store_transfer_list")
    
    return render(request, "adminapp/confirm_delete.html", {
        "object": transfer,
        "object_name": "Store Transfer"
    })

def store_transfer_list(request):
    transfers = StoreTransfer.objects.all().order_by("-date").select_related(
        'from_store', 'to_store'
    )
    
    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        transfers = transfers.filter(
            voucher_no__icontains=search_query
        )
    
    # Add pagination
    paginator = Paginator(transfers, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "transfers": page_obj,
        "search_query": search_query
    }
    return render(request, "adminapp/store_transfer_list.html", context)

def store_transfer_detail(request, transfer_id):
    transfer = get_object_or_404(
        StoreTransfer.objects.select_related('from_store', 'to_store'), 
        id=transfer_id
    )
    items = transfer.items.all().select_related('stock', 'stock__item', 'stock__brand')
    
    context = {
        "transfer": transfer,
        "items": items
    }
    return render(request, "adminapp/store_transfer_detail.html", context)

# AJAX endpoints for dynamic form behavior
@require_http_methods(["GET"])
def get_store_stocks(request, store_id):
    """
    AJAX endpoint to get stocks for a specific store
    """
    stocks = Stock.objects.filter(store_id=store_id).select_related(
        'item', 'brand', 'category'
    )
    
    stock_data = []
    for stock in stocks:
        stock_data.append({
            'id': stock.id,
            'item_name': stock.item.name,
            'brand_name': stock.brand.name,
            'category_name': stock.category.name,
            'unit': stock.unit,
            'glaze': stock.glaze or '',
            'species': stock.species or '',
            'item_grade': stock.item_grade or '',
            'cs_quantity': float(stock.cs_quantity),
            'kg_quantity': float(stock.kg_quantity),
            'display_name': f"{stock.item.name} - {stock.brand.name} ({stock.unit})"
        })
    
    return JsonResponse({'stocks': stock_data})

@require_http_methods(["GET"])
def get_stock_details(request, stock_id):
    """
    AJAX endpoint to get details of a specific stock
    """
    try:
        stock = Stock.objects.select_related(
            'item', 'brand', 'category'
        ).get(id=stock_id)
        
        stock_data = {
            'id': stock.id,
            'item_name': stock.item.name,
            'brand_name': stock.brand.name,
            'category_name': stock.category.name,
            'unit': stock.unit,
            'glaze': stock.glaze or '',
            'species': stock.species or '',
            'item_grade': stock.item_grade or '',
            'cs_quantity': float(stock.cs_quantity),
            'kg_quantity': float(stock.kg_quantity)
        }
        
        return JsonResponse({'stock': stock_data})
    except Stock.DoesNotExist:
        return JsonResponse({'error': 'Stock not found'}, status=404)

def validate_transfer_quantities(request):
    """
    AJAX endpoint to validate if transfer quantities are available in stock
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        stock_id = data.get('stock_id')
        cs_quantity = Decimal(str(data.get('cs_quantity', 0)))
        kg_quantity = Decimal(str(data.get('kg_quantity', 0)))
        
        try:
            stock = Stock.objects.get(id=stock_id)
            
            errors = []
            if cs_quantity > stock.cs_quantity:
                errors.append(f'CS quantity ({cs_quantity}) exceeds available stock ({stock.cs_quantity})')
            
            if kg_quantity > stock.kg_quantity:
                errors.append(f'KG quantity ({kg_quantity}) exceeds available stock ({stock.kg_quantity})')
            
            return JsonResponse({
                'valid': len(errors) == 0,
                'errors': errors,
                'available_cs': float(stock.cs_quantity),
                'available_kg': float(stock.kg_quantity)
            })
            
        except Stock.DoesNotExist:
            return JsonResponse({
                'valid': False,
                'errors': ['Stock not found']
            })
    
    return JsonResponse({'valid': False, 'errors': ['Invalid request']})






