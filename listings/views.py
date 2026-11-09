from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Listing, Category, PrivateMessage, ListingComment, Favorite
from .forms import ListingForm, MessageForm, ListingCommentForm
from .moderation import analyze_text_content


# 1. Wyszukiwarka, filtrowanie i sortowanie na stronie głównej
def listing_list(request):
    listings = Listing.objects.filter(status='active')
    categories = Category.objects.filter(parent=None)

    # Parametry wyszukiwania i filtrowania z GET
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    condition = request.GET.get('condition', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    location = request.GET.get('location', '').strip()
    sort_by = request.GET.get('sort', '-created_at')

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        listings = listings.filter(category=selected_category)

    if query:
        listings = listings.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if condition:
        listings = listings.filter(condition=condition)

    if price_min:
        try:
            listings = listings.filter(price__gte=float(price_min))
        except ValueError:
            pass

    if price_max:
        try:
            listings = listings.filter(price__lte=float(price_max))
        except ValueError:
            pass

    if location:
        listings = listings.filter(location__icontains=location)

    # Sortowanie
    allowed_sorts = ['created_at', '-created_at', 'price', '-price']
    if sort_by in allowed_sorts:
        listings = listings.order_by(sort_by)

    # Lista ID ulubionych ogłoszeń dla zalogowanego użytkownika
    user_favorite_ids = []
    if request.user.is_authenticated:
        user_favorite_ids = Favorite.objects.filter(user=request.user).values_list('listing_id', flat=True)

    context = {
        'listings': listings,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'condition': condition,
        'price_min': price_min,
        'price_max': price_max,
        'location': location,
        'sort_by': sort_by,
        'user_favorite_ids': user_favorite_ids,
    }
    return render(request, 'listings/listing_list.html', context)


# Details z obsługą spersonalizowanych akcji
def listing_detail(request, slug):
    listing = get_object_or_404(Listing, slug=slug)
    comments = listing.comments.filter(is_approved_by_ai=True)

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, listing=listing).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = ListingCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.listing = listing
            comment.author = request.user

            is_clean, reason = analyze_text_content(comment.content)
            if not is_clean:
                comment.is_approved_by_ai = False
                comment.ai_flag_reason = reason
                comment.save()
                messages.error(request, f"Komentarz zablokowany przez moderację AI: {reason}")
            else:
                comment.save()
                messages.success(request, "Twój komentarz został opublikowany!")

            return redirect('listing_detail', slug=listing.slug)
    else:
        comment_form = ListingCommentForm()

    if request.method == 'GET':
        listing.views_count += 1
        listing.save(update_fields=['views_count'])

    context = {
        'listing': listing,
        'comments': comments,
        'comment_form': comment_form,
        'is_favorite': is_favorite,
    }
    return render(request, 'listings/listing_detail.html', context)


@login_required
def listing_create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            messages.success(request, 'Twoje ogłoszenie zostało pomyślnie dodane!')
            return redirect('listing_detail', slug=listing.slug)
    else:
        form = ListingForm()
    return render(request, 'listings/listing_create.html', {'form': form})


# 2. Zarządzanie własnymi ogłoszeniami (Moje ogłoszenia, Edycja, Usuwanie, Status)
@login_required
def my_listings(request):
    listings = Listing.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'listings/my_listings.html', {'listings': listings})


@login_required
def listing_edit(request, slug):
    listing = get_object_or_404(Listing, slug=slug, owner=request.user)
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ogłoszenie zostało zaktualizowane!')
            return redirect('listing_detail', slug=listing.slug)
    else:
        form = ListingForm(instance=listing)
    return render(request, 'listings/listing_edit.html', {'form': form, 'listing': listing})


@login_required
def listing_delete(request, slug):
    listing = get_object_or_404(Listing, slug=slug, owner=request.user)
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Ogłoszenie zostało usunięte.')
        return redirect('my_listings')
    return render(request, 'listings/listing_confirm_delete.html', {'listing': listing})


@login_required
def toggle_status(request, slug):
    listing = get_object_or_404(Listing, slug=slug, owner=request.user)
    if listing.status == 'active':
        listing.status = 'sold'
        messages.info(request, f'Oznaczono ogłoszenie "{listing.title}" jako sprzedane/zakończone.')
    else:
        listing.status = 'active'
        messages.success(request, f'Aktywowano ponownie ogłoszenie "{listing.title}".')
    listing.save(update_fields=['status'])
    return redirect('my_listings')


# 3. System Ulubionych
@login_required
def toggle_favorite(request, slug):
    listing = get_object_or_404(Listing, slug=slug)
    favorite, created = Favorite.objects.get_or_create(user=request.user, listing=listing)
    
    if not created:
        favorite.delete()
        messages.info(request, f'Usunięto "{listing.title}" z ulubionych.')
    else:
        messages.success(request, f'Dodano "{listing.title}" do ulubionych!')
    
    # Przekierowanie z powrotem na stronę, z której kliknięto
    next_url = request.META.get('HTTP_REFERER')
    return redirect(next_url if next_url else 'listing_list')


@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('listing').order_by('-created_at')
    return render(request, 'listings/my_favorites.html', {'favorites': favorites})


# Wiadomości prywatne
@login_required
def send_message(request, listing_slug):
    listing = get_object_or_404(Listing, slug=listing_slug, status='active')
    
    if listing.owner == request.user:
        messages.warning(request, "Nie możesz wysłać wiadomości do własnego ogłoszenia.")
        return redirect('listing_detail', slug=listing.slug)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.listing = listing
            msg.sender = request.user
            msg.recipient = listing.owner

            is_clean, reason = analyze_text_content(msg.content)
            if not is_clean:
                msg.is_blocked_by_ai = True
                msg.ai_flag_reason = reason
                msg.save()
                messages.error(request, f"Wiadomość zablokowana przez moderację AI: {reason}")
            else:
                msg.save()
                messages.success(request, "Wiadomość została wysłana!")

            return redirect('listing_detail', slug=listing.slug)
    else:
        form = MessageForm()

    return render(request, 'listings/send_message.html', {'form': form, 'listing': listing})


@login_required
def inbox_view(request):
    received_messages = PrivateMessage.objects.filter(recipient=request.user).order_by('-created_at')
    sent_messages = PrivateMessage.objects.filter(sender=request.user).order_by('-created_at')

    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
    }
    return render(request, 'listings/inbox.html', context)