from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet,DailySessionViewSet,TrackingLocationViewSet,session_map_view
from django.conf.urls.static import static
from django.conf import settings


router = DefaultRouter()
router.register("users", UserViewSet)
router.register("sessions", DailySessionViewSet)
router.register(r'locations', TrackingLocationViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path('session/<int:session_id>/map/', session_map_view, name='session-map'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
