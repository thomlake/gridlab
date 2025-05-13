# gridlab

*Causal inference in grid environments*

```
█████
█.X.█
█...█
█#e.█
█.█.█
█.@.█
█████
```


## Usage

```python
from gridlab import World


w = World()
w.initialize(builder=factory)

# gridlab.run_demo(w)

while True:
    grid: str = w.to_symbolic_grid()
    desc: str = w.to_text_description()
    action = get_action(state)
    w.step(action)
    if w.is_finished:
        break

```

```python
import gridlab


w = gridlab.create_world('demo')
# gridlab.run_stdio(w)

while True:
    desc: str = gridlab.text_desc(w)
    grid: str = gridlab.text_grid(w)
    action = get_action(state)
    w.step(action)
    if w.is_finished:
        break

```

```python


while True:
    text = gridlab.render_text(w)
    action = get_action(text)
    w.step(action)
    if w.state.is_finished:
        break

```




