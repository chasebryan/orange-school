#!/usr/bin/env python3
"""Print one deterministic ASS-104 lifecycle record and claim boundary."""

from lifecycle_model import (
    MAX_TICK,
    canonical_record,
    endpoint_scenario,
    installation_decision,
    record_digest,
    support_decision,
)


def main() -> int:
    state = endpoint_scenario()
    rollback = installation_decision(state, 7)
    current = installation_decision(state, 8)
    support = support_decision(state, MAX_TICK)
    encoded = canonical_record(state)

    print("model: bounded release and incident lifecycle v1")
    print(f"final release/incident: {state.release_phase}/{state.incident_phase}")
    print(f"revision/rollback floor: {state.release_revision}/{state.min_installable_revision}")
    print(f"events/downstreams/drills: {len(state.events)}/{len(state.notified_downstreams)}/{state.recovery_drills}")
    print(f"rollback revision 7: {rollback.code}")
    print(f"current revision 8: {current.code}")
    print(f"support at tick {MAX_TICK}: {support.code}")
    print(f"canonical bytes: {len(encoded.encode('utf-8'))}")
    print(f"record sha256: {record_digest(state)}")
    print("claim limit: evidence identifiers are references, not proof that external actions occurred")
    print("claim limit: no advisory was published and no downstream was contacted")
    print("claim limit: this is not an Orange release, compatibility, support, or security claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
