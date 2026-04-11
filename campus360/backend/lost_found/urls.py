from django.urls import path
from . import views

urlpatterns = [
    path('items/', views.LostFoundItemListView.as_view(), name='item-list'),
    path('items/<uuid:item_id>/upload/', views.upload_item_image, name='upload-item-image'),
    path('claims/', views.ClaimListView.as_view(), name='claim-list'),
    path('claims/submit/', views.submit_claim, name='submit-claim'),
]
