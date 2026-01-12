"""
声紋抽出ユーティリティ

SpeechBrainを使用して音声ファイルから声紋（voiceprint/speaker embedding）を抽出します。
"""

import os
import logging
from typing import Optional, Tuple, Dict, Any
import numpy as np
import torch
import torchaudio
from pathlib import Path

logger = logging.getLogger(__name__)


class VoiceprintExtractor:
    """声紋抽出クラス"""

    def __init__(self):
        """初期化。SpeechBrainモデルをロード"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.sample_rate = 16000  # SpeechBrainの推奨サンプルレート

        logger.info(f"VoiceprintExtractor initialized on device: {self.device}")

    def _load_model(self):
        """遅延ロード：初回使用時にモデルをロード"""
        if self.model is not None:
            return

        try:
            from speechbrain.pretrained import EncoderClassifier

            # ECAPA-TDNN モデルをロード（192次元の声紋ベクトル）
            self.model = EncoderClassifier.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
                savedir="models/speaker_recognition",
                run_opts={"device": self.device}
            )
            logger.info("SpeechBrain ECAPA-TDNN model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load SpeechBrain model: {e}")
            raise

    def _load_audio(self, audio_path: str) -> Tuple[torch.Tensor, int]:
        """
        音声ファイルをロード

        Args:
            audio_path: 音声ファイルのパス

        Returns:
            (waveform, sample_rate): 波形データとサンプルレート
        """
        try:
            waveform, sr = torchaudio.load(audio_path)

            # ステレオをモノラルに変換
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)

            # サンプルレートを16kHzにリサンプリング
            if sr != self.sample_rate:
                resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
                waveform = resampler(waveform)
                sr = self.sample_rate

            return waveform, sr
        except Exception as e:
            logger.error(f"Failed to load audio file {audio_path}: {e}")
            raise

    def extract_voiceprint(
        self,
        audio_path: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> np.ndarray:
        """
        音声ファイルから声紋を抽出

        Args:
            audio_path: 音声ファイルのパス
            start_time: 抽出開始時刻（秒）。Noneの場合は先頭から
            end_time: 抽出終了時刻（秒）。Noneの場合は最後まで

        Returns:
            192次元の声紋ベクトル（numpy array）
        """
        self._load_model()

        try:
            # 音声をロード
            waveform, sr = self._load_audio(audio_path)

            # 時間範囲を指定された場合はトリミング
            if start_time is not None or end_time is not None:
                start_sample = int(start_time * sr) if start_time is not None else 0
                end_sample = int(end_time * sr) if end_time is not None else waveform.shape[1]
                waveform = waveform[:, start_sample:end_sample]

            # 声紋を抽出
            with torch.no_grad():
                waveform = waveform.to(self.device)
                embedding = self.model.encode_batch(waveform)
                embedding_np = embedding.squeeze().cpu().numpy()

            # 正規化（ユニットベクトルに）
            embedding_np = embedding_np / np.linalg.norm(embedding_np)

            logger.info(f"Voiceprint extracted: shape={embedding_np.shape}, norm={np.linalg.norm(embedding_np):.4f}")

            return embedding_np

        except Exception as e:
            logger.error(f"Failed to extract voiceprint from {audio_path}: {e}")
            raise

    def compare_voiceprints(
        self,
        voiceprint1: np.ndarray,
        voiceprint2: np.ndarray
    ) -> float:
        """
        2つの声紋を比較

        Args:
            voiceprint1: 声紋1（192次元）
            voiceprint2: 声紋2（192次元）

        Returns:
            類似度スコア（0.0-1.0）。1.0に近いほど類似
        """
        # コサイン類似度を計算
        similarity = np.dot(voiceprint1, voiceprint2) / (
            np.linalg.norm(voiceprint1) * np.linalg.norm(voiceprint2)
        )

        # -1から1の範囲を0から1にスケール
        similarity = (similarity + 1.0) / 2.0

        return float(similarity)

    def merge_voiceprints(
        self,
        voiceprints: list[np.ndarray],
        weights: Optional[list[float]] = None
    ) -> np.ndarray:
        """
        複数の声紋を統合（継続学習用）

        Args:
            voiceprints: 声紋のリスト
            weights: 各声紋の重み。Noneの場合は均等

        Returns:
            統合された声紋ベクトル
        """
        if not voiceprints:
            raise ValueError("voiceprints list is empty")

        if weights is None:
            weights = [1.0] * len(voiceprints)

        if len(voiceprints) != len(weights):
            raise ValueError("voiceprints and weights must have the same length")

        # 重み付き平均
        voiceprints_array = np.array(voiceprints)
        weights_array = np.array(weights).reshape(-1, 1)
        merged = np.average(voiceprints_array, axis=0, weights=weights_array.flatten())

        # 正規化
        merged = merged / np.linalg.norm(merged)

        logger.info(f"Merged {len(voiceprints)} voiceprints into one")

        return merged

    def get_audio_duration(self, audio_path: str) -> int:
        """
        音声ファイルの長さを取得

        Args:
            audio_path: 音声ファイルのパス

        Returns:
            音声の長さ（秒）
        """
        try:
            waveform, sr = self._load_audio(audio_path)
            duration_seconds = int(waveform.shape[1] / sr)
            return duration_seconds
        except Exception as e:
            logger.error(f"Failed to get audio duration: {e}")
            raise


# シングルトンインスタンス
_extractor_instance: Optional[VoiceprintExtractor] = None


def get_voiceprint_extractor() -> VoiceprintExtractor:
    """
    VoiceprintExtractorのシングルトンインスタンスを取得

    Returns:
        VoiceprintExtractor instance
    """
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = VoiceprintExtractor()
    return _extractor_instance
