from gridlab.action import Action
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


def verify_all_solutions() -> dict[str, tuple[bool, str]]:
    results: dict[str, tuple[bool, str]] = {}

    names = world_names()
    for name in names:
        try:
            verify_solution(world=name)
        except NotImplementedError:
            results[name] = False, 'Solve not implemented'
        except VerificationFailed:
            results[name] = False, 'Invalid solution'
        except Exception as e:
            results[name] = False, f'Unexpected error {type(e)}("{e}")'
        else:
            results[name] = True, 'ok'

    return results


def display_verification_statuses():
    results = verify_all_solutions()
    successes = {name: msg for name, (ok, msg) in results.items() if ok}
    failures = {name: msg for name, (ok, msg) in results.items() if not ok}
    success_rate = len(successes) / len(results)
    failure_rate = len(failures) / len(results)

    print(f'Success {success_rate:.2%} ({len(successes)} of {len(results)})')
    for name, msg in successes.items():
        print(f'✅ {name}: {msg}')

    print()

    print(f'Failure {failure_rate:.2%} ({len(failures)} of {len(results)})')
    for name, msg in failures.items():
        print(f'⛔️ {name}: {msg}')
