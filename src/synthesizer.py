import librosa
import yaml
import argparse
import numpy as np
import soundfile

from audiotools import *


def load_config(path):
    """
    Load the configuration from config.yaml.
    """
    return yaml.load(open('config.yaml', 'r'), Loader=yaml.SafeLoader)

def synthesize(input_path, output_path, config):
    if config is None:
        SR = 44100
        COSINE_WAVES = 10
        N_FFT = 8192
        WIN_LEN = int(N_FFT)
        HOP_LEN = int(WIN_LEN/4)
        FREQ_DELTA = 0.01
        FRAME_LEN = int(2*HOP_LEN)
    else:
        SR = config['sample_rate']
        COSINE_WAVES = config['cosine_waves']
        N_FFT = config['n_fft']
        WIN_LEN = config['window_len']
        HOP_LEN = config['hop_len']
        FREQ_TOLERANCE = config['freq_tolerance']
        FRAME_LEN = config['frame_len']

    y, sr = librosa.load(input_path,sr=SR)
    stft = librosa.stft(y,hop_length=HOP_LEN, win_length=WIN_LEN, n_fft=N_FFT, center=True)
    frames = []
    tracker = FrequencyTracker(SR, N_FFT, FREQ_TOLERANCE)
    for row in stft.T:
        peaks = tracker.find_peaks(row)
        frames.append(tracker.trackFrame(peaks[:COSINE_WAVES]))

    audio = [0]*(FRAME_LEN - HOP_LEN)
    fader = cosine_fader(FRAME_LEN)

    for df in frames:
        samples = np.zeros(FRAME_LEN)
        for tup in df:
            wav = librosa.core.tone(tup.freq, sr=SR, length=FRAME_LEN, phi=tup.phi)
            samples +=tup.mag*16/N_FFT * wav * fader
        # handle overlapping samples
        for i in range(1, FRAME_LEN - HOP_LEN +1):
            audio[-i] += samples[FRAME_LEN - HOP_LEN - i]
        # add the rest
        audio.extend(samples[-HOP_LEN:])
    print("Writing sythesized result to {}".format(output_path))
    soundfile.write(output_path, audio, SR)


parser = argparse.ArgumentParser(description='Sinusoid Synthesizer')

parser.add_argument('-i', '--input', default='./white_bellbird.wav', help='Input audio file')
parser.add_argument('-o', '--output', default='./synthesized_wbb.wav', help='Output audio path, only support WAV')
parser.add_argument('-c', '--config', default='./config.yaml', help='Config file path')

args = parser.parse_args()

input_path = args.input
output_path = args.output
config = load_config(args.config)

synthesize(input_path, output_path, config)