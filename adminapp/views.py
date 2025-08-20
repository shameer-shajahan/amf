
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
    success_url = reverse_lazy('adminapp:tenant_create')

class TenantListView(ListView):
    model = Tenant
    template_name = 'adminapp/list/tenant_list.html'
    context_object_name = 'tenants'

class TenantUpdateView(UpdateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'adminapp/forms/tenant_form.html'
    success_url = reverse_lazy('adminapp:tenant_list')

class TenantDeleteView(DeleteView):
    model = Tenant
    template_name = 'adminapp/confirm_delete.html'
    success_url = reverse_lazy('adminapp:tenant_list')

# class PeelingChargeCreateView(CreateView):
#     model = PeelingCharge
#     form_class = PeelingChargeForm
#     template_name = 'adminapp/forms/peelingcharge_form.html'
#     success_url = reverse_lazy('adminapp:peeling_charge_create')

#     def form_valid(self, form):
#         # Optional: Debug what’s being submitted
#         print("SAVING ITEM:", form.cleaned_data.get("item"))
#         print("SAVING species:", form.cleaned_data.get("species"))
#         return super().form_valid(form)

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

def settings_list(request):
    settings = Settings.objects.all()
    return render(request, 'adminapp/list/settings_list.html', {'settings': settings})

def settings_create(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('adminapp:settings_list')
    else:
        form = SettingsForm()
    return render(request, 'adminapp/forms/settings_form.html', {'form': form})

def settings_update(request, pk):
    setting = get_object_or_404(Settings, pk=pk)
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            return redirect('adminapp:settings_list')
    else:
        form = SettingsForm(instance=setting)
    return render(request, 'adminapp/forms/settings_form.html', {'form': form})

def settings_delete(request, pk):
    setting = get_object_or_404(Settings, pk=pk)
    if request.method == 'POST':
        setting.delete()
        return redirect('adminapp:settings_list')
    return render(request, 'adminapp/confirm_delete.html', {'setting': setting})


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
            'average_weight': round(avg_weight, 2)
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
    settings_obj = Settings.objects.first()
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


from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from decimal import Decimal
from .models import FreezingEntrySpot, SpotPurchase, Shed, PurchasingAgent, PurchasingSupervisor
from .forms import FreezingEntrySpotForm, FreezingEntrySpotItemFormSet


def freezing_entry_spot_update(request, pk):
    freezing_entry = get_object_or_404(FreezingEntrySpot, pk=pk)

    if request.method == "POST":
        form = FreezingEntrySpotForm(request.POST, instance=freezing_entry)
        formset = FreezingEntrySpotItemFormSet(request.POST, instance=freezing_entry, prefix="form")

        # ✅ Ensure spot list loads with all available spots
        form.fields["spot"].queryset = SpotPurchase.objects.all()
        
        # ✅ Set agent and supervisor querysets based on existing data or all available
        if freezing_entry.spot:
            form.fields["spot_agent"].queryset = PurchasingAgent.objects.all()
            form.fields["spot_supervisor"].queryset = PurchasingSupervisor.objects.all()
        else:
            form.fields["spot_agent"].queryset = PurchasingAgent.objects.all()
            form.fields["spot_supervisor"].queryset = PurchasingSupervisor.objects.all()

        # ✅ Ensure shed list loads for each child form
        for f in formset.forms:
            if "shed" in f.fields:
                f.fields["shed"].queryset = Shed.objects.all()

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                entry = form.save(commit=False)

                # ---- Aggregate totals ----
                total_slab = Decimal(0)
                total_cs = Decimal(0)
                total_kg = Decimal(0)
                total_usd = Decimal(0)
                total_inr = Decimal(0)
                yield_percentages = []

                # Process formset items
                for f in formset:
                    if f.cleaned_data and not f.cleaned_data.get("DELETE", False):
                        # Get values with proper defaults
                        slab = f.cleaned_data.get('slab_quantity') or Decimal(0)
                        cs = f.cleaned_data.get('c_s_quantity') or Decimal(0)
                        kg = f.cleaned_data.get('kg') or Decimal(0)
                        usd = f.cleaned_data.get('usd_rate_item') or Decimal(0)
                        inr = f.cleaned_data.get('usd_rate_item_to_inr') or Decimal(0)
                        yield_percent = f.cleaned_data.get('yield_percentage')

                        # Add to totals
                        total_slab += slab
                        total_cs += cs
                        total_kg += kg
                        total_usd += usd
                        total_inr += inr
                        if yield_percent is not None:
                            yield_percentages.append(yield_percent)

                # ---- Save totals back to entry ----
                entry.total_slab = total_slab
                entry.total_c_s = total_cs
                entry.total_kg = total_kg
                entry.total_usd = total_usd
                entry.total_inr = total_inr
                entry.total_yield_percentage = (
                    sum(yield_percentages) if yield_percentages else Decimal(0)
                )
                entry.save()

                # Save the formset
                formset.instance = entry
                formset.save()

            return redirect("adminapp:freezing_entry_spot_list")

        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.errors)
            print("Formset Non-Form Errors:", formset.non_form_errors())

    else:
        # GET request - initialize form and formset
        form = FreezingEntrySpotForm(instance=freezing_entry)
        formset = FreezingEntrySpotItemFormSet(instance=freezing_entry, prefix="form")

        # ✅ Preload querysets for the form
        form.fields["spot"].queryset = SpotPurchase.objects.all()
        form.fields["spot_agent"].queryset = PurchasingAgent.objects.all()
        form.fields["spot_supervisor"].queryset = PurchasingSupervisor.objects.all()

        # ✅ Preload querysets for formset
        for f in formset.forms:
            if "shed" in f.fields:
                f.fields["shed"].queryset = Shed.objects.all()

    context = {
        "form": form,
        "formset": formset,
        "freezing_entry": freezing_entry,
    }

    return render(
        request,
        "adminapp/freezing/freezing_entry_spot_update.html",
        context
    )


# Create Freezing Entry Local
def create_freezing_entry_local(request):
    if request.method == 'POST':
        form = FreezingEntryLocalForm(request.POST)
        formset = FreezingEntryLocalItemFormSet(request.POST, prefix='form')

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

                freezing_entry.total_slab = total_slab
                freezing_entry.total_c_s = total_c_s
                freezing_entry.total_kg = total_kg
                freezing_entry.total_usd = total_usd
                freezing_entry.total_inr = total_inr
                freezing_entry.total_yield_percentage = (
                    sum(yield_percentages) / len(yield_percentages)
                    if yield_percentages else Decimal(0)
                )

                freezing_entry.save()
                formset.instance = freezing_entry
                formset.save()

            return redirect('adminapp:freezing_entry_local_list')
        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.errors)
    else:
        form = FreezingEntryLocalForm()
        formset = FreezingEntryLocalItemFormSet(prefix='form')

    return render(request, 'adminapp/freezing_entry_local_create.html', {
        'form': form,
        'formset': formset,
    })

def get_parties_by_date(request):
    date = request.GET.get('date')
    parties = LocalPurchase.objects.filter(date=date).values('id', 'party_name', 'voucher_number')
    return JsonResponse({'parties': list(parties)})

def get_party_details(request):
    party_id = request.GET.get('party_id')
    try:
        purchase = LocalPurchase.objects.get(id=party_id)
        data = {
            'party_name': purchase.party_name,
            'voucher_number': purchase.voucher_number,
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
    settings_obj = Settings.objects.first()
    if settings_obj:
        return JsonResponse({
            'dollar_rate_to_inr': float(settings_obj.dollar_rate_to_inr)
        })
    return JsonResponse({'error': 'Settings not found'}, status=404)

def freezing_entry_local_list(request):
    entries = FreezingEntryLocal.objects.all()
    return render(request, 'adminapp/freezing_entry_local_list.html', {'entries': entries})

def delete_freezing_entry_local(request, pk):
    entry = get_object_or_404(FreezingEntryLocal, pk=pk)
    if request.method == 'POST':
        entry.delete()
        return redirect('adminapp:freezing_entry_local_list')
    return render(request, 'adminapp/freezing_entry_local_confirm_delete.html', {'entry': entry})

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
    return render(request, 'adminapp/freezing_entry_local_detail.html', context)

def freezing_entry_local_update(request, pk):
    entry = get_object_or_404(FreezingEntryLocal, pk=pk)

    ItemFormSet = inlineformset_factory(
        FreezingEntryLocal,
        FreezingEntryLocalItem,
        form=FreezingEntryLocalItemForm,
        extra=0,
        can_delete=True
    )

    if request.method == "POST":
        form = FreezingEntryLocalForm(request.POST, instance=entry)
        formset = ItemFormSet(request.POST, instance=entry)

        if form.is_valid() and formset.is_valid():
            parent = form.save(commit=False)
            parent.save()
            formset.instance = parent  # ✅ Make sure formset links to the saved parent
            formset.save()
            return redirect("adminapp:freezing_entry_local_detail", pk=entry.pk)
        else:
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)  # ✅ Helps debug why it's not saving

    else:
        form = FreezingEntryLocalForm(instance=entry)
        formset = ItemFormSet(instance=entry)

    return render(request, "adminapp/freezing_entry_local_update.html", {
        "form": form,
        "formset": formset,
        "entry": entry
    })




# Freezing WORK OUT 
class FreezingWorkOutView(View):
    template_name = "adminapp/freezing_workout.html"

    def get_summary(self, queryset):
        """Helper to build aggregated summary for a given queryset."""
        return (
            queryset
            .select_related(
                'item', 'grade', 'species', 'peeling_type', 'brand', 
                'glaze', 'unit', 'freezing_category'
            )
            .values(
                'item__name',
                'grade__grade',  # ItemGrade has 'grade' field, not 'name'
                'species__name',
                'peeling_type__name',  # ItemType has 'name' field
                'brand__name',
                'glaze__percentage',  # GlazePercentage has 'percentage' field, not 'name'
                'unit__unit_code',  # PackingUnit has 'unit_code' field
                'freezing_category__name',
            )
            .annotate(
                total_slab=Coalesce(Sum('slab_quantity'), V(0), output_field=DecimalField()),
                total_c_s=Coalesce(Sum('c_s_quantity'), V(0), output_field=DecimalField()),
                total_kg=Coalesce(Sum('kg'), V(0), output_field=DecimalField()),
                total_yield_sum=Coalesce(Sum('yield_percentage'), V(0), output_field=DecimalField()),
                count_yield=Count('id'),
                total_usd=Coalesce(Sum('usd_rate_item'), V(0), output_field=DecimalField()),
                total_inr=Coalesce(Sum('usd_rate_item_to_inr'), V(0), output_field=DecimalField()),
            )
            .order_by('item__name', 'grade__grade', 'species__name')
        )

    def get(self, request):
        # Spot and Local summaries
        spot_summary = self.get_summary(FreezingEntrySpotItem.objects)
        local_summary = self.get_summary(FreezingEntryLocalItem.objects)

        # Combine results
        combined_data = {}
        for dataset in [spot_summary, local_summary]:
            for row in dataset:
                key = (
                    row['item__name'],
                    row['grade__grade'],
                    row['species__name'],
                    row['peeling_type__name'],
                    row['brand__name'],
                    str(row['glaze__percentage']),  # Convert to string for consistency
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
                        'total_yield_sum': Decimal(0),
                        'count_yield': 0,
                        'total_usd': Decimal(0),
                        'total_inr': Decimal(0),
                    }
                combined_data[key]['total_slab'] += row['total_slab']
                combined_data[key]['total_c_s'] += row['total_c_s']
                combined_data[key]['total_kg'] += row['total_kg']
                combined_data[key]['total_usd'] += row['total_usd']
                combined_data[key]['total_inr'] += row['total_inr']
                combined_data[key]['total_yield_sum'] += row['total_yield_sum']
                combined_data[key]['count_yield'] += row['count_yield']

        # Calculate average yield
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
                total_yield_sum=Coalesce(Sum('yield_percentage'), V(0), output_field=DecimalField()),
                count_yield=Count('id'),
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
                        'total_yield_sum': Decimal(0),
                        'count_yield': 0,
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
                combined_data[key]['total_yield_sum'] += row['total_yield_sum']
                combined_data[key]['count_yield'] += row['count_yield']

        for val in combined_data.values():
            if val['count_yield'] > 0:
                val['avg_yield'] = val['total_yield_sum'] / val['count_yield']
            else:
                val['avg_yield'] = Decimal(0)

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
    settings_obj = Settings.objects.first()
    if settings_obj:
        return JsonResponse({
            'dollar_rate_to_inr': float(settings_obj.dollar_rate_to_inr)
        })
    return JsonResponse({'error': 'Settings not found'}, status=404)

# LIST VIEW
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

# DELETE VIEW
class PreShipmentWorkOutDeleteView(DeleteView):
    model = PreShipmentWorkOut
    template_name = "adminapp/confirm_delete.html"
    success_url = reverse_lazy("adminapp:preshipment_workout_list")

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Pre-Shipment WorkOut '{obj}' deleted successfully.")
        return super().delete(request, *args, **kwargs)

# DETAIL View
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
