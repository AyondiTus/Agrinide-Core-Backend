from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, WebSocket, WebSocketDisconnect
from uuid import UUID

from app.schemas.negotiations import NegotiationStart, NegotiationCounter
from app.repositories import negotiations as nego_repo
from app.repositories import commodities as commodity_repo

# --- Helpers ---

def _get_uid(current_user: dict) -> str:
    uid = current_user.get("uid")
    if not uid:
        raise HTTPException(status_code=401, detail="User not authenticated properly")
    return uid

def _assert_party(negotiation, uid: str):
    if uid not in (negotiation.farmer_id, negotiation.buyer_id):
        raise HTTPException(status_code=403, detail="You are not a party of this negotiation")

def _assert_negotiating(negotiation):
    if negotiation.status != "negotiating":
        raise HTTPException(status_code=400, detail=f"Negotiation is already {negotiation.status}")

# --- Service Functions ---

async def start_negotiation(db: AsyncSession, current_user: dict, payload: NegotiationStart):
    uid = _get_uid(current_user)
    
    # Validate commodity
    commodity = await commodity_repo.get_commodity_by_id(db, payload.commodity_id)
    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")
    if not commodity.is_active:
        raise HTTPException(status_code=400, detail="Commodity is no longer active")
    
    # Buyer cannot negotiate on their own commodity
    if commodity.farmer_id == uid:
        raise HTTPException(status_code=400, detail="You cannot start a negotiation on your own commodity")
    
    data = {
        "farmer_id": commodity.farmer_id,
        "buyer_id": uid,
        "commodity_id": payload.commodity_id,
        "current_price": payload.price,
        "current_volume": payload.volume,
        "quality_grade_id": payload.quality_grade_id,
        "payment_method_id": payload.payment_method_id,
        "payment_term_id": payload.payment_term_id,
        "shipping_point_id": payload.shipping_point_id,
        "delivery_type_id": payload.delivery_type_id,
        "proposed_by": uid,
        "status": "negotiating",
    }
    
    return await nego_repo.create_negotiation(db, data)

async def counter_offer(db: AsyncSession, current_user: dict, negotiation_id: UUID, payload: NegotiationCounter):
    uid = _get_uid(current_user)
    
    negotiation = await nego_repo.get_negotiation_by_id(db, negotiation_id)
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    
    _assert_party(negotiation, uid)
    _assert_negotiating(negotiation)
    
    # Turn-based check
    if negotiation.proposed_by == uid:
        raise HTTPException(
            status_code=400, 
            detail="You cannot send two consecutive offers. Wait for the other party to respond."
        )
    
    # Save current state to history (audit trail)
    history_data = {
        "negotiation_id": negotiation.id,
        "price": negotiation.current_price,
        "volume": negotiation.current_volume,
        "quality_grade_id": negotiation.quality_grade_id,
        "payment_method_id": negotiation.payment_method_id,
        "payment_term_id": negotiation.payment_term_id,
        "shipping_point_id": negotiation.shipping_point_id,
        "delivery_type_id": negotiation.delivery_type_id,
        "proposed_by": negotiation.proposed_by,
    }
    await nego_repo.create_history_entry(db, history_data)
    
    # Build update data (only update fields that are provided)
    update_data = payload.model_dump(exclude_unset=True)
    
    # Map schema fields to model fields
    field_map = {"price": "current_price", "volume": "current_volume"}
    mapped_update = {}
    for key, value in update_data.items():
        mapped_key = field_map.get(key, key)
        mapped_update[mapped_key] = value
    
    mapped_update["proposed_by"] = uid
    
    return await nego_repo.update_negotiation(db, negotiation, mapped_update)

async def accept_negotiation(db: AsyncSession, current_user: dict, negotiation_id: UUID):
    uid = _get_uid(current_user)
    
    negotiation = await nego_repo.get_negotiation_by_id(db, negotiation_id)
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    
    _assert_party(negotiation, uid)
    _assert_negotiating(negotiation)
    
    # Only the opposing party can accept
    if negotiation.proposed_by == uid:
        raise HTTPException(
            status_code=400, 
            detail="You cannot accept your own offer. The other party must accept."
        )
    
    return await nego_repo.update_negotiation(db, negotiation, {"status": "accepted"})

async def reject_negotiation(db: AsyncSession, current_user: dict, negotiation_id: UUID):
    uid = _get_uid(current_user)
    
    negotiation = await nego_repo.get_negotiation_by_id(db, negotiation_id)
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    
    _assert_party(negotiation, uid)
    _assert_negotiating(negotiation)
    
    return await nego_repo.update_negotiation(db, negotiation, {"status": "rejected"})

async def get_negotiation_detail(db: AsyncSession, current_user: dict, negotiation_id: UUID):
    uid = _get_uid(current_user)
    
    negotiation = await nego_repo.get_negotiation_by_id(db, negotiation_id)
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    
    _assert_party(negotiation, uid)
    
    return negotiation

async def list_user_negotiations(db: AsyncSession, current_user: dict, skip: int = 0, limit: int = 20):
    uid = _get_uid(current_user)
    return await nego_repo.get_negotiations_by_user(db, uid, skip=skip, limit=limit)

async def handle_websocket_chat(websocket: WebSocket, negotiation_id: UUID, current_user: dict, db: AsyncSession):
    uid = _get_uid(current_user)

    negotiation = await nego_repo.get_negotiation_by_id(db, negotiation_id)
    if not negotiation or uid not in (negotiation.farmer_id, negotiation.buyer_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    room_id = str(negotiation_id)
    from app.utils.websocket_manager import manager
    await manager.connect(websocket, room_id)

    try:
        while True:
            data = await websocket.receive_text()
            
            chat_data = {
                "negotiation_id": negotiation_id,
                "sender_id": uid,
                "message": data
            }
            chat = await nego_repo.create_chat_message(db, chat_data)

            response = {
                "id": str(chat.id),
                "negotiation_id": str(chat.negotiation_id),
                "sender_id": chat.sender_id,
                "message": chat.message,
                "created_at": chat.created_at.isoformat() if chat.created_at else None
            }
            
            await manager.broadcast_to_room(room_id, response)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
