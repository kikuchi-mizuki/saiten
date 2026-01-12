"""
話者識別（Speaker Diarization）ユーティリティ

pyannote.audioを使用して音声から話者を識別し、
各話者の発言時間帯を特定します。
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class SpeakerSegment:
    """話者セグメント（発言の時間帯）"""

    def __init__(self, speaker_id: str, start: float, end: float, text: Optional[str] = None):
        self.speaker_id = speaker_id  # 例: "SPEAKER_00"
        self.start = start  # 開始時刻（秒）
        self.end = end  # 終了時刻（秒）
        self.text = text  # テキスト（Whisperの結果とマッチング後）
        self.duration = end - start

    def __repr__(self):
        return f"SpeakerSegment({self.speaker_id}, {self.start:.1f}s-{self.end:.1f}s, {self.duration:.1f}s)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "speaker_id": self.speaker_id,
            "start": self.start,
            "end": self.end,
            "duration": self.duration,
            "text": self.text
        }


class SpeakerDiarization:
    """話者識別クラス"""

    def __init__(self):
        """初期化"""
        self.pipeline = None
        self.hf_token = os.environ.get("HUGGING_FACE_TOKEN")

        if not self.hf_token:
            logger.warning("HUGGING_FACE_TOKEN not set. Speaker diarization will not work.")

        logger.info("SpeakerDiarization initialized")

    def _load_pipeline(self):
        """遅延ロード：初回使用時にpyannote.audioパイプラインをロード"""
        if self.pipeline is not None:
            return

        if not self.hf_token:
            raise ValueError("HUGGING_FACE_TOKEN environment variable is required for speaker diarization")

        try:
            from pyannote.audio import Pipeline

            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.hf_token
            )

            logger.info("pyannote.audio pipeline loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load pyannote.audio pipeline: {e}")
            raise

    def identify_speakers(self, audio_path: str) -> List[SpeakerSegment]:
        """
        音声ファイルから話者を識別

        Args:
            audio_path: 音声ファイルのパス

        Returns:
            SpeakerSegmentのリスト
        """
        self._load_pipeline()

        try:
            logger.info(f"Running speaker diarization on {audio_path}")

            # 話者識別を実行
            diarization = self.pipeline(audio_path)

            # 結果を解析
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segment = SpeakerSegment(
                    speaker_id=speaker,
                    start=turn.start,
                    end=turn.end
                )
                segments.append(segment)

            logger.info(f"Identified {len(segments)} speaker segments from {len(set(s.speaker_id for s in segments))} speakers")

            return segments

        except Exception as e:
            logger.error(f"Failed to identify speakers: {e}")
            raise

    def get_speaker_durations(self, segments: List[SpeakerSegment]) -> Dict[str, float]:
        """
        各話者の発言時間を計算

        Args:
            segments: SpeakerSegmentのリスト

        Returns:
            {speaker_id: total_duration_seconds}
        """
        durations = {}
        for segment in segments:
            durations[segment.speaker_id] = durations.get(segment.speaker_id, 0) + segment.duration

        return durations

    def identify_longest_speaker(self, segments: List[SpeakerSegment]) -> str:
        """
        最も発言時間が長い話者を特定（教授の自動判定用）

        Args:
            segments: SpeakerSegmentのリスト

        Returns:
            最も発言時間が長い話者のID
        """
        durations = self.get_speaker_durations(segments)

        if not durations:
            raise ValueError("No speakers found")

        longest_speaker = max(durations.items(), key=lambda x: x[1])

        logger.info(f"Longest speaker: {longest_speaker[0]} ({longest_speaker[1]:.1f}s, {longest_speaker[1]/sum(durations.values())*100:.1f}%)")

        return longest_speaker[0]

    def filter_segments_by_speaker(
        self,
        segments: List[SpeakerSegment],
        speaker_id: str
    ) -> List[SpeakerSegment]:
        """
        特定の話者のセグメントのみを抽出

        Args:
            segments: SpeakerSegmentのリスト
            speaker_id: 抽出する話者のID

        Returns:
            フィルタリングされたセグメントのリスト
        """
        filtered = [s for s in segments if s.speaker_id == speaker_id]
        logger.info(f"Filtered {len(filtered)} segments for speaker {speaker_id}")
        return filtered

    def match_segments_with_transcript(
        self,
        segments: List[SpeakerSegment],
        whisper_segments: List[Dict[str, Any]]
    ) -> List[SpeakerSegment]:
        """
        話者セグメントとWhisperの文字起こしセグメントをマッチング

        Args:
            segments: SpeakerSegmentのリスト
            whisper_segments: Whisperの文字起こし結果（タイムスタンプ付き）
                例: [{"start": 0.0, "end": 3.5, "text": "こんにちは"}, ...]

        Returns:
            テキストが付与されたSpeakerSegmentのリスト
        """
        # 各Whisperセグメントに対して、最も重複する話者セグメントを見つける
        for whisper_seg in whisper_segments:
            w_start = whisper_seg["start"]
            w_end = whisper_seg["end"]
            w_text = whisper_seg["text"]

            # 重複する話者セグメントを探す
            best_segment = None
            best_overlap = 0

            for speaker_seg in segments:
                # 重複時間を計算
                overlap_start = max(w_start, speaker_seg.start)
                overlap_end = min(w_end, speaker_seg.end)
                overlap = max(0, overlap_end - overlap_start)

                if overlap > best_overlap:
                    best_overlap = overlap
                    best_segment = speaker_seg

            # 最も重複するセグメントにテキストを追加
            if best_segment is not None:
                if best_segment.text is None:
                    best_segment.text = w_text
                else:
                    best_segment.text += " " + w_text

        logger.info(f"Matched {len(whisper_segments)} transcripts with speaker segments")

        return segments

    def extract_speaker_text(
        self,
        segments: List[SpeakerSegment],
        speaker_id: str
    ) -> str:
        """
        特定の話者のテキストのみを抽出・結合

        Args:
            segments: テキストが付与されたSpeakerSegmentのリスト
            speaker_id: 抽出する話者のID

        Returns:
            結合されたテキスト
        """
        speaker_segments = self.filter_segments_by_speaker(segments, speaker_id)

        # テキストを結合
        texts = [s.text for s in speaker_segments if s.text]
        combined_text = " ".join(texts)

        logger.info(f"Extracted {len(texts)} text segments for speaker {speaker_id}, total length: {len(combined_text)}")

        return combined_text

    def get_speaker_statistics(self, segments: List[SpeakerSegment]) -> Dict[str, Any]:
        """
        話者の統計情報を取得

        Args:
            segments: SpeakerSegmentのリスト

        Returns:
            統計情報の辞書
        """
        durations = self.get_speaker_durations(segments)
        total_duration = sum(durations.values())

        speakers_info = []
        for speaker_id, duration in sorted(durations.items(), key=lambda x: x[1], reverse=True):
            percentage = (duration / total_duration * 100) if total_duration > 0 else 0
            segment_count = len([s for s in segments if s.speaker_id == speaker_id])

            speakers_info.append({
                "speaker_id": speaker_id,
                "duration_seconds": round(duration, 1),
                "percentage": round(percentage, 1),
                "segment_count": segment_count
            })

        return {
            "total_speakers": len(durations),
            "total_duration_seconds": round(total_duration, 1),
            "speakers": speakers_info
        }


# シングルトンインスタンス
_diarization_instance: Optional[SpeakerDiarization] = None


def get_speaker_diarization() -> SpeakerDiarization:
    """
    SpeakerDiarizationのシングルトンインスタンスを取得

    Returns:
        SpeakerDiarization instance
    """
    global _diarization_instance
    if _diarization_instance is None:
        _diarization_instance = SpeakerDiarization()
    return _diarization_instance
