# citation-file-format.github.io

## This branch holds the website and documentation for CFF

Documentation is provided in the form of a Jekyll site hosted on GitHub pages (using https://mmistakes.github.io/minimal-mistakes/), and a PDF.

### Versions

To work on a new version, create a branch from master with the version number, e.g., `0.9-RC1`, create a directory named after the version, e.g., `0.9-RC1`, and copy the `documentation.md` file from the last version into the directory.

Once a version is release-ready, do the following:

- Create a landing page `index.md` file for the version under the `{version}` folder, describing the version (including release notes, changes, etc.).
- In `_config.yml`, set `current` to the version number, e.g., `0.9-RC1`.
- Add the version to the table in [versions.md](https://github.com/citation-file-format/citation-file-format.github.io/blob/master/versions.md).
- Merge the version branch to master.
- Push master.