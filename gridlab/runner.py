from gridlab.action import Action
from gridlab.view import TextDescription, TextGrid
# from gridlab.visuals import Style
from gridlab.world import World


def get_action() -> Action | None:
    while True:
        cmd = input("Enter action (up/down/left/right) or 'quit': ").strip()[0].lower()
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
        world: World,
        describe: bool = False,
        draw_grid: bool = True,
        symbols: str = '04',
        grid_style: str = 'fancy',
):
    world.reset()

    text_view = TextGrid(symbols=symbols)

    while True:
        legend = gridlab.format_legend(world, style='plain')
        status = gridlab.format_status(world, style='plain')
        grid = gridlab.format_grid(world, style='plain')

        grid = text_view.format_grid(world, style=grid_style)
        print(grid)
        if world.state.is_finished:
            break

        action = get_action()
        if action is None:
            world.state.terminated = True
        else:
            world.step(player_action=action)

    # views = []
    # if describe:
    #     views.append(TextDescription())

    # if draw_grid:
    #     views.append(TextGrid())

    # while True:
    #     s = '\n\n'.join(view(world) for view in views)
    #     print(s)
    #     if world.state.is_finished:
    #         break

    #     action = get_action()
    #     if action is None:
    #         world.state.terminated = True
    #     else:
    #         world.step(player_action=action)


"""
#####
#.X.#
#...#
#=e.#
#.#.#
#.@.#
#####
"""

"""
|||||
|.X.|
|...|
|=e.|
|.|.|
|.@.|
|||||
"""

"""
|||||
|.@.|
|.|.|
|=e.|
|...|
|.X.|
|||||
"""
