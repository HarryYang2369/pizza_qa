def notifications(request):
    """Expose the unread notification count to all templates."""
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
    else:
        count = 0
    return {'unread_notifications': count}
