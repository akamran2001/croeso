from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import Site, SiteImage
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from .helpers import get_lat_lon, update_state, get_query


def index(request):
    '''
        Render a page containing all the sites in our app or only the ones searched/filtered
    '''

    # Dictionary containing all keys and values used for filtering and sorting the index page
    search_sort = {
        "search": request.GET.get('search'),
        "sort": request.GET.get(key='sort', default='title'),
        "tag": request.GET.get('tag')
    }

    if (search_sort['search']):
        if (search_sort['search'].startswith("#")):
            '''
                If a search begins with # search for it as a tag name
            '''
            return redirect(F"{reverse('index')}?tag={search_sort['search'][1:]}")

    '''
        RESTful search sort with sessions
    '''
    search_sort_keys = ['sort', 'tag', 'search']
    update_state(request.GET, request.session, search_sort_keys)
    for key in search_sort_keys:
        '''
            Redirect to url with query string that includes all search/sort parameters applied
        '''
        if key in request.session.keys() and key not in request.GET.keys():
            return redirect(F"{reverse('index')}?{get_query(request.session, search_sort_keys)}")

    sites = Site.objects.all().order_by('title')

    if (search_sort['tag']):
        sites = sites.filter(tags__name=search_sort['tag'])

    if (search_sort['search']):
        '''
            Searches by title, description, and location. Appends all filters into one search
        '''
        sites = sites.filter(title__icontains=search_sort['search']) | sites.filter(description__icontains=search_sort['search']) | sites.filter(location__icontains=search_sort['search'])

    if(search_sort['sort'] == 'rating'):
        '''
            Sort from highest to lowest average rating. Sites without reviews go to the bottom
        '''
        sites = sorted(list(sites), key=lambda site: site.avg_rating() if site.avg_rating() else 0.0, reverse=True)

    colors = []
    for site in sites:
        '''
            Color code sites by their average rating. Green is high, yellow is medium, red is low, blue is unrated
        '''
        r = site.avg_rating()
        if(r):
            if 5 >= r >= 4:
                colors.append('green')
            elif 4 > r >= 2:
                colors.append('yellow')
            else:
                colors.append('red')
        else:
            colors.append("blue")

    '''
        The placeholder on the searchbar should reflect which filter, if any, have been applied
    '''
    search_bar_placeholder = "Search by keywords. Use # to search by tags"
    if search_sort['search'] and search_sort['tag']:
        search_bar_placeholder = F"keywords: {search_sort['search']} & tag: {search_sort['tag']}"
    elif search_sort['search']:
        search_bar_placeholder = F"keywords: {search_sort['search']} "
    elif search_sort['tag']:
        search_bar_placeholder = F"tag: #{search_sort['tag']} "

    context = {
        "sites": zip(sites, colors),
        "tag_req": search_sort['tag'],
        'sort': search_sort['sort'],
        'search_bar_placeholder': search_bar_placeholder
    }

    return render(request, 'app/index.html', context)


def random_image(request):
    '''
        Redirect to a random image from the database on every request
    '''
    img: SiteImage = SiteImage.objects.order_by("?").first()
    return redirect(img.image.url)


def details(request, site_id):
    '''
        Render a view with details for a specific site indicated by the site id
    '''
    site = get_object_or_404(Site, pk=site_id)
    images = site.siteimage_set.all()
    reviews = site.review_set.all()

    lat, lon = get_lat_lon(site.location, request.session)
    if(lat and lon):
        '''
            Render page with coordinates in query string if coordinates are found.
            This will help JavaScript on that page render a map based on the coordinates.
        '''
        if(request.GET.get('lat') == lat and request.GET.get('lon') == lon):
            pass
        else:
            url = F"{reverse(viewname='details',args=[site_id])}?lat={lat}&lon={lon}"
            return redirect(url)

    '''
        Every whole number in the average rating in considered a full rating
        Anything above 0.5 but below 1 is a partial rating
        The rest are empty ratings
        This will help the page show full, partial, and empty stars
    '''
    full_rating, partial_rating, empty_rating = 0, 0, 5
    site_rating = site.avg_rating()
    if(site_rating):
        full_rating, partial_rating = divmod(site_rating, 1)
        if(partial_rating >= 0.5):
            partial_rating = 1
        else:
            partial_rating = 0
        full_rating = int(full_rating)
        empty_rating = empty_rating - (full_rating + partial_rating)

    context = {
        'site': site,
        'images': images if images.exists() else None,
        'reviews': reviews if reviews.exists() else None,
        'full_rating': range(full_rating),
        'partial_rating': range(partial_rating),
        'empty_rating': range(empty_rating)
    }

    return render(request, 'app/details.html', context)


@login_required
def create_review(request, site_id):
    '''
        Show a form for the user to review a site and add their review to the database when submitted properly
    '''
    site = get_object_or_404(Site, pk=site_id)
    if (request.method == 'POST'):
        form = ReviewForm(request.POST)
        if form.is_valid():
            site.review_set.create(rating=form.cleaned_data['rating'],
                                   comment=form.cleaned_data['comment'],
                                   user=request.user)
            return redirect('details', site.id)

    context = {'site': site, 'ratings': range(1, 6)}
    return render(request, 'app/review.html', context)
