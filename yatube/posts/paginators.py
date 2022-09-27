from django.core.paginator import Paginator


def paginator(request, query, count_posts):
    paginator = Paginator(query, count_posts)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
