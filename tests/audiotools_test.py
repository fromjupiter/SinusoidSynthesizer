import unittest
import librosa 
from synth.audiotools import Formant, FrequencyTracker, bin_to_freq

class TestFrequencyTracker(unittest.TestCase):
    def test_find_peaks(self):
        tracker = FrequencyTracker(44100, 8192, 0.1)
        frame = [0]*4097
        frame[1] = 2
        frame[2] = 5
        frame[3] = 2
        new_frame = tracker.find_peaks(frame)
        self.assertTrue(len(new_frame)==1)
        self.assertAlmostEqual(new_frame[0].mag, 5)
        self.assertAlmostEqual(new_frame[0].freq, bin_to_freq(2, tracker.sr, tracker.n_fft))

    def test_track_frames(self):
        tracker = FrequencyTracker(44100, 8192, 0.1)
        frame = []
        frame.append(Formant(1,5))
        frame.append(Formant(2,5))
        frame.append(Formant(3,5))
        tracker.trackFrame(frame)
        self.assertTrue(3==len(tracker.current))
        frame = []
        frame.append(Formant(1,2))
        frame.append(Formant(2.2,5))
        frame.append(Formant(3,4))
        tracker.trackFrame(frame)
        # verify that freq 2.2 is born, freq 2 is dead
        self.assertTrue(4==len(tracker.current))
        self.assertEqual(tracker.current[0].freq, 1)
        self.assertEqual(tracker.current[0].mag, 2)
        self.assertEqual(tracker.current[1].freq, 2)
        self.assertEqual(tracker.current[1].mag, 0)
        self.assertEqual(tracker.current[2].freq, 2.2)
        self.assertEqual(tracker.current[2].mag, 0)
        self.assertEqual(tracker.current[3].freq, 3)
        self.assertEqual(tracker.current[3].mag, 4)

        

if __name__=='__main__':
    unittest.main()
        
