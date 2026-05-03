---
description: Scaffold a new solution file via lc new
argument-hint: "<topic> <number> <title> [language]"
---

Create a new solution scaffold using the `lc new` CLI.

Arguments: $ARGUMENTS

Parse them as: `<topic> <number> <title...> [language]`. The language is optional and defaults to `python`. The title may contain spaces — everything between the number and the optional trailing language token is the title. If a language token is present (one of: python, javascript, typescript, rust, go, java, cpp, c, ruby, sql), strip it from the title.

If arguments are missing or ambiguous, ask me for them rather than guessing.

Steps:

1. Confirm the topic directory exists (it usually does — see [README.md](README.md) for the list).
2. Run `lc new --topic <topic> --number <N> --title "<title>" --language <language>`.
3. Print the path to the created file.
4. Remind me to paste the chrome extension's clipboard content over the placeholder metadata block once I solve the problem.

Do not open the file or write any solution code — that's my job.
