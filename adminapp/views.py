from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CustomUserCreationForm

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def create_user_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('adminapp:create_user')  # You can redirect elsewhere
        else:
            messages.error(request, 'Error creating user.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'adminapp/create_user.html', {'form': form})


from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.shortcuts import render
from .models import *
from .forms import *

# Dashboard View
def admin_dashboard(request):
    return render(request, 'adminapp/dashboard.html')

# -------------------------------
# Operational & Location Masters
# -------------------------------

class ProcessingCenterCreateView(CreateView):
    model = ProcessingCenter
    form_class = ProcessingCenterForm
    template_name = 'adminapp/processingcenter_form.html'
    success_url = reverse_lazy('adminapp:processing_center_create')

class ProcessingCenterListView(ListView):
    model = ProcessingCenter
    template_name = 'adminapp/processingcenter_list.html'
    context_object_name = 'processing_centers'

class ProcessingCenterUpdateView(UpdateView):
    model = ProcessingCenter
    form_class = ProcessingCenterForm
    template_name = 'adminapp/processingcenter_form.html'
    success_url = reverse_lazy('adminapp:processing_center_list')

class ProcessingCenterDeleteView(DeleteView):
    model = ProcessingCenter
    template_name = 'adminapp/processingcenter_confirm_delete.html'
    success_url = reverse_lazy('adminapp:processing_center_list')

class StoreCreateView(CreateView):
    model = Store
    form_class = StoreForm
    template_name = 'adminapp/store_form.html'
    success_url = reverse_lazy('adminapp:store_create')

class StoreListView(ListView):
    model = Store
    template_name = 'adminapp/store_list.html'
    context_object_name = 'stores'

class StoreUpdateView(UpdateView):
    model = Store
    form_class = StoreForm
    template_name = 'adminapp/store_form.html'
    success_url = reverse_lazy('adminapp:store_list')

class StoreDeleteView(DeleteView):
    model = Store
    template_name = 'adminapp/store_confirm_delete.html'
    success_url = reverse_lazy('adminapp:store_list')

class PeelingCenterCreateView(CreateView):
    model = PeelingCenter
    form_class = PeelingCenterForm
    template_name = 'adminapp/peelingcenter_form.html'
    success_url = reverse_lazy('adminapp:peeling_center_create')

class PeelingCenterListView(ListView):
    model = PeelingCenter
    template_name = 'adminapp/peelingcenter_list.html'
    context_object_name = 'peeling_centers'

class PeelingCenterUpdateView(UpdateView):
    model = PeelingCenter
    form_class = PeelingCenterForm
    template_name = 'adminapp/peelingcenter_form.html'
    success_url = reverse_lazy('adminapp:peeling_center_list')

class PeelingCenterDeleteView(DeleteView):
    model = PeelingCenter
    template_name = 'adminapp/peelingcenter_confirm_delete.html'
    success_url = reverse_lazy('adminapp:peeling_center_list')

class PurchasingSpotCreateView(CreateView):
    model = PurchasingSpot
    form_class = PurchasingSpotForm
    template_name = 'adminapp/purchasingspot_form.html'
    success_url = reverse_lazy('adminapp:purchasing_spot_create')

class PurchasingSpotListView(ListView):
    model = PurchasingSpot
    template_name = 'adminapp/purchasingspot_list.html'
    context_object_name = 'purchasing_spots'

class PurchasingSpotUpdateView(UpdateView):
    model = PurchasingSpot
    form_class = PurchasingSpotForm
    template_name = 'adminapp/purchasingspot_form.html'
    success_url = reverse_lazy('adminapp:purchasing_spot_list')

class PurchasingSpotDeleteView(DeleteView):
    model = PurchasingSpot
    template_name = 'adminapp/purchasingspot_confirm_delete.html'
    success_url = reverse_lazy('adminapp:purchasing_spot_list')

# -------------------
# Personnel Masters
# -------------------

class PurchasingSupervisorCreateView(CreateView):
    model = PurchasingSupervisor
    form_class = PurchasingSupervisorForm
    template_name = 'adminapp/purchasingsupervisor_form.html'
    success_url = reverse_lazy('adminapp:purchasing_supervisor_create')

class PurchasingSupervisorListView(ListView):
    model = PurchasingSupervisor
    template_name = 'adminapp/purchasingsupervisor_list.html'
    context_object_name = 'purchasing_supervisors'

class PurchasingSupervisorUpdateView(UpdateView):
    model = PurchasingSupervisor
    form_class = PurchasingSupervisorForm
    template_name = 'adminapp/purchasingsupervisor_form.html'
    success_url = reverse_lazy('adminapp:purchasing_supervisor_list')

class PurchasingSupervisorDeleteView(DeleteView):
    model = PurchasingSupervisor
    template_name = 'adminapp/purchasingsupervisor_confirm_delete.html'
    success_url = reverse_lazy('adminapp:purchasing_supervisor_list')

class PurchasingAgentCreateView(CreateView):
    model = PurchasingAgent
    form_class = PurchasingAgentForm
    template_name = 'adminapp/purchasingagent_form.html'
    success_url = reverse_lazy('adminapp:purchasing_agent_create')

class PurchasingAgentListView(ListView):
    model = PurchasingAgent
    template_name = 'adminapp/purchasingagent_list.html'
    context_object_name = 'purchasing_agents'

class PurchasingAgentUpdateView(UpdateView):
    model = PurchasingAgent
    form_class = PurchasingAgentForm
    template_name = 'adminapp/purchasingagent_form.html'
    success_url = reverse_lazy('adminapp:purchasing_agent_list')

class PurchasingAgentDeleteView(DeleteView):
    model = PurchasingAgent
    template_name = 'adminapp/purchasingagent_confirm_delete.html'
    success_url = reverse_lazy('adminapp:purchasing_agent_list')

# ----------------------
# Item & Product Masters
# ----------------------

class ItemCategoryCreateView(CreateView):
    model = ItemCategory
    form_class = ItemCategoryForm
    template_name = 'adminapp/itemcategory_form.html'
    success_url = reverse_lazy('adminapp:item_category_create')

class ItemCategoryListView(ListView):
    model = ItemCategory
    template_name = 'adminapp/itemcategory_list.html'
    context_object_name = 'item_categories'

class ItemCategoryUpdateView(UpdateView):
    model = ItemCategory
    form_class = ItemCategoryForm
    template_name = 'adminapp/itemcategory_form.html'
    success_url = reverse_lazy('adminapp:item_category_list')

class ItemCategoryDeleteView(DeleteView):
    model = ItemCategory
    template_name = 'adminapp/itemcategory_confirm_delete.html'
    success_url = reverse_lazy('adminapp:item_category_list')

class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'adminapp/item_form.html'
    success_url = reverse_lazy('adminapp:item_create')

class ItemListView(ListView):
    model = Item
    template_name = 'adminapp/item_list.html'
    context_object_name = 'items'

class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'adminapp/item_form.html'
    success_url = reverse_lazy('adminapp:item_list')

class ItemDeleteView(DeleteView):
    model = Item
    template_name = 'adminapp/item_confirm_delete.html'
    success_url = reverse_lazy('adminapp:item_list')

class ItemGradeCreateView(CreateView):
    model = ItemGrade
    form_class = ItemGradeForm
    template_name = 'adminapp/itemgrade_form.html'
    success_url = reverse_lazy('adminapp:item_grade_create')

class ItemGradeListView(ListView):
    model = ItemGrade
    template_name = 'adminapp/itemgrade_list.html'
    context_object_name = 'item_grades'

class ItemGradeUpdateView(UpdateView):
    model = ItemGrade
    form_class = ItemGradeForm
    template_name = 'adminapp/itemgrade_form.html'
    success_url = reverse_lazy('adminapp:item_grade_list')

class ItemGradeDeleteView(DeleteView):
    model = ItemGrade
    template_name = 'adminapp/itemgrade_confirm_delete.html'
    success_url = reverse_lazy('adminapp:item_grade_list')

class FreezingCategoryCreateView(CreateView):
    model = FreezingCategory
    form_class = FreezingCategoryForm
    template_name = 'adminapp/freezingcategory_form.html'
    success_url = reverse_lazy('adminapp:freezing_category_create')

class FreezingCategoryListView(ListView):
    model = FreezingCategory
    template_name = 'adminapp/freezingcategory_list.html'
    context_object_name = 'freezing_categories'

class FreezingCategoryUpdateView(UpdateView):
    model = FreezingCategory
    form_class = FreezingCategoryForm
    template_name = 'adminapp/freezingcategory_form.html'
    success_url = reverse_lazy('adminapp:freezing_category_list')

class FreezingCategoryDeleteView(DeleteView):
    model = FreezingCategory
    template_name = 'adminapp/freezingcategory_confirm_delete.html'
    success_url = reverse_lazy('adminapp:freezing_category_list')

class PackingUnitCreateView(CreateView):
    model = PackingUnit
    form_class = PackingUnitForm
    template_name = 'adminapp/packingunit_form.html'
    success_url = reverse_lazy('adminapp:packing_unit_create')

class PackingUnitListView(ListView):
    model = PackingUnit
    template_name = 'adminapp/packingunit_list.html'
    context_object_name = 'packing_units'

class PackingUnitUpdateView(UpdateView):
    model = PackingUnit
    form_class = PackingUnitForm
    template_name = 'adminapp/packingunit_form.html'
    success_url = reverse_lazy('adminapp:packing_unit_list')

class PackingUnitDeleteView(DeleteView):
    model = PackingUnit
    template_name = 'adminapp/packingunit_confirm_delete.html'
    success_url = reverse_lazy('adminapp:packing_unit_list')

class GlazePercentageCreateView(CreateView):
    model = GlazePercentage
    form_class = GlazePercentageForm
    template_name = 'adminapp/glazepercentage_form.html'
    success_url = reverse_lazy('adminapp:glaze_percentage_create')

class GlazePercentageListView(ListView):
    model = GlazePercentage
    template_name = 'adminapp/glazepercentage_list.html'
    context_object_name = 'glaze_percentages'

class GlazePercentageUpdateView(UpdateView):
    model = GlazePercentage
    form_class = GlazePercentageForm
    template_name = 'adminapp/glazepercentage_form.html'
    success_url = reverse_lazy('adminapp:glaze_percentage_list')

class GlazePercentageDeleteView(DeleteView):
    model = GlazePercentage
    template_name = 'adminapp/glazepercentage_confirm_delete.html'
    success_url = reverse_lazy('adminapp:glaze_percentage_list')

class ItemBrandCreateView(CreateView):
    model = ItemBrand
    form_class = ItemBrandForm
    template_name = 'adminapp/itembrand_form.html'
    success_url = reverse_lazy('adminapp:item_brand_create')

class ItemBrandListView(ListView):
    model = ItemBrand
    template_name = 'adminapp/itembrand_list.html'
    context_object_name = 'item_brands'

class ItemBrandUpdateView(UpdateView):
    model = ItemBrand
    form_class = ItemBrandForm
    template_name = 'adminapp/itembrand_form.html'
    success_url = reverse_lazy('adminapp:item_brand_list')

class ItemBrandDeleteView(DeleteView):
    model = ItemBrand
    template_name = 'adminapp/itembrand_confirm_delete.html'
    success_url = reverse_lazy('adminapp:item_brand_list')

# ----------------------------
# Financial & Expense Masters
# ----------------------------

class TenantCreateView(CreateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'adminapp/tenant_form.html'
    success_url = reverse_lazy('adminapp:tenant_create')

class TenantListView(ListView):
    model = Tenant
    template_name = 'adminapp/tenant_list.html'
    context_object_name = 'tenants'

class TenantUpdateView(UpdateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'adminapp/tenant_form.html'
    success_url = reverse_lazy('adminapp:tenant_list')

class TenantDeleteView(DeleteView):
    model = Tenant
    template_name = 'adminapp/tenant_confirm_delete.html'
    success_url = reverse_lazy('adminapp:tenant_list')

class FreezingTariffCreateView(CreateView):
    model = FreezingTariff
    form_class = FreezingTariffForm
    template_name = 'adminapp/freezingtariff_form.html'
    success_url = reverse_lazy('adminapp:freezing_tariff_create')

class FreezingTariffListView(ListView):
    model = FreezingTariff
    template_name = 'adminapp/freezingtariff_list.html'
    context_object_name = 'freezing_tariffs'

class FreezingTariffUpdateView(UpdateView):
    model = FreezingTariff
    form_class = FreezingTariffForm
    template_name = 'adminapp/freezingtariff_form.html'
    success_url = reverse_lazy('adminapp:freezing_tariff_list')

class FreezingTariffDeleteView(DeleteView):
    model = FreezingTariff
    template_name = 'adminapp/freezingtariff_confirm_delete.html'
    success_url = reverse_lazy('adminapp:freezing_tariff_list')

class PeelingChargeCreateView(CreateView):
    model = PeelingCharge
    form_class = PeelingChargeForm
    template_name = 'adminapp/peelingcharge_form.html'
    success_url = reverse_lazy('adminapp:peeling_charge_create')

class PeelingChargeListView(ListView):
    model = PeelingCharge
    template_name = 'adminapp/peelingcharge_list.html'
    context_object_name = 'peeling_charges'

class PeelingChargeUpdateView(UpdateView):
    model = PeelingCharge
    form_class = PeelingChargeForm
    template_name = 'adminapp/peelingcharge_form.html'
    success_url = reverse_lazy('adminapp:peeling_charge_list')

class PeelingChargeDeleteView(DeleteView):
    model = PeelingCharge
    template_name = 'adminapp/peelingcharge_confirm_delete.html'
    success_url = reverse_lazy('adminapp:peeling_charge_list')

class PurchaseOverheadCreateView(CreateView):
    model = PurchaseOverhead
    form_class = PurchaseOverheadForm
    template_name = 'adminapp/purchaseoverhead_form.html'
    success_url = reverse_lazy('adminapp:purchase_overhead_create')

class PurchaseOverheadListView(ListView):
    model = PurchaseOverhead
    template_name = 'adminapp/purchaseoverhead_list.html'
    context_object_name = 'purchase_overheads'

class PurchaseOverheadUpdateView(UpdateView):
    model = PurchaseOverhead
    form_class = PurchaseOverheadForm
    template_name = 'adminapp/purchaseoverhead_form.html'
    success_url = reverse_lazy('adminapp:purchase_overhead_list')

class PurchaseOverheadDeleteView(DeleteView):
    model = PurchaseOverhead
    template_name = 'adminapp/purchaseoverhead_confirm_delete.html'
    success_url = reverse_lazy('adminapp:purchase_overhead_list')

class PeelingOverheadCreateView(CreateView):
    model = PeelingOverhead
    form_class = PeelingOverheadForm
    template_name = 'adminapp/peelingoverhead_form.html'
    success_url = reverse_lazy('adminapp:peeling_overhead_create')

class PeelingOverheadListView(ListView):
    model = PeelingOverhead
    template_name = 'adminapp/peelingoverhead_list.html'
    context_object_name = 'peeling_overheads'

class PeelingOverheadUpdateView(UpdateView):
    model = PeelingOverhead
    form_class = PeelingOverheadForm
    template_name = 'adminapp/peelingoverhead_form.html'
    success_url = reverse_lazy('adminapp:peeling_overhead_list')

class PeelingOverheadDeleteView(DeleteView):
    model = PeelingOverhead
    template_name = 'adminapp/peelingoverhead_confirm_delete.html'
    success_url = reverse_lazy('adminapp:peeling_overhead_list')

class ProcessingOverheadCreateView(CreateView):
    model = ProcessingOverhead
    form_class = ProcessingOverheadForm
    template_name = 'adminapp/processingoverhead_form.html'
    success_url = reverse_lazy('adminapp:processing_overhead_create')

class ProcessingOverheadListView(ListView):
    model = ProcessingOverhead
    template_name = 'adminapp/processingoverhead_list.html'
    context_object_name = 'processing_overheads'

class ProcessingOverheadUpdateView(UpdateView):
    model = ProcessingOverhead
    form_class = ProcessingOverheadForm
    template_name = 'adminapp/processingoverhead_form.html'
    success_url = reverse_lazy('adminapp:processing_overhead_list')

class ProcessingOverheadDeleteView(DeleteView):
    model = ProcessingOverhead
    template_name = 'adminapp/processingoverhead_confirm_delete.html'
    success_url = reverse_lazy('adminapp:processing_overhead_list')

class ShipmentOverheadCreateView(CreateView):
    model = ShipmentOverhead
    form_class = ShipmentOverheadForm
    template_name = 'adminapp/shipmentoverhead_form.html'
    success_url = reverse_lazy('adminapp:shipment_overhead_create')

class ShipmentOverheadListView(ListView):
    model = ShipmentOverhead
    template_name = 'adminapp/shipmentoverhead_list.html'
    context_object_name = 'shipment_overheads'

class ShipmentOverheadUpdateView(UpdateView):
    model = ShipmentOverhead
    form_class = ShipmentOverheadForm
    template_name = 'adminapp/shipmentoverhead_form.html'
    success_url = reverse_lazy('adminapp:shipment_overhead_list')

class ShipmentOverheadDeleteView(DeleteView):
    model = ShipmentOverhead
    template_name = 'adminapp/shipmentoverhead_confirm_delete.html'
    success_url = reverse_lazy('adminapp:shipment_overhead_list')