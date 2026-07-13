//! One Rust owner for a bounded allocation created and destroyed by C.

use std::ffi::c_int;
use std::mem::ManuallyDrop;

pub const MAX_BYTES: usize = 32;

const C_OK: c_int = 0;
const C_NULL_POINTER: c_int = 1;
const C_LENGTH_ERROR: c_int = 2;
const C_STATE_ERROR: c_int = 3;
const C_ALLOCATION_ERROR: c_int = 4;

#[repr(C)]
struct RawBuffer {
    data: *mut u8,
    len: usize,
}

unsafe extern "C" {
    fn sys102_buffer_clone(source: *const u8, len: usize, out: *mut RawBuffer) -> c_int;
    fn sys102_buffer_sum(buffer: *const RawBuffer, out_sum: *mut u64) -> c_int;
    fn sys102_buffer_wipe(buffer: *mut RawBuffer) -> c_int;
    fn sys102_buffer_destroy(buffer: *mut RawBuffer) -> c_int;
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BufferError {
    TooLong { actual: usize, maximum: usize },
    CRejectedNullPointer,
    CRejectedLength,
    CRejectedState,
    CAllocationFailed,
    UnexpectedCStatus(c_int),
    CReturnedInvalidShape,
}

fn status_error(status: c_int) -> BufferError {
    match status {
        C_NULL_POINTER => BufferError::CRejectedNullPointer,
        C_LENGTH_ERROR => BufferError::CRejectedLength,
        C_STATE_ERROR => BufferError::CRejectedState,
        C_ALLOCATION_ERROR => BufferError::CAllocationFailed,
        other => BufferError::UnexpectedCStatus(other),
    }
}

fn raw_shape_is_valid(raw: &RawBuffer) -> bool {
    raw.len <= MAX_BYTES && ((raw.len == 0) == raw.data.is_null())
}

pub struct OwnedBuffer {
    raw: RawBuffer,
}

impl OwnedBuffer {
    pub fn new(source: &[u8]) -> Result<Self, BufferError> {
        if source.len() > MAX_BYTES {
            return Err(BufferError::TooLong {
                actual: source.len(),
                maximum: MAX_BYTES,
            });
        }
        let source_pointer = if source.is_empty() {
            std::ptr::null()
        } else {
            source.as_ptr()
        };
        let mut raw = RawBuffer {
            data: std::ptr::null_mut(),
            len: 0,
        };

        // SAFETY:
        // 1. The linked symbol is the reviewed C17 sys102_buffer_clone.
        // 2. RawBuffer has C layout; Rust u8/usize and C uint8_t/size_t agree
        //    for this recorded target, and c_int agrees with C int.
        // 3. source_pointer is null only for length zero; otherwise it is
        //    aligned and readable for source.len() initialized bytes through
        //    this synchronous call.
        // 4. &mut raw is initialized, non-null, aligned, uniquely writable,
        //    and disjoint from the borrowed source.
        // 5. The C function retains no source or output pointer, does not call
        //    back, and does not unwind into Rust.
        // 6. C writes one allocation owner only on success; constants and
        //    status values match owned_buffer.h.
        let status = unsafe {
            sys102_buffer_clone(source_pointer, source.len(), &mut raw as *mut RawBuffer)
        };
        if status != C_OK {
            return Err(status_error(status));
        }
        if !raw_shape_is_valid(&raw) {
            return Err(BufferError::CReturnedInvalidShape);
        }
        Ok(Self { raw })
    }

    pub fn len(&self) -> usize {
        self.raw.len
    }

    pub fn is_empty(&self) -> bool {
        self.raw.len == 0
    }

    pub fn as_slice(&self) -> &[u8] {
        if self.raw.len == 0 {
            return &[];
        }
        // SAFETY: the owner invariant comes from a successful C clone. The
        // allocation is live, contains raw.len initialized bytes, and is not
        // mutated for this shared borrow. The returned lifetime is tied to
        // &self. The nonempty branch avoids creating a slice from NULL.
        unsafe { std::slice::from_raw_parts(self.raw.data, self.raw.len) }
    }

    pub fn as_mut_slice(&mut self) -> &mut [u8] {
        if self.raw.len == 0 {
            return &mut [];
        }
        // SAFETY: &mut self gives exclusive access to the live allocation for
        // the returned borrow. The range is one allocation containing raw.len
        // initialized u8 values; it is aligned and non-null in this branch.
        unsafe { std::slice::from_raw_parts_mut(self.raw.data, self.raw.len) }
    }

    pub fn sum(&self) -> Result<u64, BufferError> {
        let mut output = 0_u64;
        // SAFETY: self maintains the live RawBuffer invariant. C reads but
        // does not mutate or retain that allocation, and &mut output is one
        // initialized, uniquely writable u64 for the synchronous call. ABI,
        // symbol, status, callback, and unwinding assumptions match new().
        let status = unsafe {
            sys102_buffer_sum(&self.raw as *const RawBuffer, &mut output as *mut u64)
        };
        if status == C_OK {
            Ok(output)
        } else {
            Err(status_error(status))
        }
    }

    pub fn wipe(&mut self) -> Result<(), BufferError> {
        // SAFETY: &mut self excludes Rust aliases. The RawBuffer still owns
        // exactly the live C allocation returned by clone. C writes within
        // that extent, retains nothing, and does not deallocate it.
        let status = unsafe { sys102_buffer_wipe(&mut self.raw as *mut RawBuffer) };
        if status == C_OK {
            Ok(())
        } else {
            Err(status_error(status))
        }
    }

    pub fn destroy(self) -> Result<(), BufferError> {
        // ManuallyDrop prevents the ordinary Drop path from issuing a second
        // foreign destroy after this explicit attempt. On a foreign error the
        // consumed owner is deliberately quarantined and may leak: the caller
        // gets the error, but cannot safely assume whether C partially changed
        // the allocation. A production policy may instead choose fail-stop.
        let mut owner = ManuallyDrop::new(self);
        // SAFETY: owner is consumed, so no safe client can retain a borrow of
        // the allocation. raw is the original C allocation owner and has not
        // been offset or freed. C wipes, frees, and resets it synchronously on
        // success. ManuallyDrop prevents a second call for either result.
        let status = unsafe { sys102_buffer_destroy(&mut owner.raw as *mut RawBuffer) };
        if status == C_OK {
            Ok(())
        } else {
            Err(status_error(status))
        }
    }
}

impl Drop for OwnedBuffer {
    fn drop(&mut self) {
        // SAFETY: every constructor establishes the one-owner RawBuffer
        // invariant; safe methods never offset, replace, or expose the raw
        // pointer. Drop has exclusive access and calls C exactly once for the
        // current state. The C function wipes, frees, and resets on success.
        let status = unsafe { sys102_buffer_destroy(&mut self.raw as *mut RawBuffer) };
        if status != C_OK {
            std::process::abort();
        }
    }
}

pub fn rust_volatile_wipe(bytes: &mut [u8]) {
    for byte in bytes {
        // SAFETY: each pointer comes from a distinct iteration of the exclusive
        // slice borrow and is live, aligned, and writable for one u8.
        unsafe { std::ptr::write_volatile(byte as *mut u8, 0) };
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn clone_move_borrow_mutate_and_wipe() {
        let source = [1_u8, 2, 3, 4];
        let original = source;
        let first_owner = OwnedBuffer::new(&source).expect("clone");
        let mut moved_owner = first_owner;

        assert_eq!(moved_owner.as_slice(), &[1, 2, 3, 4]);
        assert_eq!(moved_owner.sum(), Ok(10));
        moved_owner.as_mut_slice()[1] = 9;
        assert_eq!(moved_owner.as_slice(), &[1, 9, 3, 4]);
        assert_eq!(source, original, "owned copy changed its source");
        assert_eq!(moved_owner.sum(), Ok(17));

        moved_owner.wipe().expect("wipe");
        assert_eq!(moved_owner.as_slice(), &[0, 0, 0, 0]);
        assert_eq!(source, original, "wipe erased a separate source copy");
        moved_owner.destroy().expect("destroy");
    }

    #[test]
    fn empty_boundary_is_valid() {
        let owner = OwnedBuffer::new(&[]).expect("empty owner");
        assert!(owner.is_empty());
        assert_eq!(owner.len(), 0);
        assert_eq!(owner.as_slice(), &[]);
        assert_eq!(owner.sum(), Ok(0));
    }

    #[test]
    fn exact_maximum_is_valid() {
        let source = [u8::MAX; MAX_BYTES];
        let owner = OwnedBuffer::new(&source).expect("maximum owner");
        assert_eq!(owner.len(), MAX_BYTES);
        assert_eq!(owner.sum(), Ok(32 * u64::from(u8::MAX)));
    }

    #[test]
    fn over_maximum_is_rejected_before_ffi() {
        let source = [0_u8; MAX_BYTES + 1];
        assert!(matches!(
            OwnedBuffer::new(&source),
            Err(BufferError::TooLong {
                actual: 33,
                maximum: 32
            })
        ));
    }

    #[test]
    fn rust_volatile_wipe_covers_empty_and_nonempty_slices() {
        let mut empty: [u8; 0] = [];
        rust_volatile_wipe(&mut empty);
        let mut bytes = [9_u8, 8, 7];
        rust_volatile_wipe(&mut bytes);
        assert_eq!(bytes, [0, 0, 0]);
    }
}
