from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from typing import List, Dict
from datetime import datetime

from app.models.user import User, Message
from app.schemas.user import MessageCreate, MessageResponse
from app.routers.user import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        # Verify token and get user
        from app.core.security import verify_token
        payload = verify_token(token)
        username = payload.get("sub")
        user = User.get(User.username == username)
        
        await manager.connect(websocket, user.id)
        
        try:
            while True:
                data = await websocket.receive_text()
                # Process received message
                # You might want to parse the data and save it to the database
                await manager.send_personal_message(f"You wrote: {data}", user.id)
        except WebSocketDisconnect:
            manager.disconnect(user.id)
    except Exception as e:
        await websocket.close()

@router.post("/", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    try:
        receiver = User.get(User.id == message_data.receiver_id)
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found"
        )

    message = Message.create(
        sender=current_user,
        receiver=receiver,
        content=message_data.content
    )

    # Send real-time notification if receiver is connected
    if receiver.id in manager.active_connections:
        await manager.send_personal_message(
            str({
                "type": "new_message",
                "sender_id": current_user.id,
                "sender_username": current_user.username,
                "content": message_data.content
            }),
            receiver.id
        )

    return message

@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    other_user_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        other_user = User.get(User.id == other_user_id)
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    messages = Message.select().where(
        (
            (Message.sender == current_user) & 
            (Message.receiver == other_user)
        ) | (
            (Message.sender == other_user) & 
            (Message.receiver == current_user)
        )
    ).order_by(Message.created_at)

    return list(messages)

@router.put("/{message_id}/read")
async def mark_message_as_read(
    message_id: int,
    current_user: User = Depends(get_current_user)
):
    try:
        message = Message.get(
            (Message.id == message_id) &
            (Message.receiver == current_user)
        )
    except Message.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    if not message.is_read:
        message.is_read = True
        message.read_at = datetime.now()
        message.save()

    return {"message": "Message marked as read"}

@router.get("/unread", response_model=List[MessageResponse])
async def get_unread_messages(
    current_user: User = Depends(get_current_user)
):
    messages = Message.select().where(
        (Message.receiver == current_user) &
        (Message.is_read == False)
    ).order_by(Message.created_at)

    return list(messages)
