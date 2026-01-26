#!/bin/bash
# Frontend Environment Variables Setup Script
# Run this from the frontend directory

echo "Setting up frontend environment variables..."

# You'll be prompted to enter values for each variable
vercel env add NEXT_PUBLIC_API_URL production
vercel env add BETTER_AUTH_SECRET production
vercel env add BETTER_AUTH_URL production

echo "Frontend environment variables configured!"
echo "Now redeploy: vercel --prod"
