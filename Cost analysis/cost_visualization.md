```mermaid
pie title Распределение затрат API для генерации 1 минуты (с аудио)
    "OpenAI TTS (аудио)" : 76.8
    "GPT-4o-mini (текст)" : 23.2
    "Embeddings + Pinecone" : 0.01
```

```mermaid
graph TD
    A[Генерация 1 минуты видео] --> B{Выбор сценария}
    
    B -->|Сценарий 1| C[Скрипт + Сегменты]
    B -->|Сценарий 2| D[+ Аудио]
    B -->|Сценарий 4a| E[+ Изображения DALL-E]
    B -->|Сценарий 4b| F[+ Изображения SD]
    B -->|Сценарий 5a| P[+ Pollinations Free]
    B -->|Сценарий 5b| PP[+ Pollinations Packs]
    
    C --> C1[$0.0046]
    D --> D1[$0.0198]
    E --> E1[$0.34]
    F --> F1[$0.052]
    P --> P1[$0.0198 ⭐]
    PP --> PP1[$0.022]
    
    C1 --> G[Компоненты затрат]
    D1 --> G
    E1 --> G
    F1 --> G
    P1 --> G
    PP1 --> G
    
    G --> G1[GPT-4o-mini: 15,188 токенов]
    G --> G2[TTS: 1,011 символов]
    G --> G3[Pinecone: 5 запросов]
    G --> G4[Изображения: 0-8 шт]
    
    style C1 fill:#90EE90
    style D1 fill:#FFD700
    style E1 fill:#FF6B6B
    style F1 fill:#FFA500
    style P1 fill:#00FF00
    style PP1 fill:#98FB98
```

```mermaid
graph LR
    subgraph "Этапы генерации и их стоимость"
        A[ReAct Reasoning<br/>$0.0003] --> B[Pinecone RAG<br/>$0.0008]
        B --> C[Generate Outline<br/>$0.0002]
        C --> D[Generate Script<br/>$0.0003]
        D --> E[Fact-check<br/>$0.0000]
        E --> F[Regenerate<br/>$0.0002]
        F --> G[Segmentation<br/>$0.0001]
        G --> H[TTS Audio<br/>$0.0152]
        H --> I[Video Render<br/>$0.0000]
    end
    
    style H fill:#FFD700,stroke:#FF6B6B,stroke-width:3px
    style A fill:#E8F4FD
    style B fill:#E8F4FD
    style C fill:#E8F4FD
    style D fill:#E8F4FD
    style E fill:#D4EDDA
    style F fill:#E8F4FD
    style G fill:#E8F4FD
    style I fill:#D4EDDA
```

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'fontSize':'14px'}}}%%
timeline
    title Эволюция стоимости при масштабировании
    
    1 видео : $0.02
    10 видео : $0.20
    100 видео : $2.00
    1,000 видео : $20.00
    10,000 видео : $200.00
```

```mermaid
graph TB
    subgraph "Оптимизация затрат"
        A[Текущая стоимость<br/>$0.0198/мин]
        
        B1[Заменить TTS на gTTS<br/>Экономия: $0.0152]
        B2[Кэшировать аудио<br/>Экономия: ~30%]
        B3[Меньше Pinecone запросов<br/>Экономия: $0.0001]
        
        C[Оптимизированная<br/>$0.0046/мин]
        
        A --> B1
        A --> B2
        A --> B3
        
        B1 --> C
        B2 --> C
        B3 --> C
    end
    
    style A fill:#FFD700
    style C fill:#90EE90
    style B1 fill:#FF6B6B
```

## API Pricing Comparison

| API Service | Unit | Price | Usage per 1min | Cost |
|------------|------|-------|----------------|------|
| **GPT-4o-mini (input)** | 1M tokens | $0.150 | 10,632 tokens | $0.0016 |
| **GPT-4o-mini (output)** | 1M tokens | $0.600 | 4,556 tokens | $0.0027 |
| **OpenAI TTS-1** | 1K chars | $0.015 | 1,011 chars | $0.0152 |
| **Cohere Embeddings** | 1M tokens | $0.100 | 2,560 tokens | $0.0003 |
| **Pinecone Queries** | 1M requests | $0.200 | 5 requests | $0.0000 |
| **Pollinations Z-Image-Turbo** ⭐ | 1 image | 0.002 pollen | 8 images | **$0.00*** |
| **Pollinations P-Image-Edit** | 1 image | 0.01 pollen | 8 images | **$0.00*** |
| **DALL-E 3** (optional) | 1 image | $0.040 | 8 images | $0.3200 |
| **Stable Diffusion** (alt.) | 1 image | $0.004 | 8 images | $0.0320 |

**Total Standard (with audio):** $0.0198  
**Total with Pollinations Free:** $0.0198 ⭐ (бесплатные начисления)  
**Total with Pollinations Packs:** $0.022 (при покупке pollen)  
**Total with SD images:** $0.0518  
**Total with DALL-E images:** $0.3398

\**При использовании бесплатных начислений (Flower tier: 0.4 pollen/hr = 200 images/hr)*

## Cost Breakdown by Component

```
Сценарий 2 (Скрипт + Сегменты + Аудио):
────────────────────────────────────────────────

1. Text Generation (GPT-4o-mini)
   ├─ ReAct Reasoning          $0.0003
   ├─ Pinecone RAG             $0.0008
   ├─ Outline Generation       $0.0002
   ├─ Script Generation        $0.0003
   ├─ Fact-check Regeneration  $0.0002
   └─ Segmentation             $0.0001
   SUBTOTAL:                   $0.0019

2. Embeddings & Vector Search
   ├─ Cohere Embeddings        $0.0003
   └─ Pinecone Queries         $0.0000
   SUBTOTAL:                   $0.0003

3. Audio Generation
   └─ OpenAI TTS-1             $0.0152
   SUBTOTAL:                   $0.0152

4. Video Rendering
   └─ MoviePy (local)          $0.0000
   SUBTOTAL:                   $0.0000

────────────────────────────────────────────────
TOTAL:                         $0.0198 (~2¢)
````
