# Contributing

Thanks for your interest in contributing! Please read the [Code of Conduct](CODE_OF_CONDUCT.md) before getting started.

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

This project uses [mise](https://mise.jdx.dev/) and [uv](https://docs.astral.sh/uv/) for tooling.

```bash
# Install tools via mise
mise install

# Install dependencies
mise run setup

# Build the .alfredworkflow
mise run build

# Clean build artifacts
mise run clean
```

## Pull Requests

- Keep changes focused and atomic
- Use descriptive PR titles (they feed into release notes)
- Add appropriate labels: `feature`, `fix`, `chore`, `docs`, etc.
