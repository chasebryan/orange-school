#!/usr/bin/env bash
set -euo pipefail

workdir="$(mktemp -d)"
cleanup() {
  rm -rf -- "$workdir"
}
trap cleanup EXIT

cd -- "$workdir"
mkdir -- records
printf 'orange\nschool\n' > input.txt

wc -l -- input.txt > records/success.stdout 2> records/success.stderr
success_status=$?
printf '%s\n' "$success_status" > records/success.status

set +e
cat -- absent.txt > records/failure.stdout 2> records/failure.stderr
failure_status=$?
set -e
printf '%s\n' "$failure_status" > records/failure.status

test "$PWD" = "$workdir"
test "$(cat -- records/success.status)" = "0"
test "$(tr -d '[:space:]' < records/success.stdout)" = "2input.txt"
test ! -s records/success.stderr
test "$failure_status" -ne 0
test -s records/failure.stderr

printf 'Working directory: %s\n' "$workdir" > records/run-record.txt
printf 'Input: input.txt\n' >> records/run-record.txt
printf 'Command: wc -l -- input.txt\n' >> records/run-record.txt
printf 'Observed exit status: %s\n' "$success_status" >> records/run-record.txt
printf 'Limit: this check covers only this input and command.\n' >> records/run-record.txt
test -s records/run-record.txt
