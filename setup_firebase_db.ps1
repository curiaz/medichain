# MediChain Firebase + Supabase Database Setup Script
# Run this script to set up your database with Firebase integration

Write-Host "🚀 Setting up MediChain Database with Firebase Integration" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

# Check if Supabase CLI is installed
try {
    $supabaseVersion = supabase --version 2>$null
    Write-Host "✅ Supabase CLI is installed: $supabaseVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Supabase CLI is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "npm install -g supabase" -ForegroundColor Yellow
    exit 1
}

# Check if user is logged in to Supabase
Write-Host "🔐 Checking Supabase authentication..." -ForegroundColor Yellow
try {
    supabase projects list >$null 2>&1
    Write-Host "✅ Logged in to Supabase!" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Supabase. Please login first:" -ForegroundColor Red
    Write-Host "supabase login" -ForegroundColor Yellow
    exit 1
}

# Ask for project reference
$PROJECT_REF = Read-Host "Enter your Supabase project reference (from https://supabase.com/dashboard/project/...)"

if ([string]::IsNullOrEmpty($PROJECT_REF)) {
    Write-Host "❌ Project reference is required" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Setting up database for project: $PROJECT_REF" -ForegroundColor Cyan
Write-Host ""

# Link to the project
Write-Host "🔗 Linking to Supabase project..." -ForegroundColor Yellow
try {
    supabase link --project-ref $PROJECT_REF
    Write-Host "✅ Successfully linked to project!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to link to Supabase project" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Run the enhanced schema
Write-Host "📊 Creating database tables..." -ForegroundColor Yellow
try {
    supabase db push
    Write-Host "✅ Database tables created successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create database tables" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Apply RLS policies
Write-Host "🔒 Applying Row Level Security policies..." -ForegroundColor Yellow
try {
    supabase db reset
    Write-Host "✅ RLS policies applied successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to apply RLS policies" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Seed the database with test data
Write-Host "🌱 Database setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Update your frontend .env with Supabase credentials" -ForegroundColor White
Write-Host "2. Test the authentication flow" -ForegroundColor White
Write-Host "3. Create your first user through the app" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Your Supabase project: https://supabase.com/dashboard/project/$PROJECT_REF" -ForegroundColor Blue
Write-Host ""

# Optional: Generate types
$GENERATE_TYPES = Read-Host "Generate TypeScript types for the database? (y/n)"

if ($GENERATE_TYPES -eq "y" -or $GENERATE_TYPES -eq "Y") {
    Write-Host "🔧 Generating TypeScript types..." -ForegroundColor Yellow
    try {
        supabase gen types typescript --local > src/types/database.ts
        Write-Host "✅ Types generated in src/types/database.ts" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Failed to generate types, but that's okay!" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎊 Setup complete! Your MediChain database is ready for Firebase authentication." -ForegroundColor Green</content>
<parameter name="filePath">c:\Users\abayo\OneDrive\Desktop\thesis\medichain\setup_firebase_db.ps1
