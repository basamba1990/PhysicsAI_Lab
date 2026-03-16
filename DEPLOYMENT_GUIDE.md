# Physics AI Lab - Deployment Guide (Vercel + Supabase)

## Overview

Physics AI Lab is a full-stack Next.js application for managing Physics-Informed Neural Networks (PINN) and Physics-Informed Operator Networks (PINO) simulations. This guide covers deployment to **Vercel** (frontend/backend) and **Supabase** (database + Edge Functions).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Vercel (Next.js)                         │
│  Frontend (React) + Backend (API Routes)                    │
│  - Dashboard with Recharts visualizations                  │
│  - Authentication via Supabase                             │
│  - Simulation management interface                         │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│           Supabase (Backend Infrastructure)                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ PostgreSQL Database                                 │  │
│  │ - simulations, predictions, model_versions         │  │
│  │ - training_jobs, ethics_logs                       │  │
│  │ - Row Level Security (RLS) enabled                │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Authentication (Email, Google, GitHub OAuth)       │  │
│  │ - User management and session handling             │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Edge Functions (Deno/TypeScript)                   │  │
│  │ - predict-flow: PINN/PINO inference                │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Storage (S3-compatible)                             │  │
│  │ - ONNX models, simulation results                  │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Node.js 18+ and npm/pnpm
- Supabase account (https://supabase.com)
- Vercel account (https://vercel.com)
- GitHub repository

## Step 1: Supabase Setup

### 1.1 Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Enter project name: `physics-ai-lab`
4. Choose a region close to your users
5. Set a strong database password
6. Click "Create new project"

### 1.2 Apply Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Create a new query
3. Copy the contents of `supabase/migrations/001_initial_schema.sql`
4. Paste into the SQL editor and execute

### 1.3 Configure Authentication

1. Go to **Authentication → Providers**
2. Enable "Email" provider
3. Go to **Authentication → URL Configuration**
4. Add your Vercel deployment URL to "Redirect URLs":
   ```
   https://your-app.vercel.app/auth/callback
   https://your-app.vercel.app
   ```

### 1.4 Get Connection Details

1. Go to **Project Settings → Database**
2. Copy the "Connection string" (PostgreSQL URI)
3. Go to **Project Settings → API**
4. Copy "Project URL" and "anon key"
5. Go to **Project Settings → API → Service Role Key**
6. Copy the "Service Role Key"

## Step 2: Deploy Edge Functions to Supabase

### 2.1 Install Supabase CLI

```bash
npm install -g supabase
```

### 2.2 Link Project

```bash
cd physics-ai-lab-nextjs
supabase link --project-ref <YOUR_PROJECT_ID>
```

### 2.3 Deploy Functions

```bash
supabase functions deploy predict-flow
```

## Step 3: Deploy to Vercel

### 3.1 Prepare Environment Variables

Create a `.env.local` file with:

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT_ID].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 3.2 Push to GitHub

```bash
git add .
git commit -m "Initial Physics AI Lab deployment"
git push origin main
```

### 3.3 Deploy to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Select "Next.js" as the framework
4. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

5. Add Environment Variables:
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT_ID].supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```

6. Click "Deploy"

### 3.4 Update Supabase Redirect URLs

After deployment, update Supabase redirect URLs with your Vercel domain:

1. Go to Supabase **Authentication → URL Configuration**
2. Add:
   ```
   https://your-vercel-domain.vercel.app/auth/callback
   https://your-vercel-domain.vercel.app
   ```

## Step 4: Post-Deployment Configuration

### 4.1 Test Database Connection

```bash
# From your local machine
psql postgresql://postgres:[PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres
```

### 4.2 Verify Edge Functions

```bash
curl -X POST https://[PROJECT_ID].supabase.co/functions/v1/predict-flow \
  -H "Authorization: Bearer [ANON_KEY]" \
  -H "Content-Type: application/json" \
  -d '{
    "simulationId": "test-123",
    "modelVersionId": "model-456",
    "parameters": {"temperature": 100}
  }'
```

### 4.3 Test Application

1. Navigate to your Vercel deployment URL
2. Click "Sign In"
3. Create an account or sign in with Google/GitHub
4. Verify dashboard loads correctly

## Environment Variables Reference

| Variable | Description | Source |
|----------|-------------|--------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | Supabase Settings |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Public API key | Supabase Settings |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (secret) | Supabase Settings |

## Troubleshooting

### Issue: Authentication Redirect Loop

**Solution:**
1. Verify redirect URLs in Supabase match your Vercel domain
2. Check `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are correct
3. Clear browser cookies and retry

### Issue: Database Connection Failed

**Solution:**
1. Verify `NEXT_PUBLIC_SUPABASE_URL` is correct
2. Check firewall rules in Supabase
3. Ensure IP whitelist includes Vercel IPs

### Issue: Edge Functions Timeout

**Solution:**
1. Check function logs: `supabase functions logs predict-flow`
2. Optimize function code
3. Increase timeout if needed

## Monitoring & Maintenance

### Database Backups

1. Go to Supabase **Project Settings → Backups**
2. Enable automatic daily backups
3. Configure backup retention policy

### Logs

- **Vercel Logs**: https://vercel.com/dashboard → Project → Deployments → Logs
- **Supabase Logs**: https://supabase.com → Project → Logs

### Performance

- Monitor database query performance in Supabase
- Check Edge Function execution times
- Use Vercel Analytics for frontend performance

## Security Best Practices

1. **Secrets Management**
   - Never commit `.env` files
   - Use Vercel Environment Variables UI
   - Rotate API keys regularly

2. **Database Security**
   - Enable RLS policies (already done)
   - Use strong passwords
   - Enable SSL connections

3. **API Security**
   - Validate all inputs
   - Implement rate limiting
   - Use HTTPS only

4. **Authentication**
   - Enforce strong passwords
   - Enable 2FA for admin accounts
   - Audit access logs

## Support & Resources

- **Supabase Docs**: https://supabase.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Next.js Docs**: https://nextjs.org/docs
- **Recharts Docs**: https://recharts.org

## Next Steps

1. Set up monitoring and alerting
2. Configure backup strategy
3. Implement CI/CD pipeline
4. Add custom domain
5. Scale infrastructure as needed
