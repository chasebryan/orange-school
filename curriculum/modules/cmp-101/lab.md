# Lab: a bounded command record

## Goal

Create and inspect a temporary workspace, observe one successful and one
intentionally failing command, and preserve their result channels in a
reproducible record.

## Setup

Open a Bash terminal. Type each line separately. Do not type a displayed prompt
character.

Create a fresh workspace and verify where you are:

~~~sh
workdir="$(mktemp -d)"
printf 'Temporary workspace: %s\n' "$workdir"
cd -- "$workdir"
pwd
~~~

The path printed by <code>pwd</code> must match the temporary path. If it does
not, stop and ask for help. All writes in this lab must stay inside that path.
Do not use <code>sudo</code>, a network command, a wildcard, a permission
change, or a deletion command.

## Tasks

1. **Create and inspect a small tree.**

   ~~~sh
   mkdir -- records
   printf 'orange\nschool\n' > input.txt
   pwd
   ls -la
   ls -la -- records
   cat -- input.txt
   ~~~

   Before each writing command, identify its destination:
   <code>records</code> or <code>input.txt</code> inside the current temporary
   directory.

2. **Use relative and absolute paths.**

   ~~~sh
   cd -- records
   pwd
   ls -la -- ..
   cat -- ../input.txt
   cat -- "$workdir/input.txt"
   cd -- ..
   pwd
   ~~~

   The two <code>cat</code> commands name the same file from different starting
   points. Confirm that the final <code>pwd</code> again matches
   <code>$workdir</code>.

3. **Separate result channels and capture status immediately.**

   ~~~sh
   wc -l -- input.txt > records/success.stdout 2> records/success.stderr
   success_status=$?
   printf '%s\n' "$success_status" > records/success.status

   cat -- absent.txt > records/failure.stdout 2> records/failure.stderr
   failure_status=$?
   printf '%s\n' "$failure_status" > records/failure.status
   ~~~

   The missing file is intentional and the command only tries to read it.
   Inspect all six result files:

   ~~~sh
   cat -- records/success.stdout
   cat -- records/success.stderr
   cat -- records/success.status
   cat -- records/failure.stdout
   cat -- records/failure.stderr
   cat -- records/failure.status
   ~~~

4. **Write a reproducible record.** These commands create the record one line
   at a time and then append the preserved observations.

   ~~~sh
   printf 'Environment: ' > records/run-record.txt
   bash --version >> records/run-record.txt
   printf 'Working directory: %s\n' "$workdir" >> records/run-record.txt
   printf 'Input: input.txt has exact lines orange and school\n' >> records/run-record.txt
   printf 'Command: wc -l -- input.txt\n' >> records/run-record.txt
   printf 'Observed stdout:\n' >> records/run-record.txt
   cat -- records/success.stdout >> records/run-record.txt
   printf 'Observed stderr: <empty>\n' >> records/run-record.txt
   printf 'Observed exit status: %s\n' "$success_status" >> records/run-record.txt
   printf 'Conclusion: this command counted this input on this run.\n' >> records/run-record.txt
   printf 'Limit: this record does not test other files or tools.\n' >> records/run-record.txt
   cat -- records/run-record.txt
   ~~~

   If <code>success.stderr</code> was not empty, replace
   <code>&lt;empty&gt;</code> with the exact observed text and investigate
   before claiming success.

## Verification

Run each check, capture its status immediately, and interpret 0 as “this check
passed”:

~~~sh
test "$PWD" = "$workdir"
workspace_check=$?
printf 'workspace check: %s\n' "$workspace_check"

test -s records/success.stdout
success_output_check=$?
printf 'success stdout present: %s\n' "$success_output_check"

test ! -s records/success.stderr
success_diagnostic_check=$?
printf 'success stderr empty: %s\n' "$success_diagnostic_check"

test -s records/failure.stderr
failure_diagnostic_check=$?
printf 'failure stderr present: %s\n' "$failure_diagnostic_check"

test -s records/run-record.txt
record_check=$?
printf 'record present: %s\n' "$record_check"
~~~

Finally, inspect <code>success.status</code> and
<code>failure.status</code>. The first must contain 0 and the second must
contain an observed nonzero integer. If a check fails, inspect the named file,
correct only the command that produced it, and append a correction note to the
record.

## Reflection

Add three lines to your record:

- Which path was relative, and which was absolute?
- Why did the intentional failure produce useful evidence rather than merely
  “not work”?
- What would another person still need in order to reproduce this run on a
  different machine?
