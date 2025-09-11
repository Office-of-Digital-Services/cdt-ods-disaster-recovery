# Commits, branches, and merging

## Commits

This project enforces the [Conventional Commits][conventional-commits] style for commit message formatting:

```<!-- markdownlint-disable-line MD040 -->
<type>[(optional-scope)]: <description>

[optional body]
```

Where `<type>` indicates the nature of the commit, one of a list of possible values:

- `build` - related to the build or compile process
- `chore` - administrative tasks, cleanups, dev environment
- `ci` - related to automated builds/tests etc.
- `docs` - updates to the documentation
- `feat` - new code, features, or interfaces
- `fix` - bug fixes
- `perf` - performance improvements
- `refactor` - non-breaking logic refactors
- `revert` - undo a prior change
- `style` - code style and formatting
- `test` - having to do with testing of any kind

E.g.

```bash
git commit -m "feat(vital-records/urls): add path for start"
```

## Branches

The default GitHub branch is `main`. All new feature work should be in the form of Pull Requests (PR) that target `main` as their
base.

In addition to `main`, the repository has a few other long-lived branches:

- `gh-pages` hosts the compiled documentation, and is always forced-pushed by the
  docs build process
- `python-coverage-comment-action-data` acts as a persistent data store for the [Python Coverage Comment GitHub Action](https://github.com/py-cov-action/python-coverage-comment-action)
  and is created and managed by it

### Protection rules

[Branch protection rules][gh-branch-protection] are in place on `main` to:

- Prevent branch deletion
- Restrict force-pushing, where appropriate
- Require passing status checks before merging into the target branch is allowed

### PR branches

PR branches are typically named with a [conventional type][conventional-commits] prefix, a slash `/`, and then descriptor in `lower-dashed-case`:

```bash
<type>/<lower-dashed-descriptor>
```

E.g.

```bash
git checkout -b feat/flow-multi-select
```

and

```bash
git checkout -b refactor/flow-model
```

PR branches are deleted once their PR is merged.

## Merging

Merging of PRs should be done using the _merge commit_ strategy. The PR author should utilize `git rebase -i` to ensure
their PR commit history is clean, logical, and free of typos.

When merging a PR into `main`, it is customary to format the merge commit message like:

```console
Title of PR (#number)
```

instead of the default:

```console
Merge pull request #number from source-repo/source-branch
```

[conventional-commits]: https://www.conventionalcommits.org/en/v1.0.0/
[gh-branch-protection]: https://docs.github.com/en/github/administering-a-repository/defining-the-mergeability-of-pull-requests/about-protected-branches
