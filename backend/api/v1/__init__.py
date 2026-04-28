"""Регистрация namespace v1."""


def register_namespaces(api) -> None:
    from api.v1.categories import ns as categories_ns
    from api.v1.orders import ns as orders_ns
    from api.v1.reviews import ns as reviews_ns
    from api.v1.services import ns as services_ns
    from api.v1.specialists import ns as specialists_ns
    from api.v1.stats import ns as stats_ns
    from api.v1.users import ns as users_ns
    from api.v1.discovery import ns as discovery_ns

    api.add_namespace(categories_ns, path="/v1/categories")
    api.add_namespace(services_ns, path="/v1/services")
    api.add_namespace(orders_ns, path="/v1/orders")
    api.add_namespace(reviews_ns, path="/v1/reviews")
    api.add_namespace(specialists_ns, path="/v1/specialists")
    api.add_namespace(users_ns, path="/v1/users")
    api.add_namespace(stats_ns, path="/v1/stats")
    api.add_namespace(discovery_ns, path="/v1/discovery")
