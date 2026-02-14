# PATH: api/v1/substrate.py
# PURPOSE:
#   - API endpoints for the Beyond Frontier substrate
#   - Exposes chat, formulas, evolution, and statistics
#
# ROLE IN ARCHITECTURE:
#   - HTTP layer for substrate access
#
# MAIN EXPORTS:
#   - substrate_bp: Flask blueprint
#
# NON-RESPONSIBILITIES:
#   - Does NOT implement logic (that's in substrate/)
#
# NOTES FOR FUTURE AI:
#   - All endpoints should be RESTful
#   - Return structured JSON responses

from flask import Blueprint, request, jsonify
from typing import Optional
import json

# Will be initialized by app.py
_physics_ai = None

substrate_bp = Blueprint("substrate", __name__, url_prefix="/substrate")


def init_substrate(physics_ai):
    """Initialize the substrate API with a PhysicsAI instance."""
    global _physics_ai
    _physics_ai = physics_ai


def get_ai():
    """Get the PhysicsAI instance."""
    if _physics_ai is None:
        raise RuntimeError("PhysicsAI not initialized")
    return _physics_ai


# =============================================================================
# Chat endpoints
# =============================================================================

@substrate_bp.route("/chat", methods=["POST"])
def chat():
    """
    Send a message to the Beyond Frontier.
    
    Request body:
    {
        "message": "physics question",
        "session_id": "optional session id",
        "context": {"optional": "context"}
    }
    
    Response:
    {
        "response": {
            "content": "AI response",
            "confidence": 0.95,
            "trace_id": "trace_id",
            ...
        },
        "session_id": "session_id"
    }
    """
    try:
        data = request.get_json()
        message = data.get("message", "")
        session_id = data.get("session_id")
        context = data.get("context", {})
        
        if not message:
            return jsonify({"success": False, "error": "message is required"}), 400
        
        ai = get_ai()
        response = ai.chat(message, session_id=session_id, context=context)
        
        return jsonify({
            "response": response.to_dict(),
            "session_id": session_id or response.trace_id,  # Use trace_id as fallback session
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# Planner / Executor endpoints
# =============================================================================

@substrate_bp.route("/plan", methods=["POST"])
def dry_run_plan():
    """
    Dry-run the planner without execution.

    Request body:
    {
        "inputs": {"m": 1.0, "v": 2.0},
        "outputs": ["KE"],
        "context": {"domain": "classical"},
        "max_plans": 3
    }
    """
    try:
        data = request.get_json() or {}
        inputs = data.get("inputs", {})
        outputs = data.get("outputs", [])
        context = data.get("context", {})
        max_plans = int(data.get("max_plans", 3))

        if not outputs:
            return jsonify({"success": False, "error": "outputs are required"}), 400

        ai = get_ai()
        plans = ai.dry_run_plan(inputs=inputs, outputs=outputs, context=context, max_plans=max_plans)
        return jsonify({"plans": plans, "count": len(plans)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/execute", methods=["POST"])
def execute_formula():
    """
    Execute a single formula directly.

    Request body:
    {
        "formula_id": "newton_2",
        "inputs": {"m": 2.0, "a": 3.0}
    }
    """
    try:
        data = request.get_json() or {}
        formula_id = data.get("formula_id")
        inputs = data.get("inputs", {})

        if not formula_id:
            return jsonify({"success": False, "error": "formula_id is required"}), 400

        ai = get_ai()
        outputs = ai.execute_formula(formula_id, inputs)
        return jsonify({"outputs": outputs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/sessions", methods=["POST"])
def create_session():
    """Create a new chat session."""
    try:
        data = request.get_json() or {}
        context = data.get("context", {})
        
        ai = get_ai()
        session = ai.create_session(context)
        
        return jsonify({
            "session_id": session.id,
            "created_at": session.created_at.isoformat(),
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id: str):
    """Get session details."""
    try:
        ai = get_ai()
        session = ai.chatbot.get_session(session_id)
        
        if not session:
            return jsonify({"success": False, "error": "Session not found"}), 404
        
        return jsonify(session.to_dict())
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# Formula endpoints
# =============================================================================

@substrate_bp.route("/formulas", methods=["GET"])
def list_formulas():
    """
    List formulas with optional filtering.
    
    Query params:
    - domain: Filter by domain
    - status: Filter by status
    - limit: Max results (default 100)
    - offset: Pagination offset
    """
    try:
        ai = get_ai()
        
        domain = request.args.get("domain")
        status = request.args.get("status")
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        
        # Get all formulas and filter
        formulas = ai.graph.get_all_formulas()
        
        if domain:
            formulas = [f for f in formulas if f.domain == domain]
        
        if status:
            from substrate.graph.formula import FormulaStatus
            try:
                status_enum = FormulaStatus[status.upper()]
                formulas = [f for f in formulas if f.status == status_enum]
            except KeyError:
                pass
        
        # Paginate
        total = len(formulas)
        formulas = formulas[offset:offset + limit]
        
        return jsonify({
            "formulas": [f.to_dict() for f in formulas],
            "total": total,
            "limit": limit,
            "offset": offset,
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/formulas/<formula_id>", methods=["GET"])
def get_formula(formula_id: str):
    """Get a specific formula."""
    try:
        ai = get_ai()
        formula = ai.get_formula(formula_id)
        
        if not formula:
            return jsonify({"success": False, "error": "Formula not found"}), 404
        
        return jsonify(formula.to_dict())
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/formulas", methods=["POST"])
def add_formula():
    """
    Add a new formula.
    
    Request body: Formula object (see Formula.to_dict() for schema)
    """
    try:
        data = request.get_json()
        
        from substrate.graph.formula import Formula
        formula = Formula.from_dict(data)
        
        ai = get_ai()
        success = ai.add_formula(formula)
        
        if success:
            return jsonify({"formula_id": formula.id, "success": True}), 201
        else:
            return jsonify({"success": False, "error": "Formula already exists"}), 409
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/formulas/search", methods=["GET"])
def search_formulas():
    """
    Search formulas.
    
    Query params:
    - q: Search query
    - domain: Filter by domain
    - limit: Max results
    """
    try:
        ai = get_ai()
        
        query = request.args.get("q", "")
        domain = request.args.get("domain")
        limit = int(request.args.get("limit", 10))
        
        results = ai.search_formulas(query, domain=domain, limit=limit)
        
        return jsonify({"results": results})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# Graph endpoints
# =============================================================================

@substrate_bp.route("/graph/stats", methods=["GET"])
def graph_stats():
    """Get formula graph statistics."""
    try:
        ai = get_ai()
        return jsonify(ai.graph.stats())
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/graph/edges", methods=["GET"])
def list_edges():
    """
    List edges in the graph.
    
    Query params:
    - from_id: Filter by source formula
    - to_id: Filter by target formula
    - type: Filter by edge type
    """
    try:
        ai = get_ai()
        
        from_id = request.args.get("from_id")
        to_id = request.args.get("to_id")
        edge_type = request.args.get("type")
        
        edges = ai.graph._edges
        
        if from_id:
            edges = [e for e in edges if e.source_id == from_id]
        
        if to_id:
            edges = [e for e in edges if e.target_id == to_id]
        
        if edge_type:
            from substrate.graph.formula_graph import EdgeType
            try:
                edge_type_enum = EdgeType[edge_type.upper()]
                edges = [e for e in edges if e.edge_type == edge_type_enum]
            except KeyError:
                pass
        
        return jsonify({
            "edges": [e.to_dict() for e in edges],
            "total": len(edges),
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/graph/consistency", methods=["GET"])
def check_consistency():
    """Check graph consistency."""
    try:
        ai = get_ai()
        issues = ai.graph.check_consistency()
        
        return jsonify({
            "issues": issues,
            "issue_count": len(issues),
            "is_consistent": len(issues) == 0,
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# Trace endpoints
# =============================================================================

@substrate_bp.route("/traces/<trace_id>", methods=["GET"])
def get_trace(trace_id: str):
    """Get a reasoning trace."""
    try:
        ai = get_ai()
        trace = ai.get_trace(trace_id)
        
        if not trace:
            return jsonify({"success": False, "error": "Trace not found"}), 404
        
        return jsonify(trace)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/traces", methods=["GET"])
def list_traces():
    """
    List recent traces.
    
    Query params:
    - limit: Max traces to return
    - failed: If "true", only show failed traces
    """
    try:
        ai = get_ai()
        
        limit = int(request.args.get("limit", 10))
        failed_only = request.args.get("failed", "").lower() == "true"
        
        if failed_only:
            traces = ai.trace_store.get_failed()[:limit]
        else:
            traces = ai.trace_store.get_recent(n=limit)
        
        return jsonify({
            "traces": [t.to_dict() for t in traces],
            "count": len(traces),
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# Evolution endpoints
# =============================================================================

@substrate_bp.route("/evolution/stats", methods=["GET"])
def evolution_stats():
    """Get evolution statistics."""
    try:
        ai = get_ai()
        return jsonify(ai.evolution.get_statistics())
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/evolution/results", methods=["GET"])
def evolution_results():
    """
    Get recent evolution results.
    
    Query params:
    - limit: Max results to return
    """
    try:
        ai = get_ai()
        limit = int(request.args.get("limit", 10))
        
        results = ai.evolution.get_results(n=limit)
        
        return jsonify({
            "results": [r.to_dict() for r in results],
            "count": len(results),
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/evolution/trigger", methods=["POST"])
def trigger_evolution():
    """Trigger an immediate evolution cycle."""
    try:
        ai = get_ai()
        result = ai.force_evolution_cycle()
        
        return jsonify({
            "result": result.to_dict(),
            "success": result.actions_succeeded > 0 or result.actions_applied == 0,
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# Critic endpoints
# =============================================================================

@substrate_bp.route("/critics/stats", methods=["GET"])
def critic_stats():
    """Get critic statistics."""
    try:
        ai = get_ai()
        
        return jsonify({
            "logic_critic": ai.logic_critic.statistics(),
            "code_critic": ai.code_critic.statistics(),
            "meta_critic": ai.meta_critic.statistics(),
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/critics/report", methods=["GET"])
def critic_report():
    """Get meta-critic report."""
    try:
        ai = get_ai()
        report = ai.meta_critic.generate_report()
        
        return jsonify({
            "report": report,
            "issues": [i.to_dict() for i in ai.meta_critic.evaluate_critics()],
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# System endpoints
# =============================================================================

@substrate_bp.route("/stats", methods=["GET"])
def system_stats():
    """Get overall system statistics."""
    try:
        ai = get_ai()
        return jsonify(ai.stats())
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/arxiv-ingest", methods=["POST"])
def arxiv_ingest():
    """
    Ingest papers from arXiv into the formula graph.

    Request body:
    {
        "query": "physics",
        "max_results": 3
    }
    """
    try:
        data = request.get_json() or {}
        query = data.get("query", "physics")
        max_results = int(data.get("max_results", 3))

        from ingestion.arxiv_ingestion import ingest_arxiv_papers

        ai = get_ai()
        stats = ingest_arxiv_papers(ai, query=query, max_results=max_results)
        return jsonify({"success": True, **stats}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@substrate_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    try:
        ai = get_ai()
        return jsonify({
            "status": "healthy",
            "running": ai._running,
            "formula_count": len(ai.graph),
        })
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
        }), 500

