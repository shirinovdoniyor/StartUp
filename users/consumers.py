import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification, User


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications."""

    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        # Create a group for this user
        self.user_group_name = f"notifications_{self.user.id}"
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

        # Send user list of existing notifications on connect
        notifications = await self.get_user_notifications()
        await self.send(text_data=json.dumps({
            "type": "notification_list",
            "notifications": notifications,
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            action = data.get("action")

            if action == "mark_as_read":
                notification_id = data.get("notification_id")
                await self.mark_notification_read(notification_id)
                # Broadcast deletion to user group
                await self.channel_layer.group_send(
                    self.user_group_name,
                    {
                        "type": "notification_deleted",
                        "notification_id": notification_id,
                    }
                )

            elif action == "delete":
                notification_id = data.get("notification_id")
                await self.delete_notification(notification_id)
                # Broadcast deletion to user group
                await self.channel_layer.group_send(
                    self.user_group_name,
                    {
                        "type": "notification_deleted",
                        "notification_id": notification_id,
                    }
                )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "error": "Invalid JSON"
            }))

    async def notification_created(self, event):
        """Handle notification creation broadcast."""
        notification_data = event.get("notification")
        await self.send(text_data=json.dumps({
            "type": "notification_created",
            "notification": notification_data,
        }))

    async def notification_deleted(self, event):
        """Handle notification deletion broadcast."""
        await self.send(text_data=json.dumps({
            "type": "notification_deleted",
            "notification_id": str(event.get("notification_id")),
        }))

    @database_sync_to_async
    def get_user_notifications(self):
        """Fetch user's unread notifications."""
        notifications = Notification.objects.filter(
            user=self.user,
            is_read=False
        ).values("id", "title", "message", "created_at").order_by("-created_at")
        return [
            {
                "id": str(n["id"]),
                "title": n["title"],
                "message": n["message"],
                "created_at": n["created_at"].isoformat(),
            }
            for n in notifications
        ]

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read and delete it."""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.delete()
        except Notification.DoesNotExist:
            pass

    @database_sync_to_async
    def delete_notification(self, notification_id):
        """Delete a notification."""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.delete()
        except Notification.DoesNotExist:
            pass
