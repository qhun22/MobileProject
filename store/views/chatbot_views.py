"""
Chatbot Views (AI chatbot API) - QHUN22 Store
Auto-generated from views.py
"""
import os
import json
import uuid
import random
import time
import traceback
import logging
import requests
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.db import models
from django.db.models import Q, Count, Sum, Max
from django.utils import timezone
from django.urls import reverse
import datetime
from store.chatbot_orchestrator import HybridChatbotOrchestrator


logger = logging.getLogger("store.chatbot.api")


_CHATBOT_ORCHESTRATOR = None


def _get_orchestrator() -> HybridChatbotOrchestrator:
    global _CHATBOT_ORCHESTRATOR
    if _CHATBOT_ORCHESTRATOR is None:
        _CHATBOT_ORCHESTRATOR = HybridChatbotOrchestrator()
    return _CHATBOT_ORCHESTRATOR



def chatbot_api(request):
    import json as _json
    started_at = time.time()
    request_id = uuid.uuid4().hex[:12]

    try:
        body = _json.loads(request.body)
        request_id = (body.get("request_id") or request_id).strip()[:64]
        action = (body.get("action") or "").strip().lower()
        message = body.get("message", "").strip()
    except Exception:
        logger.warning("chatbot_api invalid_json request_id=%s", request_id)
        return JsonResponse({"message": "Tin nhắn không hợp lệ.", "suggestions": []}, status=400)

    user_id = getattr(getattr(request, "user", None), "id", None)
    session_key = getattr(getattr(request, "session", None), "session_key", None)
    logger.info(
        "chatbot_api request_id=%s action=%s user_id=%s session=%s message_len=%s",
        request_id,
        action or "message",
        user_id,
        session_key,
        len(message or ""),
    )

    if action == "reset":
        try:
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            ok = _get_orchestrator().reset_conversation(getattr(request, "session", None), user=user)
            latency_ms = int((time.time() - started_at) * 1000)
            logger.info("chatbot_api reset request_id=%s ok=%s latency_ms=%s", request_id, bool(ok), latency_ms)
            return JsonResponse({"ok": bool(ok), "request_id": request_id})
        except Exception:
            logger.exception("chatbot_api reset_error request_id=%s", request_id)
            return JsonResponse({"ok": False}, status=200)

    if not message:
        return JsonResponse({"message": "Vui lòng nhập nội dung.", "suggestions": []}, status=400)

    if len(message) > 500:
        return JsonResponse({"message": "Tin nhắn quá dài, vui lòng rút gọn lại nhé!", "suggestions": []}, status=400)

    try:
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        result = _get_orchestrator().process_message(message, user=user, session=getattr(request, "session", None))
        latency_ms = int((time.time() - started_at) * 1000)
        logger.info(
            "chatbot_api response request_id=%s intent=%s source=%s engine=%s latency_ms=%s",
            request_id,
            result.get("intent", "unknown"),
            result.get("source", "unknown"),
            result.get("engine", "unknown"),
            latency_ms,
        )
        result.setdefault("request_id", request_id)
        return JsonResponse(result)
    except Exception as e:
        logger.exception("chatbot_api error request_id=%s", request_id)
        if settings.DEBUG:
            return JsonResponse({
                "message": f"[DEBUG] Lỗi: {type(e).__name__}: {e}",
                "suggestions": [],
                "request_id": request_id,
            }, status=200)
        return JsonResponse({
            "message": "Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau!",
            "suggestions": ["Tư vấn chọn máy", "Gặp nhân viên"],
            "request_id": request_id,
        }, status=200)
