## Summary

<!--
What does this PR change? 1-3 sentences. The auto-generated release notes
will pull from this section.
-->

## Type of change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing behavior to change)
- [ ] Documentation / CI / tooling only (no gameplay impact)

## Related issues

<!-- Link the issue(s) this PR resolves: `Fixes #123`, `Closes #456`. -->

## Testing

<!--
How did you verify the change?
- [ ] Loaded a save from the prior version (no save-compat regression)
- [ ] Triggered the affected code path in-game
- [ ] Added/updated a unit test (path: `tests/test_*.py`)
- [ ] Ran `pytest`, `ruff check`, `ruff format --check` locally
-->

## Checklist

- [ ] I have read [`CONTRIBUTING.md`](../../blob/main/CODE_OF_CONDUCT.md) and the
      [Code of Conduct](../../blob/main/CODE_OF_CONDUCT.md)
- [ ] My changes introduce **no new Player.log warnings** in a fresh-game run
- [ ] For UI changes: I attached a screenshot or short clip
- [ ] For localization changes: I touched **all three** locale files
      (`en-US.json`, `uk-UA.json`, `zh-CN.json`) and ran
      `pytest tests/test_localization_keys.py`
- [ ] For `CivicSurvival.csproj` / `manifest.json` / `PublishConfiguration.xml`
      version changes: I used `python scripts/release.py bump --version ...` and
      the post-write consistency check passed
