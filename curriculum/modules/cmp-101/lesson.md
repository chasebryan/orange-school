# Terminal, files, and repeatable commands

A terminal is a text interface to a shell. The shell reads commands, asks the
operating system to run them, and reports results. This module uses Bash and
starts with the details that graphical file browsers often hide: exact paths,
separate result channels, and exit status.

## Learning objectives

- **CMP-101-01:** Navigate and inspect a workspace without relying on a
  graphical file browser.
- **CMP-101-02:** Run a command, separate standard output from diagnostics, and
  interpret its exit status.
- **CMP-101-03:** Write a reproducible command record with working directory,
  inputs, command, and observed result.

## Prerequisites

Pass <code>ori-001</code>. No prior terminal or programming experience is
assumed. Use a course-provided Bash terminal. If this command does not print a
Bash version, stop and ask for environment help:

~~~sh
bash --version
~~~

The examples use a fresh temporary directory and never require administrator
access, network access, deletion, or changes to file permissions.

## Lesson

**Read the prompt before typing.** A prompt often ends in <code>$</code>. It
shows that the shell is ready; the dollar sign is not part of the command. Type
one command, press Enter, and read the result before continuing.

**Files live at paths.** A directory contains named entries such as files and
other directories.

- An **absolute path** starts at the filesystem root, for example
  <code>/tmp/example/input.txt</code>.
- A **relative path** starts at the current working directory, for example
  <code>records/result.txt</code>.
- <code>.</code> means the current directory and <code>..</code> means its
  parent.
- Spaces and special characters can change how a shell reads text. Put paths
  from variables in double quotes, as in <code>"$workdir"</code>.

These bounded commands are enough to begin:

| Command | Purpose | Change to disk? |
| --- | --- | --- |
| <code>pwd</code> | Print the absolute current working directory. | No |
| <code>ls -la</code> | List directory entries, including hidden names. | No |
| <code>cd -- PATH</code> | Change the shell's current directory. | No file change |
| <code>cat -- FILE</code> | Print a file's contents. | No |
| <code>mkdir -- NAME</code> | Create one directory at the named path. | Yes |
| <code>printf 'text\n' &gt; FILE</code> | Write exact text to a file. | Yes |
| <code>wc -l -- FILE</code> | Count lines in a file. | No |

The <code>--</code> tells these utilities that later text is a path rather than
an option. Before a command that writes, say the destination path aloud and
confirm that it is inside your temporary workspace.

**A command has three result channels.**

1. **Standard output (stdout, channel 1)** carries the requested result.
2. **Standard error (stderr, channel 2)** carries diagnostics.
3. **Exit status** is an integer: 0 conventionally means success; nonzero means
   the command reported failure. The exact nonzero value is command-specific.

The terminal normally displays stdout and stderr together. Redirection can
preserve them separately:

~~~sh
wc -l -- input.txt > success.stdout 2> success.stderr
status=$?
~~~

<code>&gt;</code> sends stdout to one file and <code>2&gt;</code> sends stderr
to another. The shell variable <code>$?</code> contains the most recent
command's exit status. Capture it immediately: even <code>printf</code> runs a
new command and replaces it.

A nonzero exit status can be useful evidence when failure is intentional. It is
not automatically a crash. Record the diagnostic and interpret the result in
the context of the command you ran.

**A reproducible command record answers six questions:**

1. What environment or tool version was used?
2. What was the absolute working directory?
3. What were the exact inputs and their contents or identities?
4. What exact command ran?
5. What stdout, stderr, and exit status were observed?
6. What narrow conclusion follows, and what remains untested?

“It worked” answers none of them. Copy observations; do not rewrite them into
the result you expected.

## Worked example

The first line asks the operating system for a new empty temporary directory.
The assignment stores its path in <code>workdir</code>; double quotes preserve
that path as one value.

~~~sh
workdir="$(mktemp -d)"
printf 'Temporary workspace: %s\n' "$workdir"
cd -- "$workdir"
pwd
mkdir -- records
printf 'alpha\nbeta\n' > input.txt
ls -la
~~~

Every write above is contained in the fresh path printed by
<code>mktemp -d</code>. Now run one successful command:

~~~sh
wc -l -- input.txt > records/success.stdout 2> records/success.stderr
success_status=$?
printf '%s\n' "$success_status" > records/success.status
cat -- records/success.stdout
cat -- records/success.stderr
cat -- records/success.status
~~~

Expected stdout describes two lines, stderr is empty, and status is 0. Record
what your system actually prints. Next, make a safe, intentional read failure:

~~~sh
cat -- absent.txt > records/failure.stdout 2> records/failure.stderr
failure_status=$?
printf '%s\n' "$failure_status" > records/failure.status
cat -- records/failure.stdout
cat -- records/failure.stderr
cat -- records/failure.status
~~~

No file is deleted or overwritten outside the temporary workspace.
<code>failure.stdout</code> should be empty, the diagnostic should name the
missing file, and the status should be nonzero. Diagnostic wording and the
exact nonzero number may vary, so a good record preserves the observation
rather than inventing a universal value.

## Check your understanding

1. Your prompt displays <code>learner@host:~$</code>. Which part do you type?
2. If <code>pwd</code> prints <code>/tmp/a</code>, what does
   <code>records/out.txt</code> name?
3. After <code>command &gt;out 2&gt;err</code>, where are stdout and stderr?
4. Why is this status record wrong?

   ~~~sh
   cat -- missing.txt
   printf 'finished\n'
   status=$?
   ~~~

5. Why is “The command worked” not a reproducible record?

**Answers:** (1) type only the command, not the prompt; (2)
<code>/tmp/a/records/out.txt</code>; (3) stdout is in <code>out</code> and
stderr is in <code>err</code>; (4) it captures <code>printf</code>'s status
rather than <code>cat</code>'s; (5) it omits the directory, inputs, exact
command, three observed result channels, environment, and claim boundary.

## Next step

Complete the [lab](lab.md) in one Bash session. Keep the temporary path and
record files until your work has been checked; no cleanup command is required.
Then complete the [independent assessment](assessment.md). Passing requires at
least 80/100 and every critical criterion in the [rubric](rubric.md).

## Sources

- IEEE/The Open Group, [POSIX.1-2024, Shell and Utilities, Issue
  8](https://pubs.opengroup.org/onlinepubs/9799919799/), command language,
  paths, standard streams, and utility exit status.
- Free Software Foundation, [GNU Bash Reference
  Manual](https://www.gnu.org/software/bash/manual/bash.html), redirections,
  shell parameters, quoting, and exit status; examples checked with GNU Bash
  5.3 in the reference environment.
- Free Software Foundation, [GNU Coreutils
  Manual](https://www.gnu.org/software/coreutils/manual/coreutils.html),
  <code>cat</code>, <code>ls</code>, <code>mkdir</code>,
  <code>mktemp</code>, <code>pwd</code>, and <code>wc</code>; examples checked
  with GNU Coreutils 9.10 in the reference environment.
- [Assessment system](../../../docs/assessment-system.md), evidence and module
  pass policy.
