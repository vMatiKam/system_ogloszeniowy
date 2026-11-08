from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Listing, Category
from .forms import ListingForm

def listing_list(request):
    category_slug = request.GET.get('category')
    listings = Listing.objects.filter(status='active')
    categories = Category.objects.filter(parent=None)

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        listings = listings.filter(category=selected_category)

    context = {
        'listings': listings,
        'categories': categories,
        'selected_category': selected_category,
    }
    return render(request, 'listings/listing_list.html', context)


def listing_detail(request, slug):
    listing = get_object_or_404(Listing, slug=slug, status='active')
    
    # Zwiększenie licznika wyświetleń
    listing.views_count += 1
    listing.save(update_fields=['views_count'])

    return render(request, 'listings/listing_detail.html', {'listing': listing})


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