""" View for payment app"""
from rest_framework import generics
from django.conf import settings
import stripe
from common.library import AccessForbidden
from common import library as custom_lib
from v1.payment.serializers import auth as auth_serial
from v1.payment.serializers import payment as payment_serial
from .models import Invoice
from .models import Project
from .permissions import IsAuthenticated, IsOwner

# Create your views here.


class Login(generics.CreateAPIView):
    """Login view."""

    serializer_class = auth_serial.LoginSerializer


class ProjectView(generics.ListAPIView):
    """Project list view"""
    permission_classes = (IsAuthenticated,)
    serializer_class = payment_serial.ProjectSerializer
    queryset = Project.objects.all()


class InvoiceView(generics.ListCreateAPIView):
    """Invoice create and list api view"""
    permission_classes = (IsAuthenticated,)
    permissions = {
        'GET': (
            IsAuthenticated,),
        'POST': (
            IsAuthenticated,
            IsOwner,),
    }
    serializer_class = payment_serial.InvoiceSerializer
    queryset = Invoice.objects.all()


class InvoiceDetailView(generics.RetrieveAPIView):
    """ Invoice details api view"""
    permission_classes = (IsAuthenticated,)
    serializer_class = payment_serial.InvoiceSerializer

    def get_object(self):
        print("=self.kwargs['pk']_+++++++++++++++",self.kwargs['pk'])
        invoice = Invoice.objects.get(id=self.kwargs['pk'])
        print("invoice.project.client__________",invoice.project.client)
        print("user------------------",  self.kwargs['user'])
        if invoice.project.client != self.kwargs['user']:
            raise AccessForbidden("User does not have access to this invoice.")
        return invoice


class PaymentLinkView(generics.RetrieveAPIView):
    """ Payment link create api view"""
    queryset = Invoice.objects.all()

    def get_object(self):
        return Invoice.objects.get(id=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        invoice = self.get_object()
        stripe.api_key = settings.STRIPE_SECRET_KEY

        product_response = stripe.Product.create(name=invoice.project.name)
        price_res = stripe.Price.create(
            unit_amount=invoice.amount,
            currency='USD', product=product_response['id'],
            metadata={"invoice_number": invoice.invoice_number})
        link = stripe.PaymentLink.create(
            line_items=[
                {
                    "price": price_res['id'],
                    "quantity": 1,
                }
            ]
        )
        invoice.stripe_payment_link = link['url']
        invoice.save()
        return custom_lib._success_response(
            {"payment link": link['url']}, 'link created', 200
        )
