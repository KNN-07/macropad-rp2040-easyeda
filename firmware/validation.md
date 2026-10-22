# Firmware validation

Release 0.2.0 targets MACRO12 Rev C. Source checks, official VIA-definition parsing and both ARM firmware builds are run by the repository's [firmware workflow](../.github/workflows/firmware.yml). Release assets include their build manifest and logs.

Physical validation is pending: no assembled Rev C board is available in this session. See [first-article.md](first-article.md). Do not interpret successful compilation or a valid VIA definition as a tested USB/peripheral connection.
