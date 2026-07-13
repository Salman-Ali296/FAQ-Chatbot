from rest_framework.routers import DefaultRouter

from .views import ChatAPIView
from django.urls import path

from .views import FAQViewSet

router = DefaultRouter()
router.register(r"faqs", FAQViewSet, basename="faq")

urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="chat"),
] + router.urls
