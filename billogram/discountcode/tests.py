from datetime import date

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from billogram.discountcode import models
from billogram.discountcode.models import MyUser as User


TEST_PASSWORD = '1234'


def get_logged_in_client(user):
    client = APIClient()
    user.is_form_authenticated = True
    client.login(username=user.username, password=TEST_PASSWORD)
    return client


class DiscountCodeViewSetTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='Test')
        self.user.set_password(TEST_PASSWORD)
        self.user.save()
        self.client = get_logged_in_client(self.user)

        self.brand = models.Brand.objects.create(name='FancyBrand')
        self.brand_user = User.objects.create_user(username='Other', is_brand=True, brand=self.brand)
        self.brand_user.set_password(TEST_PASSWORD)
        self.brand_user.save()
        self.brand_client = get_logged_in_client(self.brand_user)

        self.discount_rule = models.DiscountRule.objects.create(brand=self.brand, discount=50)
        self.discount_code = models.DiscountCode.objects.create(
            id='foo2022', rule=self.discount_rule, valid_until=date(2022, 5, 31))

        self.list_url = reverse('code-list')
        self.detail_url = reverse('code-detail', kwargs=dict(pk=self.discount_code.id))

    def test_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        response = self.brand_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_unauthenticated(self):
        response = APIClient().get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve(self):
        response = self.client.get(reverse('code-detail', kwargs=dict(pk='nosuchcode')))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'][0], self.discount_code.id)

        response = self.brand_client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_unauthenticated(self):
        response = APIClient().get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create(self):
        data = {
            'id': 'SPRINGSALE2022',
            'rule': self.discount_rule.id,
        }
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.brand_client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete(self):
        response = self.brand_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update(self):
        data = {
            'id': 'SPRINGSALE2023',
            'rule': 1,
        }
        response = self.client.put(self.detail_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class DiscountCodeUsageViewSetTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='Test')
        self.user.set_password(TEST_PASSWORD)
        self.user.save()
        self.client = get_logged_in_client(self.user)

        self.brand = models.Brand.objects.create(name='FancyBrand')
        self.brand_user = User.objects.create_user(username='Other', is_brand=True, brand=self.brand)
        self.brand_user.set_password(TEST_PASSWORD)
        self.brand_user.save()
        self.brand_client = get_logged_in_client(self.brand_user)
        self.other_brand = models.Brand.objects.create(name='KnockoffBrand')

        self.discount_rule = models.DiscountRule.objects.create(brand=self.brand, discount=50)
        self.discount_rule_2 = models.DiscountRule.objects.create(brand=self.other_brand, discount=25)
        self.discount_code = models.DiscountCode.objects.create(
            id='foo2022', rule=self.discount_rule, valid_until=date(2022, 5, 31))
        self.discount_code_2 = models.DiscountCode.objects.create(
            id='bar2022', rule=self.discount_rule_2, valid_until=date(2022, 6, 30)
        )
        self.discount_code_usage = models.DiscountCodeUsage.objects.create(
            discount_code=self.discount_code, user=self.user,
        )
        self.discount_code_usage_2 = models.DiscountCodeUsage.objects.create(
            discount_code=self.discount_code_2, user=self.user,
        )
        # This would be invalid through the API
        self.discount_code_usage_3 = models.DiscountCodeUsage.objects.create(
            discount_code=self.discount_code, user=self.brand_user,
        )

        self.list_url = reverse('usage-list')
        self.detail_url = reverse('usage-detail', kwargs=dict(pk=self.discount_code_usage.id))

    def test_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response = self.brand_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        staff_user = User.objects.create(is_staff=True)
        staff_user.set_password(TEST_PASSWORD)
        staff_user.save()
        staff_client = get_logged_in_client(staff_user)
        response = staff_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_unauthenticated(self):
        response = APIClient().get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['discount_code'], self.discount_code_usage.discount_code.id)

        response = self.brand_client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_unauthenticated(self):
        response = APIClient().get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create(self):
        data = {
            'discount_code': 1,
            'user': 1,
        }
        response = self.client.post(self.list_url, data=data)
        # Discount code already used
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'discount_code': 2,
            'user': 2,
        }
        response = self.client.post(self.list_url, data=data)
        # Other user
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        new_discount_code = models.DiscountCode.objects.create(
            id='new2022', rule=self.discount_rule, valid_until=date(2022, 5, 31))
        data = {
            'discount_code': new_discount_code.id,
            'user': 1,
        }
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete(self):
        response = self.brand_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update(self):
        data = {
            'discountcode': 1,
            'user': 1,
        }
        response = self.client.put(self.detail_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
