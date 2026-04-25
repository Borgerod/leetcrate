"""generators

Registry of all language-specific boilerplate generators.

Each generator exposes a ``generate_boilerplate(data, indent)`` function
that accepts the problem data dict (from :func:`~core.fetch_leetcode_problem`)
and an indent string, and returns a fully formatted source file as a string.

The :data:`GENERATOR_MAP` dict maps language keys to their generator functions
and is the single lookup point used by :func:`~core.create_files`.

Supported languages: ``python``, ``java``, ``javascript``, ``go``, ``cpp``.
"""

# version for runtime access
__version__ = "1.0.0"
from .python_generator import generate_boilerplate as generate_python
from .java_generator import generate_boilerplate as generate_java
from .javascript_generator import generate_boilerplate as generate_javascript
from .go_generator import generate_boilerplate as generate_go
from .cpp_generator import generate_boilerplate as generate_cpp

GENERATOR_MAP = {
    'python': generate_python,
    'java': generate_java,
    'javascript': generate_javascript,
    'go': generate_go,
    'cpp': generate_cpp,
}

__all__ = ['GENERATOR_MAP']
