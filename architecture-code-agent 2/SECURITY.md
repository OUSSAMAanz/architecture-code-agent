# Security Notes

This is an educational agent and should not be treated as a production sandbox.

Implemented controls:

- output paths must remain inside the selected workspace;
- absolute paths and parent traversal are rejected;
- `.env`, `.git`, and `secrets` paths are blocked from model writes;
- files have a 200 KB size limit;
- the model receives no arbitrary shell tool;
- recognized, fixed test commands have a 30-second timeout;
- generation has a maximum iteration count;
- destructive `--clean` refuses roots, the workspace, and input-containing directories;
- API keys are read only from the process environment.

For production use, run the generated project in a disposable container with no
credentials, limited filesystem access, disabled network access where possible,
CPU and memory limits, and explicit human approval for side effects.

Do not report real credentials in an issue. Revoke any key that was accidentally
committed and remove it from Git history.
