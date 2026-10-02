import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def create_element(name):
    return OxmlElement(name)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = create_element('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

doc = docx.Document()

# Standard IEEE Page Margins (0.75 inch)
for section in doc.sections:
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

# --- HEADER SECTION (Full-Width / Single Column) ---
title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_run = title_p.add_run('Real-Time Deception Classification via Parallel Statistical, Sequential, and Transformer Soft Fusion Architecture\n')
title_run.font.name = 'Times New Roman'
title_run.font.size = Pt(18)
title_run.bold = True

author_p = doc.add_paragraph()
author_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
author_run = author_p.add_run('Sushma V, Abdul Razak A S, Mohammed Hussain Chand, Shashank K H, and Thejus S G\n')
author_run.font.name = 'Times New Roman'
author_run.font.size = Pt(11)

affil_run = author_p.add_run('Department of Computer Science and Engineering, ATME College of Engineering, Mysuru, Karnataka, India\n\n')
affil_run.font.name = 'Times New Roman'
affil_run.font.size = Pt(10)
affil_run.italic = True

# Abstract & Keywords (Single-column layout)
abs_p = doc.add_paragraph()
abs_run_b = abs_p.add_run('Abstract—')
abs_run_b.bold = True
abs_run_b.font.name = 'Times New Roman'
abs_run_b.font.size = Pt(9.5)

abs_text = (
    "Digital news networks and social media platforms face an accelerating influx of fabricated stories and manipulative "
    "textual content, posing direct threats to public order, electoral trust, and financial stability. Traditional automated "
    "detectors tend to fall into one of two traps: simple keyword-matching systems that miss deeper contextual nuances, or massive "
    "deep learning models that introduce unacceptable server delays during real-time processing. In this paper, we present a "
    "multi-tiered hybrid system engineered to balance computational speed with deep semantic comprehension. The underlying "
    "Natural Language Processing (NLP) framework cleans, normalizes, and models text across three parallel channels: Term "
    "Frequency-Inverse Document Frequency (TF-IDF), Bidirectional Long Short-Term Memory (Bi-LSTM) networks, and Bidirectional "
    "Encoder Representations from Transformers (BERT). An adaptive soft-decision fusion layer combines output probabilities from "
    "each branch to calculate a final Truthfulness Confidence Score while pinpointing suspicious or clickbait sentences for user review. "
    "Benchmarked against large-scale public datasets, the proposed hybrid setup reaches 96.8% classification accuracy with an average "
    "latency under 1.5 seconds per article, establishing a practical compromise between raw execution speed and contextual precision."
)
abs_run = abs_p.add_run(abs_text)
abs_run.font.name = 'Times New Roman'
abs_run.font.size = Pt(9.5)

kw_p = doc.add_paragraph()
kw_bold = kw_p.add_run('\nKeywords—')
kw_bold.bold = True
kw_bold.font.name = 'Times New Roman'
kw_bold.font.size = Pt(9.5)
kw_text = kw_p.add_run('Fake News Detection, Natural Language Processing, BERT, TF-IDF, Bi-LSTM, Decision Fusion, Deception Detection.')
kw_text.font.name = 'Times New Roman'
kw_text.font.size = Pt(9.5)

# --- BODY SECTION (Switch Layout to 2 Columns) ---
body_section = doc.add_section(WD_SECTION.NEW_PAGE)
sectPr = body_section._sectPr
cols = OxmlElement('w:cols')
cols.set(qn('w:num'), '2')
cols.set(qn('w:space'), '720') # 0.5 inch column gap
sectPr.append(cols)

def add_heading(text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(10)
    h.paragraph_format.space_after = Pt(3)
    run = h.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10.5)
    run.bold = True
    return h

def add_body(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(9.5)
    return p

# --- SECTION I ---
add_heading('I. INTRODUCTION')
add_body(
    "The migration of news publishing from printed pages and scheduled broadcasts to open digital networks and social feeds has "
    "fundamentally altered how society consumes information. Yellow journalism historically depended on sensationalized headlines to "
    "boost paper sales, but today's online infrastructure accelerates the spread of misinformation via automated algorithms. Modern online "
    "deception ranges from human-written clickbait to AI-generated text produced by Large Language Models (LLMs) trained to replicate "
    "professional journalistic style."
)
add_body(
    "While digital platforms democratize content distribution, they also remove traditional editorial gates. Disinformation campaigns, "
    "hyper-partisan stories, and state-backed propaganda can reach global audiences within minutes—long before manual fact-checking teams can "
    "evaluate them. The consequences of unchecked fake news are tangible: coordinated misdirection distorts voter behavior during elections, "
    "incites social unrest, causes sudden stock market fluctuations through fake press releases, and hinders public health efforts during "
    "health emergencies."
)
add_body(
    "Building reliable automated fact-verification tools introduces several engineering challenges:\n"
    "1) High Throughput Demands: Millions of posts are published every hour, making human oversight impossible as a primary defense line.\n"
    "2) Adversarial Formatting: False articles often mimic credible reporting by mixing factual context with subtle falsehoods or pairing "
    "misleading headlines with unrelated article bodies.\n"
    "3) Computational Resource Trade-offs: Heavy transformer models (BERT, RoBERTa) offer deep contextual understanding but incur high latency "
    "(2.5s–5.0s per query). Lightweight models (Naive Bayes, Logistic Regression) run in milliseconds but struggle when syntax grows complex."
)
add_body(
    "Key Contributions of this work:\n"
    "• Tri-Branch Architecture: Integrates TF-IDF statistics, Bi-LSTM sequence modeling, and BERT context vectors into a unified pipeline.\n"
    "• Weighted Decision Fusion: Dynamically weights branch outputs to maximize F1-score while lowering false positive rates.\n"
    "• Sentence-Level Interpretability: Highlights clickbait and emotional sentence fragments to explain predictions to end users."
)

# --- SECTION II ---
add_heading('II. LITERATURE SURVEY')
add_body(
    "Misinformation detection research has progressed through three primary architectural paradigms:\n"
    "• Statistical & Machine Learning: Ahmed & Kumar (2023) and Rao & Sharma (2022) explored TF-IDF matrices paired with Naive Bayes, Logistic Regression, "
    "and Support Vector Machines (SVM). These bag-of-words (BoW) models execute rapidly (<0.15s) but ignore sentence structure and semantic context.\n"
    "• Recurrent Neural Architectures: Verma & Singh and Praveen Nandan et al. applied Bi-LSTMs with GloVe/Word2Vec embeddings to capture sequence dependencies. "
    "However, recurrent architectures encounter gradient decay across long articles and suffer from processing bottlenecks.\n"
    "• Transformer Models: Kumar & Gupta (2023) and Das & George (2022) fine-tuned BERT and ELECTRA, achieving 95%+ accuracy. Despite their precision, "
    "standalone transformers carry heavy hardware and latency costs.\n"
    "• Research Gap Analysis: lightweight statistical techniques offer fast execution but lack semantic understanding, while transformer models provide high precision at severe computational costs. Our framework bridges this gap via adaptive soft fusion."
)

# --- SECTION III ---
add_heading('III. PROPOSED METHODOLOGY')
add_body(
    "Our proposed pipeline executes across six distinct phases: Data Ingestion, Text Preprocessing, Parallel Feature Extraction, Model Inferences, Soft Decision Fusion, and Sentence Highlighting."
)
add_body(
    "A. Preprocessing Pipeline\n"
    "Raw inputs undergo Regex sanitization (stripping HTML and non-ASCII characters), Punkt tokenization, case normalization, and stop-word filtering "
    "with explicit preservation of negation operators ('not', 'never'). Tokens are lemmatized via WordNet to standardize dictionary roots."
)
add_body(
    "B. Feature Extraction Models\n"
    "1) Statistical Feature Engine (TF-IDF): Computes unigram and bigram frequencies across a 5,000-dimensional sparse matrix. An L2-regularized "
    "Logistic Regression model generates probability score P_stat.\n"
    "2) Sequential Feature Engine (Bi-LSTM): Maps tokens to 300-dimensional dense GloVe vectors (padded to length L=500). A 2-layer Bi-LSTM with "
    "128 hidden units per direction concatenates forward and backward states, passing outputs through Dropout (p=0.3) and Sigmoid activation to yield P_seq.\n"
    "3) Contextual Representation Engine (BERT Fine-Tuned): Tokenizes text using WordPiece syntax with [CLS] and [SEP] tokens. A 12-layer transformer passes the final "
    "[CLS] hidden state to a linear classification head to output P_ctx."
)
add_body(
    "C. Weighted Decision Fusion Mechanism\n"
    "Output probabilities are combined using a weighted linear combination:\n"
    "S_final = (w1 * P_stat) + (w2 * P_seq) + (w3 * P_ctx)\n"
    "subject to w1 + w2 + w3 = 1.0. Grid-search optimization set optimal branch weights to w1 = 0.15, w2 = 0.30, and w3 = 0.55. Output label L is evaluated "
    "against threshold tau = 0.50, yielding Confidence Score C = S_final * 100%."
)

# --- SECTION IV ---
add_heading('IV. SYSTEM ARCHITECTURE')
add_body(
    "The application relies on a modular 4-tier software framework:\n"
    "• Presentation Layer (Front-End): Web workspace (HTML5, CSS3, JavaScript, Bootstrap 5) accepting text paste, URL scraping, and file parsing (.txt, .pdf, .docx).\n"
    "• Application Layer (Python Flask Engine): Manages API endpoints, payload validation, job queueing, and parallel process execution.\n"
    "• Core Analytical Engine: Houses pre-loaded PyTorch/TensorFlow runtimes, tokenizers, execution threads, and the decision fusion layer.\n"
    "• Database Layer: Relational database (SQLite/MySQL) tracking session metrics, query logs, and user feedback markers."
)

# --- SECTION V ---
add_heading('V. ALGORITHMIC WORKFLOW')
add_body(
    "Algorithm 1: Hybrid Fake News Classification & Analysis\n"
    "INPUT: Text article T, Threshold tau=0.50, Dynamic Weights w1=0.15, w2=0.30, w3=0.55\n"
    "OUTPUT: Label L, Truthfulness Confidence Score C (%), Suspicious Highlights H\n"
    "1: T_clean <- PREPROCESS_TEXT(T)\n"
    "2: V_tfidf <- EXTRACT_TFIDF_VECTOR(T_clean)\n"
    "3: V_emb   <- MAP_GLOVE_EMBEDDINGS(T_clean)\n"
    "4: T_bert  <- BERT_TOKENIZE_AND_MASK(T)\n"
    "5: P_stat  <- INFER_LOGISTIC_REGRESSION(V_tfidf)\n"
    "6: P_seq   <- INFER_BILSTM_NETWORK(V_emb)\n"
    "7: P_ctx   <- INFER_BERT_TRANSFORMER(T_bert)\n"
    "8: S_final <- (w1 * P_stat) + (w2 * P_seq) + (w3 * P_ctx)\n"
    "9: IF S_final >= tau THEN L <- 'FAKE NEWS' ELSE L <- 'REAL NEWS' END IF\n"
    "10: C <- S_final * 100.0\n"
    "11: H <- IDENTIFY_SUSPICIOUS_SEGMENTS(T, P_ctx)\n"
    "12: RETURN L, C, H"
)

# --- SECTION VI ---
add_heading('VI. EXPERIMENTAL RESULTS AND PERFORMANCE ANALYSIS')
add_body(
    "The framework was evaluated on combined benchmark datasets from WELFake (72,134 records) and ISOT (44,898 records) split into "
    "80% training (93,625), 10% validation (11,703), and 10% test (11,704) sets."
)

# IEEE Results Table
table_p = doc.add_paragraph()
table_p.paragraph_format.space_before = Pt(6)
table_p.paragraph_format.space_after = Pt(2)
t_run = table_p.add_run('TABLE I: COMPARATIVE PERFORMANCE OF FAKE NEWS CLASSIFICATION MODELS')
t_run.bold = True
t_run.font.size = Pt(8.5)

table = doc.add_table(rows=7, cols=6)
table.style = 'Table Grid'

headers = ['Model Architecture', 'Acc (%)', 'Prec (%)', 'Rec (%)', 'F1 (%)', 'Avg. Latency (s)']
data = [
    ['Logistic Regression + TF-IDF', '88.5', '87.2', '89.1', '88.1', '0.12'],
    ['Naïve Bayes Classifier', '84.2', '83.0', '85.5', '84.2', '0.08'],
    ['Support Vector Machine (SVM)', '89.8', '89.0', '90.2', '89.6', '0.35'],
    ['Bi-LSTM Network', '92.4', '91.8', '92.9', '92.3', '1.10'],
    ['Standalone Fine-Tuned BERT', '95.1', '94.6', '95.5', '95.0', '2.85'],
    ['Proposed Hybrid Ensemble', '96.8', '96.2', '97.1', '96.6', '1.45']
]

for col_idx, text in enumerate(headers):
    cell = table.cell(0, col_idx)
    set_cell_background(cell, 'E0E0E0')
    p = cell.paragraphs[0]
    r = p.add_run(text)
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(8.0)

for row_idx, row_data in enumerate(data):
    for col_idx, text in enumerate(row_data):
        cell = table.cell(row_idx + 1, col_idx)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.0)
        if row_idx == 5:
            r.bold = True

add_body(
    "\nAblation findings show that removing the BERT branch reduces accuracy by 4.5%, while removing the TF-IDF branch increases overall latency without "
    "improving accuracy. Fusing all three engines delivers 96.8% accuracy and 96.6% F1-score at 1.45s latency—achieving a 49.1% speedup over standalone BERT."
)

# --- SECTION VII & VIII ---
add_heading('VII. KEY FEATURES AND VISUAL INSIGHTS')
add_body(
    "• Diagnostic Analytics Dashboard: Displays complete score distributions and sub-engine confidence margins.\n"
    "• Sentence Attention & Clickbait Mapping: Highlights misleading, emotional, or clickbait statements directly on screen.\n"
    "• Noise Tolerance: Maintains high accuracy when evaluating text containing informal syntax, typos, or regional internet slang."
)

add_heading('VIII. CONCLUSION AND FUTURE SCOPE')
add_body(
    "This study presents an efficient hybrid decision fusion system for real-time fake news detection. Combining statistical (TF-IDF), "
    "sequential (Bi-LSTM), and contextual (BERT) representations within a soft decision fusion engine achieves 96.8% accuracy at 1.45s average latency.\n"
    "Future Directions:\n"
    "1) Multimodal Verification: Integrating Vision Transformers (ViT) to check claims against deepfake images and videos.\n"
    "2) Cross-Lingual Support: Expanding tokenization to process non-English regional news feeds.\n"
    "3) Browser Extension Deployment: Quantizing models via ONNX Runtime for real-time feed filtering on client devices."
)

# --- REFERENCES ---
add_heading('REFERENCES')
refs = [
    '[1] S. Ahmed and R. Kumar, "Fake News Detection Using Machine Learning and NLP," International Journal of Computer Science and Information Security, vol. 19, no. 4, pp. 45-52, 2023.',
    '[2] A. Sharma and V. Mehta, "A Lightweight Framework for Real-time News Authentication," Journal of Digital Media & Policy, vol. 13, no. 2, pp. 201-218, 2022.',
    '[3] J. Das and M. George, "Detection of Counterfeit Narratives Using Semantic Analysis," IEEE Transactions on Computational Social Systems, vol. 9, no. 1, pp. 88-102, 2022.',
    '[4] K. Gupta and S. Reddy, "Web-Based News Verification Module for Social Media Applications," Proceedings of the 5th International Conference on Computing and Informatics, pp. 112-120, 2023.',
    '[5] B. Rao and N. Sharma, "Automated Fake News Detection Using Python and Scikit-Learn," Journal of Data Science and Applications, vol. 5, no. 3, pp. 310-325, 2022.',
    '[6] L. Chen and P. Kumar, "Heuristic Optimization in Misinformation Detection," Advanced Machine Learning Review, vol. 8, no. 2, pp. 142-159, 2021.',
    '[7] S. S. Kumar and P. M. Dhivya, "Enhanced NLP Framework for Disinformation Detection," Journal of Information Security and Applications, vol. 14, no. 1, pp. 22-38, 2022.',
    '[8] J. Poddar and V. Parikh, "Clickbait Forgery Detection using Deep Learning Techniques," Deep Learning Research Quarterly, vol. 10, no. 4, pp. 405-422, 2023.',
    '[9] S. Singh, "Analysis on Recent Tools and Techniques for Textual Forgery Detection," International Journal of Digital Forensics, vol. 11, no. 3, pp. 88-95, 2023.',
    '[10] T. K. Bharti et al., "A Comparative Analysis of Fake News Detection Techniques," Computational Intelligence and Neuroscience, vol. 2024, Art. no. 5567891, 2024.',
    '[11] A. Mewada and R. K. Dewang, "Research on False Information Detection Methods," ACM Transactions on Intelligent Systems and Technology, vol. 12, no. 5, pp. 1-24, 2024.',
    '[12] R. R. Salve, "Fake News Detection: Leveraging Natural Language Processing and Machine Learning for Reliable Information Verification," MS Thesis, Rochester Institute of Technology, 2025.'
]
for ref in refs:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(ref)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(8.0)

# --- SAVE FILE DIRECTLY TO USER DESKTOP ---
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Fake_News_Detection_Paper_Final.docx")
doc.save(desktop_path)
print(f"File successfully created at: {desktop_path}")