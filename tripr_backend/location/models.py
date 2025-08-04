import uuid
from django.conf import settings
from django.contrib.gis.db import models


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def get_location_image_path(instance, filename):
    slug = str(uuid.uuid4())[:4]
    return f"location_images/{instance.location.id}/{slug}-{filename}"


class Location(BaseModel):
    CATEGORY_CHOICES = [
        ("religious", "Religious"),
        ("palace", "Palace"),
        ("museum", "Museum"),
        ("park", "Park"),
        ("monument", "Monument"),
        ("restaurant", "Restaurant"),
        ("accommodation", "Accommodation"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True
    )
    description = models.TextField(blank=True, null=True)

    # Geometries
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    geom = models.GeometryField(srid=4326, blank=True, null=True)

    # Amenities
    wheelchair = models.BooleanField(default=False)
    toilet = models.BooleanField(default=False)
    wifi = models.BooleanField(default=False)

    # Opening hours
    opening_hours = models.JSONField(blank=True, null=True)

    raw_tags = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.name or "Unnamed Location"


class LocationImage(BaseModel):
    location = models.ForeignKey(
        Location, related_name="images", on_delete=models.CASCADE, blank=True, null=True
    )
    image = models.ImageField(upload_to=get_location_image_path, blank=True, null=True)

    def __str__(self):
        return (
            f"Image for {self.location.name if self.location else 'Unknown Location'}"
        )


class Review(BaseModel):
    location = models.ForeignKey(
        Location,
        related_name="reviews",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reviews",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    rating = models.FloatField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return (
            f"Review by {self.user} for {self.location.name}"
            if self.user and self.location
            else "Incomplete Review"
        )
