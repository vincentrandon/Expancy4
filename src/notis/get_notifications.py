from notis.models import BroadcastNotification, Notification


def notifications(request):
    notifications = Notification.objects.all()
    return {'notifications': notifications}