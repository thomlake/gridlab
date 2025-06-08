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
