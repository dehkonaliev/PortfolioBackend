from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
import os
from .models import CustomUser

THUMB_SIZE = (300, 300)


def make_thumbnail(image_field, user):
    if not image_field:
        return None

    img = Image.open(image_field)
    img = img.convert('RGB')
    img.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)

    thumb_io = BytesIO()
    img.save(thumb_io, format='JPEG', quality=85)

    ext = os.path.splitext(os.path.basename(image_field.name))[0]
    thumb_name = f"{ext}_thumb.jpg"

    return ContentFile(thumb_io.getvalue()), thumb_name


@receiver(pre_save, sender=CustomUser)
def clear_old_thumbnail(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = CustomUser.objects.get(pk=instance.pk)
    except CustomUser.DoesNotExist:
        return

    old_photo = old.profile_photo
    new_photo = instance.profile_photo

    if old_photo and old_photo != new_photo:
        if old.profile_thumbnail:
            old.profile_thumbnail.delete(save=False)
        instance.profile_thumbnail = None


@receiver(post_save, sender=CustomUser)
def generate_thumbnail(sender, instance, created, **kwargs):
    if instance.profile_photo:
        try:
            thumb_data, thumb_name = make_thumbnail(instance.profile_photo, instance)
            if thumb_data:
                instance.profile_thumbnail.save(thumb_name, thumb_data, save=False)
                CustomUser.objects.filter(pk=instance.pk).update(
                    profile_thumbnail=instance.profile_thumbnail
                )
        except Exception:
            pass
