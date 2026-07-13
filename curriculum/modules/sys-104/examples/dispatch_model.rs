#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Variant {
    Baseline,
    Simd128,
}

fn select_variant(simd_body_built: bool, runtime_feature_observed: bool) -> Variant {
    if simd_body_built && runtime_feature_observed {
        Variant::Simd128
    } else {
        Variant::Baseline
    }
}

fn add_baseline(left: &[u32], right: &[u32]) -> Result<Vec<u32>, &'static str> {
    if left.len() != right.len() {
        return Err("input lengths differ");
    }
    if left.len() > 32 {
        return Err("input exceeds 32 lanes");
    }
    Ok(left
        .iter()
        .zip(right)
        .map(|(one, two)| one.wrapping_add(*two))
        .collect())
}

fn add_four_lane_semantic_model(
    left: [u32; 4],
    right: [u32; 4],
) -> [u32; 4] {
    // This models four independent wrapping lanes. It neither promises SIMD
    // code generation nor requires a CPU feature, so every host can run it.
    std::array::from_fn(|index| left[index].wrapping_add(right[index]))
}

fn compile_time_tuple() -> (&'static str, &'static str, u32) {
    let endian = if cfg!(target_endian = "little") {
        "little"
    } else if cfg!(target_endian = "big") {
        "big"
    } else {
        "unreported"
    };
    (std::env::consts::ARCH, endian, usize::BITS)
}

#[test]
fn dispatch_requires_built_and_observed_capability() {
    assert_eq!(select_variant(false, false), Variant::Baseline);
    assert_eq!(select_variant(false, true), Variant::Baseline);
    assert_eq!(select_variant(true, false), Variant::Baseline);
    assert_eq!(select_variant(true, true), Variant::Simd128);
}

#[test]
fn baseline_covers_positive_endpoints_and_invalid_lengths() {
    assert_eq!(
        add_baseline(&[0, u32::MAX, 10], &[0, 1, 20]),
        Ok(vec![0, 0, 30])
    );
    assert_eq!(add_baseline(&[], &[]), Ok(vec![]));
    assert_eq!(add_baseline(&[1], &[]), Err("input lengths differ"));
    assert_eq!(
        add_baseline(&[0; 33], &[0; 33]),
        Err("input exceeds 32 lanes")
    );
}

#[test]
fn four_lane_model_has_independent_wrapping_semantics() {
    assert_eq!(
        add_four_lane_semantic_model(
            [0, 1, u32::MAX, u32::MAX],
            [0, 2, 0, 1]
        ),
        [0, 3, u32::MAX, 0]
    );
}

#[test]
fn compile_time_metadata_is_observed_without_inference() {
    let (architecture, endian, pointer_width) = compile_time_tuple();
    assert!(!architecture.is_empty());
    assert!(matches!(endian, "little" | "big"));
    assert!(matches!(pointer_width, 16 | 32 | 64 | 128));
}
