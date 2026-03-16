# Physics AI Lab - Next.js + Supabase Edition

Advanced Physics-Informed Neural Networks (PINN) and Physics-Informed Operator Networks (PINO) Simulation Platform with real-time analytics, model versioning, and ethics validation.

Built with **Next.js 15**, **Supabase**, **Recharts**, and **Tailwind CSS**.

## 🚀 Features

### Core Capabilities

- **PINN/PINO Simulations**: Execute physics-informed neural network simulations for heat transfer, fluid dynamics, wave propagation, and custom physics equations
- **Real-time Analytics**: Interactive dashboards with Recharts visualizations for loss curves, accuracy metrics, and PINN vs CFD comparisons
- **Model Management**: Version control, performance tracking, and comparison of different PINN/PINO variants
- **Edge Functions**: Supabase Edge Functions (Deno) for fast inference and ethics validation
- **Secure Storage**: S3-compatible storage with pre-signed URLs for model files and results
- **Authentication**: Email, Google, and GitHub OAuth via Supabase Auth

### Technical Highlights

- **Full-Stack TypeScript**: Type-safe development from frontend to backend
- **Next.js 15**: Modern React with App Router and Server Components
- **Supabase**: PostgreSQL database with Row Level Security (RLS)
- **Recharts**: Interactive data visualizations
- **Tailwind CSS**: Scientific theme with blue/cyan/orange color palette
- **Vercel Deployment**: Optimized for serverless infrastructure

## 📋 Prerequisites

- Node.js 18+
- npm or pnpm
- Supabase account
- Vercel account
- GitHub repository

## 🛠️ Local Development

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/physics-ai-lab-nextjs.git
cd physics-ai-lab-nextjs

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local

# Update environment variables
# NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Development Server

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📦 Project Structure

```
physics-ai-lab-nextjs/
├── app/                             # Next.js App Router
│   ├── layout.tsx                  # Root layout
│   ├── page.tsx                    # Home page
│   ├── globals.css                 # Global styles
│   ├── auth/                       # Authentication pages
│   │   ├── page.tsx               # Login page
│   │   └── callback/route.ts       # OAuth callback
│   └── dashboard/                  # Dashboard pages
│       └── page.tsx               # Main dashboard
├── lib/                            # Utilities
│   └── supabase.ts                # Supabase client
├── supabase/                       # Supabase configuration
│   ├── functions/                 # Edge Functions
│   │   └── predict-flow/          # PINN prediction function
│   └── migrations/                # Database migrations
├── public/                         # Static assets
├── package.json                    # Dependencies
├── next.config.js                  # Next.js configuration
├── tailwind.config.ts              # Tailwind configuration
├── tsconfig.json                   # TypeScript configuration
├── DEPLOYMENT_GUIDE.md             # Deployment instructions
└── README.md                       # This file
```

## 🗄️ Database Schema

### Tables

| Table | Purpose |
|-------|---------|
| `simulations` | Physics simulation configurations and status |
| `predictions` | PINN/PINO model predictions |
| `model_versions` | Trained model versions with metrics |
| `training_jobs` | Long-running training job tracking |
| `ethics_logs` | Ethics validation check results |

All tables have Row Level Security (RLS) enabled for multi-tenant data isolation.

## 🔌 API Routes

### Authentication

- `GET /auth` - Login page
- `POST /auth/callback` - OAuth callback handler
- `POST /api/auth/logout` - Logout endpoint

### Simulations

- `GET /api/simulations` - List user's simulations
- `POST /api/simulations` - Create new simulation
- `GET /api/simulations/[id]` - Get simulation details
- `PUT /api/simulations/[id]` - Update simulation
- `DELETE /api/simulations/[id]` - Delete simulation

### Models

- `GET /api/models` - List user's models
- `POST /api/models` - Create new model version
- `GET /api/models/[id]` - Get model details
- `GET /api/models/[id]/metrics` - Get model metrics

## 🚀 Deployment

### Quick Start

1. **Supabase Setup**
   ```bash
   # Create project and apply schema
   # See DEPLOYMENT_GUIDE.md Step 1
   ```

2. **Deploy Edge Functions**
   ```bash
   supabase functions deploy predict-flow
   ```

3. **Deploy to Vercel**
   ```bash
   # Push to GitHub
   git push origin main
   
   # Deploy via Vercel UI
   # See DEPLOYMENT_GUIDE.md Step 3
   ```

### Environment Variables

Required environment variables for production:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## 📊 Visualizations

### Dashboard Charts

- **PINN vs CFD Comparison**: Line chart comparing PINN predictions against CFD reference
- **Training History**: Loss curves (training, validation, physics loss) across epochs
- **Model Metrics**: Performance indicators for fidelity and accuracy
- **Simulation Stats**: Overview of completed, running, and failed simulations

All charts use Recharts with dark theme optimized for scientific data.

## 🔐 Security

- **Authentication**: OAuth 2.0 via Supabase (Email, Google, GitHub)
- **Database**: Row Level Security (RLS) for multi-tenant isolation
- **API**: Server-side validation with TypeScript
- **Storage**: S3 with pre-signed URLs
- **Encryption**: HTTPS for all communications

## 📈 Performance

- **Frontend**: Next.js with optimized images and code splitting
- **Backend**: Edge Functions for low-latency inference
- **Database**: PostgreSQL with optimized indexes
- **Caching**: Supabase realtime subscriptions for live updates

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test -- auth.test.ts
```

## 📚 Documentation

- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[Next.js Documentation](https://nextjs.org/docs)** - Framework documentation
- **[Supabase Documentation](https://supabase.com/docs)** - Backend infrastructure
- **[Vercel Documentation](https://vercel.com/docs)** - Deployment platform
- **[Recharts Documentation](https://recharts.org)** - Data visualization

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: See docs/ directory
- **Email**: support@physicsailab.com

## 🎯 Roadmap

- [ ] 3D visualization with Three.js
- [ ] AI-powered simulation explanations
- [ ] Automated parameter optimization
- [ ] Real-time collaboration features
- [ ] Advanced model ensemble methods
- [ ] GPU acceleration for inference
- [ ] Mobile app (React Native)

## 🙏 Acknowledgments

- Built with [Next.js](https://nextjs.org), [React](https://react.dev), [Tailwind CSS](https://tailwindcss.com)
- Backend powered by [Supabase](https://supabase.com)
- Visualizations with [Recharts](https://recharts.org)
- Deployed on [Vercel](https://vercel.com)

---

**Physics AI Lab** - Advanced PINN/PINO Simulation Platform for Scientific Computing
