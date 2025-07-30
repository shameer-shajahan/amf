from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'adminapp'

urlpatterns = [

    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('login/', views.admin_login, name='admin_login'),
    
    path('logout/', views.admin_logout, name='admin_logout'),

    path('create-user/', views.create_user_view, name='create_user'),
    
    # Operational & Location Masters
    path('processing-center/create/', views.ProcessingCenterCreateView.as_view(), name='processing_center_create'),
    path('processing-center/list/', views.ProcessingCenterListView.as_view(), name='processing_center_list'),
    path('processing-center/update/<str:pk>/', views.ProcessingCenterUpdateView.as_view(), name='processing_center_update'),
    path('processing-center/delete/<str:pk>/', views.ProcessingCenterDeleteView.as_view(), name='processing_center_delete'),

    path('store/create/', views.StoreCreateView.as_view(), name='store_create'),
    path('store/list/', views.StoreListView.as_view(), name='store_list'),
    path('store/update/<str:pk>/', views.StoreUpdateView.as_view(), name='store_update'),
    path('store/delete/<str:pk>/', views.StoreDeleteView.as_view(), name='store_delete'),

    path('peeling-center/create/', views.ShedCreateView.as_view(), name='peeling_center_create'),
    path('peeling-center/list/', views.ShedListView.as_view(), name='peeling_center_list'),
    path('peeling-center/update/<str:pk>/', views.ShedUpdateView.as_view(), name='peeling_center_update'),
    path('peeling-center/delete/<str:pk>/', views.ShedDeleteView.as_view(), name='peeling_center_delete'),

    path('purchasing-spot/create/', views.PurchasingSpotCreateView.as_view(), name='purchasing_spot_create'),
    path('purchasing-spot/list/', views.PurchasingSpotListView.as_view(), name='purchasing_spot_list'),
    path('purchasing-spot/update/<str:pk>/', views.PurchasingSpotUpdateView.as_view(), name='purchasing_spot_update'),
    path('purchasing-spot/delete/<str:pk>/', views.PurchasingSpotDeleteView.as_view(), name='purchasing_spot_delete'),

    # Personnel Masters
    path('purchasing-supervisor/create/', views.PurchasingSupervisorCreateView.as_view(), name='purchasing_supervisor_create'),
    path('purchasing-supervisor/list/', views.PurchasingSupervisorListView.as_view(), name='purchasing_supervisor_list'),
    path('purchasing-supervisor/update/<str:pk>/', views.PurchasingSupervisorUpdateView.as_view(), name='purchasing_supervisor_update'),
    path('purchasing-supervisor/delete/<str:pk>/', views.PurchasingSupervisorDeleteView.as_view(), name='purchasing_supervisor_delete'),

    path('purchasing-agent/create/', views.PurchasingAgentCreateView.as_view(), name='purchasing_agent_create'),
    path('purchasing-agent/list/', views.PurchasingAgentListView.as_view(), name='purchasing_agent_list'),
    path('purchasing-agent/update/<str:pk>/', views.PurchasingAgentUpdateView.as_view(), name='purchasing_agent_update'),
    path('purchasing-agent/delete/<str:pk>/', views.PurchasingAgentDeleteView.as_view(), name='purchasing_agent_delete'),

    # Item & Product Masters
    path('item-category/create/', views.ItemCategoryCreateView.as_view(), name='item_category_create'),
    path('item-category/list/', views.ItemCategoryListView.as_view(), name='item_category_list'),
    path('item-category/update/<str:pk>/', views.ItemCategoryUpdateView.as_view(), name='item_category_update'),
    path('item-category/delete/<str:pk>/', views.ItemCategoryDeleteView.as_view(), name='item_category_delete'),

    path('item/create/', views.ItemCreateView.as_view(), name='item_create'),
    path('item/list/', views.ItemListView.as_view(), name='item_list'),
    path('item/update/<str:pk>/', views.ItemUpdateView.as_view(), name='item_update'),
    path('item/delete/<str:pk>/', views.ItemDeleteView.as_view(), name='item_delete'),

    path('item-grade/create/', views.ItemGradeCreateView.as_view(), name='item_grade_create'),
    path('item-grade/list/', views.ItemGradeListView.as_view(), name='item_grade_list'),
    path('item-grade/update/<str:pk>/', views.ItemGradeUpdateView.as_view(), name='item_grade_update'),
    path('item-grade/delete/<str:pk>/', views.ItemGradeDeleteView.as_view(), name='item_grade_delete'),

    path('freezing-category/create/', views.FreezingCategoryCreateView.as_view(), name='freezing_category_create'),
    path('freezing-category/list/', views.FreezingCategoryListView.as_view(), name='freezing_category_list'),
    path('freezing-category/update/<str:pk>/', views.FreezingCategoryUpdateView.as_view(), name='freezing_category_update'),
    path('freezing-category/delete/<str:pk>/', views.FreezingCategoryDeleteView.as_view(), name='freezing_category_delete'),

    path('packing-unit/create/', views.PackingUnitCreateView.as_view(), name='packing_unit_create'),
    path('packing-unit/list/', views.PackingUnitListView.as_view(), name='packing_unit_list'),
    path('packing-unit/update/<str:pk>/', views.PackingUnitUpdateView.as_view(), name='packing_unit_update'),
    path('packing-unit/delete/<str:pk>/', views.PackingUnitDeleteView.as_view(), name='packing_unit_delete'),

    path('glaze-percentage/create/', views.GlazePercentageCreateView.as_view(), name='glaze_percentage_create'),
    path('glaze-percentage/list/', views.GlazePercentageListView.as_view(), name='glaze_percentage_list'),
    path('glaze-percentage/update/<str:pk>/', views.GlazePercentageUpdateView.as_view(), name='glaze_percentage_update'),
    path('glaze-percentage/delete/<str:pk>/', views.GlazePercentageDeleteView.as_view(), name='glaze_percentage_delete'),

    path('item-brand/create/', views.ItemBrandCreateView.as_view(), name='item_brand_create'),
    path('item-brand/list/', views.ItemBrandListView.as_view(), name='item_brand_list'),
    path('item-brand/update/<str:pk>/', views.ItemBrandUpdateView.as_view(), name='item_brand_update'),
    path('item-brand/delete/<str:pk>/', views.ItemBrandDeleteView.as_view(), name='item_brand_delete'),

    # Financial & Expense Masters
    path('tenant/create/', views.TenantCreateView.as_view(), name='tenant_create'),
    path('tenant/list/', views.TenantListView.as_view(), name='tenant_list'),
    path('tenant/update/<str:pk>/', views.TenantUpdateView.as_view(), name='tenant_update'),
    path('tenant/delete/<str:pk>/', views.TenantDeleteView.as_view(), name='tenant_delete'),

    path('peeling-charge/create/', views.PeelingChargeCreateView.as_view(), name='peeling_charge_create'),
    path('peeling-charge/list/', views.PeelingChargeListView.as_view(), name='peeling_charge_list'),
    path('peeling-charge/update/<str:pk>/', views.PeelingChargeUpdateView.as_view(), name='peeling_charge_update'),
    path('peeling-charge/delete/<str:pk>/', views.PeelingChargeDeleteView.as_view(), name='peeling_charge_delete'),

    path('purchase-overhead/create/', views.PurchaseOverheadCreateView.as_view(), name='purchase_overhead_create'),
    path('purchase-overhead/list/', views.PurchaseOverheadListView.as_view(), name='purchase_overhead_list'),
    path('purchase-overhead/update/<str:pk>/', views.PurchaseOverheadUpdateView.as_view(), name='purchase_overhead_update'),
    path('purchase-overhead/delete/<str:pk>/', views.PurchaseOverheadDeleteView.as_view(), name='purchase_overhead_delete'),

    path('peeling-overhead/create/', views.PeelingOverheadCreateView.as_view(), name='peeling_overhead_create'),
    path('peeling-overhead/list/', views.PeelingOverheadListView.as_view(), name='peeling_overhead_list'),
    path('peeling-overhead/update/<str:pk>/', views.PeelingOverheadUpdateView.as_view(), name='peeling_overhead_update'),
    path('peeling-overhead/delete/<str:pk>/', views.PeelingOverheadDeleteView.as_view(), name='peeling_overhead_delete'),

    path('processing-overhead/create/', views.ProcessingOverheadCreateView.as_view(), name='processing_overhead_create'),
    path('processing-overhead/list/', views.ProcessingOverheadListView.as_view(), name='processing_overhead_list'),
    path('processing-overhead/update/<str:pk>/', views.ProcessingOverheadUpdateView.as_view(), name='processing_overhead_update'),
    path('processing-overhead/delete/<str:pk>/', views.ProcessingOverheadDeleteView.as_view(), name='processing_overhead_delete'),

    path('shipment-overhead/create/', views.ShipmentOverheadCreateView.as_view(), name='shipment_overhead_create'),
    path('shipment-overhead/list/', views.ShipmentOverheadListView.as_view(), name='shipment_overhead_list'),
    path('shipment-overhead/update/<str:pk>/', views.ShipmentOverheadUpdateView.as_view(), name='shipment_overhead_update'),
    path('shipment-overhead/delete/<str:pk>/', views.ShipmentOverheadDeleteView.as_view(), name='shipment_overhead_delete'),

# spot purchase urls.py
    path('spot-purchase/add/', views.spot_purchase_create, name='spot_purchase_add'),
    path('spot-purchases/', views.spot_purchase_list, name='spot_purchase_list'),
    path('spot-purchases/<str:pk>/edit/', views.spot_purchase_update, name='spot_purchase_update'),
    path('spot-purchases/<str:pk>/delete/', views.spot_purchase_delete, name='spot_purchase_delete'),
    path('spot-purchases/<str:pk>/', views.spot_purchase_detail, name='spot_purchase_detail'),

   # Local Purchase URLs
    path('local-purchase/create/', views.local_purchase_create, name='local_purchase_create'),
    path('local-purchase/', views.local_purchase_list, name='local_purchase_list'),
    path('local-purchase/<str:pk>/update/', views.local_purchase_update, name='local_purchase_update'),
    path('local-purchase/<str:pk>/delete/', views.local_purchase_delete, name='local_purchase_delete'),
    path('local-purchase/<str:pk>/detail/', views.local_purchase_detail, name='local_purchase_detail'),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)