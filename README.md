# SinusoidSynthesizer
Additive Sinusoid Sythesizer from scratch



## Getting started
    ./synthesize.py -i YOUR_INPUT_AUDIO_PATH -o OUTPUT_PATH -c YOUR_CONFIG_YAML_PATH


## Overview

Fourier Transformation shows that any non-period signal can be represented as a infinite number of sinusoids. This project tries to use a finite number of sinusoids to synthesize a given audio. The idea is inspired by [this paper](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1164910&tag=1).

The idea behind sinusoid synthesizer is simple: we split the audio into small frames and each frame can be simulated by a set of sinusoids. There is a parameter /**COSINE_WAVES**/ in config.yaml which tells the synthesizer how many sinusoids AT MOST can be used for each frame.

Our synthesize function basically contains four steps:
1. Short Fast Fourier Transform
2. Peak Detection
3. Frequency Tracking
4. Overlap-Add

### Short Fast Fourier Transform
To better understand the audio, we need more information than just the audio wave. SFFT gives us a M*N complex matrix (M is freq bins, N is frames) which is a good representation of how the input audio approximately is in the frequency domain.

### Peak Detection
Then we want to find all the major frequencies that best describe the input audio. A simple way is to find all local peaks in the SFFT frame but the result is not accurate enough. A better approximation is to use parabolic interpolation to find the frequency with max magnitude and use linear interpolation to find its phase. Details can be found [here](https://ccrma.stanford.edu/~jos/parshl/Peak_Detection_Steps_3.html)

### Frequency Tracking
After selecting the main frequencies for each frame, we want to match the frequencies between frames so that they sound "natural". This project implements a noise-proof birth-death algorithm to track frequencies. Refer to section IV "FRAME-TO-FRAME PEAK MATCHING" in [this paper](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1164910&tag=1)

### Overlap Add
Now All we have left is to generate a bunch of sinusoids using the frequencies we found and add them together. To avoid click-noises between frames, we adopt the overlap-add method. Each frame will be multiplied a temporal function (we call it shader)before adding to keep the magnitude at 
Refer to [Wikipedia](https://en.wikipedia.org/wiki/Overlap%E2%80%93add_method)


## Experiments
There are two demo audio files included in this project: white_bellbird.wav and tinkle.wav. Each audio clip has its own natures thus we need different hyperparameters to get the best result.
The white bellbird audio requires high frequency resolution while the tinkling audio requires high time resolution. Thus choosing different n_fft and window_size is necessary. We found that {n_fft:8192, window_size:8192} works well for white_bellbird and {n_fft:1024, window_size:512} works well for the tinkling sound.