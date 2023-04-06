try:
    import moviepy.editor
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy"])
    try:
        import moviepy.editor
    except ImportError:
        print("Failed to install moviepy. Please install it manually.")
        exit(1)

import json
import numpy
import os

def __save_frames_as_gif__(frames: numpy.ndarray, output_dir: str, gif_name: str, fps: int = 8):
    """Saves a list of frames as a gif to the given output directory.
    
    Args:
    - frames (`numpy.ndarray`): The frames to save.
    - output_dir (`str`): The output directory.
    - gif_name (`str`): The name of the gif file.
    - fps (`int`, optional): The frames per second. Defaults to `8`.
    """

    # If the output dir does not exist, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the gif file
    clip = moviepy.editor.ImageSequenceClip(list(frames), fps=fps)
    clip.write_gif(os.path.join(output_dir, gif_name + ".gif"), fps=fps)


def __frames_from_lists__(lists: list) -> numpy.ndarray:
    """Converts a list of arrays into a list of frames.
    
    Args:
    - lists (`list`): The list of arrays.

    Returns:
    - `numpy.ndarray`: The list of frames.
    """
    return [numpy.array(_list, dtype=numpy.uint8) for _list in lists]

def convert(files: 'list[str]'):
    """Converts a list of json files to gifs.

    Args:
    - files (`list[str]`): The list of json files.
    """
    for file in files:
        with open(file, "r") as f:
            json_pattern = json.load(f)

        iters = [iteration["iteration"] for iteration in json_pattern["pattern"]]

        # Generate a numpy grid for gif generation
        grids = [
            [[[0, 0, 0] for _ in range(0, 4)] for _ in range(0, 6)]
            for _ in range(0, len(iters))
        ]

        # Generate numpy array for numpy output
        np_grid = [
            [[0 for _ in range(0, 4)] for _ in range(0, 6)]
            for _ in range(0, len(iters))
        ]

        for i, iteration in enumerate(iters):
            for motor_data in iteration:
                col_coord = int(str(motor_data["coord"])[0])
                row_coord = int(str(motor_data["coord"])[1])
                amp = motor_data["amplitude"]
                grids[i][row_coord - 1][col_coord - 1] = [amp, amp, amp]
                np_grid[i][row_coord - 1][col_coord - 1] = amp

        __save_frames_as_gif__(__frames_from_lists__(grids), "gifs", file.replace(".json", ".gif"))