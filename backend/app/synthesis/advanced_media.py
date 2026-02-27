import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)


def advanced_stitch_with_crossfade(
    audio_files: list[str],
    final_output: str = "data/feed/feed_output.mp3",
    fade_duration: float = 1.0,
):
    """
    Concatenates an array of audio files using an advanced FFmpeg complex filter
    to apply crossfades between every clip. This prevents abrupt "pops" when jumping
    between podcast topics or the AI Co-Host.
    """
    if not audio_files:
        return False

    os.makedirs(os.path.dirname(final_output), exist_ok=True)

    if len(audio_files) == 1:
        # No crossfade needed for a single file
        subprocess.run(
            ["ffmpeg", "-y", "-i", audio_files[0], "-c", "copy", final_output], check=True
        )
        return True

    # Build the complex filter string for N files
    # See FFmpeg acrossfade filter documentation:
    # https://ffmpeg.org/ffmpeg-filters.html#acrossfade

    # We use a python generator to build the ffmpeg command dynamically
    inputs = []
    for f in audio_files:
        inputs.extend(["-i", f])

    filter_chains = []

    # Simple concatenation string example (if acrossfade gets too complex for N>20)
    # [0:a][1:a]acrossfade=d=1.0:c1=tri:c2=tri[a01];
    # [a01][2:a]acrossfade=d=1.0:c1=tri:c2=tri[a02]...

    last_out = "[0:a]"
    for i in range(1, len(audio_files)):
        next_in = f"[{i}:a]"
        out_node = f"[a{i}]" if i < len(audio_files) - 1 else "[aout]"

        fade_str = f"{last_out}{next_in}acrossfade=d={fade_duration}:c1=tri:c2=tri{out_node}"
        filter_chains.append(fade_str)
        last_out = out_node

    complex_filter = ";".join(filter_chains)

    command = (
        ["ffmpeg", "-y"]
        + inputs
        + ["-filter_complex", complex_filter, "-map", "[aout]", final_output]
    )

    try:
        logging.info(f"Applying crossfades to {len(audio_files)} clips...")
        subprocess.run(command, check=True, capture_output=True)
        logging.info("Advanced stitching complete.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg crossfade error: {e.stderr.decode()}")
        return False


if __name__ == "__main__":
    print("Advanced media stitching module with crossfades loaded.")
