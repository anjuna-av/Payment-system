"""Tests of the app payment."""
import unittest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import AccessToken
from .models import Client, Project, Invoice


# Create your tests here.


class PaymentTestCase(unittest.TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Client.objects.last()
        token = AccessToken.objects.filter(
            user__id=self.user.id).first()
        self.header = {
            'HTTP_TOKEN': token.key,
            'HTTP_USER_ID': self.user.idencode}
        self.project = Project.objects.filter(client=self.user).first()
        self.invoice = Invoice.objects.filter(project__client=self.user).first()

    def test_user_can_login(self):
        """ test for login"""
        login_url = reverse("login")
        login_data = {"username": self.user.email,
                      "password": 'anjunasree'
                      }
        response = self.client.post(login_url, login_data,
                                    format="json")
        # print("@@@@@@@@@@@@@@ response2", response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authentication_with_wrong_password(self):
        """ test login with wrong password"""
        login_url = reverse("login")
        login_data = {"username": self.user.email,
                      "password": "wrong-pass"}
        response = self.client.post(login_url, login_data,
                                    format="json")
        # print("@@@@@@@@@@@@@@ response2", response.content)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_project_list(self):
        """
        Test for list project.
        """
        project_list_url = reverse("project")
        response = self.client.get(
            project_list_url, format='json', **self.header)
        # print("@@@@@@@@@@@@@@ response11111", response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoice_create(self):
        """
        Test for create invoice.
        """
        project_list_url = reverse("invoice")
        data = {
                "project": self.project.idencode,
                "invoice_number": "INV1235",
                "amount": "200",
                "date": "22/5/2022",
                "note": "Test invoice"
            }
        response = self.client.post(
            project_list_url, data, format='json', **self.header)
        # print("@@@@@@@@@@@@@@ response11111", response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invoice_list(self):
        """
        Test for list invoice.
        """
        project_list_url = reverse("invoice")
        response = self.client.get(
            project_list_url, format='json', **self.header)
        # print("@@@@@@@@@@@@@@ response11111", response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invoice_details(self):
        """
        Test for get invoice details.
        """

        invoice_details = reverse(
            "Invoice-detail", kwargs={'pk': self.invoice.id})
        response = self.client.get(
            invoice_details, format='json', **self.header)
        # print("@@@@@@@@@@@@@@ response1333", response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_link(self):
        """
        Test for create payment link.
        """
        payment_link = reverse("api_payment-link", kwargs={'pk': self.invoice.id})

        response = self.client.post(
            payment_link, format='json', **self.header)
        # print("@@@@@@@@@@@@@@ response1555", response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
