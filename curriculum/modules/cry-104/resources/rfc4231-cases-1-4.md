# RFC 4231 HMAC-SHA-256 cases 1 through 4

This is a course-maintained, byte-oriented data sheet for the independent
assessment. It transcribes only the HMAC-SHA-256 inputs and full outputs from
RFC 4231 Sections 4.2 through 4.5. It is not a replacement for the RFC, an
authenticated publisher artifact, or a validation certificate.

All fields below are lowercase hexadecimal and encode whole bytes.

| Case | RFC section | Key hex | Data hex | HMAC-SHA-256 hex |
| --- | --- | --- | --- | --- |
| 1 | 4.2 | `0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b` | `4869205468657265` | `b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7` |
| 2 | 4.3 | `4a656665` | `7768617420646f2079612077616e7420666f72206e6f7468696e673f` | `5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843` |
| 3 | 4.4 | `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` | `dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd` | `773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe` |
| 4 | 4.5 | `0102030405060708090a0b0c0d0e0f10111213141516171819` | `cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd` | `82558a389a443c0ea4cc819899f2083a85f0faa3e578f8077a2e3ff46729665b` |

Source identity:

- M. Nystrom, *Identifiers and Test Vectors for HMAC-SHA-224,
  HMAC-SHA-256, HMAC-SHA-384, and HMAC-SHA-512*, RFC 4231, Standards
  Track, December 2005.
- Stable source: <https://www.rfc-editor.org/rfc/rfc4231.html>
- Course transcription reviewed: 2026-07-12.

Before using this sheet, hash its local bytes, record the repository revision
or workspace state, and retain the RFC identity. A local digest detects later
byte changes only relative to the recorded value; it does not authenticate the
transcription as publisher-supplied.
