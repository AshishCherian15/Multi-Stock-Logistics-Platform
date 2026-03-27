from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.products_list, name='list'),
    path('<int:product_id>/', views.product_detail_page, name='detail_page'),
    path('marketplace/', views.customer_marketplace, name='marketplace'),
    
    # API endpoints
    path('api/', views.products_api, name='api'),
    path('api/create/', views.create_product, name='create'),
    path('api/<int:product_id>/', views.product_detail_api, name='detail_api'),
    path('api/detail/<int:product_id>/', views.product_detail_api, name='detail'),
    path('api/update/<int:product_id>/', views.update_product, name='update'),
    path('api/delete/<int:product_id>/', views.delete_product, name='delete'),
    path('api/update-field/', views.update_product_field, name='update_field'),
    path('api/bulk-update/', views.bulk_update_products, name='bulk_update'),
    path('api/bulk-delete/', views.bulk_delete_products, name='bulk_delete'),
    path('api/bulk-import/', views.bulk_import_products, name='bulk_import'),
    path('api/import-template/', views.download_import_template, name='import_template'),
    path('api/export/', views.export_products, name='export'),
    path('api/analytics/', views.product_analytics_api, name='analytics'),
    path('api/categories/', views.get_categories_api, name='categories'),
    path('api/categories/create/', views.create_category, name='create_category'),
    path('api/categories/rename/', views.rename_category, name='rename_category'),
    path('api/categories/delete/', views.delete_category, name='delete_category'),
    path('api/categories/merge/', views.merge_categories, name='merge_categories'),
    path('api/suppliers/', views.get_suppliers_api, name='suppliers'),
]
