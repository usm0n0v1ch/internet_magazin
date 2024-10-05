# app/urls.py
from django.urls import path

from app import views
from app.views import MainView, CatalogView, search_view, ProductDetailView

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('search/', search_view, name='search_view'),
    path('add_to_order/<int:product_id>/', views.add_to_order, name='add_to_order'),
    path('view_order/', views.view_order, name='view_order'),
    path('place_order/', views.place_order, name='place_order'),
    path('order_history/', views.order_history, name='order_history'),
    path('view_order/', views.view_order, name='view_order'),
    path('advanced_search/', views.advanced_search, name='advanced_search'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('order/update/<int:item_id>/', views.update_order_item, name='update_order_item'),
]