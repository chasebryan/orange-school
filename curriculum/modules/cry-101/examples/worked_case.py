#!/usr/bin/env python3
"""Worked structural threat model for a sealed-export service."""

from __future__ import annotations

from security_requirements import (
    Asset,
    Assumption,
    AttackerCapability,
    AttackerModel,
    CompositionDependency,
    MaterialKind,
    MaterialProperty,
    MaterialRequirement,
    SecurityGoal,
    SecurityRequirement,
    ThreatModel,
    TrustBoundary,
    evaluate_model,
    render_evaluation,
)


def make_model() -> ThreatModel:
    return ThreatModel(
        name="sealed-export teaching model",
        assets=(
            Asset(
                "export-record",
                "one export record while it crosses an untrusted queue",
                frozenset(
                    {
                        SecurityGoal.CONFIDENTIALITY,
                        SecurityGoal.INTEGRITY,
                        SecurityGoal.FRESHNESS,
                    }
                ),
            ),
        ),
        attacker=AttackerModel(
            capabilities=frozenset(
                {
                    AttackerCapability.OBSERVE_NETWORK,
                    AttackerCapability.ALTER_NETWORK,
                    AttackerCapability.REPLAY,
                }
            ),
            resource_bound=(
                "probabilistic polynomial-time network attacker with at most one million "
                "chosen-message interactions during one key epoch"
            ),
            exclusions=(
                "sender and receiver endpoint compromise is out of scope",
                "denial of service is recorded as an unsatisfied availability goal",
            ),
        ),
        assumptions=(
            Assumption(
                "approved-aead",
                "the selected standard AEAD and parameter set meet the deployment policy",
                "cryptography owner",
                "standard withdrawal, parameter deprecation, or implementation validation failure",
            ),
            Assumption(
                "state-persists",
                "the sender preserves its per-key nonce counter across ordinary restart",
                "service owner",
                "counter rollback, duplicate allocation, or loss of durable state",
            ),
        ),
        boundaries=(
            TrustBoundary(
                "queue-crossing",
                "trusted sender process",
                "untrusted queue and transport",
                "ciphertext, public nonce, authenticated record identifier, and version",
                "receiver authenticates the complete encoded record before releasing plaintext",
                "reject the record without releasing plaintext and emit a bounded audit event",
            ),
        ),
        materials=(
            MaterialRequirement(
                "record-key",
                MaterialKind.SECRET_KEY,
                "protect export records during one key epoch",
                frozenset(
                    {MaterialProperty.SECRET, MaterialProperty.UNPREDICTABLE}
                ),
                "approved platform key service",
                "one service instance and declared key epoch",
                "stop encryption, revoke the epoch, and re-establish keys after review",
            ),
            MaterialRequirement(
                "record-nonce",
                MaterialKind.NONCE,
                "supply the AEAD nonce input",
                frozenset(
                    {MaterialProperty.PUBLIC, MaterialProperty.UNIQUE_WITHIN_SCOPE}
                ),
                "durable monotonic allocation under the sender's key epoch",
                "unique for every encryption under one record key",
                "stop the affected key epoch before another encryption if reuse is suspected",
            ),
            MaterialRequirement(
                "key-randomness",
                MaterialKind.RANDOMNESS,
                "seed approved secret-key generation",
                frozenset({MaterialProperty.UNPREDICTABLE}),
                "approved platform random-bit generator with documented initialization",
                "fresh generation event for each record key",
                "fail closed and do not create a key when generator health fails",
            ),
        ),
        requirements=(
            SecurityRequirement(
                "hide-record",
                "export-record",
                SecurityGoal.CONFIDENTIALITY,
                AttackerCapability.OBSERVE_NETWORK,
                "queue observations must not reveal record plaintext beyond declared metadata",
                "plaintext, secret key, or protected field is exposed to the queue observer",
                "stop the affected export path, contain exposure, and rotate the key epoch",
                "protocol review, approved-library tests, and deployment key-access evidence",
                ("approved-aead",),
                ("queue-crossing",),
            ),
            SecurityRequirement(
                "detect-change",
                "export-record",
                SecurityGoal.INTEGRITY,
                AttackerCapability.ALTER_NETWORK,
                "altered ciphertext or authenticated metadata must be rejected before release",
                "any changed protected record is accepted",
                "reject without plaintext release and emit a bounded audit event",
                "negative tests mutate every encoded field and verify one indistinguishable rejection path",
                ("approved-aead",),
                ("queue-crossing",),
            ),
            SecurityRequirement(
                "reject-replay",
                "export-record",
                SecurityGoal.FRESHNESS,
                AttackerCapability.REPLAY,
                "a previously accepted record identifier must not be accepted in the same receiver epoch",
                "the receiver releases a duplicate record",
                "reject the duplicate and preserve receiver replay state for investigation",
                "state-machine tests cover first delivery, duplicate delivery, restart, and rollback alarm",
                ("state-persists",),
                ("queue-crossing",),
            ),
        ),
        dependencies=(
            CompositionDependency(
                "aead-to-export",
                "approved AEAD library",
                "sealed-export protocol",
                "authentication covers canonical record identifier and version, and nonce uniqueness holds per key",
                ("approved-aead", "state-persists"),
                "stop the key epoch when either dependency is false; do not claim confidentiality or integrity",
            ),
        ),
    )


def main() -> int:
    model = make_model()
    evaluation = evaluate_model(model)
    print(render_evaluation(model, evaluation))
    return 0 if evaluation.structurally_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
