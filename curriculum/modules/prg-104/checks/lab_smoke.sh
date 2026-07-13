#!/usr/bin/env bash
set -euo pipefail

source_dir="$(cd -- "$(dirname -- "$0")/../examples" && pwd)"
workspace="$(mktemp -d)"

cleanup() {
    rm -rf -- "$workspace"
}
trap cleanup EXIT

fail() {
    printf 'prg-104 lab smoke: FAIL: %s\n' "$1" >&2
    exit 1
}

command -v cc >/dev/null 2>&1 || fail "cc is unavailable"
command -v rustc >/dev/null 2>&1 || fail "rustc is unavailable"

# The repository host checker deliberately replaces HOME. Resolve any
# user-local cc wrapper against the home inferred from its installed path while
# keeping all compiler output in the fresh workspace.
cc_command="$(command -v cc)"
cc_tool_home="$(dirname -- "$(dirname -- "$(dirname -- "$cc_command")")")"
run_cc() {
    HOME="$cc_tool_home" "$cc_command" "$@"
}

# Point the rustup proxy at the already-installed, read-only toolchain store
# inferred from the proxy path; do not let rustup attempt a network install.
set +u
current_rustup_home="$RUSTUP_HOME"
set -u
if [ -z "$current_rustup_home" ]; then
    rustc_proxy="$(command -v rustc)"
    tool_home="$(dirname -- "$(dirname -- "$(dirname -- "$rustc_proxy")")")"
    inferred_rustup_home="$tool_home/.rustup"
    [ -d "$inferred_rustup_home/toolchains" ] ||
        fail "installed rustup toolchain store is unavailable"
    export RUSTUP_HOME="$inferred_rustup_home"
fi

rust_version="$(rustc +1.96.1 --version)"
case "$rust_version" in
    "rustc 1.96.1 "*) ;;
    *) fail "expected rustc 1.96.1, observed $rust_version" ;;
esac

mkdir -- "$workspace/src" "$workspace/tmp"
cp -- \
    "$source_dir/bounded_sum.h" \
    "$source_dir/bounded_sum.c" \
    "$source_dir/c_harness.c" \
    "$source_dir/ffi_bridge.rs" \
    "$workspace/src/"

export TMPDIR="$workspace/tmp"
export LC_ALL=C

run_cc \
    -std=c17 \
    -Wall \
    -Wextra \
    -Wpedantic \
    -Werror \
    -I "$workspace/src" \
    -c "$workspace/src/bounded_sum.c" \
    -o "$workspace/bounded_sum.o"

run_cc \
    -std=c17 \
    -Wall \
    -Wextra \
    -Wpedantic \
    -Werror \
    -I "$workspace/src" \
    "$workspace/src/c_harness.c" \
    "$workspace/bounded_sum.o" \
    -o "$workspace/c_harness"

"$workspace/c_harness" >"$workspace/c.stdout" 2>"$workspace/c.stderr"
[ ! -s "$workspace/c.stderr" ] || fail "C harness wrote diagnostics"
[ "$(cat "$workspace/c.stdout")" = "c bounded_sum tests: PASS" ] ||
    fail "C harness output changed"

HOME="$cc_tool_home" rustc +1.96.1 \
    --edition=2024 \
    --test \
    -D warnings \
    -C "link-arg=$workspace/bounded_sum.o" \
    "$workspace/src/ffi_bridge.rs" \
    -o "$workspace/ffi_tests"

"$workspace/ffi_tests" --test-threads=1 \
    >"$workspace/rust.stdout" 2>"$workspace/rust.stderr"
[ ! -s "$workspace/rust.stderr" ] || fail "Rust tests wrote diagnostics"

printf 'prg-104 lab smoke: PASS\n'
