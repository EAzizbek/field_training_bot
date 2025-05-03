from django.db import models
from django.utils import timezone

class User(models.Model):
    user_id = models.CharField(max_length=50, unique=True)  # foydalanuvchi ID
    telegram_id = models.BigIntegerField(unique=True)       # telegram ID
    full_name = models.CharField(max_length=255)            # ism familiya
    phone_number = models.CharField(max_length=20)
    role = models.CharField(max_length=50)  # TM / TS / TA

    def __str__(self):
        return f"{self.full_name} ({self.role})"

class DailySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    is_started = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    selfie = models.ImageField(upload_to='selfies/', null=True, blank=True)
    map_file = models.FileField(upload_to="maps/", null=True, blank=True)

    class Meta:
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.user.full_name} - {self.date}"


class TrackingLocation(models.Model):
    session = models.ForeignKey(DailySession, on_delete=models.CASCADE, related_name="locations")
    lat = models.FloatField()
    lon = models.FloatField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.session.user.full_name} - {self.timestamp}"
