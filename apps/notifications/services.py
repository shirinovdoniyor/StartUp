"""Notification write logic + real-time broadcast."""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def _broadcast(notification: Notification) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        f"notifications_{notification.user_id}",
        {
            "type": "notification_created",
            "notification": {
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "created_at": notification.created_at.isoformat(),
            },
        },
    )


def create_notification(*, user, title: str, message: str) -> Notification:
    notification = Notification.objects.create(user=user, title=title, message=message)
    _broadcast(notification)
    return notification


def broadcast_to_users(users, *, title: str, message: str) -> int:
    count = 0
    for user in users:
        create_notification(user=user, title=title, message=message)
        count += 1
    return count


def delete_notification(*, user, notification_id) -> bool:
    deleted, _ = Notification.objects.filter(id=notification_id, user=user).delete()
    return bool(deleted)
