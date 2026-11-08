from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Listing, Category, PrivateMessage, ListingComment
from .forms import ListingForm, MessageForm, ListingCommentForm
from .moderation import analyze_text_content


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
    comments = listing.comments.filter(is_approved_by_ai=True)

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