Contents Menu Expand Light mode Dark mode Auto light/dark, in light mode Auto light/dark, in dark mode
Hide navigation sidebar
Hide table of contents sidebar
Skip to content
Back to top
Toggle Light / Dark / Auto color theme
Toggle table of contents sidebar
# How to set up bash completion¶
When using bash as your shell, `pytest` can use argcomplete (https://kislyuk.github.io/argcomplete/) for auto-completion. For this `argcomplete` needs to be installed **and** enabled.
Install argcomplete using:
```
sudopipinstall'argcomplete>=0.5.7'

```

For global activation of all argcomplete enabled python applications run:
```
sudoactivate-global-python-argcomplete

```

For permanent (but not global) `pytest` activation, use:
```
register-python-argcompletepytest>>~/.bashrc

```

For one-time activation of argcomplete for `pytest` only, use:
```
eval"$(register-python-argcompletepytest)"

```

