import sys
sys.path.insert(0, r"D:\WORKSPACE\ORIONIS_FRAMEWORK\framework")

from orionis.http.routes.route_compiler import RouteCompiler
from orionis.http.routes.route_resolver import RouteResolver
from orionis.http.enums.route_types import RouteType
from orionis.http.routes.compiled_route import CompiledRoute

def make_route(path, method="GET"):
    is_static, regex, converters = RouteCompiler.compilePath(path)
    return is_static, CompiledRoute(
        path=path, method=method, type=RouteType.FUNCTION,
        action={"function": "dummy", "module": "dummy"},
        name=None, regex=regex,
        segment_count=sum(1 for s in path.split("/") if s),
        priority_score=10, converters=converters,
        middleware=[], without_middleware=set(),
    )

# Test 1: dynamic only - HEAD should be added when GET is present
_, route1 = make_route("/users/{id}")
routes1 = {"GET": {"static": {}, "dynamic": [route1]}}
r1 = RouteResolver(routes1)
result = r1.options("/users/123")
print("Test1 options('/users/123'):", result)
assert "GET" in result, "GET missing"
assert "HEAD" in result, "HEAD missing - should be implicit when GET is present"
print("PASS: HEAD is included")

# Test 2: path type crossing slashes
_, route2 = make_route("/files/{filepath:path}")
routes2 = {"GET": {"static": {}, "dynamic": [route2]}}
r2 = RouteResolver(routes2)
result2 = r2.options("/files/a/b/c.txt")
print("\nTest2 options('/files/a/b/c.txt'):", result2)
assert "GET" in result2, "GET missing for cross-slash path route"
assert "HEAD" in result2, "HEAD missing for cross-slash path route"
print("PASS: cross-segment path route works")

# Test3: options for path that has no matching route returns []
result3 = r1.options("/nonexistent/path")
print("\nTest3 options('/nonexistent/path'):", result3)
assert result3 == [], f"Expected empty, got {result3}"
print("PASS: no match returns []")

print("\nAll tests passed!")
