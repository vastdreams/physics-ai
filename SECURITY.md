# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for
receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of Physics AI seriously. If you believe you have found a
security vulnerability, please report it to us as described below.

### Please do the following:

1. **Do not** open a public GitHub issue
2. Email the security team at: [INSERT SECURITY EMAIL]
   - Include a detailed description of the vulnerability
   - Include steps to reproduce the issue
   - Include potential impact assessment
   - Include any suggested fixes (if available)

### What to expect:

- You will receive a response within 48 hours acknowledging your report
- We will work with you to understand and resolve the issue quickly
- We will keep you informed of our progress
- Once the issue is resolved, we will credit you in our security advisories (if desired)

### Security Best Practices

When using Physics AI:

1. **Keep dependencies updated**: Regularly update your dependencies using `pip install --upgrade -r requirements.txt`
2. **Review code**: Always review code before executing, especially when using the self-evolution features
3. **Validate inputs**: Use the provided validators for all inputs
4. **Monitor logs**: Check logs regularly for suspicious activity
5. **Use in isolated environments**: When testing self-modification features, use isolated environments

### Known Security Considerations

- **Code Generation**: The self-evolution module can generate code. Always review generated code before execution.
- **Rule Execution**: Rules are executed dynamically. Ensure rules come from trusted sources.
- **File System Access**: Some modules may access the file system. Be cautious with file paths.

### Security Updates

Security updates will be announced via:
- GitHub Security Advisories
- Release notes
- Project discussions

Thank you for helping keep Physics AI and its users safe!

