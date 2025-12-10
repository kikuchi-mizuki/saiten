# PPT生成機能 技術仕様書

**作成日**: 2025-12-08
**対象**: Phase 2 Week 7

---

## システムアーキテクチャ

```
[Frontend: Next.js]
  ↓ HTTP/REST
[Backend: FastAPI]
  ↓
[OpenAI API] + [Supabase] + [pgvector]
```

---

## データベース設計

### professor_profile テーブル

```sql
CREATE TABLE professor_profile (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id) UNIQUE,

  -- 基本情報
  name TEXT,
  title TEXT,
  career_description TEXT,
  expertise_tags TEXT[],

  -- 話し方
  speaking_characteristics JSONB,
  common_phrases TEXT[],

  -- デザイン
  design_preferences JSONB DEFAULT '{
    "colors": {
      "primary": "#2C5F7C",
      "secondary": "#FF6B6B",
      "accent": "#F4A259",
      "background": "#F8F9FA"
    },
    "layout_style": "balanced",
    "typography": {
      "heading_font": "gothic",
      "body_font": "mincho"
    }
  }',

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### ppt_generations テーブル

```sql
CREATE TABLE ppt_generations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES auth.users(id),

  original_prompt TEXT NOT NULL,
  generated_markdown TEXT,
  edited_markdown TEXT,
  genspark_prompt TEXT,

  slide_count INTEGER,
  estimated_duration INTEGER,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 90日後自動削除
CREATE INDEX idx_ppt_created ON ppt_generations(created_at);

-- Cron job
SELECT cron.schedule(
  'cleanup-ppt-generations',
  '0 3 * * *',
  $$ DELETE FROM ppt_generations WHERE created_at < NOW() - INTERVAL '90 days'; $$
);
```

---

## バックエンド実装

### utils/ppt_generator.py

```python
async def generate_search_queries(prompt: str) -> List[str]:
    """gpt-4o-miniで検索クエリ生成"""
    response = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"以下のプロンプトから3-5個の検索クエリを生成:\n{prompt}"
        }],
        temperature=0.3,
        max_tokens=200
    )
    return parse_queries(response.choices[0].message.content)

async def search_knowledge_base(
    queries: List[str],
    user_id: str
) -> List[KnowledgeBase]:
    """ベクトル検索でナレッジ取得"""
    all_results = []
    for query in queries:
        embedding = await get_embedding(query)
        results = await supabase.rpc(
            'search_knowledge',
            {
                'query_embedding': embedding,
                'user_id': user_id,
                'limit': 7,
                'min_similarity': 0.7
            }
        ).execute()
        all_results.extend(results.data)

    # 重複排除してスコア順
    unique = {r['id']: r for r in all_results}.values()
    return sorted(unique, key=lambda x: x['similarity'], reverse=True)[:20]

async def generate_markdown_content(
    prompt: str,
    knowledge: List[dict],
    profile: dict
) -> str:
    """gpt-4oでMarkdown生成"""
    system_prompt = build_system_prompt(profile)
    knowledge_text = "\n".join([k['text'] for k in knowledge])

    response = await openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"【プロンプト】\n{prompt}\n\n【教授の知識】\n{knowledge_text}"}
        ],
        temperature=0.7,
        max_tokens=min(int(len(prompt) * 3.5), 15000),
        timeout=120
    )
    return response.choices[0].message.content

async def generate_genspark_prompt(
    markdown: str,
    profile: dict
) -> str:
    """Gensparkプロンプト組み立て

    重要な設計方針:
    1. 教授の思考を本文に統合（別枠にしない）
    2. スライドサイズを16:9で統一
    3. 各スライドに視覚要素の指示を含める
    """
    speaker_section = build_speaker_profile(profile)
    design_section = build_design_specs(profile['design_preferences'])
    # 16:9のアスペクト比指定を追加
    design_section += "\n\n### Slide Format\n- Aspect Ratio: 16:9\n- Consistent sizing across all slides"
    content_section = convert_markdown_to_genspark(markdown)
    # 視覚要素の指示を含める
    visual_guidelines = build_visual_guidelines()

    return f"""# Presentation Generation Request

{speaker_section}

{design_section}

{visual_guidelines}

{content_section}
"""
```

---

## フロントエンド実装

### app/ppt/generate/page.tsx

```typescript
'use client'

export default function PPTGeneratePage() {
  const [prompt, setPrompt] = useState('')
  const [markdown, setMarkdown] = useState('')
  const [step, setStep] = useState<'input' | 'generating' | 'editing' | 'done'>('input')

  async function handleGenerate() {
    setStep('generating')
    const response = await fetch('/api/ppt/generate-content', {
      method: 'POST',
      body: JSON.stringify({ prompt })
    })
    const data = await response.json()
    setMarkdown(data.markdown_content)
    setStep('editing')
  }

  async function handleGeneratePrompt() {
    const response = await fetch('/api/ppt/generate-genspark-prompt', {
      method: 'POST',
      body: JSON.stringify({ markdown })
    })
    const data = await response.json()
    // プロンプト表示
    setStep('done')
  }

  return (/* UI */)
}
```

---

## エラーハンドリング

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2),
    retry=retry_if_exception_type((TimeoutError, APIError))
)
async def generate_with_retry(prompt: str):
    try:
        return await generate_markdown_content(prompt)
    except TimeoutError:
        # フォールバック to gpt-4o-mini
        return await generate_with_mini(prompt)
```

---

## パフォーマンス最適化

```python
# 並列検索
tasks = [search_for_query(q) for q in queries]
results = await asyncio.gather(*tasks)

# キャッシング
@cache(ttl=300)
async def get_professor_profile(user_id):
    return await db.get_profile(user_id)
```

---

**作成者**: Claude
