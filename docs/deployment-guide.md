# Deployment Guide

Complete guide for deploying both the standalone visualizer and Next.js application.

## Table of Contents

1. [Standalone Version (GitHub Pages)](#standalone-deployment)
2. [Next.js Application](#nextjs-deployment)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Troubleshooting](#troubleshooting)

---

## Standalone Deployment (GitHub Pages)

The standalone visualizer is a static website that runs entirely in the browser using Brython.

### Prerequisites

- Git installed
- GitHub account
- Web browser

### Step 1: Prepare Repository

```bash
# Clone or navigate to your repository
cd ai-search-v2

# Ensure all files are committed
git add .
git commit -m "Prepare for GitHub Pages deployment"
git push origin main
```

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings**
3. Scroll to **Pages** section
4. Under **Source**, select:
   - Branch: `main`
   - Folder: `/ (root)`
5. Click **Save**

### Step 3: Access Your Site

Your site will be available at:
```
https://[username].github.io/[repository-name]/
```

Example: `https://john doe.github.io/ai-search-v2/`

**Note:** It may take 1-2 minutes for the site to become available.

### Step 4: Custom Domain (Optional)

1. Purchase a domain (e.g., from Namecheap, GoDaddy)
2. In GitHub Pages settings, add your custom domain
3. Configure DNS records:
   ```
   A Record:
   185.199.108.153
   185.199.109.153
   185.199.110.153
   185.199.111.153
   
   CNAME Record (www):
   [username].github.io
   ```

### Updating Your Site

```bash
# Make changes to files
git add .
git commit -m "Update visualizer"
git push origin main

# GitHub Pages will auto-deploy in ~1 minute
```

### Local Testing

Before deploying, test locally:

```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000

# Node.js
npx http-server -p 8000
```

Visit `http://localhost:8000`

---

## Next.js Deployment

The Next.js application provides full-featured functionality with authentication and database.

### Prerequisites

- Node.js 18+ installed
- PostgreSQL or MongoDB database
- Vercel account (recommended) or alternative hosting

### Step 1: Setup Project

```bash
cd nextjs-app
npm install
```

### Step 2: Environment Configuration

Create `.env.local`:

```env
# Database
DATABASE_URL="postgresql://user:password@host:5432/dbname"
# Or MongoDB:
# DATABASE_URL="mongodb+srv://user:password@cluster.mongodb.net/dbname"

# NextAuth.js
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="generate-with-openssl-rand-base64-32"

# OAuth Providers
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"

# Email (optional for email auth)
EMAIL_SERVER="smtp://username:password@smtp.example.com:587"
EMAIL_FROM="noreply@example.com"
```

### Step 3: Database Setup

#### PostgreSQL

```bash
# Install PostgreSQL locally or use cloud service:
# - Heroku Postgres
# - Railway
# - Neon
# - Supabase

# Run Prisma migrations
npx prisma generate
npx prisma db push

# (Optional) Seed database
npx prisma db seed
```

#### MongoDB

```bash
# Use MongoDB Atlas or local MongoDB

# Update schema.prisma to use MongoDB
# Change datasource db provider to "mongodb"

# Run Prisma
npx prisma generate
npx prisma db push
```

### Step 4: OAuth Setup

#### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - **Authorized JavaScript origins:** `http://localhost:3000`, `https://yourdomain.com`
   - **Authorized redirect URIs:** `http://localhost:3000/api/auth/callback/google`
5. Copy Client ID and Secret to `.env.local`

#### GitHub OAuth

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click **New OAuth App**
3. Fill in:
   - **Homepage URL:** `http://localhost:3000`
   - **Authorization callback URL:** `http://localhost:3000/api/auth/callback/github`
4. Copy Client ID and Secret to `.env.local`

### Step 5: Local Development

```bash
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

### Step 6: Deploy to Vercel

#### Method 1: GitHub Integration (Recommended)

1. Push code to GitHub
2. Visit [Vercel](https://vercel.com)
3. Click **Import Project**
4. Select your repository
5. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `nextjs-app`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
6. Add environment variables from `.env.local`
7. Click **Deploy**

#### Method 2: Vercel CLI

```bash
npm install -g vercel
cd nextjs-app
vercel login
vercel --prod
```

### Step 7: Production Database

#### Option 1: Railway (Free tier available)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and create project
railway login
railway init
railway add postgres

# Get DATABASE_URL
railway variables

# Add to Vercel environment variables
```

#### Option 2: Neon (Serverless Postgres)

1. Visit [neon.tech](https://neon.tech)
2. Create project
3. Copy connection string
4. Add to Vercel environment variables

#### Option 3: MongoDB Atlas

1. Visit [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create cluster (free tier available)
3. Create database user
4. Get connection string
5. Add to Vercel environment variables

### Step 8: Run Migrations in Production

```bash
# After deploying, run migrations
vercel env pull .env.production.local
npx prisma generate
npx prisma db push
```

### Alternative Hosting Platforms

#### Netlify

```bash
# netlify.toml
[build]
  command = "cd nextjs-app && npm run build"
  publish = "nextjs-app/.next"

[build.environment]
  NODE_VERSION = "18"
```

Deploy:
```bash
npm install -g netlify-cli
netlify deploy --prod
```

#### Railway

```bash
railway login
railway init
railway up
```

#### Docker (Self-hosted)

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY nextjs-app/package*.json ./
RUN npm ci --only=production

COPY nextjs-app ./
RUN npx prisma generate
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t ai-search-app .
docker run -p 3000:3000 --env-file .env.local ai-search-app
```

---

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `postgresql://...` |
| `NEXTAUTH_URL` | Application URL | `https://yourdomain.com` |
| `NEXTAUTH_SECRET` | Secret for JWT | Generate with `openssl` |
| `GOOGLE_CLIENT_ID` | Google OAuth ID | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Secret | From Google Cloud Console |
| `GITHUB_CLIENT_ID` | GitHub OAuth ID | From GitHub Settings |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth Secret | From GitHub Settings |

### Generating Secrets

```bash
# Generate NEXTAUTH_SECRET
openssl rand -base64 32

# On Windows (PowerShell)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

### Environment-Specific Variables

**Development (`.env.local`):**
```env
NEXTAUTH_URL="http://localhost:3000"
NODE_ENV="development"
```

**Production (Vercel Dashboard):**
```env
NEXTAUTH_URL="https://yourdomain.vercel.app"
NODE_ENV="production"
```

---

## Database Setup

### Schema Overview

```prisma
model User {
  id            String    @id @default(cuid())
  name          String?
  email         String    @unique
  emailVerified DateTime?
  image         String?
  accounts      Account[]
  sessions      Session[]
  graphs        Graph[]
}

model Graph {
  id          String   @id @default(cuid())
  name        String
  description String?
  data        Json
  userId      String
  user        User     @relation(fields: [userId], references: [id])
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  versions    GraphVersion[]
}

model GraphVersion {
  id        String   @id @default(cuid())
  graphId   String
  graph     Graph    @relation(fields: [graphId], references: [id])
  data      Json
  createdAt DateTime @default(now())
}
```

### Initial Migration

```bash
# Create migration
npx prisma migrate dev --name init

# Apply to production
npx prisma migrate deploy
```

### Database Backups

#### PostgreSQL

```bash
# Backup
pg_dump database_name > backup.sql

# Restore
psql database_name < backup.sql
```

#### MongoDB

```bash
# Backup
mongodump --uri="mongodb+srv://..." --out=./backup

# Restore
mongorestore --uri="mongodb+srv://..." ./backup
```

---

## Performance Optimization

### Next.js Configuration

```javascript
// next.config.js
module.exports = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['lh3.googleusercontent.com', 'avatars.githubusercontent.com'],
  },
  compress: true,
  poweredByHeader: false,
}
```

### Caching Strategy

```typescript
// API route with caching
export async function GET(request: Request) {
  return new Response(JSON.stringify(data), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=86400',
    },
  })
}
```

### Image Optimization

Use Next.js Image component:
```tsx
import Image from 'next/image'

<Image src="/graph-thumbnail.png" width={300} height={200} alt="Graph" />
```

---

## Monitoring and Analytics

### Vercel Analytics

```bash
npm install @vercel/analytics
```

```tsx
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

### Error Tracking (Sentry)

```bash
npm install @sentry/nextjs
```

```javascript
// sentry.client.config.js
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 1.0,
})
```

---

## Troubleshooting

### Common Issues

**Issue: "Module not found" during build**
```bash
# Solution: Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build
```

**Issue: Database connection fails**
```bash
# Solution: Check DATABASE_URL format
# PostgreSQL: postgresql://USER:PASSWORD@HOST:PORT/DATABASE
# MongoDB: mongodb+srv://USER:PASSWORD@CLUSTER/DATABASE
```

**Issue: OAuth redirect mismatch**
```
# Solution: Verify redirect URIs match exactly
# Google/GitHub Console: http://localhost:3000/api/auth/callback/provider
# Production: https://yourdomain.com/api/auth/callback/provider
```

**Issue: Build fails on Vercel**
```bash
# Solution: Check Node version
# Ensure package.json has:
"engines": {
  "node": ">=18.0.0"
}
```

### Logs

**Vercel:**
```bash
vercel logs [deployment-url]
```

**Railway:**
```bash
railway logs
```

**Local:**
```bash
npm run dev -- --debug
```

---

## Security Checklist

- [ ] Environment variables stored securely
- [ ] NEXTAUTH_SECRET is random and strong
- [ ] Database credentials not in code
- [ ] OAuth redirects use HTTPS in production
- [ ] CORS configured properly
- [ ] Rate limiting enabled on API routes
- [ ] Input validation on all forms
- [ ] SQL injection prevention (use Prisma)
- [ ] XSS prevention (React handles this)
- [ ] CSRF protection (NextAuth handles this)

---

## Maintenance

### Regular Updates

```bash
# Update dependencies
npm outdated
npm update

# Security audit
npm audit
npm audit fix
```

### Database Maintenance

```bash
# Backup before updates
# Test migrations in staging
npx prisma migrate dev
npx prisma migrate deploy
```

### Monitoring

- Check error logs weekly
- Review analytics monthly
- Test all features after updates
- Monitor database size and performance

---

## Support

- **Documentation:** [Next.js Docs](https://nextjs.org/docs)
- **Deployment:** [Vercel Docs](https://vercel.com/docs)
- **Database:** [Prisma Docs](https://www.prisma.io/docs)
- **Auth:** [NextAuth.js Docs](https://next-auth.js.org)

---

**Previous:** [Algorithm Guide](algorithm-guide.md) | [API Reference](api-reference.md) | [Back to README](../README.md)
