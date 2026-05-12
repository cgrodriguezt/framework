from __future__ import annotations
import re
from typing import TYPE_CHECKING
from orionis.http.routes.contracts.method_not_allowed import MethodNotAllowed
from orionis.http.routes.contracts.resolved_route import ResolvedRoute
from orionis.http.routes.contracts.route_not_found import RouteNotFound
from orionis.http.routes.contracts.route_resolver import IRouteResolver

if TYPE_CHECKING:
    from orionis.http.routes.compiled_route import CompiledRoute

# ── Module-level compiled helper ──────────────────────────────────────────────
# Pre-compiled pattern used to rename ``(?P<name>...)`` groups inside each
# route's regex when building combined alternation buckets.  Compiled once at
# import time so _build_depth_bucket pays no repeated compilation cost.
_GROUP_NAME_RE: re.Pattern = re.compile(r"\(\?P<(\w+)>")

# ── Internal pre-computed bucket ──────────────────────────────────────────────

class _DepthBucket:
    """
    Pre-computed matching structure for dynamic routes at a fixed segment depth.

    All candidate routes are merged into a **single combined alternation
    regex**, replacing N sequential ``Pattern.match()`` calls with one
    C-level NFA traversal.  Each route's named capture groups are
    prefixed ``_r{i}_`` so they cannot collide inside the combined
    pattern.

    Attributes
    ----------
    pattern : re.Pattern
        Combined regex of the form
        ``^(?:(?:route0_pattern)|(?:route1_pattern)|...)$``.
    entries : list
        Parallel list of ``(sentinel_group, extractors, route)``
        triples, one per route, in the same order as the alternation:

        * ``sentinel_group`` - name of the *first* prefixed param group
          for this route; ``None`` when the route has no params (not
          possible for truly dynamic routes, but handled defensively).
        * ``extractors`` - ``list[tuple[param_name, group_key, converter]]``
          used to build the final ``params`` dict after a match.
        * ``route`` - the :class:`~orionis.http.routes.compiled_route.CompiledRoute`.
    """

    __slots__ = ("entries", "pattern")

    def __init__(
        self,
        pattern: re.Pattern,
        entries: list,
    ) -> None:
        """
        Initialise the bucket with a combined pattern and route entries.

        Parameters
        ----------
        pattern : re.Pattern
            Combined alternation regex covering all routes in the bucket.
        entries : list
            Parallel list of ``(sentinel, extractors, route)`` triples.

        Returns
        -------
        None
            State is stored on the instance; no value is returned.
        """
        self.pattern = pattern
        self.entries = entries


# ── Module-level pure helpers (no self overhead on hot path) ──────────────────

def _strip_anchors(pattern: str) -> str:
    """
    Remove leading ``^`` and trailing ``$`` anchors from a regex pattern.

    Parameters
    ----------
    pattern : str
        Raw regex pattern string, potentially anchored.

    Returns
    -------
    str
        Pattern with leading ``^`` and trailing ``$`` removed.
    """
    if pattern and pattern[0] == "^":
        pattern = pattern[1:]
    if pattern and pattern[-1] == "$":
        pattern = pattern[:-1]
    return pattern


def _path_allowed_for_method(
    static_table: dict,
    dynamic_table: dict[int, _DepthBucket],
    path: str,
    depth: int,
) -> bool:
    """
    Return ``True`` if *path* is handled by any route in the given method tables.

    Checks, in order:

    1. Static O(1) lookup.
    2. Depth-exact dynamic bucket.
    3. Cross-segment fallback scan (for ``{param:path}`` type routes).

    Parameters
    ----------
    static_table : dict
        Static route table for one HTTP method: ``{path: CompiledRoute}``.
    dynamic_table : dict[int, _DepthBucket]
        Dynamic route table for one HTTP method: ``{depth: _DepthBucket}``.
    path : str
        Normalised request path.
    depth : int
        Slash count of *path* (pre-computed by the caller).

    Returns
    -------
    bool
        ``True`` when at least one route matches *path*, ``False`` otherwise.
    """
    if path in static_table:
        return True
    bucket = dynamic_table.get(depth)
    if bucket is not None and bucket.pattern.match(path) is not None:
        return True
    # Cross-segment fallback: ``{param:path}`` regex spans multiple slashes,
    # so its bucket depth (segment_count) may not equal path.count('/').
    for bucket in dynamic_table.values():
        if bucket.pattern.match(path) is not None:
            return True
    return False


def _build_depth_bucket(routes: list[CompiledRoute]) -> _DepthBucket:
    """
    Merge same-depth :class:`CompiledRoute` objects into a :class:`_DepthBucket`.

    Parameters
    ----------
    routes : list[CompiledRoute]
        Dynamic routes at the same ``segment_count``, already sorted
        descending by ``priority_score`` (done by
        :class:`~orionis.http.routes.route_compiler.RouteCompiler`).

    Returns
    -------
    _DepthBucket
        Ready-to-use bucket containing the combined pattern and per-route
        extractor metadata.
    """
    parts: list[str] = []
    entries: list = []

    for i, route in enumerate(routes):
        raw = _strip_anchors(route.regex.pattern)

        # Rename every ``(?P<name>...)`` → ``(?P<_r{i}_name>...)`` so that
        # group names are unique across all alternatives in the combined regex.
        prefix = f"_r{i}_"
        prefixed = _GROUP_NAME_RE.sub(
            lambda m, _p=prefix: f"(?P<{_p}{m.group(1)}>",
            raw,
        )
        parts.append(prefixed)

        # Build the ordered list of (param_name, group_key, converter) triples
        # that will be evaluated after a successful match.
        extractors = [
            (name, f"{prefix}{name}", conv)
            for name, conv in route.converters.items()
        ]

        # The sentinel is the group key of the *first* param.  It is non-None
        # in the match dict if and only if this route's alternative matched.
        sentinel: str | None = extractors[0][1] if extractors else None
        entries.append((sentinel, extractors, route))

    # Wrap each alternative in a non-capturing group so that the outer ``|``
    # operators bind correctly regardless of the route's internal structure.
    combined = re.compile(
        "^(?:" + "|".join(f"(?:{p})" for p in parts) + ")$",
    )
    return _DepthBucket(pattern=combined, entries=entries)


def _extract_result(
    match: re.Match,
    bucket: _DepthBucket,
) -> ResolvedRoute:
    """
    Extract the matching route and params from a combined-regex ``Match``.

    Iterates ``bucket.entries`` left-to-right (highest priority first) until
    the first entry whose sentinel group is non-``None``.  Since exactly one
    alternative can match in an alternation, this loop exits on the first hit.

    Parameters
    ----------
    match : re.Match
        Successful match against ``bucket.pattern``.
    bucket : _DepthBucket
        The depth bucket that produced the match.

    Returns
    -------
    ResolvedRoute
        The matched route with type-converted parameters.
    """
    # Fast path: single-route bucket — skip the sentinel check entirely.
    if len(bucket.entries) == 1:
        _, extractors, route = bucket.entries[0]
        return ResolvedRoute(
            route=route,
            params={name: conv(match.group(key)) for name, key, conv in extractors},
        )

    group = match.group  # local alias eliminates one attribute lookup per iteration

    for sentinel, extractors, route in bucket.entries:
        # A sentinel of None means the route has no params, which is
        # structurally impossible for a dynamic route but handled defensively.
        if sentinel is None or group(sentinel) is not None:
            return ResolvedRoute(
                route=route,
                params={name: conv(group(key)) for name, key, conv in extractors},
            )

    # Unreachable unless the bucket was constructed incorrectly.
    _msg = "internal: combined regex matched but no bucket entry claimed it"
    raise RouteNotFound(_msg)


# ── Resolver ──────────────────────────────────────────────────────────────────

class RouteResolver(IRouteResolver):

    __slots__ = (
        "_cache",
        "_cache_max",
        "_dynamic",
        "_fallback",
        "_global_dynamic",
        "_global_static",
        "_static",
    )

    def __init__(
        self,
        routes: dict[str, dict],
        hot_cache_size: int = 512,
        fallback: tuple | None = None,
    ) -> None:
        """
        Initialise the resolver and pre-compute all lookup structures.

        Parameters
        ----------
        routes : dict[str, dict]
            Compiled route table from ``RouteCompiler.compile``.
            Shape: ``{method: {"static": {path: CompiledRoute},
            "dynamic": [CompiledRoute, ...]}}``.
        hot_cache_size : int, optional
            Maximum ``(method, path)`` pairs in the hot-path cache.
            Eviction is FIFO. Default ``512``. Pass ``0`` to disable.
        fallback : tuple | None, optional
            Fallback handler tuple from ``RouteCompiler.compile``.
            ``(None, callable)`` for function fallbacks,
            ``(class, method_name)`` for controller fallbacks,
            or ``None`` if no fallback is registered.

        Returns
        -------
        None
            All lookup structures are built at construction time;
            no value is returned.
        """
        # ── Per-method static lookup tables ────────────────────────────────
        # method → {path: CompiledRoute}
        static: dict[str, dict[str, CompiledRoute]] = {}

        # ── Per-method depth-bucketed dynamic tables ────────────────────────
        # method → {segment_count: _DepthBucket}
        dynamic: dict[str, dict[int, _DepthBucket]] = {}

        # ── Global cross-method data (for 405 detection) ────────────────────
        # Union of all static paths across all methods.
        all_static_paths: set[str] = set()

        # depth → set of raw (anchor-stripped) regex patterns from ALL methods.
        # Using a set deduplicates routes registered under multiple methods
        # (e.g. /users/{id} on both GET and POST).
        global_patterns: dict[int, set[str]] = {}

        for method, bucket in routes.items():
            static[method] = bucket["static"]
            all_static_paths.update(bucket["static"])

            by_depth: dict[int, list[CompiledRoute]] = {}
            for route in bucket["dynamic"]:
                depth = route.segment_count
                by_depth.setdefault(depth, []).append(route)
                # Collect raw pattern for the global 405-detection index.
                global_patterns.setdefault(depth, set()).add(
                    _strip_anchors(route.regex.pattern),
                )

            dynamic[method] = {
                depth: _build_depth_bucket(depth_routes)
                for depth, depth_routes in by_depth.items()
            }

        self._static: dict[str, dict[str, CompiledRoute]] = static
        self._dynamic: dict[str, dict[int, _DepthBucket]] = dynamic

        # ── Global 405 indices ──────────────────────────────────────────────
        self._global_static: frozenset[str] = frozenset(all_static_paths)
        self._global_dynamic: dict[int, re.Pattern] = {
            depth: re.compile(
                "^(?:" + "|".join(f"(?:{p})" for p in patterns) + ")$",
            )
            for depth, patterns in global_patterns.items()
        }

        # ── Hot-path cache ──────────────────────────────────────────────────
        self._cache: dict[tuple[str, str], ResolvedRoute] = {}
        self._cache_max: int = hot_cache_size

        # ── Fallback handler ────────────────────────────────────────────────
        self._fallback: tuple | None = fallback

    # ── Public entry point ────────────────────────────────────────────────────

    def resolve( # NOSONAR
        self,
        method: str,
        path: str,
    ) -> ResolvedRoute:
        """
        Resolve ``(method, path)`` to a :class:`ResolvedRoute`.

        Parameters
        ----------
        method : str
            HTTP verb (case-insensitive).
        path : str
            Raw request URL path.

        Returns
        -------
        ResolvedRoute
            Matched route descriptor with type-converted path params.

        Raises
        ------
        RouteNotFound
            If ``path`` does not match any registered route.
        MethodNotAllowed
            If ``path`` is registered under a *different* HTTP method,
            or if the method is ``HEAD`` and no ``GET`` route exists.
        """
        method = method.upper()
        path = _normalize(path)

        # ── HEAD: delegate to GET ───────────────────────────────────────────
        # RFC 9110 §9.3.2: HEAD is identical to GET without a response body.
        # We resolve HEAD as GET and always raise MethodNotAllowed (never
        # RouteNotFound) when no matching GET route exists.
        is_head = method == "HEAD"
        if is_head:
            method = "GET"

        # ── Layer 1: hot-path cache ─────────────────────────────────────────
        cache_key = (method, path)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # ── Layer 2: static O(1) lookup ─────────────────────────────────────
        method_static = self._static.get(method)
        if method_static is not None:
            static_hit = method_static.get(path)
            if static_hit is not None:
                result = ResolvedRoute(route=static_hit, params={})
                self.__store(cache_key, result)
                return result

        # ── Layer 3: dynamic depth-bucketed combined regex ──────────────────
        # Segment count: path.count('/') equals segment_count for all
        # normalised paths (always start with '/') except the root '/'.
        depth = path.count("/") if path != "/" else 0

        method_dynamic = self._dynamic.get(method)
        if method_dynamic is not None:
            bucket = method_dynamic.get(depth)
            if bucket is not None:
                match = bucket.pattern.match(path)
                if match is not None:
                    result = _extract_result(match, bucket)
                    self.__store(cache_key, result)
                    return result

        # ── Layer 4: 405 vs 404 determination ──────────────────────────────
        # If the path is registered under any *other* method (but not the
        # one requested), the resource exists but the method is not allowed.
        if path in self._global_static:
            raise MethodNotAllowed(path)

        global_bucket = self._global_dynamic.get(depth)
        if global_bucket is not None and global_bucket.match(path) is not None:
            raise MethodNotAllowed(path)

        # Path is completely unknown: raise RouteNotFound for all methods,
        # including HEAD.  This allows the application's fallback handler to
        # respond to HEAD with headers-only (no body), mirroring GET behaviour
        # as required by RFC 9110 §9.3.2.  Raising MethodNotAllowed here
        # would incorrectly suppress the 404 signal and block the fallback.
        raise RouteNotFound(path)

    # ── OPTIONS / fallback helpers ────────────────────────────────────────────

    def options(self, path: str) -> list[str]:
        """
        Return all HTTP methods registered for the given path.

        Searches both the static O(1) table and the depth-bucketed dynamic
        index across every registered HTTP method and returns the sorted
        list of methods that match *path*.  This is the data needed to
        build the ``Allow`` response header for an OPTIONS request.

        ``HEAD`` is always appended when ``GET`` is present because
        :meth:`resolve` handles ``HEAD`` by delegating to ``GET``
        (RFC 9110 §9.3.2), making ``HEAD`` implicitly available for
        every ``GET`` route without requiring an explicit registration.

        For dynamic routes whose regex crosses segment boundaries
        (e.g. ``{filepath:path}``), the standard depth-bucket lookup
        by ``path.count('/')`` may not reach the correct bucket.  A
        second pass over all dynamic buckets for each method is
        performed as a fallback so that such routes are not silently
        missed.

        Parameters
        ----------
        path : str
            Raw request URL path; normalised internally.

        Returns
        -------
        list[str]
            Sorted list of uppercase HTTP method strings that have a
            route matching *path* (e.g. ``['DELETE', 'GET', 'PUT']``).
            Empty when *path* is not registered under any method.
        """
        path = _normalize(path)
        depth = path.count("/") if path != "/" else 0
        allowed: list[str] = []

        all_methods = set(self._static) | set(self._dynamic)
        allowed: list[str] = [
            method
            for method in sorted(all_methods)
            if _path_allowed_for_method(
                self._static.get(method, {}),
                self._dynamic.get(method, {}),
                path,
                depth,
            )
        ]

        # ── HEAD is implicitly available whenever GET is registered ────────
        # RFC 9110 §9.3.2: HEAD is identical to GET without a response body.
        # resolve() already delegates HEAD to GET, so HEAD must appear in
        # the Allow header for any resource that supports GET.
        if "GET" in allowed and "HEAD" not in allowed:
            allowed.append("HEAD")

        # ── OPTIONS is always available ─────────────────────────────────────
        # The kernel intercepts OPTIONS before route resolution, so OPTIONS
        # is implicitly supported for every resource that has at least one
        # registered method.  When the path has no explicit routes but a
        # fallback is registered, GET+HEAD+OPTIONS are added because the
        # fallback handles any path that would otherwise be a 404.
        if allowed:
            if "OPTIONS" not in allowed:
                allowed.append("OPTIONS")
        elif self._fallback is not None:
            allowed = ["GET", "HEAD", "OPTIONS"]

        allowed.sort()
        return allowed

    def fallback(self) -> tuple | None:
        """
        Return the registered fallback handler, if any.

        The fallback is invoked by the dispatcher when no route matches
        the incoming request (i.e. after :exc:`RouteNotFound` or
        :exc:`MethodNotAllowed` is raised).

        Returns
        -------
        tuple | None
            ``(None, callable)`` for function-based fallbacks,
            ``(class, method_name)`` for controller-based fallbacks,
            or ``None`` when no fallback has been registered.
        """
        return self._fallback

    # ── Cache management ──────────────────────────────────────────────────────

    def __store(
        self,
        key: tuple[str, str],
        result: ResolvedRoute,
    ) -> None:
        """
        Insert *result* into the hot-path cache under *key*.

        When the cache is at capacity the oldest entry (FIFO) is evicted
        before inserting.  The operation is O(1) amortised thanks to
        CPython's insertion-ordered dict.

        Parameters
        ----------
        key : tuple[str, str]
            Cache key as ``(method, normalised_path)``.
        result : ResolvedRoute
            Resolved route to store.

        Returns
        -------
        None
            Cache is mutated in place; no value is returned.
        """
        if not self._cache_max:
            return
        cache = self._cache
        if len(cache) >= self._cache_max:
            # ``next(iter(cache))`` is O(1) in CPython — no list allocation.
            del cache[next(iter(cache))]
        cache[key] = result

    def invalidateCache(self) -> None:
        """
        Discard all hot-path cache entries.

        Call this after a live route-table reload so that stale
        ``(method, path) -> ResolvedRoute`` mappings are evicted.

        Returns
        -------
        None
            Cache is cleared in place; no value is returned.
        """
        self._cache.clear()


# ── Path normalisation (module-level for minimum call overhead) ───────────────

def _normalize(path: str) -> str:
    """
    Normalise a raw request path.

    * Ensures a leading ``/``.
    * Strips all trailing slashes from non-root paths.

    This is a module-level function (not a method) so that it can be
    called without any attribute lookup overhead from
    :meth:`RouteResolver.resolve`.

    Parameters
    ----------
    path : str
        Raw URL path, e.g. ``'users/profile/'``.

    Returns
    -------
    str
        Normalised path, e.g. ``'/users/profile'``.
    """
    if not path:
        return "/"
    if path[0] != "/":
        path = "/" + path
    if len(path) > 1 and path[-1] == "/":
        path = path.rstrip("/") or "/"
    return path
