from typing import TypeVar, Optional, Any, List, Dict

T = TypeVar('T')


class Util:
    @staticmethod
    def is_null(value: Any) -> bool:
        return value is None
    
    @staticmethod
    def is_not_null(value: Any) -> bool:
        return value is not None
    
    @staticmethod
    def is_empty(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            return len(value.strip()) == 0
        if isinstance(value, (list, dict, set, tuple)):
            return len(value) == 0
        return False
    
    @staticmethod
    def is_not_empty(value: Any) -> bool:
        return not Util.is_empty(value)
    
    @staticmethod
    def get_or_default(value: Optional[T], default: T) -> T:
        return value if value is not None else default
    
    @staticmethod
    def require_non_null(value: Optional[T], message: str = "Value cannot be null") -> T:
        if value is None:
            raise ValueError(message)
        return value
    
    @staticmethod
    def safe_get(data: Optional[Dict], key: str, default: Any = None) -> Any:
        if data is None:
            return default
        return data.get(key, default)
    
    @staticmethod
    def safe_list_get(data: Optional[List], index: int, default: Any = None) -> Any:
        if data is None or index < 0 or index >= len(data):
            return default
        return data[index]

