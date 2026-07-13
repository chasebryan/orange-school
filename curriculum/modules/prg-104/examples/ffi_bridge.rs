//! Safe Rust and a narrow safe wrapper around the C bounded-sum function.

use std::ffi::c_int;

pub const MAX_ITEMS: usize = 8;

const C_OK: c_int = 0;
const C_NULL_POINTER: c_int = 1;
const C_LENGTH_ERROR: c_int = 2;

/*
 * Declaration assumptions:
 * - this declaration is linked to bounded_sum_i32 from bounded_sum.c;
 * - Rust i32 and i64 match C int32_t and int64_t;
 * - Rust usize matches C size_t for the common compilation target;
 * - c_int matches the C int used for the status return;
 * - both objects use the same target ABI.
 */
unsafe extern "C" {
    fn bounded_sum_i32(values: *const i32, len: usize, out_sum: *mut i64) -> c_int;
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RustSumError {
    TooManyItems { actual: usize, maximum: usize },
    ArithmeticOverflow,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FfiSumError {
    TooManyItems { actual: usize, maximum: usize },
    CRejectedNullPointer,
    CRejectedLength,
    UnexpectedCStatus(c_int),
}

pub fn rust_bounded_sum(values: &[i32]) -> Result<i64, RustSumError> {
    if values.len() > MAX_ITEMS {
        return Err(RustSumError::TooManyItems {
            actual: values.len(),
            maximum: MAX_ITEMS,
        });
    }

    let mut sum = 0_i64;
    for &value in values {
        sum = sum
            .checked_add(i64::from(value))
            .ok_or(RustSumError::ArithmeticOverflow)?;
    }
    Ok(sum)
}

pub fn c_bounded_sum(values: &[i32]) -> Result<i64, FfiSumError> {
    if values.len() > MAX_ITEMS {
        return Err(FfiSumError::TooManyItems {
            actual: values.len(),
            maximum: MAX_ITEMS,
        });
    }

    let values_pointer = if values.is_empty() {
        std::ptr::null()
    } else {
        values.as_ptr()
    };
    let mut output = 0_i64;

    /*
     * SAFETY assumptions for this call:
     * 1. The external declaration and linked C definition have identical ABI,
     *    parameter, return, and status-code contracts.
     * 2. A nonempty Rust slice supplies a non-null, aligned pointer readable
     *    for exactly values.len() initialized i32 elements.
     * 3. The empty case passes NULL with length zero, which the C contract
     *    explicitly accepts without dereferencing.
     * 4. &mut output is non-null, aligned, initialized, and uniquely writable
     *    as one i64 for the duration of the call.
     * 5. The C function reads no element outside length, writes only output on
     *    success, does not mutate values, and retains neither pointer.
     * 6. The C function does not call back into Rust, unwind, access shared
     *    mutable global state, or outlive this synchronous call.
     * 7. MAX_ITEMS and the numeric status values match bounded_sum.h.
     */
    let status =
        unsafe { bounded_sum_i32(values_pointer, values.len(), &mut output as *mut i64) };

    match status {
        C_OK => Ok(output),
        C_NULL_POINTER => Err(FfiSumError::CRejectedNullPointer),
        C_LENGTH_ERROR => Err(FfiSumError::CRejectedLength),
        other => Err(FfiSumError::UnexpectedCStatus(other)),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rust_normal_and_empty() {
        assert_eq!(rust_bounded_sum(&[4, -1, 7]), Ok(10));
        assert_eq!(rust_bounded_sum(&[]), Ok(0));
    }

    #[test]
    fn rust_accepts_exact_limit() {
        let values = [i32::MAX; MAX_ITEMS];
        let expected = i64::from(i32::MAX) * MAX_ITEMS as i64;
        assert_eq!(rust_bounded_sum(&values), Ok(expected));
    }

    #[test]
    fn rust_rejects_over_limit() {
        let values = [0_i32; MAX_ITEMS + 1];
        assert_eq!(
            rust_bounded_sum(&values),
            Err(RustSumError::TooManyItems {
                actual: MAX_ITEMS + 1,
                maximum: MAX_ITEMS,
            })
        );
    }

    #[test]
    fn ffi_normal_and_empty() {
        assert_eq!(c_bounded_sum(&[4, -1, 7]), Ok(10));
        assert_eq!(c_bounded_sum(&[]), Ok(0));
    }

    #[test]
    fn ffi_accepts_exact_limit() {
        let values = [i32::MIN; MAX_ITEMS];
        let expected = i64::from(i32::MIN) * MAX_ITEMS as i64;
        assert_eq!(c_bounded_sum(&values), Ok(expected));
    }

    #[test]
    fn ffi_rejects_over_limit_before_calling_c() {
        let values = [0_i32; MAX_ITEMS + 1];
        assert_eq!(
            c_bounded_sum(&values),
            Err(FfiSumError::TooManyItems {
                actual: MAX_ITEMS + 1,
                maximum: MAX_ITEMS,
            })
        );
    }
}
