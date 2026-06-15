# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scaffold a platform-std package that conforms to the convention and is
package-able out of the gate (`uv sync` / `uv build` work immediately).

See docs/final-proposal.md for the rules this encodes.

Usage:
    uv run python scripts/scaffold.py <layer> [feature] [backend] [options]

    <layer>     one of: std | core | sdk        (ext is out of scope)
    feature     feature/domain name (snake_case); omit for `std`
    backend     backend name (snake_case); REQUIRED for `sdk`

Options:
    --org ORG       import namespace root (default: org)
    --author EMAIL  author email (default: `git config user.email`)
    --no-sync       don't run `uv sync` after generating

Examples:
    uv run python scripts/scaffold.py std
    uv run python scripts/scaffold.py core cache
    uv run python scripts/scaffold.py sdk cache redis      # new feature + 1st backend
    uv run python scripts/scaffold.py sdk cache memcached   # add a backend to existing feature

Layout produced (PEP 420 namespaces — only the leaf gets __init__.py):
    core/<feature>/  → dist `<feature>-core`, module `<org>.core.<feature>`
    sdk/<feature>/   → dist `<feature>-sdk`,  module(s) `<org>.sdk.<feature>.<backend>`
    std/             → dist `std`,            module `<org>.std`

Why not wrap `uv init`? `uv init` can't express the namespace-package layout
(no __init__.py at the `<org>`/`<layer>`/sdk-`<feature>` levels) nor the
list-valued `module-name`, so we template the files directly, then `uv sync`.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path

UV_BUILD = "uv_build>=0.10.3,<0.11.0"
CORE_PIN = ">=0.1,<0.2"
STD_PIN = ">=0.1,<0.2"
_IDENT = re.compile(r"^[a-z][a-z0-9_]*$")


def die(msg: str) -> None:
    sys.exit(f"error: {msg}")


def repo_root() -> Path:
    start = Path.cwd()
    for d in (start, *start.parents):
        pp = d / "pyproject.toml"
        if pp.exists() and "tool.uv.workspace" in pp.read_text():
            return d
    die("not inside a uv workspace (no root pyproject.toml with [tool.uv.workspace])")
    raise AssertionError  # unreachable


def requires_python(root: Path) -> str:
    data = tomllib.loads((root / "pyproject.toml").read_text())
    return data.get("project", {}).get("requires-python", ">=3.14")


def default_author() -> str:
    try:
        out = subprocess.run(
            ["git", "config", "user.email"], capture_output=True, text=True, check=False
        ).stdout.strip()
    except OSError:
        out = ""
    return out or "dev@example.com"


def validate_ident(kind: str, value: str) -> None:
    if not _IDENT.match(value):
        die(f"{kind} {value!r} must be snake_case matching ^[a-z][a-z0-9_]*$")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  + {path.relative_to(path.cwd() if False else Path.cwd())}")


# --- templates --------------------------------------------------------------


def pyproject(
    *,
    name: str,
    module_name: str,
    description: str,
    deps: list[str],
    sources: dict[str, str],
    rpy: str,
    author: str,
    extras_hint: str = "",
) -> str:
    dep_lines = ", ".join(f'"{d}"' for d in deps)
    src_lines = "".join(f"{k} = {{ workspace = true }}\n" for k in sources)
    src_block = f"\n[tool.uv.sources]\n{src_lines}" if sources else ""
    return f"""\
[project]
name = "{name}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
authors = [{{ email = "{author}" }}]
requires-python = "{rpy}"
dependencies = [{dep_lines}]
{extras_hint}
[build-system]
requires = ["{UV_BUILD}"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-name = {module_name}
{src_block}"""


def leaf_init(module: str, kind: str) -> str:
    if kind == "std":
        body = f'"""{module} — platform foundation (primitives + cross-domain standards)."""'
    elif kind == "core":
        body = (
            f'"""{module} — interface: role-segregated typing.Protocol contracts,\n'
            "data models, and config. Depends only on std; no external SDK.\n"
            'See docs/final-proposal.md (Phần B).\n"""'
        )
    else:  # sdk backend
        body = (
            f'"""{module} — backend implementation.\n\n'
            "Implement the org.core.<feature> protocol(s): stateless + injected\n"
            "client; stateful parts as a resource (initialize/cleanup). When you\n"
            "add the third-party SDK: declare it as the named extra in pyproject\n"
            "and wrap the SDK import in a lazy-import guard. See final-proposal C1.\n"
            '"""'
        )
    return f"{body}\n\n__all__: list[str] = []\n"


def smoke_test(module: str) -> str:
    return f"""\
def test_import() -> None:
    import {module} as module

    assert module is not None
"""


def readme(name: str, module: str) -> str:
    return f"# {name}\n\n`{module}`\n\n```python\nfrom {module} import ...\n```\n"


# --- backend discovery (sdk) ------------------------------------------------


def backend_modules(org: str, feature: str, feature_dir: Path) -> list[str]:
    leaf_root = feature_dir / "src" / org / "sdk" / feature
    backends = sorted(
        p.name for p in leaf_root.iterdir() if (p / "__init__.py").exists()
    )
    return [f"{org}.sdk.{feature}.{b}" for b in backends]


def module_list_repr(modules: list[str]) -> str:
    return "[" + ", ".join(f'"{m}"' for m in modules) + "]"


# --- scaffolders ------------------------------------------------------------


def make_std(root: Path, org: str, rpy: str, author: str) -> str:
    pkg = root / "std"
    if pkg.exists():
        die(f"{pkg} already exists")
    module = f"{org}.std"
    write(
        pkg / "pyproject.toml",
        pyproject(
            name="std",
            module_name=f'"{module}"',
            description=f"{module} — platform foundation.",
            deps=[],
            sources={},
            rpy=rpy,
            author=author,
        ),
    )
    write(pkg / "README.md", readme("std", module))
    leaf = pkg / "src" / org / "std"
    write(leaf / "__init__.py", leaf_init(module, "std"))
    write(leaf / "py.typed", "")
    write(pkg / "tests" / "test_smoke.py", smoke_test(module))
    return "std"


def make_core(root: Path, org: str, feature: str, rpy: str, author: str) -> str:
    pkg = root / "core" / feature
    if pkg.exists():
        die(f"{pkg} already exists")
    name = f"{feature}-core"
    module = f"{org}.core.{feature}"
    write(
        pkg / "pyproject.toml",
        pyproject(
            name=name,
            module_name=f'"{module}"',
            description=f"{module} — {feature} interface.",
            deps=[f"std{STD_PIN}"],
            sources={"std": "workspace"},
            rpy=rpy,
            author=author,
        ),
    )
    write(pkg / "README.md", readme(name, module))
    leaf = pkg / "src" / org / "core" / feature
    write(leaf / "__init__.py", leaf_init(module, "core"))
    write(leaf / "py.typed", "")
    write(pkg / "tests" / "test_smoke.py", smoke_test(module))
    return name


def make_sdk(
    root: Path, org: str, feature: str, backend: str, rpy: str, author: str
) -> str:
    pkg = root / "sdk" / feature
    name = f"{feature}-sdk"
    module = f"{org}.sdk.{feature}.{backend}"
    leaf = pkg / "src" / org / "sdk" / feature / backend
    if leaf.exists():
        die(f"backend {leaf} already exists")

    # backend files (same whether new feature or added to existing)
    write(leaf / "__init__.py", leaf_init(module, "sdk"))
    write(leaf / "py.typed", "")
    write(pkg / "tests" / f"test_{backend}.py", smoke_test(module))

    if (pkg / "pyproject.toml").exists():
        # adding a backend to an existing feature: recompute the module-name list
        text = (pkg / "pyproject.toml").read_text()
        modules = backend_modules(org, feature, pkg)
        text = re.sub(
            r"module-name = \[[^\]]*\]",
            f"module-name = {module_list_repr(modules)}",
            text,
            count=1,
        )
        (pkg / "pyproject.toml").write_text(text)
        print(
            f"  ~ {(pkg / 'pyproject.toml').relative_to(Path.cwd())} (module-name updated)"
        )
    else:
        write(
            pkg / "pyproject.toml",
            pyproject(
                name=name,
                module_name=module_list_repr([module]),
                description=f"{module.rsplit('.', 1)[0]} — {feature} implementations.",
                deps=[f"{feature}-core{CORE_PIN}", f"std{STD_PIN}"],
                sources={f"{feature}-core": "workspace", "std": "workspace"},
                rpy=rpy,
                author=author,
                extras_hint=(
                    "\n[project.optional-dependencies]\n"
                    f'# {backend} = ["the-sdk>=x.y"]   # add the backend SDK, then guard its import\n'
                ),
            ),
        )
        write(pkg / "README.md", readme(name, f"{module.rsplit('.', 1)[0]}"))
    return name


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Scaffold a platform-std package (std/core/sdk) per the convention.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("layer", choices=["std", "core", "sdk"])
    ap.add_argument("feature", nargs="?", help="feature name (omit for std)")
    ap.add_argument("backend", nargs="?", help="backend name (required for sdk)")
    ap.add_argument("--org", default="org", help="import namespace root (default: org)")
    ap.add_argument("--author", default=None, help="author email")
    ap.add_argument("--no-sync", action="store_true", help="skip `uv sync` afterwards")
    args = ap.parse_args()

    root = repo_root()
    rpy = requires_python(root)
    author = args.author or default_author()
    validate_ident("org", args.org)

    if args.layer == "std":
        if args.feature:
            die("`std` takes no feature/backend argument")
        created = make_std(root, args.org, rpy, author)
    elif args.layer == "core":
        if not args.feature:
            die("`core` requires a feature name")
        if args.backend:
            die("`core` does not take a backend argument")
        validate_ident("feature", args.feature)
        created = make_core(root, args.org, args.feature, rpy, author)
    else:  # sdk
        if not args.feature or not args.backend:
            die("`sdk` requires both a feature and a backend name")
        validate_ident("feature", args.feature)
        validate_ident("backend", args.backend)
        created = make_sdk(root, args.org, args.feature, args.backend, rpy, author)

    print(f"\nScaffolded {created!r}.")
    if args.no_sync:
        print("Skipped sync. Run `uv sync --all-packages` to register & install.")
        return 0

    print("Running `uv sync --all-packages` ...")
    rc = subprocess.run(
        ["uv", "sync", "--all-packages"], cwd=root, check=False
    ).returncode
    if rc != 0:
        return rc
    print(f"\nDone. {created!r} is registered and importable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
