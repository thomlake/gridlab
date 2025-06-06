from gridlab.action import Action
from gridlab.view.pipeline_builder import build_view_pipeline
from gridlab.view.pipeline import ViewPipeline
from gridlab.view.theme import Theme
from gridlab.world import World
from gridlab.world_builder import create_world

TERMINAL_TEMPLATE_FIRST = '{legend}\n\n{status}\n{grid}'
TERMINAL_TEMPLATE_REST = '{status}\n{grid}'


def get_action() -> Action | None:
    while True:
        cmd = input("Enter action (u)p/(d)own/(l)eft/(r)ight/(q)uit': ").strip()[:1].lower()
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


VERIFICATION_FAILED_TEMPLATE = """
{status}
Taken: {taken}
Remain: {remain}

## Legend

{legend}

## Status

{status}

## Grid

{grid}"""


class VerificationFailed(Exception):
    def __init__(self, status: str, taken: list[Action], remain: list[Action], views: dict[str, str]):
        taken = ', '.join(taken)
        remain = ', '.join(remain)
        message = VERIFICATION_FAILED_TEMPLATE.format(status=status, taken=taken, remain=remain, **views)
        super().__init__(message)


def verify_solution(world: World | str):
    if not isinstance(world, World):
        world = create_world(world)

    solution = world.solve()
    taken = []
    for action in solution:
        world.step(action=action)
        taken.append(action)
        if world.state.is_finished:
            break

    remain = solution[len(taken):]
    status = 'ok'
    if not world.state.goal_reached:
        status = 'Finished without reaching goal!'
    elif solution != taken:
        status = 'Finished with actions remaining!'
    else:
        return True

    pipeline = build_view_pipeline(mode='text')
    views = pipeline.render(world)
    raise VerificationFailed(status, taken, remain, views)
