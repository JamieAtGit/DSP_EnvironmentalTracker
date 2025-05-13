
# Updated migration script based on actual DSProject structure
$oldProject = "C:\Users\jamie\OneDrive\Documents\University\ComputerScience\Year3\DigitalSP\DSProject"
$newProject = "C:\Dev\DSP"

$files = @{
    # Backend scripts
    "app.py" = "backend/api/app.py"
    "clean_dataset.py" = "backend/data/processing/clean_dataset.py"
    "debug_checks.py" = "backend/data/validation/debug_checks.py"
    "generate_dataset.py" = "backend/data/processing/generate_dataset.py"
    "predict_xgboost.py" = "backend/ml/prediction/predict_xgboost.py"
    "batch_predict_xgboost.py" = "backend/ml/prediction/batch_predict_xgboost.py"
    "train_model.py" = "backend/ml/training/train_model.py"
    "train_xgboost.py" = "backend/ml/training/train_xgboost.py"
    "test_model_prediction.py" = "backend/ml/evaluation/test_model_prediction.py"
    "rebuild_pipeline.py" = "tools/scripts/rebuild_pipeline.py"
    "open_demo_tabs.bat" = "tools/scripts/open_demo_tabs.bat"

    # Encoders from xgb_encoders
    "ml_model/xgb_encoders/label_encoder.pkl" = "backend/ml/encoders/label_encoder.pkl"
    "ml_model/xgb_encoders/material_encoder.pkl" = "backend/ml/encoders/material_encoder.pkl"
    "ml_model/xgb_encoders/origin_encoder.pkl" = "backend/ml/encoders/origin_encoder.pkl"
    "ml_model/xgb_encoders/recycle_encoder.pkl" = "backend/ml/encoders/recycle_encoder.pkl"
    "ml_model/xgb_encoders/transport_encoder.pkl" = "backend/ml/encoders/transport_encoder.pkl"
    "ml_model/xgb_encoders/weight_bin_encoder.pkl" = "backend/ml/encoders/weight_bin_encoder.pkl"

    # ML model and data files
    "ml_model/eco_model.pkl" = "backend/ml/models/eco_model.pkl"
    "ml_model/xgb_model.json" = "backend/ml/models/xgb_model.json"
    "ml_model/confusion_matrix.png" = "backend/ml/evaluation/confusion_matrix.png"
    "ml_model/export_priority_products.py" = "backend/data/export/export_priority_products.py"
    "ml_model/xgb_metrics.json" = "common/data/json/xgb_metrics.json"
    "ml_model/user_feedback.json" = "common/data/json/user_feedback.json"
    "ml_model/eco_dataset.csv" = "common/data/csv/eco_dataset.csv"
    "ml_model/defra_material_intensity.csv" = "common/data/csv/defra_material_intensity.csv"
    "ml_model/ml_vs_baseline.csv" = "common/data/csv/ml_vs_baseline.csv"
    "ml_model/prediction_log.csv" = "common/data/csv/prediction_log.csv"

    # JSON and CSV data
    "priority_products.json" = "common/data/json/priority_products.json"
    "cleaned_products.json" = "common/data/json/cleaned_products.json"
    "scraped_products_tmp.json" = "common/data/json/scraped_products_tmp.json"
    "brand_locations.json" = "common/data/json/brand_locations.json"
    "products_to_prioritize.csv" = "common/data/csv/products_to_prioritize.csv"
    "unmatched_brands.csv" = "common/data/csv/unmatched_brands.csv"
    "real_scraped_data.csv" = "common/data/csv/real_scraped_data.csv"

    # Extension JS and config files
    "Extension/manifest.json" = "frontend/extension/src/manifest.json"
    "Extension/background.js" = "frontend/extension/src/background.js"
    "Extension/dataCollector.py" = "frontend/extension/src/services/dataCollector.py"
    "Extension/tooltip.css" = "frontend/extension/src/styles/tooltip.css"
    "Extension/eco_tooltips/content/contentScript.js" = "frontend/extension/src/contentScript.js"
    "Extension/eco_tooltips/content/productPage.js" = "frontend/extension/src/components/ProductPage.js"
    "Extension/eco_tooltips/utils/lookup.js" = "frontend/extension/src/utils/lookup.js"
    "Extension/popup/hooks/useAuth.js" = "frontend/extension/src/hooks/useAuth.js"
    "Extension/popup/popup.js" = "frontend/extension/src/components/popup.js"
    "Extension/icon.png" = "frontend/extension/public/icon.png"

    # Website
    "Website/src/components/Header.jsx" = "frontend/website/src/components/Header.jsx"
    "Website/src/components/Footer.jsx" = "frontend/website/src/components/Footer.jsx"
    "Website/src/components/Layout.jsx" = "frontend/website/src/components/Layout.jsx"
    "Website/src/components/EcoLogTable.jsx" = "frontend/website/src/components/EcoLogTable.jsx"
    "Website/src/components/MLvsDEFRAChart.jsx" = "frontend/website/src/components/MLvsDefraChart.jsx"
    "Website/src/components/ModelInfoModal.jsx" = "frontend/website/src/components/ModelInfoModal.jsx"
    "Website/src/components/ModelMetricsChart.jsx" = "frontend/website/src/components/ModelMetricsChart.jsx"
    "Website/src/components/PaperPlaneTrail.jsx" = "frontend/website/src/components/PaperPlaneTrail.jsx"
    "Website/src/components/ChallengeForm.jsx" = "frontend/website/src/components/ChallengeForm.jsx"
    "Website/src/components/ImportantChart.jsx" = "frontend/website/src/components/ImportantChart.jsx"
    "Website/src/pages/HomePage.jsx" = "frontend/website/src/pages/HomePage.jsx"
    "Website/src/pages/AdminPage.jsx" = "frontend/website/src/pages/AdminPage.jsx"
    "Website/src/pages/PredictPage.jsx" = "frontend/website/src/pages/PredictPage.jsx"
    "Website/src/pages/LearnPage.jsx" = "frontend/website/src/pages/LearnPage.jsx"
    "Website/src/pages/LogOnPage.jsx" = "frontend/website/src/pages/LoginPage.jsx"
    "Website/src/pages/SignupPage.jsx" = "frontend/website/src/pages/SignupPage.jsx"
    "Website/src/pages/ExtensionPage.jsx" = "frontend/website/src/pages/ExtensionPage.jsx"
    "Website/src/hooks/useAuth.js" = "frontend/website/src/hooks/useAuth.js"
    "Website/src/services/api.js" = "frontend/website/src/services/api.js"
    "Website/src/utils/counter.js" = "frontend/website/src/utils/counter.js"
    "Website/src/index.css" = "frontend/website/src/styles/index.css"
    "Website/src/style.css" = "frontend/website/src/styles/style.css"
    "Website/src/App.jsx" = "frontend/website/src/App.jsx"
    "Website/src/main.jsx" = "frontend/website/src/main.jsx"
}

foreach ($src in $files.Keys) {
    $sourcePath = Join-Path $oldProject $src
    $destPath = Join-Path $newProject $files[$src]
    $destDir = Split-Path $destPath -Parent

    if (!(Test-Path $destDir)) {
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    }

    if (Test-Path $sourcePath) {
        Copy-Item -Force $sourcePath -Destination $destPath
        Write-Host "✅ Copied: $src → $($files[$src])"
    } else {
        Write-Host "⚠️  Missing: $sourcePath"
    }
}
