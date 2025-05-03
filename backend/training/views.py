from rest_framework import viewsets
from .models import User,DailySession,TrackingLocation
from .serializers import UserSerializer,DailySessionSerializer,TrackingLocationSerializer
import folium
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['telegram_id']  # 👈 bu qator muhim!

class DailySessionViewSet(viewsets.ModelViewSet):
    queryset = DailySession.objects.all()
    serializer_class = DailySessionSerializer

    def create(self, request, *args, **kwargs):
        telegram_id = request.data.get("telegram_id")

        # ❗Userni telegram_id orqali topamiz
        user = get_object_or_404(User, telegram_id=telegram_id)

        # Yangi data: user_id qo‘shamiz
        data = request.data.copy()
        data["user"] = user.id  # ForeignKey user_id bo'lishi kerak

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Telegram_id bilan filtering (optional, lekin foydali)
    def get_queryset(self):
        queryset = DailySession.objects.all()
        telegram_id = self.request.query_params.get('telegram_id')
        date = self.request.query_params.get('date')

        if telegram_id:
            user = User.objects.filter(telegram_id=telegram_id).first()
            if user:
                queryset = queryset.filter(user=user)
            else:
                queryset = queryset.none()

        if date:
            queryset = queryset.filter(date=date)

        return queryset

class TrackingLocationViewSet(viewsets.ModelViewSet):
    queryset = TrackingLocation.objects.all()
    serializer_class = TrackingLocationSerializer

def session_map_view(request, session_id):
    """
    Har bir sessiyaga tegishli joylashuvlarni xarita orqali ko‘rsatadi.
    """
    session = get_object_or_404(DailySession, id=session_id)
    locations = session.locations.order_by('timestamp')  # related_name='locations'

    if not locations.exists():
        return HttpResponse("⛔ Bu sessiyada joylashuv mavjud emas.")

    # Xarita markazini birinchi joylashuvga qo‘yish
    first = locations.first()
    m = folium.Map(location=[first.lat, first.lon], zoom_start=15)

    path = []
    for loc in locations:
        lat, lon = loc.lat, loc.lon
        timestamp = loc.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        folium.Marker([lat, lon], popup=timestamp).add_to(m)
        path.append((lat, lon))

    # Polyline chizish
    folium.PolyLine(path, color="blue", weight=4.5, opacity=0.8).add_to(m)

    return HttpResponse(m._repr_html_())