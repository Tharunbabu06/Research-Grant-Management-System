"""
Lab 5: MCP-Style Connector -- One Server for All Sources
========================================================
Domain: Research Grant Management System (Chapter 13 / Lab Guide Lab 5)
Phase: A - Foundations | Goal: Expose every data source through one typed connector

Description:
A Model Context Protocol (MCP) inspired integration server that acts as the single
governed surface for all six grant data sources:
1. `funding`: Verified agency calls and guideline text.
2. `literature`: Approved academic papers and citation records.
3. `history`: Prior institutional grant submissions and outcomes.
4. `hr`: Staff salary register and institutional rate card.
5. `policy`: Institutional rules (ethics, overhead, AI disclosure).
6. `rules`: Agency compliance rulebooks and document registries.

Key concepts demonstrated:
- Unified capability manifest with typed input/output contracts.
- Distinction between `resource` (static data) and `tool` (dynamic query/compute).
- Authentication boundary: internal agent token required for all data access.
- Authorization: Caller allowlisting for sensitive endpoints (e.g., HR salary records).
- Capability discovery: Client dynamically discovers and invokes endpoints without hardcoded methods.
- Full audit logging of all data reads.

Assignments included:
- Assignment 1: Dynamic capability discovery (adding a fourth capability 'history.stats' discovered at runtime).
- Assignment 2: Security boundary check (enforcing token check and caller restrictions).
"""

import time
from typing import Dict, Any, List, Optional
from seed_data import (
    CALLS, LITERATURE, HISTORY, PERSONNEL, RATE_CARD, POLICIES,
    COMPLIANCE_RULES, DOCUMENT_REGISTER, INSTITUTION
)

CONNECTOR_TOKEN = "aura-internal-agent-token"

# Manifest declaring all exposed resources and tools
CAPABILITIES = [
    {
        "name": "funding.calls",
        "kind": "resource",
        "source": "funding",
        "description": "Lists verified funding calls filtered by funding type",
        "input": {"fundingType": "Optional[str]"},
        "output": {"calls": "List[dict]"},
    },
    {
        "name": "hr.personnel",
        "kind": "resource",
        "source": "hr",
        "description": "Reads personnel register and monthly salaries",
        "input": {"role": "Optional[str]"},
        "output": {"personnel": "List[dict]"},
    },
    {
        "name": "compliance.rules",
        "kind": "resource",
        "source": "rules",
        "description": "Reads compliance checklist rules for a given funding type",
        "input": {"appliesTo": "Optional[str]"},
        "output": {"rules": "List[dict]"},
    },
    {
        "name": "query_guidelines",
        "kind": "tool",
        "source": "funding",
        "description": "Queries specific guidelines for a call with section filter",
        "input": {"callId": "str", "section": "Optional[str]"},
        "output": {"guidelines": "List[dict]"},
    },
]

ALLOWED_CALLERS_HR = {"coordinator", "budget_agent", "dean"}


class MCPServer:
    """
    Central Integration Server fronting all grant sources.
    No agent is permitted to touch a raw source directly.
    """
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    def list_capabilities(self) -> List[Dict[str, Any]]:
        """Capability discovery endpoint."""
        return CAPABILITIES

    def invoke(self, endpoint: str, args: Dict[str, Any], token: str, caller: str) -> Dict[str, Any]:
        """Governed execution of an MCP capability."""
        start_time = time.time()
        base_log = {
            "endpoint": endpoint,
            "caller": caller,
            "args": args,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        # 1. Authentication Check
        if token != CONNECTOR_TOKEN:
            err = {"error": "Unauthorized: invalid agent token"}
            self._log_audit({**base_log, "status": "error", "error": err["error"]})
            return err

        # 2. Authorization Check for Sensitive HR Data
        if endpoint == "hr.personnel" and caller not in ALLOWED_CALLERS_HR:
            err = {"error": f"Permission denied: caller '{caller}' cannot access HR personnel records"}
            self._log_audit({**base_log, "status": "denied", "error": err["error"]})
            return err

        # 3. Dispatch to internal handlers
        try:
            if endpoint == "funding.calls":
                ft = args.get("fundingType")
                data = [c for c in CALLS if not ft or c.get("fundingType") == ft]
                res = {"calls": data, "count": len(data)}

            elif endpoint == "hr.personnel":
                role = args.get("role")
                data = [p for p in PERSONNEL if not role or p.get("role") == role]
                res = {"personnel": data, "count": len(data)}

            elif endpoint == "compliance.rules":
                app = args.get("appliesTo")
                data = [r for r in COMPLIANCE_RULES if not app or r.get("appliesTo") in ("all", app)]
                res = {"rules": data, "count": len(data)}

            elif endpoint == "query_guidelines":
                call_id = args.get("callId")
                section = args.get("section")
                call = next((c for c in CALLS if c["id"] == call_id), None)
                if not call:
                    return {"error": f"Call '{call_id}' not found"}
                guides = call.get("guidelines", [])
                if section:
                    guides = [g for g in guides if g.get("section") == section]
                res = {"guidelines": guides, "count": len(guides)}

            elif endpoint == "history.stats":
                # Added for Assignment 1
                total = len(HISTORY)
                funded = sum(1 for h in HISTORY if h.get("outcome") == "funded")
                res = {"total": total, "funded": funded, "success_rate": round(funded / total, 2)}

            else:
                return {"error": f"Unknown capability '{endpoint}'"}

            latency_ms = round((time.time() - start_time) * 1000, 2)
            self._log_audit({**base_log, "status": "ok", "latency_ms": latency_ms, "count": res.get("count", 1)})
            return {"result": res, "latency_ms": latency_ms}

        except Exception as e:
            return {"error": f"Server invocation error: {str(e)}"}

    def _log_audit(self, entry: Dict[str, Any]):
        self.audit_log.append(entry)


class MCPClient:
    """
    Client used by all pipeline agents to discover and invoke capabilities.
    """
    def __init__(self, server: MCPServer, caller_name: str, token: str = CONNECTOR_TOKEN):
        self.server = server
        self.caller_name = caller_name
        self.token = token

    def discover(self) -> List[Dict[str, Any]]:
        """Dynamically queries the server's manifest."""
        return self.server.list_capabilities()

    def call(self, capability_name: str, **kwargs) -> Dict[str, Any]:
        """Dispatches dynamic call through the discovered interface."""
        manifest = {c["name"]: c for c in self.discover()}
        if capability_name not in manifest:
            raise ValueError(f"Capability '{capability_name}' not available in server manifest")

        return self.server.invoke(
            endpoint=capability_name,
            args=kwargs,
            token=self.token,
            caller=self.caller_name,
        )


# ==============================================================================
# Graded Assignments
# ==============================================================================

def run_assignment_1_add_capability(server: MCPServer):
    """
    Assignment 1 -- Add a Fourth, Discoverable Capability:
    Add 'history.stats' to CAPABILITIES and verify that MCPClient can
    discover and invoke it without any hard-coded methods added to MCPClient.
    """
    print("\n--- [Assignment 1] Dynamic Discovery of New Capability ---")
    CAPABILITIES.append({
        "name": "history.stats",
        "kind": "resource",
        "source": "history",
        "description": "Aggregates historical grant success rates",
        "input": {},
        "output": {"total": "int", "funded": "int", "success_rate": "float"},
    })

    client = MCPClient(server, caller_name="coordinator")
    discovered = [c["name"] for c in client.discover()]
    print(f"Discovered Capabilities: {discovered}")
    assert "history.stats" in discovered, "New capability was not discovered!"

    stats = client.call("history.stats")
    print(f"Invoked 'history.stats' dynamically: {stats['result']}")


def run_assignment_2_security_boundary(server: MCPServer):
    """
    Assignment 2 -- Security Boundary Enforcement:
    1. Test invalid token rejection.
    2. Test unauthorized caller accessing restricted HR records.
    """
    print("\n--- [Assignment 2] Security Boundary Enforcement ---")

    # Adversarial test 1: Bad token
    unauthorized_client = MCPClient(server, caller_name="coordinator", token="invalid-secret-key")
    res1 = unauthorized_client.call("funding.calls", fundingType="government")
    print(f"Bad Token Test: {res1}")
    assert "error" in res1 and "Unauthorized" in res1["error"], "Token security check bypassed!"

    # Adversarial test 2: Unpermitted caller accessing HR
    guest_client = MCPClient(server, caller_name="guest_agent", token=CONNECTOR_TOKEN)
    res2 = guest_client.call("hr.personnel")
    print(f"Unpermitted Caller Test: {res2}")
    assert "error" in res2 and "Permission denied" in res2["error"], "Caller permission check bypassed!"
    print("Verification passed: Security boundaries strictly enforced.")


# ==============================================================================
# Main Demonstration
# ==============================================================================

if __name__ == "__main__":
    print("======================================================================")
    print("Lab 5: MCP-Style Connector -- Mini Integration Server")
    print("======================================================================")

    server = MCPServer()
    client = MCPClient(server, caller_name="budget_agent")

    # 1. Capability Discovery
    print("=== Capability Discovery from Manifest ===")
    for cap in client.discover():
        print(f"  [{cap['kind'].upper()}] {cap['name']} -> {cap['description']}")

    # 2. Call 1: Read funding calls (resource)
    print("\n=== Call 1: Read Funding Calls ===")
    calls_res = client.call("funding.calls", fundingType="government")
    print(f"Retrieved {calls_res['result']['count']} government calls (Latency: {calls_res['latency_ms']} ms)")

    # 3. Call 2: Read HR Personnel (resource with authorized caller)
    print("\n=== Call 2: Read HR Personnel (Authorized caller 'budget_agent') ===")
    hr_res = client.call("hr.personnel", role="RA")
    print(f"Personnel records: {hr_res['result']['personnel']}")

    # 4. Call 3: Query Guidelines (tool)
    print("\n=== Call 3: Query Guidelines ===")
    guide_res = client.call("query_guidelines", callId="call-serb-crg", section="budget")
    print(f"Budget Guidelines for SERB CRG: {guide_res['result']['guidelines']}")

    # 5. Assignments
    run_assignment_1_add_capability(server)
    run_assignment_2_security_boundary(server)

    # 6. Audit Log inspection
    print("\n=== Server Audit Log Sample ===")
    for log in server.audit_log[:4]:
        print(f"  {log['timestamp']} | Caller: {log['caller']} | Endpoint: {log['endpoint']} | Status: {log['status']}")
