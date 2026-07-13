#!/usr/bin/env python3
"""A strict metadata and dispatch policy model; it emits no SIMD instructions."""

from __future__ import annotations

from dataclasses import dataclass


ALLOWED_ENDIAN = frozenset({"big", "little"})
ALLOWED_POINTER_WIDTHS = frozenset({16, 32, 64, 128})


def _text(value: object, label: str) -> str:
    if type(value) is not str or value.strip() != value or not value:
        raise TypeError(f"{label} must be a nonempty trimmed string")
    return value


def _features(value: object, label: str) -> frozenset[str]:
    if type(value) is not frozenset:
        raise TypeError(f"{label} must be a frozenset")
    for feature in value:
        _text(feature, f"{label} feature")
    return value


@dataclass(frozen=True, slots=True)
class ArtifactTuple:
    """The target facts attached to one exact artifact, not to a source tree."""

    target: str
    isa: str
    abi: str
    operating_system: str
    object_format: str
    endian: str
    pointer_width: int

    def __post_init__(self) -> None:
        for label, value in (
            ("target", self.target),
            ("isa", self.isa),
            ("abi", self.abi),
            ("operating_system", self.operating_system),
            ("object_format", self.object_format),
            ("endian", self.endian),
        ):
            _text(value, label)
        if self.endian not in ALLOWED_ENDIAN:
            raise ValueError("endian must be 'big' or 'little'")
        if type(self.pointer_width) is not int:
            raise TypeError("pointer_width must be an integer")
        if self.pointer_width not in ALLOWED_POINTER_WIDTHS:
            raise ValueError("pointer_width is outside the model")


@dataclass(frozen=True, slots=True)
class Variant:
    name: str
    lane_bits: int
    vector_bits: int
    required_features: frozenset[str]

    def __post_init__(self) -> None:
        _text(self.name, "variant name")
        if type(self.lane_bits) is not int:
            raise TypeError("lane_bits must be an integer")
        if self.lane_bits <= 0 or self.lane_bits % 8 != 0:
            raise ValueError("lane_bits must be a positive multiple of 8")
        if type(self.vector_bits) is not int:
            raise TypeError("vector_bits must be an integer")
        if self.vector_bits < self.lane_bits or self.vector_bits % self.lane_bits != 0:
            raise ValueError("vector_bits must be a positive multiple of lane_bits")
        _features(self.required_features, "required_features")

    @property
    def lane_count(self) -> int:
        return self.vector_bits // self.lane_bits


@dataclass(frozen=True, slots=True)
class BuildManifest:
    artifact: ArtifactTuple
    variants: tuple[Variant, ...]

    def __post_init__(self) -> None:
        if type(self.artifact) is not ArtifactTuple:
            raise TypeError("artifact must be an ArtifactTuple")
        if type(self.variants) is not tuple:
            raise TypeError("variants must be a tuple")
        if not self.variants:
            raise ValueError("variants must include a baseline")
        for variant in self.variants:
            if type(variant) is not Variant:
                raise TypeError("variants must contain only Variant values")
        baselines = [item for item in self.variants if not item.required_features]
        if len(baselines) != 1 or baselines[0].name != "baseline":
            raise ValueError("variants must contain exactly one feature-free baseline")
        names = [item.name for item in self.variants]
        if len(set(names)) != len(names):
            raise ValueError("variant names must be unique")


def select_variant(
    manifest: object,
    runtime_artifact: object,
    runtime_features: object,
) -> Variant:
    """Select the largest-vector eligible built variant, or the baseline."""

    if type(manifest) is not BuildManifest:
        raise TypeError("manifest must be a BuildManifest")
    if type(runtime_artifact) is not ArtifactTuple:
        raise TypeError("runtime_artifact must be an ArtifactTuple")
    features = _features(runtime_features, "runtime_features")
    if runtime_artifact != manifest.artifact:
        raise ValueError("runtime artifact tuple does not match the build manifest")
    eligible = [
        item
        for item in manifest.variants
        if item.required_features.issubset(features)
    ]
    return max(eligible, key=lambda item: item.vector_bits)


def add_u32_lanes(left: object, right: object, lane_count: object) -> tuple[int, ...]:
    """Model independent wrapping u32 lane semantics without native SIMD."""

    if type(left) is not tuple or type(right) is not tuple:
        raise TypeError("lane inputs must be tuples")
    if type(lane_count) is not int or lane_count <= 0:
        raise ValueError("lane_count must be a positive integer")
    if len(left) != lane_count or len(right) != lane_count:
        raise ValueError("lane input length must equal lane_count")
    maximum = (1 << 32) - 1
    output: list[int] = []
    for left_lane, right_lane in zip(left, right, strict=True):
        if type(left_lane) is not int or type(right_lane) is not int:
            raise TypeError("lanes must be integers")
        if not 0 <= left_lane <= maximum or not 0 <= right_lane <= maximum:
            raise ValueError("lanes must fit u32")
        output.append((left_lane + right_lane) & maximum)
    return tuple(output)
