import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    """Real-time per-user notification stream."""

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f"notifications_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        notifications = await self.get_user_notifications()
        await self.send(text_data=json.dumps({"type": "notification_list", "notifications": notifications}))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
            return

        action = data.get("action")
        notification_id = data.get("notification_id")
        if action in {"mark_as_read", "delete"} and notification_id:
            await self.delete_notification(notification_id)
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "notification_deleted", "notification_id": notification_id},
            )

    async def notification_created(self, event):
        await self.send(text_data=json.dumps({"type": "notification_created", "notification": event.get("notification")}))

    async def notification_deleted(self, event):
        await self.send(
            text_data=json.dumps(
                {"type": "notification_deleted", "notification_id": str(event.get("notification_id"))}
            )
        )

    @database_sync_to_async
    def get_user_notifications(self):
        rows = (
            Notification.objects.filter(user=self.user, is_read=False)
            .values("id", "title", "message", "created_at")
            .order_by("-created_at")
        )
        return [
            {
                "id": str(r["id"]),
                "title": r["title"],
                "message": r["message"],
                "created_at": r["created_at"].isoformat(),
            }
            for r in rows
        ]

    @database_sync_to_async
    def delete_notification(self, notification_id):
        Notification.objects.filter(id=notification_id, user=self.user).delete()
