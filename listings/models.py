from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nazwa kategorii")
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Kategoria nadrzędna")
    order = models.PositiveIntegerField(default=0, verbose_name="Kolejność")

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Listing(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Nowy'),
        ('used', 'Używany'),
        ('damaged', 'Uszkodzony'),
    ]

    STATUS_CHOICES = [
        ('active', 'Aktywne'),
        ('sold', 'Sprzedane / Zakończone'),
        ('draft', 'Szkic / Ukryte'),
    ]

    title = models.CharField(max_length=200, verbose_name="Tytuł")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(verbose_name="Opis")
    
    # Cena opcjonalna (pusta lub 0 = Bezpłatnie)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Cena (zostaw puste dla bezpłatnych)")
    is_negotiable = models.BooleanField(default=False, verbose_name="Do negocjacji")
    
    # Stan opcjonalny (dla eventów/usług zostawiamy puste)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, null=True, blank=True, verbose_name="Stan")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings', verbose_name="Kategoria")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', verbose_name="Właściciel")
    
    image = models.ImageField(upload_to='listings_photos/', null=True, blank=True, verbose_name="Zdjęcie główne")
    location = models.CharField(max_length=100, verbose_name="Miejscowość")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Liczba wyświetleń")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data aktualizacji")

    class Meta:
        verbose_name = "Ogłoszenie"
        verbose_name_plural = "Ogłoszenia"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Listing.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def display_price(self):
        if self.price is None or self.price == 0:
            return "Bezpłatnie"
        return f"{self.price} zł"


class ProfileComment(models.Model):
    profile_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_comments', verbose_name="Kogo dotyczy opinia")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_comments', verbose_name="Autor opinii")
    content = models.TextField(verbose_name="Treść komentarza")
    
    # Moderacja AI
    is_approved_by_ai = models.BooleanField(default=True, verbose_name="Zatwierdzone przez AI")
    ai_flag_reason = models.CharField(max_length=255, null=True, blank=True, verbose_name="Powód flagi AI")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data wystawienia")

    class Meta:
        verbose_name = "Komentarz na profilu"
        verbose_name_plural = "Komentarze na profilach"


class PrivateMessage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='messages', verbose_name="Ogłoszenie")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="Nadawca")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name="Odbiorca")
    content = models.TextField(verbose_name="Treść wiadomości")
    
    # Moderacja AI
    is_blocked_by_ai = models.BooleanField(default=False, verbose_name="Zabronione przez AI")
    ai_flag_reason = models.CharField(max_length=255, null=True, blank=True, verbose_name="Powód blokady")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data wysłania")

    class Meta:
        verbose_name = "Wiadomość prywatna"
        verbose_name_plural = "Wiadomości prywatne"