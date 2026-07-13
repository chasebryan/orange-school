# Assessment: terminal evidence record

## Instructions

Complete the task in a fresh Bash session without copying the lab command
sequence. You may consult the lesson and standard command documentation. Use
only a new directory produced by <code>mktemp -d</code>. Do not use
administrator access, network commands, wildcards, permission changes, or
deletion commands.

Submit the temporary workspace path, your exact command transcript, and the
contents of both <code>incoming</code> and <code>evidence</code>. If a platform
prevents use of Bash or <code>mktemp</code>, stop and report that environment
blocker instead of substituting unrecorded tools.

This assessment covers:

- **CMP-101-01:** Navigate and inspect a workspace without relying on a
  graphical file browser.
- **CMP-101-02:** Run a command, separate standard output from diagnostics, and
  interpret its exit status.
- **CMP-101-03:** Write a reproducible command record with working directory,
  inputs, command, and observed result.

## Knowledge check

1. Explain the difference between an absolute and relative path. If
   <code>pwd</code> prints <code>/tmp/example</code>, give both kinds of path
   for <code>incoming/items.txt</code>.
2. Name the three result channels of a command and explain the usual meaning of
   exit status 0 versus a nonzero status.
3. Find and repair the evidence error:

   ~~~sh
   cat -- missing.txt > out.txt 2> err.txt
   printf 'command finished\n'
   result=$?
   ~~~

4. List the minimum fields needed in a reproducible command record, and explain
   why expected output cannot replace observed output.

## Independent task

Create a fresh temporary workspace. Your exact path will differ from the lab.

1. **Workspace navigation — CMP-101-01.** Inside the workspace, create
   directories named <code>incoming</code> and <code>evidence</code>. Create
   <code>incoming/items.txt</code> with exactly these three lines, in order:
   <code>cedar</code>, <code>maple</code>, and <code>orange</code>. From at
   least two different working directories, use terminal commands to record the
   current directory and inspect the tree. Read <code>items.txt</code> once
   with a relative path and once with an absolute path. Record which was which.
2. **Result channels — CMP-101-02.** From the workspace root, run
   <code>wc -l -- incoming/items.txt</code>. Preserve stdout and stderr in
   separate files under <code>evidence</code> and capture the exit status
   immediately. Then run the safe, intentionally failing read
   <code>cat -- incoming/not-present.txt</code>, again preserving stdout,
   stderr, and immediate exit status separately. Interpret both statuses using
   the corresponding observations; do not assume a particular nonzero value.
3. **Reproducible record — CMP-101-03.** Create
   <code>evidence/run-record.txt</code>. Include the Bash version, absolute
   working directory, exact input path and contents, every assessed command,
   observed stdout, observed stderr including empty streams, observed exit
   statuses, a narrow conclusion for each command, and at least two limits.
   Include the navigation commands needed to explain where each relative path
   was resolved.
4. Verify that all files you created are inside the fresh workspace. Keep the
   workspace for review; no cleanup command is part of this assessment.

## Completion criteria

The [rubric](rubric.md) requires at least 80/100 and every critical criterion.
Passing evidence must show:

- accurate terminal-only navigation and inspection for **CMP-101-01**, with all
  writes contained in the fresh temporary workspace;
- genuinely separate stdout and stderr files plus immediately captured,
  correctly interpreted statuses for **CMP-101-02**;
- a complete, replayable observation record for **CMP-101-03**; and
- correct knowledge-check answers and no use of elevated, destructive, network,
  permission-changing, or wildcard commands.

An undocumented successful result is not reproducible evidence.
