# Next.js Application - AI Search Visualizer

This directory will contain the full-featured Next.js application with authentication, user accounts, and cloud storage.

## 🚀 Quick Setup

### 1. Initialize Next.js Project

```bash
# From the ai-search-v2 directory
npx create-next-app@latest nextjs-app --typescript --tailwind --app --src-dir

# Navigate to nextjs-app
cd nextjs-app

# Install additional dependencies
npm install prisma @prisma/client
npm install next-auth @auth/prisma-adapter
npm install bcryptjs zod react-hook-form @hookform/resolvers
npm install lucide-react
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install -D @types/bcryptjs
```

### 2. Initialize Prisma

```bash
npx prisma init
```

### 3. Copy Core Python Files

```bash
# Copy visualization files to public directory
cp ../Node.py public/
cp ../SearchAgent.py public/
cp ../PriorityQueue.py public/
cp ../main.py public/
```

### 4. Setup Environment Variables

Create `.env.local`:

```env
# Database URL (choose one):
# PostgreSQL:
DATABASE_URL="postgresql://user:password@localhost:5432/aisearch"

# MongoDB:
# DATABASE_URL="mongodb+srv://user:password@cluster.mongodb.net/aisearch"

# NextAuth Configuration
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="generate-random-secret-here"

# OAuth Providers (Get from respective developer consoles)
GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"
```

**Generate NEXTAUTH_SECRET:**
```bash
# On Mac/Linux:
openssl rand -base64 32

# On Windows (PowerShell):
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

### 5. Update Prisma Schema

Replace `prisma/schema.prisma` content with:

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  // or "mongodb" for MongoDB
  url      = env("DATABASE_URL")
}

model User {
  id            String    @id @default(cuid())
  name          String?
  email         String    @unique
  emailVerified DateTime?
  image         String?
  password      String?
  accounts      Account[]
  sessions      Session[]
  graphs        Graph[]
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
}

model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String? @db.Text
  access_token      String? @db.Text
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String? @db.Text
  session_state     String?
  user              User    @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model Graph {
  id          String         @id @default(cuid())
  name        String
  description String?
  data        Json
  thumbnail   String?
  userId      String
  user        User           @relation(fields: [userId], references: [id], onDelete: Cascade)
  versions    GraphVersion[]
  isPublic    Boolean        @default(false)
  tags        String[]
  createdAt   DateTime       @default(now())
  updatedAt   DateTime       @updatedAt

  @@index([userId])
  @@index([isPublic])
}

model GraphVersion {
  id        String   @id @default(cuid())
  graphId   String
  graph     Graph    @relation(fields: [graphId], references: [id], onDelete: Cascade)
  data      Json
  comment   String?
  createdAt DateTime @default(now())

  @@index([graphId])
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
}
```

### 6. Push Database Schema

```bash
# Generate Prisma Client
npx prisma generate

# Push schema to database
npx prisma db push

# (Optional) Open Prisma Studio to view database
npx prisma studio
```

### 7. Project Structure

Create this structure:

```
nextjs-app/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── signin/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── visualizer/
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── api/
│   │   │   ├── auth/
│   │   │   │   └── [...nextauth]/
│   │   │   │       └── route.ts
│   │   │   └── graphs/
│   │   │       ├── route.ts
│   │   │       └── [id]/
│   │   │           └── route.ts
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── Navbar.tsx
│   │   ├── GraphCanvas.tsx
│   │   ├── AlgorithmSelector.tsx
│   │   ├── AnimationControls.tsx
│   │   ├── DataPanel.tsx
│   │   ├── GraphCard.tsx
│   │   └── ProtectedRoute.tsx
│   ├── lib/
│   │   ├── prisma.ts
│   │   ├── auth.ts
│   │   ├── utils.ts
│   │   └── validations.ts
│   └── types/
│       └── index.ts
├── public/
│   ├── Node.py
│   ├── SearchAgent.py
│   ├── PriorityQueue.py
│   └── main.py
├── prisma/
│   └── schema.prisma
├── .env.local
├── next.config.js
├── package.json
├── tsconfig.json
└── tailwind.config.ts
```

### 8. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 📁 Key Files to Create

### src/lib/prisma.ts

```typescript
import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
```

### src/lib/auth.ts

```typescript
import { NextAuthOptions } from 'next-auth'
import { PrismaAdapter } from '@auth/prisma-adapter'
import GoogleProvider from 'next-auth/providers/google'
import GitHubProvider from 'next-auth/providers/github'
import CredentialsProvider from 'next-auth/providers/credentials'
import { prisma } from './prisma'
import bcrypt from 'bcryptjs'

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error('Invalid credentials')
        }

        const user = await prisma.user.findUnique({
          where: { email: credentials.email }
        })

        if (!user || !user.password) {
          throw new Error('Invalid credentials')
        }

        const isValid = await bcrypt.compare(credentials.password, user.password)

        if (!isValid) {
          throw new Error('Invalid credentials')
        }

        return user
      }
    })
  ],
  session: {
    strategy: 'jwt'
  },
  pages: {
    signIn: '/signin',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
      }
      return session
    }
  }
}
```

### src/app/api/auth/[...nextauth]/route.ts

```typescript
import NextAuth from 'next-auth'
import { authOptions } from '@/lib/auth'

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST }
```

## 🎨 UI Components

### Basic Navbar Component

```tsx
// src/components/Navbar.tsx
import Link from 'next/link'
import { useSession, signOut } from 'next-auth/react'

export default function Navbar() {
  const { data: session } = useSession()

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold text-blue-600">
              AI Search Visualizer
            </Link>
          </div>
          
          <div className="flex items-center gap-4">
            {session ? (
              <>
                <Link href="/dashboard" className="text-gray-700 hover:text-blue-600">
                  Dashboard
                </Link>
                <Link href="/visualizer" className="text-gray-700 hover:text-blue-600">
                  Visualizer
                </Link>
                <button
                  onClick={() => signOut()}
                  className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                >
                  Sign Out
                </button>
              </>
            ) : (
              <>
                <Link href="/signin" className="text-gray-700 hover:text-blue-600">
                  Sign In
                </Link>
                <Link href="/signup" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
```

## 🔐 OAuth Setup

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google+ API
4. Create OAuth credentials:
   - **Authorized JavaScript origins:** `http://localhost:3000`, `https://yourdomain.com`
   - **Authorized redirect URIs:** `http://localhost:3000/api/auth/callback/google`
5. Copy Client ID and Secret to `.env.local`

### GitHub OAuth

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in:
   - **Homepage URL:** `http://localhost:3000`
   - **Authorization callback URL:** `http://localhost:3000/api/auth/callback/github`
4. Copy Client ID and Secret to `.env.local`

## 🚀 Deployment

### Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

Or connect your GitHub repo to Vercel dashboard for automatic deployments.

### Environment Variables on Vercel

Add all variables from `.env.local` in:
Vercel Dashboard → Project → Settings → Environment Variables

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Prisma Documentation](https://www.prisma.io/docs)
- [NextAuth.js Documentation](https://next-auth.js.org)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## ⚠️ Important Notes

1. **Never commit `.env.local`** to version control
2. Use different OAuth credentials for development and production
3. Set up proper database backups in production
4. Enable HTTPS in production (Vercel does this automatically)
5. Configure CORS if API is accessed from other domains

## 🐛 Troubleshooting

**Database connection fails:**
- Check DATABASE_URL format
- Ensure database server is running
- Verify credentials

**OAuth not working:**
- Check redirect URLs match exactly
- Verify client IDs and secrets
- Clear browser cookies and try again

**Build fails:**
- Run `npx prisma generate` before build
- Check all environment variables are set
- Clear `.next` folder and rebuild

---

## 🎉 You're Ready!

The standalone version is fully functional. This Next.js app adds:
- 👤 User authentication
- ☁️ Cloud storage for graphs
- 🔄 Version history
- 🔗 Sharing capabilities
- 📊 Advanced analytics

Follow the steps above to build the full-featured version!
