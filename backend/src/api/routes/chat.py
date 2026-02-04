# """Chat API routes for AI-powered conversational task management."""
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from pydantic import BaseModel, Field
# from typing import Optional, List, Dict, Any
# import logging
# import asyncio
# import os

# # from ...database import get_session
# # from src.database import get_session
# from ...database import get_session
# from ...services.chat_service import ChatService
# from ...agents.todo_agent import todo_agent

# logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/api", tags=["chat"])


# class ChatRequest(BaseModel):
#     """Request model for chat endpoint."""
#     conversation_id: Optional[int] = Field(None, description="Existing conversation ID to continue")
#     message: str = Field(..., min_length=1, max_length=5000, description="User's message")


# class ChatResponse(BaseModel):
#     """Response model for chat endpoint."""
#     conversation_id: int = Field(..., description="Conversation ID")
#     response: str = Field(..., description="AI assistant's response")
#     tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="MCP tools invoked")


# @router.post("/{user_id}/chat", response_model=ChatResponse)
# async def chat(
#     user_id: str,
#     request: ChatRequest,
#     session: AsyncSession = Depends(get_session)
# ) -> ChatResponse:
#     """
#     Send a message to the AI chatbot and get a response.

#     This endpoint:
#     1. Fetches conversation history from database
#     2. Creates an AI agent with MCP tools
#     3. Runs the agent to process the user's message
#     4. Stores the conversation in the database
#     5. Returns the assistant's response

#     The server is stateless - all state is persisted to the database.
#     """
#     try:
#         # Input validation
#         if not request.message.strip():
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Message cannot be empty"
#             )

#         if len(request.message) > 5000:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Message exceeds maximum length of 5000 characters"
#             )

#         # Get or create conversation
#         conversation = await ChatService.get_or_create_conversation(
#             session=session,
#             user_id=user_id,
#             conversation_id=request.conversation_id
#         )

#         # Fetch conversation history
#         history = await ChatService.get_conversation_history(
#             session=session,
#             conversation_id=conversation.id
#         )

#         # Process message with AI agent (with timeout)
#         try:
#             timeout = int(os.getenv("CHAT_REQUEST_TIMEOUT", "30"))
#             assistant_response, tool_calls = await asyncio.wait_for(
#                 todo_agent.process_message(
#                     user_id=user_id,
#                     message=request.message,
#                     conversation_history=history
#                 ),
#                 timeout=timeout
#             )
#         except asyncio.TimeoutError:
#             logger.error(f"Chat request timeout for user {user_id}")
#             raise HTTPException(
#                 status_code=status.HTTP_504_GATEWAY_TIMEOUT,
#                 detail="Request timeout - please try again"
#             )
#         except Exception as e:
#             logger.error(f"AI agent error: {str(e)}")
#             # Graceful degradation
#             assistant_response = "I'm having trouble processing your request right now. Please try again in a moment."
#             tool_calls = []

#         # Store messages
#         await ChatService.store_messages(
#             session=session,
#             conversation_id=conversation.id,
#             user_id=user_id,
#             user_message=request.message,
#             assistant_message=assistant_response
#         )

#         return ChatResponse(
#             conversation_id=conversation.id,
#             response=assistant_response,
#             tool_calls=tool_calls
#         )

#     except HTTPException:
#         raise
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#     except Exception as e:
#         logger.error(f"Chat endpoint error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An error occurred processing your message"
#         )










# """Chat API routes for AI-powered conversational task management."""
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from pydantic import BaseModel, Field
# from typing import Optional, List, Dict, Any
# import logging
# import os

# from ...database import get_db
# from ...services.chat_service import ChatService
# from ...agents.todo_agent import todo_agent

# logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/api", tags=["chat"])


# class ChatRequest(BaseModel):
#     conversation_id: Optional[int] = Field(None)
#     message: str = Field(..., min_length=1, max_length=5000)


# class ChatResponse(BaseModel):
#     conversation_id: int
#     response: str
#     tool_calls: List[Dict[str, Any]] = []


# @router.post("/{user_id}/chat", response_model=ChatResponse)
# def chat(
#     user_id: str,
#     request: ChatRequest,
#     session: Session = Depends(get_db)
# ) -> ChatResponse:
#     try:
#         if not request.message.strip():
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Message cannot be empty"
#             )

#         # conversation
#         conversation = ChatService.get_or_create_conversation(
#             session=session,
#             user_id=user_id,
#             conversation_id=request.conversation_id
#         )

#         history = ChatService.get_conversation_history(
#             session=session,
#             conversation_id=conversation.id
#         )

#         # AI processing (SYNC)
#         assistant_response, tool_calls = todo_agent.process_message(
#             user_id=user_id,
#             message=request.message,
#             conversation_history=history
#         )

#         # store messages
#         ChatService.store_messages(
#             session=session,
#             conversation_id=conversation.id,
#             user_id=user_id,
#             user_message=request.message,
#             assistant_message=assistant_response
#         )

#         return ChatResponse(
#             conversation_id=conversation.id,
#             response=assistant_response,
#             tool_calls=tool_calls
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Chat endpoint error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An error occurred processing your message"
#         )





# """Chat API routes for AI-powered conversational task management."""

# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from pydantic import BaseModel, Field
# from typing import Optional, List, Dict, Any
# import logging
# import os

# from ...database import get_session

# from ...services.chat_service import ChatService
# from ...agents.todo_agent import todo_agent

# logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/api", tags=["chat"])


# class ChatRequest(BaseModel):
#     conversation_id: Optional[int] = Field(None, description="Existing conversation ID to continue")
#     message: str = Field(..., min_length=1, max_length=5000, description="User's message")


# class ChatResponse(BaseModel):
#     conversation_id: int
#     response: str
#     tool_calls: List[Dict[str, Any]] = Field(default_factory=list)


# @router.post("/{user_id}/chat", response_model=ChatResponse)
# def chat(
#     user_id: str,
#     request: ChatRequest,
#     session: AsyncSession = Depends(get_session)
# ) -> ChatResponse:
#     try:
#         # Validation
#         if not request.message.strip():
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Message cannot be empty"
#             )

#         # Get or create conversation
#         conversation = ChatService.get_or_create_conversation(
#             session=session,
#             user_id=user_id,
#             conversation_id=request.conversation_id
#         )

#         # Fetch history
#         history = ChatService.get_conversation_history(
#             session=session,
#             conversation_id=conversation.id
#         )

#         # Process message with agent (synchronous)
#         try:
#             assistant_response, tool_calls = todo_agent.process_message(
#                 user_id=user_id,
#                 message=request.message,
#                 conversation_history=history
#             )
#         except Exception as e:
#             logger.error(f"AI agent error: {str(e)}")
#             assistant_response = "I'm having trouble processing your request right now. Please try again."
#             tool_calls = []

#         # Store messages
#         ChatService.store_messages(
#             session=session,
#             conversation_id=conversation.id,
#             user_id=user_id,
#             user_message=request.message,
#             assistant_message=assistant_response
#         )

#         return ChatResponse(
#             conversation_id=conversation.id,
#             response=assistant_response,
#             tool_calls=tool_calls
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Chat endpoint error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An error occurred processing your message"
#         )



"""Chat API routes for AI-powered conversational task management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession  # <-- Import async session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import os
import asyncio

from ...database import get_session
from ...services.chat_service import ChatService
from ...agents.todo_agent import get_todo_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID to continue")
    message: str = Field(..., min_length=1, max_length=5000, description="User's message")


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(  # <-- async def
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session)  # <-- async session
) -> ChatResponse:
    try:
        # Validation
        if not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )

        # Get or create conversation
        conversation = await ChatService.get_or_create_conversation(
            session=session,
            user_id=user_id,
            conversation_id=request.conversation_id
        )

        # Fetch history
        history = await ChatService.get_conversation_history(
            session=session,
            conversation_id=conversation.id
        )

        # Process message with agent (async)
        try:
            agent = get_todo_agent()
            assistant_response, tool_calls = await agent.process_message(
                user_id=user_id,
                message=request.message,
                conversation_history=history
            )
        except asyncio.TimeoutError:
            logger.error(f"Chat request timeout for user {user_id}")
            assistant_response = "Request timed out. Please try again."
            tool_calls = []
        except Exception as e:
            logger.error(f"AI agent error: {str(e)}")
            assistant_response = "I'm having trouble processing your request right now. Please try again."
            tool_calls = []

        # Store messages
        await ChatService.store_messages(
            session=session,
            conversation_id=conversation.id,
            user_id=user_id,
            user_message=request.message,
            assistant_message=assistant_response
        )

        return ChatResponse(
            conversation_id=conversation.id,
            response=assistant_response,
            tool_calls=tool_calls
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your message"
        )
