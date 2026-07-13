use std::mem::{align_of, offset_of, size_of};
use std::ptr;

const MAX_PAYLOAD: usize = 16;
const STATUS_OK: i32 = 0;
const STATUS_NULL: i32 = 1;
const STATUS_LENGTH: i32 = 2;
const STATUS_KIND: i32 = 3;

#[repr(C)]
#[derive(Clone, Copy, Debug)]
struct Request {
    request_id: u32,
    kind: u16,
    payload_len: u16,
}

#[repr(C)]
#[derive(Clone, Copy, Debug)]
struct LayoutDemo {
    tag: u8,
    value: u32,
    code: u16,
}

#[derive(Debug, Eq, PartialEq)]
enum ChecksumError {
    PayloadTooLong,
    InvalidKind,
    ForeignNull,
    ForeignLength,
    ForeignKind,
    UnknownStatus(i32),
}

unsafe extern "C" {
    fn sys103_checksum(
        request: *const Request,
        payload: *const u8,
        payload_len: u32,
        out_checksum: *mut u32,
    ) -> i32;

    fn sys103_request_size() -> u32;
    fn sys103_request_align() -> u32;
    fn sys103_request_request_id_offset() -> u32;
    fn sys103_request_kind_offset() -> u32;
    fn sys103_request_payload_len_offset() -> u32;

    fn sys103_demo_size() -> u32;
    fn sys103_demo_align() -> u32;
    fn sys103_demo_tag_offset() -> u32;
    fn sys103_demo_value_offset() -> u32;
    fn sys103_demo_code_offset() -> u32;
}

fn checksum(request_id: u32, kind: u16, payload: &[u8]) -> Result<u32, ChecksumError> {
    if kind > 3 {
        return Err(ChecksumError::InvalidKind);
    }
    if payload.len() > MAX_PAYLOAD {
        return Err(ChecksumError::PayloadTooLong);
    }
    let payload_len = u16::try_from(payload.len())
        .map_err(|_| ChecksumError::PayloadTooLong)?;
    let request = Request {
        request_id,
        kind,
        payload_len,
    };
    let payload_pointer = if payload.is_empty() {
        ptr::null()
    } else {
        payload.as_ptr()
    };
    let mut output = 0_u32;

    // SAFETY:
    // 1. The build links declarations here to the inspected C17 archive or
    //    the two exact C objects produced in the same temporary workspace.
    // 2. Both sides select this target's C ABI and agree on every fixed-width
    //    parameter and return type; runtime probes compare repr(C) layout.
    // 3. `request` is live, aligned, initialized, and readable for the call.
    // 4. A nonempty slice supplies exactly `payload.len()` readable bytes;
    //    the C contract explicitly accepts null only for an empty payload.
    // 5. `output` is live, aligned, uniquely writable, and disjoint from both
    //    inputs; C writes it only after successful validation.
    // 6. The wrapper validates kind and the 16-byte bound before conversion.
    // 7. Shared slice access prevents safe Rust mutation during this call.
    // 8. C performs a synchronous call, retains no pointer, and invokes no
    //    callback, so no pointer escapes and no hidden Rust alias is created.
    // 9. C does not unwind; this wrapper uses the non-unwinding `"C"` ABI and
    //    lets no Rust panic originate inside a callback across the boundary.
    // 10. Header constants, status values, symbol identity, and target layout
    //     are tied to this build and must be revalidated after either changes.
    let status = unsafe {
        sys103_checksum(
            &request,
            payload_pointer,
            u32::from(payload_len),
            &mut output,
        )
    };

    match status {
        STATUS_OK => Ok(output),
        STATUS_NULL => Err(ChecksumError::ForeignNull),
        STATUS_LENGTH => Err(ChecksumError::ForeignLength),
        STATUS_KIND => Err(ChecksumError::ForeignKind),
        other => Err(ChecksumError::UnknownStatus(other)),
    }
}

fn rust_checksum(request_id: u32, kind: u16, payload: &[u8]) -> u32 {
    let mut state = request_id
        .wrapping_add(u32::from(kind))
        .wrapping_add(u32::try_from(payload.len()).expect("bounded test payload"));
    for byte in payload {
        state = state.wrapping_mul(33).wrapping_add(u32::from(*byte));
    }
    state
}

#[test]
fn normal_empty_and_maximum_endpoints_match() {
    let normal = [2_u8, 4, 8];
    assert_eq!(checksum(100, 2, &normal), Ok(3_775_703));
    assert_eq!(checksum(7, 0, &[]), Ok(7));

    let maximum = [u8::MAX; MAX_PAYLOAD];
    assert_eq!(
        checksum(u32::MAX, 3, &maximum),
        Ok(rust_checksum(u32::MAX, 3, &maximum))
    );
}

#[test]
fn safe_wrapper_rejects_before_foreign_call() {
    assert_eq!(checksum(1, 4, &[1]), Err(ChecksumError::InvalidKind));
    assert_eq!(
        checksum(1, 1, &[0; MAX_PAYLOAD + 1]),
        Err(ChecksumError::PayloadTooLong)
    );
}

#[test]
fn raw_invalid_calls_fail_without_output_change() {
    let payload = [9_u8];
    let one = Request {
        request_id: 1,
        kind: 1,
        payload_len: 1,
    };
    let wrong_length = Request {
        payload_len: 2,
        ..one
    };
    let wrong_kind = Request { kind: 4, ..one };
    let mut output = 0xdecafbad_u32;

    // SAFETY: these calls deliberately violate only null/value preconditions
    // that C checks before any dereference. All non-null pointers are valid.
    unsafe {
        assert_eq!(
            sys103_checksum(ptr::null(), payload.as_ptr(), 1, &mut output),
            STATUS_NULL
        );
        assert_eq!(
            sys103_checksum(&one, payload.as_ptr(), 17, &mut output),
            STATUS_LENGTH
        );
        assert_eq!(
            sys103_checksum(&wrong_length, payload.as_ptr(), 1, &mut output),
            STATUS_LENGTH
        );
        assert_eq!(
            sys103_checksum(&wrong_kind, payload.as_ptr(), 1, &mut output),
            STATUS_KIND
        );
        assert_eq!(
            sys103_checksum(&one, ptr::null(), 1, &mut output),
            STATUS_NULL
        );
    }
    assert_eq!(output, 0xdecafbad_u32);
}

#[test]
fn target_layout_matches_c_probe() {
    // SAFETY: these C functions take no input, return fixed-width values, and
    // are linked from the inspected build artifacts.
    unsafe {
        assert_eq!(u32::try_from(size_of::<Request>()).unwrap(), sys103_request_size());
        assert_eq!(u32::try_from(align_of::<Request>()).unwrap(), sys103_request_align());
        assert_eq!(
            u32::try_from(offset_of!(Request, request_id)).unwrap(),
            sys103_request_request_id_offset()
        );
        assert_eq!(
            u32::try_from(offset_of!(Request, kind)).unwrap(),
            sys103_request_kind_offset()
        );
        assert_eq!(
            u32::try_from(offset_of!(Request, payload_len)).unwrap(),
            sys103_request_payload_len_offset()
        );

        assert_eq!(u32::try_from(size_of::<LayoutDemo>()).unwrap(), sys103_demo_size());
        assert_eq!(u32::try_from(align_of::<LayoutDemo>()).unwrap(), sys103_demo_align());
        assert_eq!(
            u32::try_from(offset_of!(LayoutDemo, tag)).unwrap(),
            sys103_demo_tag_offset()
        );
        assert_eq!(
            u32::try_from(offset_of!(LayoutDemo, value)).unwrap(),
            sys103_demo_value_offset()
        );
        assert_eq!(
            u32::try_from(offset_of!(LayoutDemo, code)).unwrap(),
            sys103_demo_code_offset()
        );
    }
}
