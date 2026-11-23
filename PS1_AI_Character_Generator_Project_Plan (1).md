# AI-Powered PS1 Character Generator
## Project Plan and Implementation Roadmap

**Project type:** Computer Vision + Machine Learning + Generative AI + 3D Asset Generation  
**Primary input:** One uploaded photograph  
**Primary output:** A retro PlayStation 1 (PS1)-style 3D character suitable for game-development workflows  
**Target users:** Indie game developers, hobbyist game developers, and character creators

---

## 1. Project Overview

Build a web application where a user uploads **one photograph**, selects the character's gender presentation and outfit, and generates a PS1-inspired 3D character.

The system should:
1. Accept one photo (preferably a clear, full-body image; a portrait can be supported with reduced accuracy).
2. Let the user choose a character gender presentation.
3. Let the user choose an outfit, such as Casual, Formal, Police, Horror, Traditional, or Custom.
4. Use AI to create a character that retains recognizable visual features from the uploaded photo while applying the selected choices.
5. Generate or reconstruct a 3D model.
6. Apply a low-poly, low-resolution retro game-art treatment.
7. Preview the result and export it for use in game engines.

**Important limitation:** One photograph does not contain information about the unseen sides or back of a person. The 3D system must estimate those areas, so the generated model may not perfectly match the real person from every angle. A full-body, well-lit, unobstructed photo will generally produce better results.

---

## 2. User Workflow

1. Open the character-generator website.
2. Upload one photograph.
3. Select gender presentation: Male, Female, or another inclusive/custom option if supported.
4. Select outfit: Casual, Formal, Police, Horror, Traditional, or Custom.
5. Optionally choose output settings:
   - Polygon level: Low / Medium / High
   - Texture size: 64×64 / 128×128 / 256×256
   - Pose: T-pose / Neutral standing
6. Click **Generate Character**.
7. Backend validates the image and runs the generation pipeline.
8. Show job status and a 3D preview.
9. Let the user download supported formats, initially GLB; add FBX/OBJ if the pipeline supports reliable conversion.

---

## 3. Recommended Technology Stack

| Layer | Recommended technology | Responsibility |
|---|---|---|
| Frontend | React + Vite | Upload form, gender/outfit controls, progress, preview |
| 3D viewer | Three.js | Display and rotate the generated GLB |
| Backend API | Python + FastAPI | Validation, job orchestration, download endpoints |
| Image processing | Pillow + OpenCV | Image loading, resizing, quality checks |
| Human analysis | MediaPipe or another suitable vision model | Optional person/pose/landmark analysis |
| Image generation | A compatible image-generation model or service | Apply the chosen visual style and outfit |
| Image-to-3D | A suitable image-to-3D model/service | Estimate 3D geometry from the generated/reference image |
| 3D processing | Blender + Python | Mesh cleanup, polygon reduction, materials, export |
| ML experiments | scikit-learn, PyTorch as needed | Train/evaluate any project-specific predictive model |
| Data storage | Local folders for MVP; MongoDB if accounts/history are needed | Jobs and metadata |
| Environment | Python virtual environment or Conda | Reproducible dependencies |

**Model choice note:** Image generation and image-to-3D are generative-AI tasks. A traditional scikit-learn `.pkl` file alone cannot turn a photograph into a 3D character. Use pretrained generative models for the difficult image/3D generation steps; use a project-trained `.pkl` model for a clearly defined supporting ML task.

---

## 4. System Architecture

```text
React + Vite frontend
        |
        | photo + gender + outfit + settings
        v
FastAPI backend
        |
        +--> Input validation and image preprocessing
        |
        +--> Optional ML classifier (.pkl)
        |       Example: predict image quality/readiness
        |
        +--> Image-generation model
        |       Preserve visible identity cues; apply outfit/style
        |
        +--> Image-to-3D model
        |       Estimate mesh and texture from one image
        |
        +--> Blender Python processing
        |       Cleanup -> decimation -> materials -> export
        |
        v
GLB 3D asset + preview + metadata
        |
        v
React 3D viewer / download
```

### Suggested backend structure

```text
ps1-character-generator/
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── utils/
│   ├── models/
│   │   └── image_quality_model.pkl
│   ├── uploads/
│   ├── generated/
│   └── requirements.txt
├── ml/
│   ├── data/
│   ├── notebooks/
│   │   └── ps1_character_ml_experiments.ipynb
│   ├── src/
│   │   ├── train_model.py
│   │   ├── evaluate_model.py
│   │   └── predict.py
│   ├── artifacts/
│   │   └── image_quality_model.pkl
│   └── reports/
├── blender/
│   └── optimize_and_export.py
├── docs/
│   └── PROJECT_PLAN.md
├── .gitignore
└── README.md
```

---

## 5. ML Model Requirement: What to Train and Save

The project should include a genuine, reproducible ML component and save its trained model as a `.pkl` file.

### Recommended first ML component: Image Readiness Classifier

Train a model to classify whether an uploaded image is suitable for character generation.

Possible labels:
- `ready`: person is visible, image is sufficiently clear, and framing is useful.
- `retake`: image is too blurry, too dark, heavily obstructed, or the person is poorly framed.

Possible input features:
- Image width and height
- Aspect ratio
- Brightness and contrast statistics
- Blur score (for example, variance of the Laplacian)
- Person-detection confidence, if available from a pretrained detector

A Random Forest or other scikit-learn classifier can be trained on a labelled dataset of image-quality examples. The model should be evaluated on a held-out test set. Do not claim accuracy until it has been measured on real, representative data.

**Saved artifact:** `image_quality_model.pkl`

This model is a supporting quality-check model. It does **not** generate the character. The generative image and 3D models perform that work.

### Optional future ML components
- Outfit category classifier, if users upload reference outfit images.
- Pose suitability classifier.
- Generation-quality ranking model, once enough human-rated examples are collected.

Avoid training a gender classifier from appearance. Gender should be a user-selected character setting, not an inferred sensitive attribute.

### Model artifact rules
- Save the fitted preprocessing pipeline and classifier together using `joblib` or `pickle`.
- Record feature names, training-data version, library versions, evaluation metrics, and date.
- Load only trusted `.pkl`/`.joblib` files: deserializing untrusted pickle files can execute malicious code.
- Keep a copy of the training code and notebook so the model can be reproduced.

---

## 6. Required Python and Jupyter Deliverables

The project must contain all of these:

| Deliverable | Required file | Purpose |
|---|---|---|
| Training script | `ml/src/train_model.py` | Train and save the ML model |
| Evaluation script | `ml/src/evaluate_model.py` | Report test metrics |
| Prediction script | `ml/src/predict.py` | Load `.pkl` and predict on new image features |
| Trained model | `ml/artifacts/image_quality_model.pkl` | Saved trained ML pipeline |
| Jupyter notebook | `ml/notebooks/ps1_character_ml_experiments.ipynb` | Data exploration, training, evaluation, visualizations |
| Blender script | `blender/optimize_and_export.py` | Automate mesh optimization/export where possible |
| API entry point | `backend/app/main.py` | Run FastAPI backend |
| Dependency list | `backend/requirements.txt` | Reproduce Python environment |

The notebook should include:
1. Project objective and dataset description.
2. Data loading and label checks.
3. Exploratory data analysis.
4. Feature extraction.
5. Train/test split.
6. Baseline model.
7. Model training and hyperparameter tuning.
8. Evaluation (accuracy, precision, recall, F1, confusion matrix).
9. Save the final pipeline as `.pkl`.
10. Reload the `.pkl` and demonstrate prediction on test examples.

If a labelled dataset is not yet available, first create a small, ethically sourced and correctly labelled pilot dataset. Do not fabricate evaluation metrics or present a placeholder model as trained.

---

## 7. Development Phases

### Phase 1 — Project foundation
- Create Git repository and folder structure.
- Set up React + Vite frontend.
- Set up FastAPI backend and image-upload endpoint.
- Validate file type, file size, and image dimensions.
- Store uploads temporarily and securely.

**Completion criteria:** A user can upload one image and see a preview.

### Phase 2 — User selections and image preparation
- Add gender-presentation selection.
- Add outfit selection.
- Add polygon, texture, and pose settings.
- Add image-quality checks and useful retake guidance.
- Build the ML training notebook and first `.pkl` classifier.

**Completion criteria:** The backend receives the image and all selections, and the ML model can assess image readiness.

### Phase 3 — 2D style-generation prototype
- Integrate a permitted image-generation model.
- Use the uploaded photo as the visual reference.
- Apply the selected outfit and PS1-inspired low-poly visual direction.
- Review identity consistency, outfit accuracy, and image quality.

**Completion criteria:** Produce a consistent PS1-style character concept image from one upload.

### Phase 4 — 3D generation
- Integrate an image-to-3D model.
- Generate mesh and texture.
- Inspect geometry, face, hands, clothing, and unseen surfaces.
- Handle generation failures and retry states.

**Completion criteria:** Generate a viewable 3D asset from the single-image workflow.

### Phase 5 — PS1-style optimization
- Use Blender Python to clean the mesh.
- Reduce polygon count to selected target levels.
- Create or resize low-resolution textures.
- Configure materials and normals for a retro appearance.
- Export GLB and validate it in the browser viewer.

**Completion criteria:** The exported model opens correctly in the 3D viewer and can be imported into a test game project.

### Phase 6 — Testing and release
- Test different lighting, skin tones, clothing, poses, and image qualities.
- Test upload validation and generation failures.
- Measure generation time and resource usage.
- Add privacy controls and automatic deletion of temporary uploads.
- Document model limitations and supported export formats.

**Completion criteria:** A documented MVP works end-to-end with known limitations.

---

## 8. API Design (Initial)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/generate` | Submit image, gender presentation, outfit, and settings |
| GET | `/api/jobs/{job_id}` | Check generation status |
| GET | `/api/jobs/{job_id}/preview` | Retrieve preview image |
| GET | `/api/jobs/{job_id}/model` | Download generated GLB |
| GET | `/api/health` | Check backend health |

Example request fields (multipart form):
- `image`: one uploaded image
- `gender`: user-selected value
- `outfit`: selected outfit
- `polygon_level`: low / medium / high
- `texture_size`: 64 / 128 / 256
- `pose`: t_pose / standing

---

## 9. Quality, Privacy, and Safety

- Ask users to upload only images they have permission to use.
- Explain that the system estimates hidden body surfaces from a single image.
- Do not infer a person's gender; use the user's explicit character selection.
- Avoid retaining uploaded photos longer than necessary.
- Provide a delete option and clear data-retention policy.
- Validate file types and size; do not trust filenames or client-provided MIME types.
- Run image and 3D generation in isolated workers with resource limits.
- Check licences and commercial-use terms for every pretrained model, dataset, texture, and asset.
- Never load `.pkl` files from unknown sources.

---

## 10. MVP Scope: Build in This Order

To keep the project achievable, implement in this order:

1. Photo upload + gender/outfit selection UI.
2. FastAPI upload endpoint and image validation.
3. ML image-readiness classifier with `.pkl`, `.py`, and `.ipynb` deliverables.
4. PS1-style 2D concept generation.
5. Single-image 3D generation.
6. Blender optimization and GLB export.
7. Three.js preview and download.

**Do not start by training a 3D foundation model from scratch.** That would require a large licensed 3D dataset and substantial GPU resources. First build the application around existing pretrained models, then train project-specific ML components where you have useful labelled data.

---

## 11. Definition of Done

The MVP is complete when:
- A user can upload exactly one photo.
- A user can select gender presentation and outfit.
- The app validates the photo and provides clear feedback.
- The trained ML quality-check model is saved as a `.pkl` file.
- Training, evaluation, and prediction Python scripts are included.
- A Jupyter notebook documents the ML workflow and reproduces the saved model.
- The AI pipeline can generate a PS1-inspired character concept and a 3D asset.
- The 3D asset can be previewed and downloaded as GLB.
- The README explains setup, model requirements, limitations, and licensing.

---

## 12. Suggested Project Name

**RetroMorph AI** — One Photo. One Custom Character. Game-Ready Retro Style.

Alternative names: PolyPersona, PSXForge, RetroAvatar AI.
