# sourcebot/utils/output.py
import re
import json

def extract_json(text: str) -> dict:

    match = re.search(r'```(?:json)?\s*(.*?)```', text, flags=re.DOTALL)
    if match:
        text = match.group(1)

    text = text.strip()
    return json.loads(text)

def strip_think(text: str | None) -> str | None:
        """Remove <think>…</think> blocks that some models embed in content."""
        if not text:
            return None
        return re.sub(r"<think>[\s\S]*?</think>", "", text).strip() or None



def parse_tool_args(args):
    if isinstance(args, dict):
        return args
    if isinstance(args, str):
        try:
            return json.loads(args)
        except Exception:
            return {"input": args}
    return {}

def ensure_string(value: any, pretty: bool = True) -> str:
    """
    Ensure the return value is a string.
    Args:
        value: Input value of any type

        pretty: If True, the JSON output will be formatted (indented); otherwise, it will be in compact format.

    Returns:
        String representation
    """
    if value is None:
        return ""
    
    if isinstance(value, str):
        return value
    
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return str(value)
    
    if isinstance(value, (dict, list, tuple, set)):
        try:
            import json
            from datetime import datetime, date
            
            def json_serializer(obj):
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                if isinstance(obj, set):
                    return list(obj)
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                raise TypeError(f"Type {type(obj)} not serializable")
            
            if pretty:
                return json.dumps(value, ensure_ascii=False, indent=2, default=json_serializer)
            else:
                return json.dumps(value, ensure_ascii=False, default=json_serializer)
        except Exception as e:
            return f"<Failed to serialize: {e}>\n{str(value)}"
    
    if hasattr(value, '__str__'):
        return str(value)
    
    return repr(value)