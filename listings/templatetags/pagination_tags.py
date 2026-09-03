from django import template

register = template.Library()


@register.simple_tag
def elided_page_range(page_obj):
    paginator = page_obj.paginator
    current = page_obj.number
    total = paginator.num_pages

    if total <= 7:
        return range(1, total + 1)

    page_range = [1]

    if current > 3:
        page_range.append(paginator.ELLIPSIS)

    for page in range(max(2, current - 1), min(total, current + 1) + 1):
        page_range.append(page)

    if current < total - 2:
        page_range.append(paginator.ELLIPSIS)

    if total not in page_range:
        page_range.append(total)

    return page_range

@register.simple_tag
def pagination_url(request, page):
    query = request.GET.copy()
    query["page"] = page
    return "?" + query.urlencode()