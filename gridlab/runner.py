from gridlab.action import Action
from gridlab.view.pipeline_builder import build_view_pipeline
from gridlab.view.pipeline import ViewPipeline
from gridlab.view.theme import Theme
from gridlab.world import World
from gridlab.world_builder import create_world

TERMINAL_TEMPLATE_FIRST = '{legend}\n\n{status}\n{grid}'
TERMINAL_TEMPLATE_REST = '{status}\n{grid}'
ACTION_PROMPT = "Select action (u)p, (d)own, (l)eft, (r)ight, (n)one, (q)uit': "


def get_action() -> Action | None:
    while True:
        cmd = input(ACTION_PROMPT)
        cmd = cmd.strip()[:1].lower()
        if cmd == 'q':
            return None

        try:
            action = Action(cmd)
        except ValueError:
            print("Invalid action. Try again.")
            continue

        print()
        return action


def run_stdio(
        world: World | str,
        *,
        pipeline: ViewPipeline | None = None,
        theme: str | Theme = 'desert',
):
    if not isinstance(world, World):
        world = create_world(world)

    pipeline = pipeline or build_view_pipeline(mode='terminal', theme=theme)

    template = TERMINAL_TEMPLATE_FIRST
    taken: list[Action] = []
    while True:
        views = pipeline.render(world)
        text = template.format(**views)
        print(text, end='\n\n')
        template = TERMINAL_TEMPLATE_REST

        if world.state.is_finished:
            break

        action = get_action()
        if action is None:
            print()
            break
        else:
            world.step(action=action)
            taken.append(action)

    if world.state.goal_reached:
        status = '✅ SUCCESS'
    elif world.state.player_dead:
        status = '☠️ DIED'
    else:
        status = '⛔️ QUIT'

    action_list = '\n'.join(f'    Action.{action.name},' for action in taken)
    print(f'World: {world.name}\n\n{status}\n\nactions = [\n{action_list}\n]')


def render_rollout(
        world: World | str,
        pipeline: ViewPipeline | None = None,
        max_width: int = 75,
        sep: str = ' → ',
        actions: list[Action] | None = None,
):
    if not isinstance(world, World):
        world = create_world(world)

    if not pipeline:
        pipeline = build_view_pipeline(mode='text', theme='ascii')

    if not actions:
        actions = world.solve()

    frames = [pipeline.render(world)['grid']]
    for action in actions:
        world.step(action=action)
        frames.append(pipeline.render(world)['grid'])

    first_frame_lines = frames[0].split('\n')
    n_rows = len(first_frame_lines)
    n_cols = len(first_frame_lines[0])
    n_per_line = max_width // (n_cols + len(sep))
    text_blocks = []

    while frames:
        first_frame, *frames_rest = frames[:n_per_line]
        frames = frames[n_per_line:]

        actions_block = actions[:n_per_line]
        actions = actions[n_per_line:]

        merged_lines = first_frame.split('\n')
        for frame in frames_rest:
            lines = frame.split('\n')
            assert len(merged_lines) == len(lines) == n_rows
            for i, line in enumerate(lines):
                merged_lines[i] = f'{merged_lines[i]}{sep}{line}'

        header_parts = [action.upper().center(n_cols) for action in actions_block]
        header = (' ' * len(sep)).join(header_parts)
        # header = sep.join(header_parts)

        if text_blocks:
            # Not the first block
            header = ' ' * len(sep.lstrip()) + header
            merged_lines = [f'{sep}{line}'.lstrip() for line in merged_lines]

        block = '\n'.join([header] + merged_lines)
        text_blocks.append(block)

    return '\n'.join(text_blocks)
