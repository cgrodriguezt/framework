import sys
sys.path.insert(0, r"D:\WORKSPACE\ORIONIS_FRAMEWORK\framework")

from orionis.http.routes.route_compiler import RouteCompiler
from orionis.http.routes.route_resolver import RouteResolver, RouteNotFound, MethodNotAllowed
from orionis.http.enums.route_types import RouteType
from orionis.http.routes.compiled_route import CompiledRoute

def make_route(path, method="GET"):
    is_static, regex, converters = RouteCompiler.compilePath(path)
    return CompiledRoute(
        path=path, method=method, type=RouteType.FUNCTION,
        action={"function": "dummy", "module": "dummy"},
        name=None, regex=regex,
        segment_count=sum(1 for s in path.split("/") if s),
        priority_score=10, converters=converters,
        middleware=[], without_middleware=set(),
    )

print("=== Test 1: HEAD on matched GET dynamic route returns resolved route ===")
route1 = make_route("/users/{id}")
routes1 = {"GET": {"static": {}, "dynamic": [route1]}}
r1 = RouteResolver(routes1)
try:
    resolved = r1.resolve("HEAD", "/users/123")
    print(f"PASS: HEAD resolved to route '{resolved.route.path}'")
except Exception as e:
    print(f"FAIL: {e}")

print("\n=== Test 2: HEAD on completely unknown path raises RouteNotFound (not MethodNotAllowed) ===")
try:
    r1.resolve("HEAD", "/nonexistent")
    print("FAIL: should have raised RouteNotFound")
except RouteNotFound:
    print("PASS: RouteNotFound raised for unknown path")
except MethodNotAllowed:
    print("FAIL: MethodNotAllowed raised (wrong - should be RouteNotFound)")
except Exception as e:
    print(f"FAIL: unexpected error: {e}")

print("\n=== Test 3: HEAD on path registered under different method raises MethodNotAllowed ===")
route_post = make_route("/items/{id}", method="POST")
routes2 = {"POST": {"static": {}, "dynamic": [route_post]}}
r2 = RouteResolver(routes2)
try:
    r2.resolve("HEAD", "/items/42")
    print("FAIL: should have raised MethodNotAllowed")
except MethodNotAllowed:
    print("PASS: MethodNotAllowed raised for POST-only route")
except RouteNotFound:
    print("FAIL: RouteNotFound raised (wrong - path IS registered under POST)")
except Exception as e:
    print(f"FAIL: unexpected error: {e}")

print("\n=== Test 4: options() includes OPTIONS in allowed list ===")
result = r1.options("/users/123")
print(f"options('/users/123') = {result}")
assert "OPTIONS" in result, "OPTIONS missing from Allow list"
assert "GET" in result, "GET missing"
assert "HEAD" in result, "HEAD missing"
print("PASS: OPTIONS included in Allow header")

print("\n=== Test 5: options() returns GET+HEAD+OPTIONS when fallback registered and no specific route ===")
fallback = (None, lambda: None)
r3 = RouteResolver(routes1, fallback=fallback)
result3 = r3.options("/completely/unknown/path")
print(f"options('/completely/unknown/path') with fallback = {result3}")
assert "GET" in result3, "GET missing"
assert "HEAD" in result3, "HEAD missing"
assert "OPTIONS" in result3, "OPTIONS missing"
print("PASS: fallback path returns GET+HEAD+OPTIONS")

print("\n=== Test 6: options() returns [] when no routes and no fallback ===")
r4 = RouteResolver({})
result4 = r4.options("/unknown")
print(f"options('/unknown') with no routes, no fallback = {result4}")
assert result4 == [], f"Expected [], got {result4}"
print("PASS: empty list returned with no routes and no fallback")

print("\n=== Test 7: options() with cross-segment path type ===")
route_file = make_route("/files/{filepath:path}")
routes3 = {"GET": {"static": {}, "dynamic": [route_file]}}
r5 = RouteResolver(routes3)
result5 = r5.options("/files/a/b/c.txt")
print(f"options('/files/a/b/c.txt') = {result5}")
assert "GET" in result5 and "HEAD" in result5 and "OPTIONS" in result5, f"Missing methods: {result5}"
print("PASS: cross-segment path type works")

print("\nAll tests passed!")
