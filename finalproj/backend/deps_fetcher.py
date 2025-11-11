def parse_dependency_json(obj):
    """Recursively walk a dependency JSON tree."""
    nodes = []
    edges = []

    def walk(name, deps):
        nodes.append({"data": {"id": name}})
        for dep, meta in (deps or {}).items():
            edges.append({"data": {"source": name, "target": dep}})
            walk(dep, meta.get("dependencies", {}))

    root_name = obj.get("name", "root")
    walk(root_name, obj.get("dependencies", {}))
    return {"nodes": nodes, "edges": edges}
