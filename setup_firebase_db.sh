#!/bin/bash

# MediChain Firebase + Supabase Database Setup Script
# Run this script to set up your database with Firebase integration

echo "🚀 Setting up MediChain Database with Firebase Integration"
echo "=========================================================="

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI is not installed. Please install it first:"
    echo "npm install -g supabase"
    exit 1
fi

# Check if user is logged in to Supabase
echo "🔐 Checking Supabase authentication..."
if ! supabase projects list &> /dev/null; then
    echo "❌ Not logged in to Supabase. Please login first:"
    echo "supabase login"
    exit 1
fi

echo "✅ Supabase CLI is ready!"

# Ask for project reference
read -p "Enter your Supabase project reference (from https://supabase.com/dashboard/project/...): " PROJECT_REF

if [ -z "$PROJECT_REF" ]; then
    echo "❌ Project reference is required"
    exit 1
fi

echo "📋 Setting up database for project: $PROJECT_REF"
echo ""

# Link to the project
echo "🔗 Linking to Supabase project..."
supabase link --project-ref $PROJECT_REF

if [ $? -ne 0 ]; then
    echo "❌ Failed to link to Supabase project"
    exit 1
fi

echo "✅ Successfully linked to project!"
echo ""

# Run the enhanced schema
echo "📊 Creating database tables..."
supabase db push

if [ $? -ne 0 ]; then
    echo "❌ Failed to create database tables"
    exit 1
fi

echo "✅ Database tables created successfully!"
echo ""

# Apply RLS policies
echo "🔒 Applying Row Level Security policies..."
supabase db reset

if [ $? -ne 0 ]; then
    echo "❌ Failed to apply RLS policies"
    exit 1
fi

echo "✅ RLS policies applied successfully!"
echo ""

# Seed the database with test data
echo "🌱 Seeding database with test data..."

# Create a test admin user (this would normally be done through the app)
echo "Note: Test users will be created when users sign up through the Firebase-authenticated app"
echo ""

echo "🎉 Database setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update your frontend .env with Supabase credentials"
echo "2. Test the authentication flow"
echo "3. Create your first user through the app"
echo ""
echo "🔗 Your Supabase project: https://supabase.com/dashboard/project/$PROJECT_REF"
echo ""

# Optional: Generate types
read -p "Generate TypeScript types for the database? (y/n): " GENERATE_TYPES

if [ "$GENERATE_TYPES" = "y" ] || [ "$GENERATE_TYPES" = "Y" ]; then
    echo "🔧 Generating TypeScript types..."
    supabase gen types typescript --local > src/types/database.ts
    echo "✅ Types generated in src/types/database.ts"
fi

echo ""
echo "🎊 Setup complete! Your MediChain database is ready for Firebase authentication."</content>
<parameter name="filePath">c:\Users\abayo\OneDrive\Desktop\thesis\medichain\setup_firebase_db.sh
