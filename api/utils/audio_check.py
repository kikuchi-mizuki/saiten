"""
音声処理機能の可用性チェックヘルパー
"""

from fastapi import HTTPException


AUDIO_PROCESSING_AVAILABLE = False

def check_audio_processing_available():
	"""音声処理機能が利用可能かチェックし、利用不可の場合は例外を発生"""
	if not AUDIO_PROCESSING_AVAILABLE:
		raise HTTPException(
			status_code=501,
			detail="音声処理機能は現在利用できません。PyTorch、SpeechBrain、pyannote.audioをインストールしてください。詳細はドキュメントを参照してください。"
		)
