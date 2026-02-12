# Security Policy

## Reporting a Vulnerability

Found a security issue? We'd appreciate you reporting it privately so we can fix it before public disclosure.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report details to our Security Operations team via email to: **security@twelvelabs.io**

Include the following information in your report:

- Type of vulnerability (e.g., API key exposure, injection, authentication bypass)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability and how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 72 hours.
- **Communication**: We will keep you informed of the progress toward a fix and full announcement.

### Scope

This security policy applies to:

- The TwelveLabs Claude Code Plugin source code in this repository
- Configuration files and hooks included in the plugin

This security policy does **not** apply to:

- Other TwelveLabs Repositories or services (report those to TwelveLabs directly)
- Third-party dependencies (report those to the respective maintainers)
- Claude Code or Anthropic services

## Security Best Practices for Users

When using this plugin:
1. **Protect your API key**: Never commit your `TWELVELABS_API_KEY` to version control. Use environment variables.
2. **Review hooks**: If modifying the provided hooks, ensure you don't introduce security vulnerabilities.
3. **Keep updated**: Use the latest version of the plugin to benefit from security fixes.

Thank you for helping keep TwelveLabs and our users safe!
