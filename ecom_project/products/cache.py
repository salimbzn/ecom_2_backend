from django.core.cache import cache

DEFAULT_TTL = 300  # 5 minutes


def build_cache_key(prefix, **kwargs):
    """
    Constructs a consistent cache key from prefix and query parameters.
    Example: build_cache_key('products:list', page=1, search='protein')
    """
    parts = [f"{key}:{value}" for key, value in sorted(kwargs.items())]
    return f"{prefix}:" + ":".join(parts)


def get_or_set_cache(key, compute_fn, timeout=DEFAULT_TTL):
    """
    Attempts to get from cache. If missing, computes and sets.
    compute_fn should return the data to cache.
    """
    data = cache.get(key)
    if data is None:
        data = compute_fn()
        cache.set(key, data, timeout=timeout)
    return data


def clear_cache_by_prefix(prefix):
    """
    Clears all keys that start with a given prefix.
    WARNING: Only works with Redis backends that support key pattern deletion.
    """
    from django_redis import get_redis_connection
    conn = get_redis_connection("default")
    pattern = f"{prefix}*"
    for key in conn.scan_iter(match=pattern):
        conn.delete(key)
