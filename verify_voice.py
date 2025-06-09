import numpy as np
import librosa
from scipy.spatial.distance import cdist


def extract_features(file_path):
    try:
        signal, sr = librosa.load(file_path, sr=16000, mono=True)
        signal, _ = librosa.effects.trim(signal, top_db=20)

        if len(signal) < sr * 0.5:
            raise ValueError("Nagranie po usunięciu ciszy jest za krótkie.")

        # Normalizacja głośności
        signal = signal / np.max(np.abs(signal))

        mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13)
        return mfcc.T
    except Exception as e:
        print(f"Błąd podczas ekstrakcji cech: {e}")
        raise e


def dtw_distance(features1, features2):
    D = cdist(features1, features2, metric='euclidean')
    n, m = D.shape
    cost = np.zeros((n + 1, m + 1))
    cost[0, :] = np.inf
    cost[:, 0] = np.inf
    cost[0, 0] = 0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost[i, j] = D[i - 1, j - 1] + min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1])

    return cost[n, m]


def verify_voice(reference_path, test_path, threshold=900):
    try:
        ref_feat = extract_features(reference_path)
        test_feat = extract_features(test_path)

        distance = dtw_distance(ref_feat, test_feat)
        print(f"Obliczony dystans DTW: {distance}")

        return distance < threshold
    except Exception as e:
        print(f"Błąd weryfikacji: {e}")
        return False