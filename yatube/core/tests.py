from django.test import Client, TestCase


class CoreTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404(self):
        response = self.guest_client.get('/weoiufaksjv')
        self.assertTemplateUsed(response, 'core/404.html')
