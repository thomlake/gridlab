from gridlab.action import Action
from gridlab.view.pipeline import ViewPipeline
from gridlab.view.pipeline_builder import build_view_pipeline
from gridlab.world import World
from gridlab.world_builder import create_world, world_names


VERIFICATION_FAILED_TEMPLATE = """
{message}
Taken: {taken}
Remain: {remain}

## Legend

{legend}

## Status

{status}

## Grid

{grid}"""


class VerificationFailed(Exception):
    def __init__(self, message: str, taken: list[Action], remain: list[Action], views: dict[str, str]):
        taken = ', '.join(taken)
        remain = ', '.join(remain)
        message = VERIFICATION_FAILED_TEMPLATE.format(
            message=message,
            taken=taken,
            remain=remain,
            **views,
        )
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


def verify_all_solutions(report: bool = True) -> dict[str, dict[str, str]]:
    successes: dict[str, str] = {}
    failures: dict[str, str] = {}

    names = world_names()
    for name in names:
        try:
            verify_solution(world=name)
        except NotImplementedError:
            failures[name] = 'Solve not implemented'
        except VerificationFailed:
            failures[name] = 'Invalid solution'
        except Exception as e:
            failures[name] = f'Unexpected error {type(e)}("{e}")'
        else:
            successes[name] = 'ok'

    if report:
        total = len(names)
        success_rate = len(successes) / total
        failure_rate = len(failures) / total

        print(f'Success {success_rate:.2%} ({len(successes)} of {total})')
        for name, msg in successes.items():
            print(f'✅ {name}: {msg}')

        print()

        print(f'Failure {failure_rate:.2%} ({len(failures)} of {total})')
        for name, msg in failures.items():
            print(f'⛔️ {name}: {msg}')

    return {'success': successes, 'failure': failures}
