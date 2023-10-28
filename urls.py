from django.urls import path
from . import views
from . import wallet_views


app_name = 'mlmurls'

urlpatterns = [

    path('wallet/request/<str:price>/', wallet_views.wallet_send_request, name='wallet_send_request'),
    path('wallet/verify/', wallet_views.wallet_verify, name='wallet_verify'),
    path('payment/request/', views.send_request, name='send_request'),
    path('payment/verify/', views.verify, name='verify'),
    path('products/', views.products_page, name='products_page'),
    path('products/detail/<int:id>/<str:slug>/', views.products_detail_page,name='products_detail_page'),
    path('carts/', views.carts_page, name='carts_page'),
]
