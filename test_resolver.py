import re, sys
sys.path.insert(0, r'D:\WORKSPACE\ORIONIS_FRAMEWORK\framework')
from orionis.http.routes.route_compiler import RouteCompiler
from orionis.http.routes.route_resolver import RouteResolver
from orionis.http.enums.route_types import RouteType
from orionis.http.routes.compiled_route import CompiledRoute

# Simulate a compiled dynamic route GET /users/{id}
is_static, regex, converters = RouteCompiler.compilePath('/users/{id}')
print(f'is_static={is_static}, regex={regex}, converters={converters}')

route = CompiledRoute(
    path='/users/{id}',
    method='GET',
    type=RouteType.FUNCTION,
    action={'function': 'dummy', 'module': 'dummy'},
    name=None,
    regex=regex,
    segment_count=sum(1 for s in '/users/{id}'.split('/') if s),
    priority_score=10,
    converters=converters,
    middleware=[],
    without_middleware=set(),
)

print(f'segment_count={route.segment_count}')

routes = {
    'GET': {
        'static': {},
        'dynamic': [route],
    }
}

resolver = RouteResolver(routes)

# Try options on a dynamic path
result = resolver.options('/users/123')
print(f"options('/users/123') = {result}")

# Also test resolve
try:
    r = resolver.resolve('GET', '/users/123')
    print(f"resolve('GET', '/users/123') = {r}")
except Exception as e:
    print(f'resolve error: {e}')
