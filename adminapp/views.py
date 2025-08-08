
# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.shortcuts import render
from .models import *
from .forms import *
from decimal import Decimal



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

from django.http import JsonResponse
from .models import ItemGrade

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
            return redirect('adminapp:spot_purchase_list')

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

# Delete View
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

    return render(request, 'adminapp/purchases/local_purchase_form.html', {
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



# views.py

from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy
from .models import PeelingShedSupply

class PeelingShedSupplyListView(ListView):
    model = PeelingShedSupply
    template_name = 'adminapp/purchases/peeling_shed_supply_list.html'
    context_object_name = 'supplies'

# views.py

class PeelingShedSupplyDeleteView(DeleteView):
    model = PeelingShedSupply
    template_name = 'adminapp/purchases/confirm_delete.html'
    success_url = reverse_lazy('adminapp:peeling_shed_supply_list')




# views.py
from django.shortcuts import render, redirect
from .forms import PeelingShedSupplyForm, PeelingShedPeelingTypeFormSet

from django.db import transaction
from django.shortcuts import render, redirect
from .models import PeelingShedSupply, PeelingShedPeelingType
from .forms import PeelingShedSupplyForm, PeelingShedPeelingTypeFormSet

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

                return redirect('adminapp:peeling_shed_supply_list')
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
            'name': item.item.name
        }
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



# create freezing entry spot

def create_freezing_entry_spot(request):
    if request.method == 'POST':
        form = FreezingEntrySpotForm(request.POST)
        formset = FreezingEntrySpotItemFormSet(request.POST, prefix='form')

        # Set shed queryset for each inline form
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

            return redirect('adminapp:freezing_entry_spot_list')
        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.errors)
    else:
        form = FreezingEntrySpotForm()
        form.fields['spot_agent'].queryset = PurchasingAgent.objects.none()
        form.fields['spot_supervisor'].queryset = PurchasingSupervisor.objects.none()
        formset = FreezingEntrySpotItemFormSet(prefix='form')

    return render(request, 'adminapp/freezing_entry_spot_create.html', {
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
        data = {
            'agent_id': spot.agent.id,
            'agent_name': str(spot.agent),  # e.g. "John - AG001"
            'supervisor_id': spot.supervisor.id,
            'supervisor_name': str(spot.supervisor),  # e.g. "Anita - 9876543210"
        }
        return JsonResponse(data)
    except SpotPurchase.DoesNotExist:
        return JsonResponse({'error': 'SpotPurchase not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_sheds_by_date(request):
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'error': 'Missing date'}, status=400)

    supplies = PeelingShedSupply.objects.filter(
        spot_purchase__date=date
    ).select_related('shed', 'spot_purchase_item__item')

    seen_pairs = set()
    result = []

    for supply in supplies:
        shed = supply.shed
        item = supply.spot_purchase_item.item
        key = (shed.id, item.id)

        if key not in seen_pairs:
            seen_pairs.add(key)
            result.append({
                'shed_id': shed.id,
                'shed_name': str(shed),
                'item_id': item.id,
                'item_name': str(item),
                'boxes_received_shed': supply.boxes_received_shed,
                'quantity_received_shed': str(supply.quantity_received_shed),
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
    return render(request, 'adminapp/freezing_entry_spot_list.html', {'entries': entries})

def delete_freezing_entry_spot(request, pk):
    entry = get_object_or_404(FreezingEntrySpot, pk=pk)
    if request.method == 'POST':
        entry.delete()
        return redirect('adminapp:freezing_entry_spot_list')
    return render(request, 'adminapp/confirm_delete.html', {'entry': entry})


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











