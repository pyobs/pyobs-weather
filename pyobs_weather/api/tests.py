import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class MeViewTests(TestCase):
    def test_anonymous_user_is_not_authenticated(self):
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"authenticated": False, "username": None})

    def test_logged_in_user_is_authenticated(self):
        user = User.objects.create_user(username="someone", password="secret")
        self.client.force_login(user)

        response = self.client.get(reverse("me"))

        self.assertEqual(json.loads(response.content), {"authenticated": True, "username": "someone"})
