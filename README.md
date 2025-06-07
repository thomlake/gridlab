# Gridlab

*Causal inference in text-based grid games*

## Themes

Gridlab supports rendering in plain text, terminal styling with ANSI codes, and HTML+CSS.

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

```
Output:

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

world = gridlab.create_world('demo')
pipeline = gridlab.build_view_pipeline()
# pipeline = gridlab.build_view_pipeline(mode='text', theme='ascii')  # default values, same as above
# pipeline = gridlab.build_view_pipeline(mode='text', theme='fancy')  # use non-strict ASCII chars
# pipeline = gridlab.build_view_pipeline(mode='terminal')  #  terminal styling with ANSI codes
views = pipeline.render(world)
text = '\n\n'.join(f'## {k}\n\n{v}' for k, v in views.items())
print(text)
```

```
Output:

## legend

- `@`: player
- `0`: block
- `#`: wall
- `^`: spike
- `X`: goal
- `e`: enemy

## status

- Turn: 1

## grid

############
####.#######
##..0..^.X##
##...0###e##
##.@.......#
############
```

Actions are simple string values `up`, `down`, `left`, and `right`.
Single characters, `udlr`, also work.

```python
world.step(action='up')
views = pipeline.render(world)
print(views['grid'])
```

```
Output:

############
####.#######
##..0..^.X##
##.@.0###.##
##.......e.#
############
```
