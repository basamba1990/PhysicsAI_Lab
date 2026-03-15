# Physics AI Dashboard - TODO

## Phase 1: Analyse et Architecture
- [ ] Analyse comparative complète des deux versions (lean vs industrial)
- [ ] Architecture détaillée avec Supabase intégration
- [ ] Définition du modèle de données (schema Drizzle)
- [ ] Rapport d'analyse comparative

## Phase 2: Backend Python
- [ ] PINN Engine amélioré avec export ONNX
- [ ] PINO (Physics-Informed Neural Operator) implementation
- [ ] CFD Data Pipeline avec synthétique et prétraitement
- [ ] Ethics Validator avec règles configurables
- [ ] Model versioning et tracking
- [ ] Tests unitaires Python

## Phase 3: Edge Function Supabase
- [ ] Inférence ONNX avec support Deno/WASM
- [ ] Monte Carlo Dropout pour quantification d'incertitude
- [ ] Cache des prédictions avec Supabase
- [ ] Gestion des versions de modèles
- [ ] Error handling et logging
- [ ] Tests Edge Function

## Phase 4: Frontend Web
- [ ] Dashboard layout avec sidebar navigation
- [ ] Simulation interactive 2D/3D (Three.js/Babylon.js)
- [ ] Visualisation en temps réel des champs physiques
- [ ] Formulaire de configuration simulation
- [ ] Graphiques de performance du modèle
- [ ] Comparaison PINN vs CFD
- [ ] Export/téléchargement modèles ONNX
- [ ] Gestion des versions de modèles
- [ ] Validation éthique UI
- [ ] Responsive design

## Phase 5: Base de Données et Tests
- [ ] Schema Drizzle complet (simulations, predictions, models, users)
- [ ] Migrations SQL via webdev_execute_sql
- [ ] Query helpers dans server/db.ts
- [ ] tRPC procedures pour toutes les features
- [ ] Vitest tests pour backend
- [ ] Vitest tests pour frontend

## Phase 6: Documentation
- [ ] Rapport d'analyse comparative détaillé
- [ ] Architecture documentation
- [ ] API documentation
- [ ] Deployment guide

## Phase 7: Livraison
- [ ] Checkpoint final
- [ ] Archive complète du projet
- [ ] Rapport de synthèse
