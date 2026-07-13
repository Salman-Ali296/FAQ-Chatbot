from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FAQ
from .nlp_matcher import get_matcher
from .serializers import ChatRequestSerializer, FAQSerializer


class FAQViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for FAQs, exposed at /api/faqs/.

    Anyone can read (GET). Only authenticated staff can create/update/delete
    -- in a real product, front this with your actual auth (session, token,
    or whatever HitTrack/your admin panel already uses).
    """

    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        from .nlp_matcher import invalidate_matcher_cache
        serializer.save()
        invalidate_matcher_cache()

    def perform_update(self, serializer):
        from .nlp_matcher import invalidate_matcher_cache
        serializer.save()
        invalidate_matcher_cache()

    def perform_destroy(self, instance):
        from .nlp_matcher import invalidate_matcher_cache
        instance.delete()
        invalidate_matcher_cache()


class ChatAPIView(APIView):
    """POST { "message": "..." } -> best-matching FAQ answer."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        matcher = get_matcher()
        result = matcher.find_best_match(serializer.validated_data["message"])
        return Response(result)
