# version for runtime access
__version__ = "0.2.0"
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
