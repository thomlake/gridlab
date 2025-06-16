from gridlab.action import Action
from gridlab.difficulty import get_difficulty_score
from gridlab.view.pipeline_builder import ViewMode, build_view_pipeline
from gridlab.world import World
from gridlab.world_builder import create_world, world_metadata, world_names


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
        taken_csv = ', '.join(taken)
        remain_csv = ', '.join(remain)
        message = VERIFICATION_FAILED_TEMPLATE.format(
            message=message,
            taken=taken_csv,
            remain=remain_csv,
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

    pipeline = build_view_pipeline(mode=ViewMode.TEXT)
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
            results[name] = False, f'Unexpected error {type(e).__name__}("{e}")'
        else:
            results[name] = True, 'ok'

    return results


def display_verification_statuses():
    results = verify_all_solutions()

    def post_process(ok_status: bool):
        subset = []
        for name, (ok, msg) in results.items():
            if ok == ok_status:
                metadata = world_metadata(name)
                difficulty = metadata['difficulty']
                score = metadata['difficulty_score']
                subset.append((name, difficulty, score, msg))

        return sorted(subset, key=lambda x: (x[2], x[0]))

    successes = post_process(ok_status=True)
    failures = post_process(ok_status=False)
    success_rate = len(successes) / len(results)
    failure_rate = len(failures) / len(results)

    print(f'Success {success_rate:.2%} ({len(successes)} of {len(results)})')
    for name, difficulty, _, _ in successes:
        print(f'✅ ({difficulty}) {name}')

    print()

    print(f'Failure {failure_rate:.2%} ({len(failures)} of {len(results)})')
    for name, difficulty, _, msg in failures:
        print(f'⛔️ ({difficulty}) {name}: {msg}')
