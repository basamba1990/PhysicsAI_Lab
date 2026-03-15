# Physics AI Dashboard - Guide de Déploiement Complet

## 📋 Table des Matières

1. [Architecture Globale](#architecture-globale)
2. [Prérequis](#prérequis)
3. [Installation Locale](#installation-locale)
4. [Configuration Supabase](#configuration-supabase)
5. [Déploiement Production](#déploiement-production)
6. [Intégration ONNX](#intégration-onnx)
7. [Monitoring et Maintenance](#monitoring-et-maintenance)

---

## Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                    Physics AI Dashboard                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Frontend (React + Tailwind)                               │
│  ├─ Dashboard avec visualisations 2D/3D                    │
│  ├─ Formulaires de simulation                              │
│  ├─ Graphiques de performance                              │
│  └─ Gestion des versions de modèles                        │
│                                                             │
│  Backend (Express + tRPC)                                  │
│  ├─ API REST pour simulations                              │
│  ├─ Gestion des jobs d'entraînement                        │
│  ├─ Validation éthique                                     │
│  └─ Versioning de modèles                                  │
│                                                             │
│  Edge Functions (Supabase + Deno)                          │
│  ├─ Inférence ONNX                                         │
│  ├─ Monte Carlo Dropout (UQ)                               │
│  ├─ Cache des prédictions                                  │
│  └─ Logging et traçabilité                                 │
│                                                             │
│  Base de Données (MySQL/TiDB)                              │
│  ├─ Simulations                                            │
│  ├─ Prédictions (cache)                                    │
│  ├─ Versions de modèles                                    │
│  ├─ Logs éthiques                                          │
│  └─ Jobs d'entraînement                                    │
│                                                             │
│  Stockage (Supabase Storage)                               │
│  ├─ Modèles ONNX                                           │
│  ├─ Datasets CFD                                           │
│  └─ Checkpoints d'entraînement                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Prérequis

### Outils Requis
- Node.js 18+ avec pnpm
- Python 3.10+ avec pip
- Docker (optionnel, pour Supabase local)
- Git

### Comptes Externes
- Supabase (gratuit ou payant)
- Manus (pour OAuth)

### Dépendances Python
```bash
pip install -r requirements.txt
```

### Dépendances Node.js
```bash
pnpm install
```

---

## Installation Locale

### 1. Cloner le projet
```bash
git clone <repository-url>
cd physics-ai-dashboard
```

### 2. Configurer les variables d'environnement
```bash
cp .env.example .env.local
```

Éditer `.env.local` avec :
```
DATABASE_URL=mysql://user:password@localhost:3306/physics_ai
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
ONNX_MODEL_PATH=https://storage.supabase.co/models/pinn_model.onnx
```

### 3. Initialiser la base de données
```bash
pnpm drizzle-kit generate
pnpm drizzle-kit migrate
```

### 4. Lancer le serveur de développement
```bash
pnpm dev
```

L'application sera disponible à `http://localhost:3000`

---

## Configuration Supabase

### 1. Créer un projet Supabase
- Aller sur https://supabase.com
- Créer un nouveau projet
- Copier l'URL et la clé de service

### 2. Créer les tables
```bash
# Exécuter le schema SQL
psql -h your-project.supabase.co -U postgres -d postgres -f infrastructure/supabase/schema.sql
```

### 3. Configurer les Edge Functions
```bash
# Déployer l'Edge Function predict-flow
supabase functions deploy predict-flow --project-id your-project-id
```

### 4. Configurer le stockage
```bash
# Créer les buckets
supabase storage create-bucket models --public
supabase storage create-bucket datasets --public
```

---

## Déploiement Production

### Option 1: Manus Hosting (Recommandé)
```bash
# Créer un checkpoint
pnpm webdev-save-checkpoint "Production v1.0"

# Cliquer sur "Publish" dans l'interface Manus
```

### Option 2: Vercel
```bash
# Installer Vercel CLI
npm i -g vercel

# Déployer
vercel --prod
```

### Option 3: Railway
```bash
# Installer Railway CLI
npm i -g @railway/cli

# Déployer
railway up
```

---

## Intégration ONNX

### 1. Exporter le modèle PINN
```python
from core.pinn_engine import PINNSurrogate

# Charger le modèle entraîné
pinn = PINNSurrogate(config)
pinn.load_model("models/pinn_v1.pt")

# Exporter en ONNX
pinn.export_onnx("models/pinn_v1.onnx")
```

### 2. Uploader le modèle ONNX
```bash
# Uploader vers Supabase Storage
supabase storage upload models pinn_v1.onnx --project-id your-project-id
```

### 3. Configurer l'Edge Function
```typescript
// infrastructure/supabase/functions/predict-flow/index.ts
const modelPath = "https://storage.supabase.co/models/pinn_v1.onnx"
```

---

## Monitoring et Maintenance

### Logs
```bash
# Voir les logs du serveur
pnpm dev 2>&1 | tee logs/server.log

# Voir les logs des Edge Functions
supabase functions logs predict-flow --project-id your-project-id
```

### Métriques
- Dashboard Supabase : https://app.supabase.com
- Monitoring des prédictions : `/api/trpc/simulations.list`
- Logs éthiques : `/api/trpc/ethics.getLogs`

### Maintenance
```bash
# Nettoyer le cache des prédictions
DELETE FROM predictions WHERE created_at < NOW() - INTERVAL 7 DAY;

# Archiver les jobs d'entraînement anciens
UPDATE training_jobs SET status = 'archived' WHERE completed_at < NOW() - INTERVAL 30 DAY;
```

---

## Troubleshooting

### Erreur: "Model not loaded"
- Vérifier que `ONNX_MODEL_PATH` est correct
- Vérifier que le fichier ONNX existe dans Supabase Storage
- Vérifier les logs de l'Edge Function

### Erreur: "Database connection failed"
- Vérifier `DATABASE_URL`
- Vérifier que la base de données est accessible
- Vérifier les credentials

### Erreur: "CORS error"
- Vérifier les headers CORS dans l'Edge Function
- Vérifier que l'URL frontend est whitelistée

---

## Support et Documentation

- **Documentation API** : `/api/docs`
- **Docs Supabase** : https://supabase.com/docs
- **Docs Deno** : https://deno.land/manual
- **Docs ONNX** : https://onnx.ai/docs

---

## Checklist de Déploiement

- [ ] Variables d'environnement configurées
- [ ] Base de données initialisée
- [ ] Modèle ONNX exporté et uploadé
- [ ] Edge Functions déployées
- [ ] Tests passants (`pnpm test`)
- [ ] Build production réussi (`pnpm build`)
- [ ] Monitoring configuré
- [ ] Backups configurés
- [ ] Documentation à jour
- [ ] Équipe informée

---

**Dernière mise à jour** : 2026-03-15
**Version** : 1.0.0
