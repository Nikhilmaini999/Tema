"""AI-based music analysis engine."""

import numpy as np
import librosa
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict
import json

logger = logging.getLogger(__name__)


@dataclass
class MusicFeatures:
    """Extracted music features."""
    tempo: float
    key: str
    energy: float
    danceability: float
    valence: float  # Musical positiveness
    acousticness: float
    instrumentalness: float
    speechiness: float
    mfcc: np.ndarray  # Mel-frequency cepstral coefficients
    chroma: np.ndarray
    
    def to_dict(self) -> Dict:
        return {
            'tempo': float(self.tempo),
            'key': self.key,
            'energy': float(self.energy),
            'danceability': float(self.danceability),
            'valence': float(self.valence),
            'acousticness': float(self.acousticness),
            'instrumentalness': float(self.instrumentalness),
            'speechiness': float(self.speechiness)
        }


class MusicAnalyzer:
    """Analyze audio tracks for features and recommendations."""
    
    # Chromatic scale
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    def __init__(self, sr: int = 22050):
        """Initialize analyzer.
        
        Args:
            sr: Sample rate in Hz
        """
        self.sr = sr
    
    def analyze_file(self, audio_path: str) -> Optional[MusicFeatures]:
        """Analyze audio file and extract features.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            MusicFeatures object or None if analysis fails
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sr)
            return self.analyze_audio(y, sr)
        
        except Exception as e:
            logger.error(f"Failed to analyze {audio_path}: {e}")
            return None
    
    def analyze_audio(self, y: np.ndarray, sr: int) -> MusicFeatures:
        """Analyze audio array.
        
        Args:
            y: Audio time series
            sr: Sample rate
        
        Returns:
            MusicFeatures object
        """
        # Tempo detection
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, _ = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
        
        # Key detection (using chroma features)
        S = np.abs(librosa.stft(y))
        chroma = librosa.feature.chroma_stft(S=S, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        key_idx = np.argmax(chroma_mean)
        key = self.NOTES[key_idx]
        
        # MFCC features
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        
        # Energy
        energy = np.mean(librosa.feature.melspectrogram(y=y, sr=sr))
        
        # Spectral features
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
        
        # Zero crossing rate
        zcr = np.mean(librosa.feature.zero_crossing_rate(y))
        
        # Calculate derived features (approximations)
        danceability = self._estimate_danceability(onset_env, tempo)
        valence = self._estimate_valence(chroma_mean, spectral_centroid)
        acousticness = self._estimate_acousticness(zcr, energy)
        instrumentalness = self._estimate_instrumentalness(mfcc_mean, zcr)
        speechiness = self._estimate_speechiness(zcr, spectral_rolloff)
        
        return MusicFeatures(
            tempo=float(tempo),
            key=key,
            energy=float(energy),
            danceability=danceability,
            valence=valence,
            acousticness=acousticness,
            instrumentalness=instrumentalness,
            speechiness=speechiness,
            mfcc=mfcc_mean,
            chroma=chroma_mean
        )
    
    @staticmethod
    def _estimate_danceability(onset_env: np.ndarray, tempo: float) -> float:
        """Estimate danceability (0-1)."""
        # Regular beat detection + moderate tempo
        regularity = np.std(np.diff(onset_env))
        tempo_score = 1 - abs(tempo - 120) / 120  # Optimal at 120 BPM
        return float(np.clip((1 - regularity) * tempo_score, 0, 1))
    
    @staticmethod
    def _estimate_valence(chroma_mean: np.ndarray, spectral_centroid: float) -> float:
        """Estimate musical positiveness/valence (0-1)."""
        # Major keys and higher frequency content suggest positivity
        major_keys_energy = np.mean(chroma_mean[[0, 2, 4, 5, 7, 9, 11]])  # C, D, E, F, G, A, B
        frequency_contribution = spectral_centroid / 8000  # Normalize to audio range
        return float(np.clip((major_keys_energy * 0.7 + frequency_contribution * 0.3), 0, 1))
    
    @staticmethod
    def _estimate_acousticness(zcr: float, energy: float) -> float:
        """Estimate acousticness (0-1)."""
        # Higher ZCR and lower energy suggest acoustic instruments
        return float(np.clip(zcr * (1 - energy), 0, 1))
    
    @staticmethod
    def _estimate_instrumentalness(mfcc_mean: np.ndarray, zcr: float) -> float:
        """Estimate instrumentalness (0-1)."""
        # Lower ZCR typically means fewer vocals
        return float(np.clip(1 - zcr, 0, 1))
    
    @staticmethod
    def _estimate_speechiness(zcr: float, spectral_rolloff: float) -> float:
        """Estimate speechiness (0-1)."""
        # Higher ZCR and specific spectral characteristics suggest speech
        speech_score = zcr * (spectral_rolloff / 8000)
        return float(np.clip(speech_score, 0, 1))
