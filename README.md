# Gridlab

*Causal inference in text-based grid games*

## Themes

Gridlab supports text rendering in a variety of simple text formats.

```
ascii           fancy
#####           █████
#.@.#           █.@.█
#.#.#           █.█.█
#0.e#           █■.e█
#.X.#           █.X.█
#####           █████
```

## Usage

### Interactive Terminal

```python
import gridlab

gridlab.run_stdio('demo')
```

### Manual Orchestration

```python
import gridlab

world = gridlab.create_world('patrol')
pipeline = gridlab.view.build_text_pipeline(theme='fancy')
views = pipeline.render_views(world)

print(views.keys())
```

```
Output:
dict_keys(['legend', 'status', 'grid'])
```

```python
print(views['grid'])
```

```
Output:
█████
█.X.█
█■.e█
█.█.█
█.@.█
█████
```

```python
template = """\
## Legend

{legend}

## Status

{status}

## Grid

{grid}"""
print(template.format(**views))
```

```
Output:
## Legend
- `e`: enemy
- `@`: player
- `█`: wall
- `X`: goal
- `■`: block

## Status
- Turn: 1

## Grid
█████
█.X.█
█■.e█
█.█.█
█.@.█
█████
```

```python
worl