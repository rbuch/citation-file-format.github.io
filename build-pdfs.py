import glob
import os
import pypandoc
import shutil
import re
import frontmatter
from frontmatter.default_handlers import YAMLHandler


def conditional_sub(match):
    """
    Takes a regex match and returns a repl string, which depends on whether
    the capture group "page" for that match is empty or not. If the group
    is emtpy, it returns a Pandoc-style cite tag without page information.
    If the group is not empty, it returns a Pandoc-style cite tag with a "p."
    part followed by a whitespace and the contents of the catprure group
    "page".

    :param match: A match against a regex pattern which includes the groups
    "ref" and "page" and possibly more.
    :returns: A Pandoc-style citation tag string with included page ("p.")
    material, depending on whether the match's capture group "page" is empty
    or not.
    """
    if match.group("page"):
        return "[@" + match.group("ref") + " p. " + match.group("page") + "]"
    else:
        return "[@" + match.group("ref") + "]"


# Find all files called specifications.md, recursively
for specsfile in glob.iglob('./**/specifications.md', recursive=True):
    # Copy specs file to tmp file
    specsdir = os.path.dirname(specsfile)
    version = str(os.path.basename(specsdir))
    shutil.copy2(specsfile, specsdir + "/tmp.md")

    #################################################################
    # Replace all kramdown-specific material (e.g., Liquid tags) with
    # Pandoc-specific material where necessary (e.g., citations),
    # else remove.
    #################################################################

    with open(specsdir + "/tmp.md", "r") as f:
        contents = f.read()

        # Replace citations
        p = r"""
            (?P<cite>{%\scite\s)   # Liquid cite tag start
            (?P<ref>[\w-]+)        # Reference id, BibTeX key
            (\s-l\s(?P<page>\d+))? # Optional page number
            (?P<style>\s--style\s\./_bibliography/apa-text\.csl)?
            # Optional CSL style
            (?P<suff>\s%})         # Liquid cite tag end
            """
        pattern = re.compile(p, re.VERBOSE)

        new_contents = re.sub(pattern, conditional_sub, contents)

        # Remove Liquid CSS style tags
        new_contents = re.sub(r"{: \.[\w-]+}", "", new_contents)

        # Remove Liquid include toc tag
        new_contents = re.sub(r"{% include toc %}", "", new_contents)

        # Replace version with real version
        new_contents = re.sub(r"{{ page.version }}", version, new_contents)

        # Replace code highlighting
        new_contents = re.sub(r"{% highlight yaml %}", "```yaml", new_contents)
        new_contents = re.sub(r"{% endhighlight %}", "```", new_contents)

        # Remove Liquid bibliography tag
        new_contents = re.sub(r"{% bibliography --cited %}", "", new_contents)

        # Remove Zenodo DOI badge
        zdp = r"""
                             \[!\[DOI\]\(https://zenodo.org/badge/DOI/
                             \d+\.\d+/zenodo\.\d+\.svg\)\]\(https://doi\.org/
                             \d+\.\d+/zenodo\.\d+\)
                             """
        zenodo_doi_pattern = re.compile(zdp, re.VERBOSE)
        new_contents = re.sub(zenodo_doi_pattern, "", new_contents)

    # Write new Pandoc markdown file
    with open(specsdir + "/tmp.md", "w") as f:
        f.write(new_contents)
    output = pypandoc.convert_file(specsdir + "/tmp.md", 'markdown',
                                   outputfile=specsdir +
                                   "/cff-specifications-" +
                                   version + ".md")
    # todo handle multiline tables for pandoc

    # Replace links to GitHub users using @ notation
    # Has to be done here, otherwise the first pandoc conversion simply
    # gets rid of the backslashes before the "@".
    with open(specsdir + "/cff-specifications-" + version + ".md", "r") as f:
        contents = f.read()
        new_contents = re.sub(r"\(\[@(?P<user>[\w-]+)\]",
                              "([" + r"\\@" + "\g<user>]",
                              contents)
    with open(specsdir + "/cff-specifications-" + version + ".md", "w") as f:
        f.write(new_contents)

    # Read YAML frontmatter from the original specifications.md and
    # write it to the new Pandoc markdown file
    with open(specsdir + "/tmp.md", "r") as f:
        metadata, content = frontmatter.parse(f.read())
        e = YAMLHandler().export(metadata)
    with open(specsdir + "/cff-specifications-" + version + ".md", "r") as f:
        contents = f.read()
        new_contents = "---\n" + e + "\n---\n\n" + contents
    with open(specsdir + "/cff-specifications-" + version + ".md", "w") as f:
        f.write(new_contents)
