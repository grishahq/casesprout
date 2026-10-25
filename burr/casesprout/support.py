"""A real deterministic Burr support workflow; no model or network calls.

Copyright 2026 CaseSprout contributors. Licensed under Apache-2.0.
"""
from burr.core import ApplicationBuilder, State, action, expr


@action(reads=[], writes=["request"])
def intake(state: State, request: dict) -> State:
    if request.get("topic") not in {"faq", "refund", "security", "escalation", "outage"}:
        raise ValueError("Unknown support topic")
    return state.update(request=request)


@action(reads=["request"], writes=["disposition"])
def faq(state: State) -> State:
    return state.update(disposition="self_service")


@action(reads=["request"], writes=["disposition"])
def refund(state: State, variant: str = "fixed") -> State:
    return state.update(disposition="auto_approved" if variant == "refund_auto_approve" else "refund_review")


@action(reads=["request"], writes=["disposition"])
def security(state: State, variant: str = "fixed") -> State:
    return state.update(disposition="auto_reset" if variant in {"security_auto_reset", "historical_security_bug"} else "human_security_review")


@action(reads=["request"], writes=["disposition"])
def escalation(state: State) -> State:
    return state.update(disposition="human_escalation")


@action(reads=["request"], writes=["disposition"])
def outage(state: State, variant: str = "fixed") -> State:
    if variant != "outage_swallowed":
        raise ConnectionError("Controlled unavailable support backend")
    return state.update(disposition="silently_ignored")


def run(inputs, variant="fixed", storage=None, app_id=None):
    builder = (ApplicationBuilder().with_actions(intake, faq, refund=refund.bind(variant=variant),
                security=security.bind(variant=variant), escalation=escalation, outage=outage.bind(variant=variant))
               .with_transitions(*[("intake", name, expr(f"request['topic'] == '{name}'"))
                                   for name in ("faq", "refund", "security", "escalation", "outage")])
               .with_entrypoint("intake"))
    if storage is not None:
        builder = builder.with_identifiers(app_id=app_id).with_tracker(project="support", params={"storage_dir": str(storage)})
    app = builder.build()
    _, _, state = app.run(halt_after=["faq", "refund", "security", "escalation", "outage"], inputs=inputs)
    return {k: v for k, v in state.get_all().items() if not k.startswith("__")}


def replay(inputs):
    """Adapter for exported tests: accepts first-action inputs, returns public final state."""
    return run(inputs)


def replay_refund_bug(inputs):
    return run(inputs, variant="refund_auto_approve")


def replay_security_bug(inputs):
    return run(inputs, variant="security_auto_reset")


def replay_outage_bug(inputs):
    return run(inputs, variant="outage_swallowed")
