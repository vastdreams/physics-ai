"""
Discovery endpoints: cross-domain inference, gap analysis.
"""

from flask import jsonify, request

from api.v1 import api_v1


def _get_graph():
    try:
        from physics.knowledge import get_knowledge_graph
        return get_knowledge_graph()
    except Exception:
        return {"nodes": {}, "domains": {}}


@api_v1.route("/discovery/cross-domain", methods=["POST"])
def cross_domain_inference():
    """
    Find connections between two domains (e.g. quantum_mechanics and general_relativity).

    Request body: {"domain_a": "quantum_mechanics", "domain_b": "general_relativity"}
    """
    data = request.get_json() or {}
    domain_a = data.get("domain_a", "quantum_mechanics")
    domain_b = data.get("domain_b", "general_relativity")
    graph = _get_graph()
    nodes = graph.get("nodes", {})
    domains = graph.get("domains", {})
    shared = []
    for nid, node in nodes.items():
        d = getattr(node, "domain", None) or (node.get("domain") if isinstance(node, dict) else None)
        if not d:
            continue
        if d == domain_a or d == domain_b:
            shared.append({"id": nid, "domain": d, "name": getattr(node, "name", nid)})
    derives = graph.get("outgoing", {}) or {}
    connections = []
    for n in shared:
        for target in derives.get(n["id"], []):
            t_node = nodes.get(target)
            if t_node:
                td = getattr(t_node, "domain", None) or (t_node.get("domain") if isinstance(t_node, dict) else None)
                if td and td != n["domain"]:
                    connections.append({"from": n["id"], "to": target, "from_domain": n["domain"], "to_domain": td})
    return jsonify({
        "success": True,
        "domain_a": domain_a,
        "domain_b": domain_b,
        "bridges": connections[:20],
        "node_count": len(shared),
    }), 200


@api_v1.route("/discovery/gaps", methods=["GET"])
def gap_analysis():
    """
    Find gaps in the knowledge graph — domains with few equations, missing derivations, etc.
    """
    graph = _get_graph()
    nodes = graph.get("nodes", {})
    domains = graph.get("domains", {})
    domain_counts = {}
    for nid, node in nodes.items():
        d = getattr(node, "domain", None) or (node.get("domain") if isinstance(node, dict) else "unknown")
        domain_counts[d] = domain_counts.get(d, 0) + 1
    sparse = [d for d, c in domain_counts.items() if c < 5 and d != "unknown"]
    incoming = graph.get("incoming", {})
    orphaned = [nid for nid in nodes if not incoming.get(nid)]
    return jsonify({
        "success": True,
        "sparse_domains": sparse,
        "orphaned_nodes": orphaned[:30],
        "domain_counts": domain_counts,
        "total_nodes": len(nodes),
    }), 200
