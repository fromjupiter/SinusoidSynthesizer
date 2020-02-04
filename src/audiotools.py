import librosa
import scipy
import math
from scipy.signal import medfilt, butter, lfilter, find_peaks
import numpy as np

def bin_to_freq(bn, sr, n_fft):
    return bn * sr/n_fft

def mag_to_sin(amp, phi):
    return 2*amp/np.abs(complex(math.cos(phi), math.sin(phi)))

class Formant:
    def __init__(self,freq=0,mag=0,phi=0):
        self.freq = freq
        self.mag = mag
        self.phi = phi
    
    def __repr__(self):
        return str((self.freq,self.mag,self.phi))

# Implement birth-death peak matching algorithm
class FrequencyTracker:
    def __init__(self, sr, n_fft, tolerance):
        self.sr = sr
        self.n_fft = n_fft
        self.current = None
        self.tolerance = tolerance

    # detect peak using parabolic interpolation
    def find_peaks(self, frame):
        # find peaks by magnitude
        row = librosa.amplitude_to_db(np.abs(frame))
        peaks = find_peaks(row)[0]
        res = [None] * len(peaks)
        # phase
        phases = np.angle(frame)
        res = [None]*len(peaks)
        for i, x in enumerate(peaks):
            # parabolic for maglitude
            xv = 1/2 * (row[x-1] - row[x+1]) / (row[x-1] - 2 * row[x] + row[x+1]) + x
            yv = row[x] - 1/4 * (row[x-1] - row[x+1]) * (xv - x)
            # linear for phase
            if xv>x:
                phi = phases[x]+ (phases[x+1]-phases[x])/(xv-x)
            else:
                phi = phases[x-1] + (phases[x]-phases[x-1])/(xv-x+1)
            res[i] = Formant(bin_to_freq(xv, self.sr, self.n_fft), librosa.db_to_amplitude(yv), phi)
        res.sort(key=lambda x:x.mag,reverse=True)
        return res

    def trackFrame(self, frame):
        frame = sorted(frame, key=lambda x:x.freq)
        if self.current is None:
            self.current = frame
            return self.current
        i=0
        new_frame = []
        while i<len(self.current):
            j=0
            # find potential match
            while j<len(frame) and abs(self.current[i].freq-frame[j].freq)>self.tolerance*self.current[i].freq:
                j+=1
            while j<len(frame)-1 and abs(frame[j].freq-self.current[i].freq) > abs(frame[j+1].freq-self.current[i].freq):
                j+=1
                
            if j==len(frame):
                if self.current[i].mag>0:
                    new_frame.append(Formant(self.current[i].freq, 0, self.current[i].phi))
            elif j==len(frame)-1:
                new_frame.append(frame.pop(j))
            elif i<len(self.current)-1 and abs(self.current[i+1].freq-frame[j].freq)<abs(self.current[i].freq-frame[j].freq):
                if abs(self.current[i].freq-frame[j-1].freq)<self.tolerance*self.current[i].freq:
                    new_frame.append(frame.pop(j-1))
                elif self.current[i].mag>0:
                    new_frame.append(Formant(self.current[i].freq, 0, self.current[i].phi))
            else:
                new_frame.append(frame.pop(j))
            i+=1
        while len(frame)!=0:
            t = frame.pop()
            t.mag = 0
            new_frame.append(t)
        new_frame.sort(key=lambda x:x.freq)
        self.current = new_frame
        return self.current

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

# fader for frame overlapping
def linear_fader(frame_len):
    res = [0]*(frame_len)
    for i in range(int(frame_len/2)):
        res[i] = 2*i/frame_len
    for i in range(int(frame_len/2), frame_len):
        res[i] = 2*(frame_len-i)/frame_len
    return np.array(res)

def cosine_fader(frame_len):
    period = frame_len
    res = []
    for i in range(period):
        res.append((1-0.99*math.cos(2*math.pi*i/period))/2)
    return np.array(res)

def no_fader(frame_len):
    return np.ones(frame_len)
