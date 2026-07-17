# Python Style Guide

## General Rules

- Maximum line length: 100 characters
- Use 4 spaces for indentation (no tabs)
- Files must end with a newline
- No trailing whitespace

## Naming Conventions

| Type | Style | Example |
|------|-------|---------|
| Variables | snake_case | `user_name` |
| Functions | snake_case | `get_user_by_id()` |
| Classes | PascalCase | `UserService` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |
| Private members | _leading_underscore | `_internal_cache` |

## Documentation

- All public functions must have docstrings
- Use triple double quotes (`"""`) for docstrings
- Include parameter types and return types in docstrings

## Imports

- Group imports: stdlib → third-party → local
- One import per line
- Use absolute imports over relative imports

## Type Hints

- All function signatures should include type hints
- Use `Optional[T]` for nullable parameters
- Use `List[T]`, `Dict[K, V]` for collections
