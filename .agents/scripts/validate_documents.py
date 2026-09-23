"""Validate required documents and local Markdown links without network access.

Supports inline links and full reference links. Markdown code blocks and code
spans are excluded. HTML links and shortcut references need manual review.
"""
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

REQUIRED_DOCUMENTS = (
    'AGENTS.md', '.agents/teaching.md', '.agents/language.md',
    '.agents/project-instructions.md', 'planning/system-plan.md',
)


def markdown_files(root):
    for path in sorted(root.rglob('*.md')):
        if not any(p in {'.git', '.venv', '__pycache__'} for p in path.relative_to(root).parts):
            yield path


def without_code(text):
    text = re.sub(r'(?ms)^\s*(```|~~~).*?^\s*\1[^\n]*$', '', text)
    return re.sub(r'`+[^`\n]*`+', '', text)


def heading_ids(text):
    counts, result = {}, set()
    # Keep code text in headings because it contributes to GitHub fragment IDs.
    text = re.sub(r'(?ms)^\s*(```|~~~).*?^\s*\1[^\n]*$', '', text)
    for heading in re.findall(r'^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$', text, re.M):
        heading = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', heading)
        slug = re.sub(r'[^\w\-\s]', '', heading.lower()).replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(slug if count == 0 else f'{slug}-{count}')
    return result


def validate_documents(root):
    root = Path(root).resolve()
    errors = []

    def add(rule, file, message):
        errors.append(dict(rule_id=rule, file=file, json_pointer='', message=message))

    for relative in REQUIRED_DOCUMENTS:
        path = root / relative
        if not path.is_file():
            add('MISSING_DOCUMENT', relative, 'The required document is missing.')
        elif path.is_symlink() or not path.resolve().is_relative_to(root):
            add('UNSAFE_FILE', relative, 'Do not use linked instruction files.')
        elif not path.read_text(encoding='utf-8').strip():
            add('EMPTY_DOCUMENT', relative, 'The required document is empty.')
    for path in markdown_files(root):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            add('UNSAFE_FILE', relative, 'Do not use linked Markdown files.')
            continue
        text = without_code(path.read_text(encoding='utf-8'))
        links = re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', text)
        definitions = dict((label.casefold(), target) for label, target in re.findall(
            r'^ {0,3}\[([^\]]+)\]:\s*(\S+)', text, re.M))
        for label, reference in re.findall(r'\[([^\]\n]+)\]\[([^\]\n]*)\]', text):
            key = (reference or label).casefold()
            if key not in definitions:
                add('BROKEN_LINK', relative, f'Undefined reference: {key}')
            else:
                links.append(definitions[key])
        for link in links:
            link = re.sub(r'\s+["\'].*$', '', link).strip('<>')
            parsed = urlsplit(link)
            if parsed.scheme in {'http', 'https', 'mailto'}:
                continue  # External URLs are not fetched by this validator.
            target_path = unquote(parsed.path)
            if parsed.scheme or parsed.netloc or '\\' in target_path or target_path.startswith('/'):
                add('BROKEN_LINK', relative, f'Unsupported or unsafe link: {link}')
                continue
            target = (path.parent / target_path).resolve() if target_path else path
            if not target.is_relative_to(root) or not target.is_file():
                add('BROKEN_LINK', relative, link)
                continue
            if parsed.fragment and target.suffix == '.md':
                if unquote(parsed.fragment) not in heading_ids(target.read_text(encoding='utf-8')):
                    add('BROKEN_ANCHOR', relative, link)
    return errors
