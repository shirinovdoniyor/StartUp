# Notification System - Real-Time WebSocket API

## Overview

This project includes a real-time notification system that uses Django Channels with WebSocket for instant notifications. Admins can broadcast notifications to all users, and users receive them instantly via a persistent WebSocket connection.

## Features

- **Real-Time Notifications**: Users receive notifications instantly via WebSocket
- **Admin Broadcasting**: Admins can send notifications to all active users
- **Notification Management**: Users can delete notifications or mark them as read (auto-deletes)
- **HTTP API Fallback**: REST API endpoints for fetching and managing notifications

## Setup

### Installation

All required packages have been installed:
- `channels` - WebSocket support for Django
- `channels-redis` - Channel layer backend (optional, for production)
- `daphne` - ASGI server

### Running the Development Server

**With WebSocket Support (Daphne):**
```bash
python manage.py runserver
# or use Daphne explicitly
daphne -b 127.0.0.1 -p 8000 root.asgi:application
```

**Note**: The standard Django development server works with both HTTP and WebSocket in development thanks to Daphne being in INSTALLED_APPS first.

## API Endpoints

### REST API

#### Get All Unread Notifications
```
GET /api/v1/users/notifications/
```
**Headers**: `Authorization: Bearer {access_token}`

**Response**:
```json
{
  "count": 2,
  "notifications": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "New Service Available",
      "message": "A new service has been added to your workshop",
      "created_at": "2026-07-09T10:30:00Z"
    }
  ]
}
```

#### Mark Notification as Read (Deletes it)
```
POST /api/v1/users/notifications/{notification_id}/read/
```
**Headers**: `Authorization: Bearer {access_token}`

**Response**:
```json
{
  "message": "Notification deleted."
}
```

#### Delete a Notification
```
DELETE /api/v1/users/notifications/{notification_id}/delete/
```
**Headers**: `Authorization: Bearer {access_token}`

**Response**:
```json
{
  "message": "Notification deleted."
}
```

#### Admin: Send Notification to All Users
```
POST /api/admin/notifications/send/
```
**Headers**: 
- `Authorization: Bearer {access_token}`
- User must be admin (`is_staff=True` and `is_superuser=True`)

**Request Body**:
```json
{
  "title": "Maintenance Scheduled",
  "message": "System maintenance on July 10 from 2-4 AM UTC"
}
```

**Response**:
```json
{
  "message": "Notification sent to all users",
  "count": 42
}
```

### WebSocket

#### Connect to Notifications WebSocket
```javascript
// URL
ws://127.0.0.1:8000/ws/notifications/

// Headers (passed as part of connection)
Authorization: Bearer {access_token}
```

#### Initial Connection Response
Upon connection, server sends all unread notifications:
```json
{
  "type": "notification_list",
  "notifications": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "New Service",
      "message": "Service added",
      "created_at": "2026-07-09T10:30:00Z"
    }
  ]
}
```

#### Receive New Notification (Broadcast from Admin)
```json
{
  "type": "notification_created",
  "notification": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "System Update",
    "message": "Update available",
    "created_at": "2026-07-09T11:00:00Z"
  }
}
```

#### Mark Notification as Read
**Send**:
```json
{
  "action": "mark_as_read",
  "notification_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Receive (broadcast to user)**:
```json
{
  "type": "notification_deleted",
  "notification_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Delete Notification
**Send**:
```json
{
  "action": "delete",
  "notification_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Receive (broadcast to user)**:
```json
{
  "type": "notification_deleted",
  "notification_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## JavaScript Client Example

```javascript
// Connect to WebSocket
const token = localStorage.getItem('access_token');
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${protocol}//127.0.0.1:8000/ws/notifications/`);

// Handle connection open
ws.onopen = (event) => {
  console.log('WebSocket connected');
  // Send auth token (if needed for custom auth)
};

// Handle incoming messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'notification_list') {
    console.log('Initial notifications:', data.notifications);
    updateNotificationBadge(data.notifications.length);
  } else if (data.type === 'notification_created') {
    console.log('New notification:', data.notification);
    showNotification(data.notification);
    playNotificationSound();
  } else if (data.type === 'notification_deleted') {
    console.log('Notification deleted:', data.notification_id);
    removeNotificationFromUI(data.notification_id);
  }
};

// Mark notification as read
function markAsRead(notificationId) {
  ws.send(JSON.stringify({
    action: 'mark_as_read',
    notification_id: notificationId
  }));
}

// Delete notification
function deleteNotification(notificationId) {
  ws.send(JSON.stringify({
    action: 'delete',
    notification_id: notificationId
  }));
}

// Handle disconnection
ws.onclose = (event) => {
  console.log('WebSocket disconnected');
  // Attempt to reconnect after 3 seconds
  setTimeout(() => {
    location.reload();
  }, 3000);
};

// Handle errors
ws.onerror = (event) => {
  console.error('WebSocket error:', event);
};
```

## Architecture

### Components

1. **NotificationConsumer** (`users/consumers.py`)
   - WebSocket handler for real-time messaging
   - Manages user-specific notification groups
   - Handles mark-as-read and delete actions

2. **REST Views** (`users/views.py`)
   - HTTP endpoints for notification management
   - Compatible with REST clients

3. **Routing** (`root/routing.py`)
   - WebSocket URL routing

4. **Configuration** (`root/settings.py`, `root/asgi.py`)
   - Channels setup
   - Channel layers (in-memory for development, Redis for production)

### Database Model

```python
class Notification(models.Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey(User, cascade)
    title = CharField(max_length=255)
    message = TextField()
    is_read = BooleanField(default=False)  # Currently unused, notifications auto-delete
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## Production Deployment

For production, use Redis as the channel layer:

### 1. Update `root/settings.py`

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis.example.com', 6379)],
        },
    }
}
```

### 2. Use Daphne in production

```bash
daphne -b 0.0.0.0 -p 8000 root.asgi:application
```

Or with Uvicorn:

```bash
pip install uvicorn
uvicorn root.asgi:application --host 0.0.0.0 --port 8000
```

### 3. Nginx reverse proxy configuration

```nginx
upstream asgi {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://asgi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://asgi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Testing

### Using `curl` for REST API

```bash
# Get access token
curl -X POST http://127.0.0.1:8000/api/v1/users/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567"}'

# Get notifications
curl -X GET http://127.0.0.1:8000/api/v1/users/notifications/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Admin sends notification
curl -X POST http://127.0.0.1:8000/api/admin/notifications/send/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "message": "Test message"}'
```

### Using WebSocket in Browser Console

```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/ws/notifications/');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({action: 'mark_as_read', notification_id: 'id-here'}));
```

## Troubleshooting

### WebSocket Connection Failed
- Ensure Daphne or another ASGI server is running
- Check that WebSocket URL is correct (http→ws, https→wss)
- Verify ALLOWED_HOSTS includes your domain

### In-Memory Channel Layer Issues
For production, use Redis. The in-memory layer doesn't scale across multiple processes.

### Authentication Issues
WebSocket uses the token from HTTP headers via `AuthMiddlewareStack`. Ensure the token is valid.

## Changes Made

- **Modified Files**:
  - `requirements.txt` - Added channels, channels-redis, daphne
  - `root/settings.py` - Added Channels configuration
  - `root/asgi.py` - Integrated ProtocolTypeRouter for WebSocket
  - `users/views.py` - Added notification endpoints
  - `users/urls.py` - Added notification URL patterns
  - `admin_panel/views.py` - Updated broadcast to support WebSocket

- **New Files**:
  - `users/consumers.py` - WebSocket consumer
  - `root/routing.py` - WebSocket URL routing
