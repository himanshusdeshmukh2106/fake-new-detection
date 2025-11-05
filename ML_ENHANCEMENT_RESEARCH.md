# ML Enhancement Research for Fake News Detection System

## Current Architecture Analysis

### Existing Pipeline (LLM-Based)
1. **Decompose** - Breaks text into claims using Gemini
2. **CheckWorthy** - Identifies which claims need verification using Gemini
3. **QueryGenerator** - Generates search queries using Gemini
4. **EvidenceRetrieval** - Searches web using Serper API
5. **ClaimVerify** - Verifies claims against evidence using Gemini

**Current Limitations:**
- Heavy reliance on LLM API calls (expensive, rate-limited)
- No learning from historical data
- No confidence scoring beyond simple factuality
- No source credibility assessment
- No user feedback loop

---

## Recommended ML Enhancements

### 🎯 Priority 1: High-Impact, Easy to Implement

#### 1. **Claim Classification Model (Supervised Learning)**
**Purpose:** Pre-filter claims before expensive LLM calls

**Implementation:**
- **Model:** Fine-tuned BERT/RoBERTa or DistilBERT (lightweight)
- **Training Data:** 
  - LIAR dataset (12.8K labeled claims)
  - FEVER dataset (185K claims)
  - PolitiFact/Snopes scraped data
- **Classes:** 
  - Checkworthy vs Not-checkworthy
  - Factual vs Opinion vs Satire
  - Verifiable vs Unverifiable

**Benefits:**
- Reduce LLM API calls by 40-60%
- Faster response time
- Works offline

**Code Structure:**
```python
factcheck/ml_models/
├── claim_classifier.py
├── models/
│   ├── claim_classifier.pkl
│   └── vectorizer.pkl
└── training/
    └── train_claim_classifier.py
```

---

#### 2. **Source Credibility Scoring (ML + Rule-Based)**
**Purpose:** Assess reliability of evidence sources

**Implementation:**
- **Features:**
  - Domain reputation (whitelist/blacklist)
  - HTTPS presence
  - Domain age
  - Backlink count
  - Content quality metrics
  - Historical accuracy rate
  
- **Model:** Random Forest or XGBoost
- **Training Data:** 
  - MediaBiasFactCheck.com dataset
  - NewsGuard ratings
  - Manual annotations

**Benefits:**
- Weight evidence by source quality
- Flag unreliable sources
- Improve verification accuracy

**Integration Point:** 
Add to `EvidenceRetrieval` module to score each evidence source

---

#### 3. **Semantic Similarity Model (Deep Learning)**
**Purpose:** Better match claims with evidence

**Implementation:**
- **Model:** Sentence-BERT (already in requirements!)
- **Use Cases:**
  - Rank evidence by relevance to claim
  - Detect paraphrased claims (deduplication)
  - Find contradictory statements
  
**Benefits:**
- More accurate evidence matching
- Detect duplicate/similar claims
- Better context understanding

**Code:**
```python
from sentence_transformers import SentenceTransformer, util

class SemanticMatcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def rank_evidence(self, claim, evidences):
        claim_emb = self.model.encode(claim)
        evidence_embs = self.model.encode(evidences)
        scores = util.cos_sim(claim_emb, evidence_embs)
        return scores
```

---

### 🎯 Priority 2: Medium Impact, Moderate Complexity

#### 4. **Stance Detection Model**
**Purpose:** Determine if evidence supports/refutes/is neutral to claim

**Implementation:**
- **Model:** Fine-tuned BERT for Natural Language Inference (NLI)
- **Pre-trained:** Use FEVER-trained models or SNLI models
- **Classes:** SUPPORTS, REFUTES, NOT_ENOUGH_INFO

**Benefits:**
- Reduce LLM calls for verification
- More consistent stance detection
- Faster processing

**Datasets:**
- FEVER (Fact Extraction and VERification)
- SNLI (Stanford Natural Language Inference)
- MultiNLI

---

#### 5. **Named Entity Recognition (NER) Enhancement**
**Purpose:** Extract and verify specific entities (people, places, dates, numbers)

**Implementation:**
- **Model:** spaCy NER (already installed!) + custom training
- **Enhancements:**
  - Fact-check specific entities separately
  - Cross-reference with knowledge bases (Wikidata, DBpedia)
  - Temporal verification (date consistency)

**Benefits:**
- Catch specific factual errors
- Verify numerical claims
- Timeline consistency checking

---

#### 6. **Fake News Detection Classifier (End-to-End)**
**Purpose:** Direct classification of entire articles

**Implementation:**
- **Model:** Multi-modal approach
  - Text: BERT/RoBERTa
  - Metadata: Domain, author, publish date
  - Social signals: Shares, engagement patterns
  
- **Architecture:** Ensemble model
  - Text classifier (70% weight)
  - Source credibility (20% weight)
  - Linguistic features (10% weight)

**Training Data:**
- FakeNewsNet dataset
- LIAR-PLUS dataset
- BuzzFeed-Webis dataset

---

### 🎯 Priority 3: Advanced Features

#### 7. **Temporal Claim Verification**
**Purpose:** Verify time-sensitive claims

**Implementation:**
- Extract temporal expressions
- Build timeline of events
- Check consistency with historical data
- Use time-series models for trend verification

---

#### 8. **Multi-Modal Fake Detection**
**Purpose:** Analyze images/videos for manipulation

**Implementation:**
- **Image Analysis:**
  - Reverse image search integration
  - Deepfake detection (CNN-based)
  - EXIF data analysis
  - Image manipulation detection
  
- **Video Analysis:**
  - Frame-by-frame analysis
  - Audio-visual consistency
  - Deepfake video detection

**Models:**
- EfficientNet for image classification
- XceptionNet for deepfake detection
- Audio-visual sync models

---

#### 9. **Active Learning Pipeline**
**Purpose:** Continuously improve from user feedback

**Implementation:**
- Collect user corrections
- Retrain models periodically
- A/B testing for model improvements
- Confidence-based sampling for labeling

---

#### 10. **Explainable AI (XAI) Module**
**Purpose:** Provide interpretable results

**Implementation:**
- LIME/SHAP for model explanations
- Attention visualization for BERT models
- Feature importance for tree-based models
- Generate human-readable explanations

---

## Implementation Roadmap

### Phase 1: Quick Wins (1-2 weeks)
1. ✅ Integrate Sentence-BERT for semantic similarity
2. ✅ Add source credibility scoring (rule-based)
3. ✅ Implement NER-based entity extraction

### Phase 2: Core ML Models (3-4 weeks)
1. Train claim classification model
2. Implement stance detection model
3. Build source credibility ML model
4. Add confidence scoring

### Phase 3: Advanced Features (4-6 weeks)
1. Multi-modal fake detection
2. Temporal verification
3. Active learning pipeline
4. Explainable AI module

---

## Technical Stack Recommendations

### ML Frameworks
- **PyTorch** - Deep learning models
- **Transformers (Hugging Face)** - Pre-trained models
- **scikit-learn** - Traditional ML models
- **Sentence-Transformers** - Semantic similarity
- **spaCy** - NLP tasks (already installed)

### Model Serving
- **FastAPI** - ML model API endpoints
- **Redis** - Caching predictions
- **MLflow** - Model versioning and tracking

### Training Infrastructure
- **Google Colab** - Free GPU for training
- **Weights & Biases** - Experiment tracking
- **DVC** - Data version control

---

## Dataset Resources

### Fact-Checking Datasets
1. **LIAR** - 12.8K short statements with labels
2. **FEVER** - 185K claims with evidence
3. **FakeNewsNet** - Social media fake news
4. **PHEME** - Rumor detection dataset
5. **MultiFC** - Multi-domain fact-checking

### Source Credibility
1. **MediaBiasFactCheck.com** - Source ratings
2. **NewsGuard** - News source scores
3. **OpenSources** - Fake news source list

### NLI Datasets
1. **SNLI** - 570K sentence pairs
2. **MultiNLI** - 433K sentence pairs
3. **FEVER** - Claim-evidence pairs

---

## Cost-Benefit Analysis

### Current System Costs (per 1000 requests)
- Gemini API calls: ~50-100 calls per request
- Cost: $0.50-$2.00 per request
- Time: 30-60 seconds per request

### With ML Enhancements
- Gemini API calls: ~20-30 calls per request (60% reduction)
- Cost: $0.20-$0.60 per request (70% savings)
- Time: 10-20 seconds per request (66% faster)
- Accuracy: +10-15% improvement

---

## Metrics to Track

### Model Performance
- Accuracy, Precision, Recall, F1-Score
- ROC-AUC for binary classification
- Confusion matrix analysis

### System Performance
- API call reduction %
- Response time improvement
- Cost per verification
- User satisfaction score

### Business Metrics
- Daily active users
- Verification requests
- Accuracy feedback from users
- False positive/negative rates

---

## Next Steps

1. **Immediate:** Integrate Sentence-BERT for semantic matching
2. **Week 1:** Implement source credibility scoring
3. **Week 2:** Train claim classification model
4. **Week 3:** Deploy stance detection model
5. **Week 4:** Add confidence scoring and explanations

---

## References & Resources

### Papers
- "FEVER: Fact Extraction and VERification" (Thorne et al., 2018)
- "LIAR: A Benchmark Dataset for Fake News Detection" (Wang, 2017)
- "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks" (Reimers & Gurevych, 2019)

### GitHub Repositories
- https://github.com/huggingface/transformers
- https://github.com/UKPLab/sentence-transformers
- https://github.com/several/fever-baselines

### Tutorials
- Hugging Face NLI fine-tuning
- Sentence-BERT semantic search
- spaCy custom NER training
