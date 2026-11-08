from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Użytkownik")
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name="Numer telefonu")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="Miejscowość")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Zdjęcie profilowe")
    show_phone = models.BooleanField(default=True, verbose_name="Pokazuj telefon w ogłoszeniach")

    class Meta:
        verbose_name = "Profil użytkownika"
        verbose_name_plural = "Profile użytkowników"

    def __str__(self):
        return f"Profil: {self.user.username}"


# Sygnały automatycznie tworzące i zapisujące profil przy rejestracji Usera
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()