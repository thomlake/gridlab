# Gridlab

*Causal inference in text-based grid games*

## Themes

Gridlab supports text rendering in a variety of simple text formats.

```
ascii           fancy
#####           █████
#.X.#           █.X.█
#0.e#           █■.e█
#.#.#           █.█.█
#.@.#           █.@.█
#####           █████
```

## Usage

### Interactive Terminal

```python
import gridlab

gridlab.run_stdio('demo')
```

**Output:**
```
e: enemy
@: player
▴: spike
X: goal
█: wall
■: block

[Turn: 1]
████████████
████.███████
██..■..▴.X██
██...■███e██
██.@.......█
████████████

Enter action (u)p/(d)own/(l)eft/(r)ight/(q)uit':
```

### Manual Orchestration

```python
import gridlab

world = gridlab.create_world('patrol')
pipeline = gridlab.build_view_pipeline()
# pipeline = gridlab.build_view_pipeline(mode='text', theme='ascii')  # default values, same as above
# pipeline = gridlab.build_view_pipeline(mode='text', theme='fancy')  # use non-strict ASCII chars
# pipeline = gridlab.build_view_pipeline(mode='terminal')  # styling for terminal using ANSI codes
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

#####
#.X.#
#0.e#
#.#.#
#.@.#
#####
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
- `@`: player
- `#`: wall
- `0`: block
- `X`: goal
- `e`: enemy

## Status
- Turn: 1

## Grid
#####
#.X.#
#0.e#
#.#.#
#.@.#
#####
```
