from django.urls import path
from .views import Login, \
    ProjectView, InvoiceView, InvoiceDetailView, PaymentLinkView

urlpatterns = [
    # auth
    path('login/', Login.as_view(), name="login"),

    # payment
    path('', ProjectView.as_view(), name='project'),
    path('invoice/', InvoiceView.as_view(), name='invoice'),
    path('invoice/<idencode:pk>/', InvoiceDetailView.as_view(),
         name='Invoice-detail'),
    path('api/payment-link/<idencode:pk>/', PaymentLinkView.as_view(),
         name='api_payment-link'),
]