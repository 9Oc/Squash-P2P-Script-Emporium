"""
@author squash
Draws the waveform of a FLAC/WAV audio file with clipping highlighted.
Colors adjustable through editing hex codes.

Dependencies:
pip install soundfile numpy matplotlib
"""
import argparse
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def visualize_waveform(input_path: str | Path, output_path: str | Path):
    """
    Reads a FLAC/WAV file, draws its waveform by processing in chunks, and highlights clipped samples.
    Saves the drawn image to a png file.

    Arguments:
        input_path (str): The path to the input FLAC file.
        output_path (str): The path to save the output PNG image.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        print(f"Failed to find '{input_path}'")
        return

    try:
        print(f"Reading chunks for {input_path.name}...")
        # get file information without loading all data into memory
        # to avoid memory overflow
        info = sf.info(str(input_path))
        num_channels = info.channels
        samplerate = info.samplerate
        total_samples = info.frames

        # downsample the data to a fixed number of points for drawing
        # prevents plotting too many points for very long files
        target_points = 50000
        if total_samples > target_points:
            downsample_factor = int(total_samples / target_points)
        else:
            downsample_factor = 1

        # use a large buffer size for reading, more efficient for sf.blocks
        # use a multiple of the downsample factor to make chunking easier
        chunk_size_samples = int(samplerate * 5)
        
        # store the downsampled data and clipping status
        downsampled_data = [[] for _ in range(num_channels)]
        clipped_status = [[] for _ in range(num_channels)]
        
        # process the audio file in chunks
        with sf.SoundFile(str(input_path), 'r') as f:
            for block in f.blocks(blocksize=chunk_size_samples, dtype='float32'):
                if block.ndim == 1:
                    block = block.reshape(-1, 1)

                # add the data from this block
                for i, channel_data in enumerate(block.T):
                    for j in range(0, len(channel_data), downsample_factor):
                        window = channel_data[j:j+downsample_factor]
                        if len(window) > 0:
                            # use min/max to represent the waveform range
                            downsampled_data[i].append(np.max(window))
                            downsampled_data[i].append(np.min(window))
                            
                            # check for clipping
                            is_clipped = np.any(np.abs(window) >= 1.0 - 1e-6)
                            clipped_status[i].append(is_clipped)
                            clipped_status[i].append(is_clipped) # add it twice for the min/max pair
        
        print(f"Plotting waveforms for {input_path.name}...")
        # create the figure with downsampled data
        fig, axes = plt.subplots(
            nrows=num_channels, 
            ncols=1, 
            figsize=(17, 2 * num_channels), 
            sharex=True,
            facecolor='#141414'
        )

        if num_channels == 1:
            axes = [axes]
        
        # set the title for the figure
        plt.suptitle(input_path.name, fontsize=16, color='#EFEFEF')
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        total_downsampled_points = len(downsampled_data[0])
        total_duration = total_samples / samplerate
        time_downsampled = np.linspace(0, total_duration, total_downsampled_points)

        for i, ax in enumerate(axes):
            ax.set_facecolor('#141414')
            ax.set_yticks([])
            ax.set_xticks([])
            for spine in ax.spines.values():
                spine.set_edgecolor('#7393B3')
            ax.set_xlim(time_downsampled[0], time_downsampled[-1])
            channel_data = np.array(downsampled_data[i])
            channel_clipped = np.array(clipped_status[i])

            # plot the non-clipped waveforms
            non_clipped_data = np.where(channel_clipped, np.nan, channel_data)
            ax.plot(time_downsampled, non_clipped_data, color='#A9A9A9', linewidth=0.5) # EFEFEF

            # plot clipped samples
            clipped_data = np.where(~channel_clipped, np.nan, channel_data)
            ax.plot(time_downsampled, clipped_data, color='red', linewidth=0.5)
            
            ax.fill_between(time_downsampled, 0, non_clipped_data, color='#A9A9A9', alpha=0.3)
            ax.fill_between(time_downsampled, 0, clipped_data, color='red', alpha=0.5)
            
            ax.set_ylim(-1.1, 1.1)
            ax.set_title(f'Channel {i + 1}', color='#EFEFEF')
            ax.grid(True)

        # save the image
        plt.savefig(output_path, dpi=120)
        print(f"Successfully generated waveform image: '{output_path}'")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # close the plot to free up memory
        plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize a FLAC/WAV audio waveforms with clipping highlighted.')
    parser.add_argument('-i', '--input', type=str, required=True, default='example.flac',
                        help='Path to the input FLAC/WAV file.')
    parser.add_argument('-o', '--output', type=str, required=False, default='waveform_with_clipping.png',
                        help='Path to the output PNG image.')
    
    args = parser.parse_args()

    # create a dummy FLAC file for demonstration if the given file does not exist
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"'{args.input}' not found. Generating a dummy FLAC file with clipping for demonstration...")
        samplerate = 44100
        duration = 10.0  # seconds, a bit longer to show chunking
        frequency = 440  # Hz
        time_points = np.linspace(0., duration, int(samplerate * duration))
        
        sine_wave = np.sin(2. * np.pi * frequency * time_points)
        clipped_wave = np.clip(sine_wave * 1.5, -1.0, 1.0)
        
        stereo_data = np.vstack([sine_wave, clipped_wave]).T
        sf.write(args.input, stereo_data, samplerate)

    visualize_waveform(args.input, args.output)
