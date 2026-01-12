"""
声紋管理・音声識別のAPIエンドポイント
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Dict, List, Optional
import tempfile
import os
import numpy as np
from datetime import datetime

from utils.voiceprint_extractor import get_voiceprint_extractor
from utils.speaker_diarization import get_speaker_diarization

# このファイルは main.py から import されることを想定
router = APIRouter(prefix="/voiceprint", tags=["voiceprint"])


class VoiceprintCreate(BaseModel):
	"""声紋登録リクエスト"""
	voiceprint_name: str
	audio_duration_seconds: int
	embedding: List[float]
	confidence_score: Optional[float] = None
	metadata: Optional[Dict] = None


class VoiceprintResponse(BaseModel):
	"""声紋レスポンス"""
	id: str
	user_id: str
	voiceprint_name: str
	audio_duration_seconds: int
	sample_count: int
	confidence_score: Optional[float]
	metadata: Optional[Dict]
	created_at: str
	updated_at: str
	is_active: bool


@router.post("/register")
async def register_voiceprint(
	file: UploadFile = File(...),
	voiceprint_name: str = "",
	supabase=None,
	user: dict = None
):
	"""
	教授の声紋を登録

	音声ファイルから声紋を抽出し、データベースに保存します。
	初回登録後、以降の音声アップロードで自動識別に使用されます。
	"""
	if not supabase:
		raise HTTPException(status_code=500, detail="Supabaseが設定されていません")

	temp_audio_path = None

	try:
		# 音声ファイルを一時保存
		with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
			content = await file.read()
			tmp.write(content)
			temp_audio_path = tmp.name

		print(f"🎤 声紋登録開始: {file.filename}")

		# 声紋抽出
		extractor = get_voiceprint_extractor()
		embedding = extractor.extract_voiceprint(temp_audio_path)
		duration = extractor.get_audio_duration(temp_audio_path)

		# 声紋名（未指定の場合はタイムスタンプ）
		if not voiceprint_name:
			voiceprint_name = f"教授の声_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

		# データベースに保存
		voiceprint_data = {
			"user_id": user["id"],
			"voiceprint_name": voiceprint_name,
			"embedding": embedding.tolist(),
			"audio_duration_seconds": duration,
			"sample_count": 1,
			"confidence_score": 0.95,  # 初回登録時は0.95
			"metadata": {
				"filename": file.filename,
				"registered_at": datetime.now().isoformat()
			},
			"is_active": True
		}

		response = supabase.table("professor_voiceprints").insert(voiceprint_data).execute()

		print(f"✅ 声紋登録完了: {voiceprint_name} (duration: {duration}s)")

		return {
			"success": True,
			"message": "声紋を登録しました",
			"voiceprint_id": response.data[0]["id"],
			"voiceprint_name": voiceprint_name,
			"audio_duration_seconds": duration,
			"confidence_score": 0.95
		}

	except Exception as e:
		print(f"❌ 声紋登録エラー: {e}")
		raise HTTPException(status_code=500, detail=f"声紋の登録に失敗しました: {str(e)}")

	finally:
		# 一時ファイルを削除
		if temp_audio_path and os.path.exists(temp_audio_path):
			os.unlink(temp_audio_path)


@router.get("/list")
async def list_voiceprints(supabase=None, user: dict = None):
	"""
	登録済み声紋のリストを取得
	"""
	if not supabase:
		raise HTTPException(status_code=500, detail="Supabaseが設定されていません")

	try:
		response = supabase.table("professor_voiceprints") \
			.select("*") \
			.eq("user_id", user["id"]) \
			.order("created_at", desc=True) \
			.execute()

		return {
			"success": True,
			"voiceprints": response.data
		}

	except Exception as e:
		raise HTTPException(status_code=500, detail=f"声紋リストの取得に失敗しました: {str(e)}")


@router.delete("/{voiceprint_id}")
async def delete_voiceprint(voiceprint_id: str, supabase=None, user: dict = None):
	"""
	声紋を削除
	"""
	if not supabase:
		raise HTTPException(status_code=500, detail="Supabaseが設定されていません")

	try:
		# ユーザーの声紋かチェック
		check_response = supabase.table("professor_voiceprints") \
			.select("id") \
			.eq("id", voiceprint_id) \
			.eq("user_id", user["id"]) \
			.execute()

		if not check_response.data:
			raise HTTPException(status_code=404, detail="声紋が見つかりません")

		# 削除
		supabase.table("professor_voiceprints").delete().eq("id", voiceprint_id).execute()

		return {
			"success": True,
			"message": "声紋を削除しました"
		}

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"声紋の削除に失敗しました: {str(e)}")


@router.post("/identify-speakers")
async def identify_speakers_endpoint(
	file: UploadFile = File(...),
	user: dict = None
):
	"""
	音声ファイルから話者を識別

	pyannote.audioを使用して音声から話者を識別し、
	各話者の発言時間帯を特定します。
	"""
	temp_audio_path = None

	try:
		# 音声ファイルを一時保存
		with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
			content = await file.read()
			tmp.write(content)
			temp_audio_path = tmp.name

		print(f"🔍 話者識別開始: {file.filename}")

		# 話者識別
		diarization = get_speaker_diarization()
		segments = diarization.identify_speakers(temp_audio_path)
		statistics = diarization.get_speaker_statistics(segments)

		print(f"✅ 話者識別完了: {statistics['total_speakers']}人検出")

		return {
			"success": True,
			"filename": file.filename,
			"statistics": statistics,
			"segments": [s.to_dict() for s in segments]
		}

	except Exception as e:
		print(f"❌ 話者識別エラー: {e}")
		raise HTTPException(status_code=500, detail=f"話者識別に失敗しました: {str(e)}")

	finally:
		# 一時ファイルを削除
		if temp_audio_path and os.path.exists(temp_audio_path):
			os.unlink(temp_audio_path)


@router.post("/extract-professor-speech")
async def extract_professor_speech(
	file: UploadFile = File(...),
	use_voiceprint: bool = True,
	supabase=None,
	user: dict = None
):
	"""
	音声ファイルから教授の発言のみを抽出

	1. 話者識別（pyannote.audio）
	2. 各話者の声紋を抽出
	3. 登録済み声紋と照合して教授を特定
	4. Whisper APIで文字起こし
	5. 教授の発言のみを返す
	"""
	if not supabase:
		raise HTTPException(status_code=500, detail="Supabaseが設定されていません")

	temp_audio_path = None

	try:
		from openai import OpenAI
		openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

		# 音声ファイルを一時保存
		with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
			content = await file.read()
			tmp.write(content)
			temp_audio_path = tmp.name

		print(f"🎤 教授音声抽出開始: {file.filename}")

		# ステップ1: 話者識別
		print("📊 Step 1/5: 話者識別中...")
		diarization = get_speaker_diarization()
		segments = diarization.identify_speakers(temp_audio_path)
		statistics = diarization.get_speaker_statistics(segments)

		print(f"✅ {statistics['total_speakers']}人の話者を検出")

		# ステップ2: 教授を特定
		print("🔍 Step 2/5: 教授を特定中...")
		professor_speaker_id = None
		best_match_score = 0.0

		if use_voiceprint:
			# 登録済み声紋と照合
			voiceprints_response = supabase.table("professor_voiceprints") \
				.select("*") \
				.eq("user_id", user["id"]) \
				.eq("is_active", True) \
				.order("created_at", desc=True) \
				.limit(1) \
				.execute()

			if voiceprints_response.data:
				# 登録済み声紋がある場合
				registered_voiceprint = voiceprints_response.data[0]
				registered_embedding = np.array(registered_voiceprint["embedding"])

				extractor = get_voiceprint_extractor()

				# 各話者の声紋を抽出して照合
				best_match_speaker = None

				for speaker_info in statistics["speakers"]:
					speaker_id = speaker_info["speaker_id"]
					speaker_segments = diarization.filter_segments_by_speaker(segments, speaker_id)

					# 最初の3セグメントから声紋を抽出（代表的な声紋を取得）
					speaker_embeddings = []
					for seg in speaker_segments[:3]:
						try:
							embedding = extractor.extract_voiceprint(
								temp_audio_path,
								start_time=seg.start,
								end_time=seg.end
							)
							speaker_embeddings.append(embedding)
						except:
							continue

					if speaker_embeddings:
						# 平均声紋を計算
						avg_embedding = extractor.merge_voiceprints(speaker_embeddings)

						# 登録済み声紋と照合
						similarity = extractor.compare_voiceprints(registered_embedding, avg_embedding)

						print(f"  - {speaker_id}: 類似度 {similarity:.2%}")

						if similarity > best_match_score:
							best_match_score = similarity
							best_match_speaker = speaker_id

				# 閾値以上なら教授と判定
				if best_match_score >= 0.75:
					professor_speaker_id = best_match_speaker
					print(f"✅ 声紋照合成功: {professor_speaker_id} (類似度: {best_match_score:.2%})")
				else:
					print(f"⚠️ 声紋照合失敗: 最高類似度 {best_match_score:.2%} < 75%")

		# 声紋照合に失敗した場合は最も発言時間が長い話者を教授と判定
		if professor_speaker_id is None:
			professor_speaker_id = diarization.identify_longest_speaker(segments)
			print(f"ℹ️ 発言時間ベースで判定: {professor_speaker_id}")

		# ステップ3: Whisper APIで文字起こし
		print("📝 Step 3/5: Whisper APIで文字起こし中...")
		with open(temp_audio_path, "rb") as audio_file:
			transcript = openai_client.audio.transcriptions.create(
				model="whisper-1",
				file=audio_file,
				language="ja",
				response_format="verbose_json",
				timestamp_granularities=["segment"]
			)

		whisper_segments = [
			{
				"start": seg["start"],
				"end": seg["end"],
				"text": seg["text"]
			}
			for seg in transcript.segments
		]

		print(f"✅ 文字起こし完了: {len(whisper_segments)}セグメント")

		# ステップ4: 話者セグメントとWhisperセグメントをマッチング
		print("🔗 Step 4/5: セグメントをマッチング中...")
		segments_with_text = diarization.match_segments_with_transcript(segments, whisper_segments)

		# ステップ5: 教授の発言のみを抽出
		print("✂️ Step 5/5: 教授の発言を抽出中...")
		professor_text = diarization.extract_speaker_text(segments_with_text, professor_speaker_id)

		print(f"✅ 教授音声抽出完了: {len(professor_text)}文字")

		return {
			"success": True,
			"filename": file.filename,
			"professor_speaker_id": professor_speaker_id,
			"professor_text": professor_text,
			"text_length": len(professor_text),
			"statistics": statistics,
			"match_method": "voiceprint" if use_voiceprint and best_match_score >= 0.75 else "longest_speaker",
			"match_score": best_match_score if use_voiceprint else None
		}

	except Exception as e:
		print(f"❌ 教授音声抽出エラー: {e}")
		import traceback
		traceback.print_exc()
		raise HTTPException(status_code=500, detail=f"教授音声の抽出に失敗しました: {str(e)}")

	finally:
		# 一時ファイルを削除
		if temp_audio_path and os.path.exists(temp_audio_path):
			os.unlink(temp_audio_path)
