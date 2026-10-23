import time
import json
from functools import wraps
from datetime import datetime

def observe_stage(stage_name: str):
    """
    Decorador que mide la latencia de una etapa y la registra como un span.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                latency_ms = (time.time() - start_time) * 1000
                span = {
                    "timestamp": datetime.now().isoformat(),
                    "stage": stage_name,
                    "latency_ms": round(latency_ms, 2),
                    "status": "ok"
                }
                print(f"[OBSERVABILITY] {json.dumps(span)}")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                latency_ms = (time.time() - start_time) * 1000
                span = {
                    "timestamp": datetime.now().isoformat(),
                    "stage": stage_name,
                    "latency_ms": round(latency_ms, 2),
                    "status": "ok"
                }
                print(f"[OBSERVABILITY] {json.dumps(span)}")
        
        # Detecta si la función es async o sync
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator