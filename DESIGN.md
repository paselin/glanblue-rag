# グランブルーファンタジー Agent RAGシステム 設計書

## 1. システム概要

### 1.1 目的
OpenAI互換APIを利用して、グランブルーファンタジー（グラブル）の攻略情報を取得・分析し、ユーザーの質問に対して的確な攻略情報を提供するAgent RAGシステム。

### 1.2 主な機能
- グラブルの攻略情報（キャラクター、武器、編成、クエスト等）の収集と保存
- ベクトルデータベースを用いた類似情報検索
- LLMエージェントによる質問応答と攻略アドバイス
- リアルタイム情報の更新・追加

## 2. システムアーキテクチャ

### 2.1 全体構成
```
┌─────────────┐
│   ユーザー   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│      Agent RAG システム              │
│  ┌──────────────────────────────┐  │
│  │    Agent Layer (LLM)         │  │
│  │  - Query Understanding       │  │
│  │  - Response Generation       │  │
│  │  - Tool Selection            │  │
│  └────────┬─────────────────────┘  │
│           │                         │
│  ┌────────▼─────────────────────┐  │
│  │    RAG Core                  │  │
│  │  - Retrieval Engine          │  │
│  │  - Re-ranking                │  │
│  │  - Context Management        │  │
│  └────────┬─────────────────────┘  │
│           │                         │
│  ┌────────▼─────────────────────┐  │
│  │    Data Layer                │  │
│  │  - Vector DB (Chroma/Qdrant) │  │
│  │  - Document Store            │  │
│  │  - Cache Layer               │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   External Data Sources             │
│  - グラブル攻略Wiki                  │
│  - GameWith / Game8                 │
│  - 公式情報                          │
└─────────────────────────────────────┘
```

### 2.2 技術スタック

#### バックエンド
- **言語**: Python 3.11+
- **フレームワーク**: FastAPI
- **LLM統合**: LangChain / LlamaIndex
- **ベクトルDB**: ChromaDB / Qdrant
- **Embeddings**: OpenAI text-embedding-3-small / text-embedding-3-large

#### データ処理
- **Webスクレイピング**: BeautifulSoup4, Playwright
- **データ処理**: Pandas, NumPy
- **文書分割**: LangChain TextSplitters

#### インフラ
- **コンテナ**: Docker / Docker Compose
- **キャッシュ**: Redis
- **データベース**: PostgreSQL (メタデータ管理)

## 3. データモデル

### 3.1 Document Structure
```python
{
  "id": "uuid",
  "type": "character|weapon|summon|quest|party_composition",
  "name": "キャラクター/武器名",
  "content": "詳細情報",
  "metadata": {
    "rarity": "SSR|SR|R",
    "element": "火|水|土|風|光|闇",
    "weapon_type": "剣|杖|槍|...",
    "tier": "最上位|上位|中位|...",
    "updated_at": "2026-04-13",
    "source_url": "https://...",
    "tags": ["初心者向け", "高難易度", "フルオート"]
  },
  "embedding": [0.123, 0.456, ...],
  "chunk_index": 0
}
```

### 3.2 主要エンティティ

#### キャラクター情報
- 基本情報（名前、属性、レアリティ、タイプ）
- アビリティ詳細
- サポートアビリティ
- 評価・使用場面
- おすすめ編成

#### 武器情報
- 基本ステータス
- スキル効果
- 奥義効果
- 評価・運用方法

#### 編成情報
- 目的（高難易度、周回、フルオート等）
- 推奨キャラクター・武器
- 代用可能なキャラ・武器
- プレイング方法

#### クエスト攻略
- 敵の行動パターン
- 推奨編成
- 攻略手順
- 注意点

## 4. Agent機能設計

### 4.1 Agent Tools

#### Tool 1: 情報検索ツール (search_knowledge)
```python
def search_knowledge(
    query: str,
    filters: dict = None,
    top_k: int = 5
) -> List[Document]:
    """
    ベクトルDBから関連情報を検索
    
    Args:
        query: 検索クエリ
        filters: フィルタ条件 (属性、レアリティ等)
        top_k: 取得件数
    """
```

#### Tool 2: 編成構築ツール (build_party)
```python
def build_party(
    objective: str,
    element: str,
    available_characters: List[str] = None
) -> PartyComposition:
    """
    目的に応じた編成を提案
    
    Args:
        objective: 目的（高難易度、周回等）
        element: 属性
        available_characters: 所持キャラリスト
    """
```

#### Tool 3: キャラクター比較ツール (compare_characters)
```python
def compare_characters(
    character_names: List[str],
    criteria: List[str] = ["damage", "utility", "survivability"]
) -> ComparisonResult:
    """
    キャラクター性能を比較
    """
```

#### Tool 4: 情報更新ツール (update_knowledge)
```python
def update_knowledge(
    source_url: str = None,
    force: bool = False
) -> UpdateResult:
    """
    外部ソースから最新情報を取得・更新
    """
```

### 4.2 Agent Workflow

```
1. ユーザークエリ受信
   ↓
2. クエリ分析・意図理解
   - 質問タイプ判定（情報照会、編成相談、比較等）
   - エンティティ抽出（キャラ名、属性等）
   ↓
3. Tool選択・実行
   - 必要なツールの決定
   - 複数ツールの連携実行
   ↓
4. コンテキスト構築
   - 検索結果の統合
   - 関連情報の追加取得
   ↓
5. 回答生成
   - LLMによる自然な回答生成
   - 根拠となる情報源の提示
   ↓
6. レスポンス返却
```

## 5. RAG処理フロー

### 5.1 Indexing Pipeline
```
データソース
  ↓
収集 (Scraping/API)
  ↓
前処理 (Cleaning, Normalization)
  ↓
チャンク分割 (Semantic Chunking)
  ↓
Embedding生成
  ↓
ベクトルDB保存
```

### 5.2 Retrieval Pipeline
```
ユーザークエリ
  ↓
クエリ拡張 (Query Expansion)
  ↓
Embedding生成
  ↓
ベクトル類似度検索
  ↓
Re-ranking (Optional)
  ↓
関連文書取得
```

### 5.3 チャンク戦略
- **セマンティックチャンク**: 意味単位で分割（キャラごと、アビリティごと等）
- **オーバーラップ**: 50-100トークンのオーバーラップを設定
- **メタデータ保持**: 元文書へのリンク、更新日時等

## 6. API設計

### 6.1 エンドポイント

#### POST /api/chat
```json
{
  "message": "水属性の初心者におすすめのキャラを教えて",
  "context": {
    "user_rank": 100,
    "owned_characters": ["カタリナ", "ランスロット"]
  }
}
```

**Response:**
```json
{
  "response": "水属性の初心者には以下のキャラがおすすめです...",
  "sources": [
    {
      "type": "character",
      "name": "ランスロット",
      "url": "https://...",
      "relevance_score": 0.92
    }
  ],
  "suggested_actions": [
    "編成例を見る",
    "武器編成を相談する"
  ]
}
```

#### POST /api/search
```json
{
  "query": "火属性 高難易度",
  "filters": {
    "type": "party_composition",
    "element": "火"
  },
  "top_k": 10
}
```

#### POST /api/party/build
```json
{
  "objective": "ルシファーHL",
  "element": "光",
  "owned_characters": ["..."],
  "owned_weapons": ["..."]
}
```

#### POST /api/update
```json
{
  "sources": ["gamewith", "wiki"],
  "target_types": ["character", "weapon"]
}
```

## 7. データソース

### 7.1 主要情報源
1. **グラブル攻略Wiki** (https://gbf-wiki.com/)
   - 全キャラ・武器・召喚石の詳細情報
   
2. **GameWith グラブル攻略** (https://gamewith.jp/granblue/)
   - 最新評価、おすすめ編成
   
3. **Game8 グラブル攻略**
   - クエスト攻略情報

4. **公式お知らせ**
   - バランス調整、新キャラ情報

### 7.2 データ更新戦略
- **定期更新**: 毎日深夜に自動実行
- **差分更新**: 変更検知時のみ再Embedding
- **優先度**: 新キャラ > バランス調整 > 既存情報

## 8. セキュリティ・パフォーマンス

### 8.1 セキュリティ
- API Key管理（環境変数）
- Rate Limiting（ユーザーあたり100req/hour）
- Input Validation（インジェクション対策）

### 8.2 パフォーマンス最適化
- **キャッシング**: 頻出クエリの結果をRedisにキャッシュ
- **バッチ処理**: Embedding生成をバッチ化
- **インデックス最適化**: ベクトルDBのHNSWインデックス利用

### 8.3 モニタリング
- レスポンスタイム
- 検索精度（Relevance Score）
- API使用量
- エラーレート

## 9. 実装フェーズ

### Phase 1: MVP（2週間）
- [ ] 基本的なRAG機能実装
- [ ] キャラクター情報の収集・保存
- [ ] シンプルな質問応答

### Phase 2: Agent機能（2週間）
- [ ] LangChain/LlamaIndexによるAgent実装
- [ ] Tools開発（検索、編成構築）
- [ ] コンテキスト管理強化

### Phase 3: 拡張機能（2週間）
- [ ] 武器・召喚石情報追加
- [ ] 編成シミュレーション
- [ ] UI/UX改善

### Phase 4: 運用・改善（継続）
- [ ] データ更新自動化
- [ ] フィードバック収集
- [ ] モデル・プロンプトチューニング

## 10. ディレクトリ構成

```
granblue-rag/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── chat.py
│   │   │   ├── search.py
│   │   │   └── party.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── agents/
│   │   ├── tools/
│   │   │   ├── search.py
│   │   │   ├── party_builder.py
│   │   │   └── character_compare.py
│   │   └── agent.py
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   ├── reranker.py
│   │   └── vector_store.py
│   ├── models/
│   │   ├── schemas.py
│   │   └── entities.py
│   └── services/
│       ├── scraper/
│       │   ├── wiki_scraper.py
│       │   └── gamewith_scraper.py
│       └── indexer.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── vector_db/
├── tests/
│   ├── unit/
│   └── integration/
├── scripts/
│   ├── setup_db.py
│   └── update_data.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── .env.example
├── DESIGN.md
└── README.md
```

## 11. 評価指標

### 11.1 検索精度
- **Precision@K**: 上位K件の適合率
- **Recall@K**: 上位K件の再現率
- **MRR (Mean Reciprocal Rank)**: 最初の正解の順位

### 11.2 回答品質
- **Faithfulness**: 情報源との一致度
- **Answer Relevance**: 質問との関連性
- **Context Relevance**: 取得コンテキストの適切性

### 11.3 ユーザー体験
- **レスポンスタイム**: 平均2秒以内
- **ユーザー満足度**: フィードバック収集

## 12. フロントエンド・UI設計

### 12.1 UI選択肢

#### オプション1: Webチャットインターフェース（推奨）
**技術スタック:**
- **フロントエンド**: React / Next.js + TypeScript
- **UIライブラリ**: Tailwind CSS + shadcn/ui
- **状態管理**: Zustand / Jotai
- **通信**: WebSocket (リアルタイム) + REST API

**特徴:**
```
┌─────────────────────────────────────────┐
│  グラブル攻略AI アシスタント              │
├─────────────────────────────────────────┤
│  [チャット履歴]                          │
│  ┌───────────────────────────────────┐  │
│  │ User: 水属性の初心者向け編成は？  │  │
│  │                                   │  │
│  │ AI: 水属性の初心者には...         │  │
│  │ ┌─────────────────────────────┐ │  │
│  │ │ 📊 推奨編成                  │ │  │
│  │ │ メイン: カタリナ             │ │  │
│  │ │ サブ: ランスロット、ヨダ爺   │ │  │
│  │ │ [詳細を見る]                │ │  │
│  │ └─────────────────────────────┘ │  │
│  │ 情報源: GameWith, Wiki (0.92)   │  │
│  └───────────────────────────────────┘  │
│                                         │
│  [💬 メッセージを入力...]      [送信]    │
│                                         │
│  [サイドバー]                            │
│  - 新しいチャット                        │
│  - 履歴                                  │
│  - クイックアクション                    │
│    • キャラ検索                          │
│    • 編成相談                            │
│    • クエスト攻略                        │
└─────────────────────────────────────────┘
```

**主要機能:**
- チャット形式の対話インターフェース
- ストリーミングレスポンス（タイピング効果）
- リッチコンテンツ表示（カード、テーブル、画像）
- 情報源の表示とクリック可能なリンク
- チャット履歴の保存・管理
- サジェスト機能（よくある質問）

#### オプション2: Discord Bot
**技術スタック:**
- discord.py / discord.js
- Slash Commands対応

**使用例:**
```
/gbf ask 火属性の高難易度編成を教えて
/gbf compare キャラA キャラB
/gbf party 光属性 ルシファーHL
/gbf search 六竜 攻略
```

**特徴:**
- グラブルプレイヤーコミュニティで直接利用可能
- サーバー内での情報共有が容易
- 通知機能（最新情報の自動投稿）

#### オプション3: CLI / API直接利用
**技術スタック:**
- Click / Typer (CLIフレームワーク)
- Rich (ターミナル装飾)

**使用例:**
```bash
$ gbf-rag ask "水属性の初心者向け編成は？"
$ gbf-rag search --element 火 --type party
$ gbf-rag update --source gamewith
```

### 12.2 推奨UI: Webチャット詳細設計

#### 12.2.1 ページ構成

**メインページ (`/`)**
```
Header
  - ロゴ + タイトル
  - 設定ボタン
  
Sidebar (左側, 250px)
  - 新規チャット
  - チャット履歴一覧
  - フィルター（日付、トピック）
  - クイックアクション
  
Main Chat Area (中央)
  - メッセージ一覧（スクロール）
  - 入力欄
    - テキストエリア（自動拡張）
    - 送信ボタン
    - オプションメニュー
      - 所持キャラ設定
      - フィルター設定
  
Info Panel (右側, 300px, オプション)
  - 関連情報カード
  - 推奨アクション
  - 最近の検索
```

#### 12.2.2 メッセージコンポーネント

**ユーザーメッセージ**
```tsx
<UserMessage>
  <Avatar />
  <Content>
    <Text>水属性の初心者向け編成は？</Text>
    <Timestamp>14:30</Timestamp>
  </Content>
</UserMessage>
```

**AIレスポンス（基本）**
```tsx
<AIMessage>
  <Avatar icon="bot" />
  <Content>
    <StreamingText>
      水属性の初心者には以下の編成がおすすめです...
    </StreamingText>
    <Timestamp>14:30</Timestamp>
    <Sources>
      <SourceChip href="..." score={0.92}>GameWith</SourceChip>
      <SourceChip href="..." score={0.88}>Wiki</SourceChip>
    </Sources>
    <Actions>
      <Button variant="outline">詳細を見る</Button>
      <Button variant="ghost">編成を保存</Button>
    </Actions>
  </Content>
</AIMessage>
```

**AIレスポンス（リッチコンテンツ）**
```tsx
<AIMessage>
  <Content>
    <Text>以下の編成がおすすめです：</Text>
    
    <PartyCard>
      <Header>水属性 初心者向け編成</Header>
      <CharacterSlots>
        <Slot>
          <CharacterIcon name="カタリナ" rarity="SSR" />
          <Label>メイン</Label>
        </Slot>
        <Slot>
          <CharacterIcon name="ランスロット" rarity="SSR" />
        </Slot>
        <Slot>
          <CharacterIcon name="ヨダルラーハ" rarity="SSR" />
        </Slot>
      </CharacterSlots>
      <Stats>
        <Stat label="難易度">★★☆☆☆</Stat>
        <Stat label="用途">周回・初心者向け</Stat>
      </Stats>
      <Actions>
        <Button>代用キャラを見る</Button>
      </Actions>
    </PartyCard>
    
    <Sources>...</Sources>
  </Content>
</AIMessage>
```

#### 12.2.3 クイックアクション

**テンプレート質問:**
```tsx
<QuickActions>
  <ActionButton icon="search">
    おすすめキャラを教えて
  </ActionButton>
  <ActionButton icon="party">
    編成を相談したい
  </ActionButton>
  <ActionButton icon="quest">
    クエスト攻略を知りたい
  </ActionButton>
  <ActionButton icon="compare">
    キャラを比較したい
  </ActionButton>
</QuickActions>
```

#### 12.2.4 状態管理

```typescript
interface ChatStore {
  // チャット履歴
  conversations: Conversation[];
  currentConversationId: string | null;
  
  // メッセージ
  messages: Message[];
  isStreaming: boolean;
  
  // ユーザー設定
  userContext: {
    rank: number;
    ownedCharacters: string[];
    favoriteElement: string;
  };
  
  // アクション
  sendMessage: (content: string) => Promise<void>;
  createConversation: () => void;
  updateUserContext: (context: Partial<UserContext>) => void;
}
```

#### 12.2.5 API通信フロー

```typescript
// WebSocket接続（ストリーミング用）
const ws = new WebSocket('ws://api/chat/stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'token':
      // テキストを追加表示
      appendToken(data.content);
      break;
    case 'source':
      // 情報源を表示
      addSource(data.source);
      break;
    case 'action':
      // サジェストアクションを表示
      addSuggestedAction(data.action);
      break;
    case 'complete':
      // ストリーミング完了
      setStreaming(false);
      break;
  }
};

// メッセージ送信
async function sendMessage(content: string) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      message: content,
      context: userContext,
      conversation_id: currentConversationId
    })
  });
  
  // WebSocketでストリーミングレスポンスを受信
}
```

### 12.3 モバイル対応

**レスポンシブデザイン:**
- モバイル: シングルカラム、サイドバーはドロワー
- タブレット: 2カラム（チャット + サイドバー）
- デスクトップ: 3カラム（サイドバー + チャット + 情報パネル）

**PWA対応:**
- オフライン閲覧（キャッシュされたチャット履歴）
- ホーム画面追加
- プッシュ通知（新情報リリース時）

### 12.4 実装優先度

**Phase 1: MVP**
- [ ] 基本的なチャットインターフェース
- [ ] テキストメッセージの送受信
- [ ] シンプルなレスポンス表示
- [ ] 情報源リンク表示

**Phase 2: リッチコンテンツ**
- [ ] パーティ編成カード
- [ ] キャラクター比較テーブル
- [ ] ストリーミングレスポンス
- [ ] チャット履歴管理

**Phase 3: 高度な機能**
- [ ] 所持キャラ管理
- [ ] 編成シミュレーター統合
- [ ] 画像アップロード（編成画像認識）
- [ ] エクスポート機能（編成をSNSシェア）

### 12.5 ディレクトリ構成（フロントエンド）

```
frontend/
├── src/
│   ├── app/
│   │   ├── (chat)/
│   │   │   ├── page.tsx
│   │   │   └── layout.tsx
│   │   ├── settings/
│   │   └── api/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatContainer.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   ├── UserMessage.tsx
│   │   │   ├── AIMessage.tsx
│   │   │   └── StreamingText.tsx
│   │   ├── party/
│   │   │   ├── PartyCard.tsx
│   │   │   ├── CharacterSlot.tsx
│   │   │   └── WeaponGrid.tsx
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   └── Avatar.tsx
│   │   └── layout/
│   │       ├── Sidebar.tsx
│   │       ├── Header.tsx
│   │       └── InfoPanel.tsx
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── useWebSocket.ts
│   │   └── useUserContext.ts
│   ├── store/
│   │   ├── chatStore.ts
│   │   └── userStore.ts
│   ├── lib/
│   │   ├── api.ts
│   │   └── websocket.ts
│   └── types/
│       ├── chat.ts
│       ├── party.ts
│       └── character.ts
├── public/
│   ├── icons/
│   └── images/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 13. 今後の拡張案

- [ ] マルチモーダル対応（画像からの編成認識）
- [ ] ユーザー別パーソナライゼーション
- [ ] Discord/LINE Bot連携
- [ ] ダメージ計算シミュレーター統合
- [ ] トレンド分析（人気編成の可視化）
- [ ] 音声入力対応
- [ ] 多言語対応（英語、中国語）
