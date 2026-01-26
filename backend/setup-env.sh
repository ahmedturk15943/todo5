#!/bin/bash
# Backend Environment Variables Setup Script
# Run this from the backend directory

echo "Setting up backend environment variables..."

# You'll be prompted to enter values for each variable
vercel env add DATABASE_URL production
vercel env add BETTER_AUTH_SECRET production
vercel env add CORS_ORIGINS production
vercel env add JWT_ALGORITHM production
vercel env add JWT_EXPIRY_DAYS production
vercel env add DEBUG production
vercel env add LOG_LEVEL production

echo "Backend environment variables configured!"
echo "Now redeploy: vercel --prod"
